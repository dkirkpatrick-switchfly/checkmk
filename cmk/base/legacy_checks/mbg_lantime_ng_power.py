#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from cmk.base.check_api import LegacyCheckDefinition
from cmk.base.config import check_info
from cmk.base.plugins.agent_based.agent_based_api.v1 import SNMPTree

from cmk.plugins.lib.mbg_lantime import DETECT_MBG_LANTIME_NG


def inventory_mbg_lantime_ng_power(info):
    for line in info:
        yield line[0], None


def check_mbg_lantime_ng_power(item, _no_params, info):
    power_states = {
        "0": (2, "not available"),
        "1": (2, "down"),
        "2": (0, "up"),
    }
    for index, power_status in info:
        if item == index:
            power_state, power_state_name = power_states[power_status]
            infotext = "Status: %s" % power_state_name
            return power_state, infotext
    return None


check_info["mbg_lantime_ng_power"] = LegacyCheckDefinition(
    detect=DETECT_MBG_LANTIME_NG,
    fetch=SNMPTree(
        base=".1.3.6.1.4.1.5597.30.0.5.0.2.1",
        oids=["1", "2"],
    ),
    service_name="Power Supply %s",
    discovery_function=inventory_mbg_lantime_ng_power,
    check_function=check_mbg_lantime_ng_power,
)
