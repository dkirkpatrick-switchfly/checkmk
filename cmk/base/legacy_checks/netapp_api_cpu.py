#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.


import time

from cmk.base.check_api import LegacyCheckDefinition
from cmk.base.check_legacy_includes.cpu_util import check_cpu_util
from cmk.base.config import check_info
from cmk.base.plugins.agent_based.agent_based_api.v1 import get_rate, get_value_store

# 7mode
# <<<netapp_api_cpu:sep(9)>>>
# cpu_busy        8362860064
# num_processors  2

# clustermode
# cpu-info clu1-01        num_processors 2
# cpu-info clu1-02        num_processors 2
# cpu-info clu1-01        cpu_busy 5340000        nvram-battery-status battery_ok
# cpu-info clu1-02        cpu_busy 5400000        nvram-battery-status battery_ok


def inventory_netapp_api_cpu_utilization(parsed):
    if "7mode" in parsed:
        yield None, {}


def inventory_netapp_api_cpu(parsed):
    if "clustermode" in parsed:
        for node in parsed.get("clustermode", {}):
            yield node, {}


def check_netapp_api_cpu_utilization(item, params, parsed, mode):
    mode_data = parsed.get(mode)
    if item:
        data = mode_data.get(item)
        if data is None:
            return 3, "No data available!"
    else:
        data = mode_data

    now = time.time()

    cpu_busy = int(data["cpu_busy"])
    num_cpus_str = data.get("num_processors")
    ticks_per_sec = get_rate(
        get_value_store(), "netapp_api_cpu.utilization", now, cpu_busy, raise_overflow=True
    )
    cpusecs_per_sec = ticks_per_sec / 1000000.0
    used_perc = 100.0 * cpusecs_per_sec

    # Due to timeing invariancies the measured level can become > 100%.
    # This makes users unhappy, so cut it off.
    if used_perc < 0:
        used_perc = 0
    elif used_perc > 100:
        used_perc = 100

    state, infotext, perfdata = next(check_cpu_util(used_perc, params, now))
    if num_cpus_str is not None:
        num_cpus = int(num_cpus_str)
        perfdata[0] = perfdata[0][:5] + (num_cpus,)
        infotext += ", %d CPUs" % num_cpus
    else:
        perfdata[0] = perfdata[0][:5] + (1,)

    return state, infotext, perfdata


# Clustermode CPU utilization
check_info["netapp_api_cpu"] = LegacyCheckDefinition(
    service_name="CPU utilization Node %s",
    discovery_function=inventory_netapp_api_cpu,
    check_function=lambda item, params, parsed: check_netapp_api_cpu_utilization(
        item, params, parsed, "clustermode"
    ),
    check_ruleset_name="cpu_utilization_multiitem",
)

# 7Mode CPU utilization
check_info["netapp_api_cpu.utilization"] = LegacyCheckDefinition(
    service_name="CPU utilization",
    sections=["netapp_api_cpu"],
    discovery_function=inventory_netapp_api_cpu_utilization,
    check_function=lambda item, params, parsed: check_netapp_api_cpu_utilization(
        item, params, parsed, "7mode"
    ),
    check_ruleset_name="cpu_utilization",
    check_default_parameters={"util": (90.0, 95.0)},
)


def inventory_netapp_api_nvram_bat(parsed):
    for node, values in parsed.get("clustermode", {}).items():
        if "nvram-battery-status" in values:
            yield node, None


def check_netapp_api_nvram_bat(item, _no_params, parsed):
    state_map = {
        "battery_ok": 0,
        "battery_partially_discharged": 0,
        "battery_fully_discharged ": 2,
        "battery_not_present": 2,
        "battery_near_end_of_life": 1,
        "battery_at_end_of_life": 2,
        "battery_unknown": 3,
        "battery_over_charged": 1,
        "battery_fully_charged": 0,
    }

    info = parsed.get("clustermode", {}).get(item)
    if not info or "nvram-battery-status" not in info:
        return

    yield state_map.get(info["nvram-battery-status"], 3), "Status: %s" % info[
        "nvram-battery-status"
    ].replace("_", " ").title()


# Clustermode NVRAM Bat
check_info["netapp_api_cpu.nvram_bat"] = LegacyCheckDefinition(
    service_name="NVRAM Battery %s",
    sections=["netapp_api_cpu"],
    discovery_function=inventory_netapp_api_nvram_bat,
    check_function=check_netapp_api_nvram_bat,
)
