#!/usr/bin/env python3
# Copyright (C) 2020 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.


import json
from collections.abc import Callable, Iterable, Mapping, Sequence

from cmk.base.check_api import check_levels, get_bytes_human_readable, LegacyCheckDefinition
from cmk.base.check_legacy_includes.mem import check_memory_element
from cmk.base.check_legacy_includes.uptime import check_uptime_seconds
from cmk.base.config import check_info
from cmk.base.plugins.agent_based.agent_based_api.v1 import render

# <<<rabbitmq_nodes>>>
# {"fd_total": 1098576, "sockets_total": 973629, "mem_limit": 6808874700,
# "mem_alarm": false, "disk_free_limit": 70000000, "disk_free_alarm": false,
# "proc_total": 1088576, "run_queue": 1, "name": "rabbit@my-rabbit", "type":
# "disc", "running": true, "mem_key": 108834752, "fd_key": 35,
# "sockets_key": 0, "proc_key": 429, "gc_num": 70927, "gc_bytes_reclaimed":
# 1586846120, "io_file_handle_open_attempt_count": 13, "node_links":
# []}
# {"fd_total": 1048576, "sockets_total": 943629, "mem_limit": 6608874700,
# "mem_alarm": false, "disk_free_limit": 50000000, "disk_free_alarm": false,
# "proc_total": 1048576, "run_queue": 1, "name": "rabbit2@my-rabbit", "type":
# "disc", "running": true, "mem_key": 101834752, "fd_key": 33,
# "sockets_key": 0, "proc_key": 426, "gc_num": 70827, "gc_bytes_reclaimed":
# 1556846120, "io_file_handle_open_attempt_count": 11, "node_links":
# []}

_ItemData = dict

Section = Mapping[str, _ItemData]


def discover_key(key: str) -> Callable[[Section], Iterable[tuple[str, dict]]]:
    def _discover_bound_key(section: Section) -> Iterable[tuple[str, dict]]:
        yield from ((item, {}) for item, data in section.items() if key in data)

    return _discover_bound_key


def parse_rabbitmq_nodes(string_table):
    parsed: dict[str, _ItemData] = {}

    for nodes in string_table:
        for node_json in nodes:
            node = json.loads(node_json)

            node_name = node.get("name")
            if node_name is not None:
                fd_stats = {
                    "fd_used": node.get("fd_used"),
                    "fd_total": node.get("fd_total"),
                    "fd_open": node.get("io_file_handle_open_attempt_count"),
                    "fd_open_rate": node.get("io_file_handle_open_attempt_count_details", {}).get(
                        "rate"
                    ),
                }

                sockets = {
                    "sockets_used": node.get("sockets_used"),
                    "sockets_total": node.get("sockets_total"),
                }

                proc = {
                    "proc_used": node.get("proc_used"),
                    "proc_total": node.get("proc_total"),
                }

                mem = {
                    "mem_used": node.get("mem_used"),
                    "mem_limit": node.get("mem_limit"),
                }

                gc_stats = {
                    "gc_num": node.get("gc_num"),
                    "gc_num_rate": node.get("gc_num_details", {}).get("rate"),
                    "gc_bytes_reclaimed": node.get("gc_bytes_reclaimed"),
                    "gc_bytes_reclaimed_rate": node.get("gc_bytes_reclaimed_details", {}).get(
                        "rate"
                    ),
                    "run_queue": node.get("run_queue"),
                }

                uptime = {"uptime": node.get("uptime")}

                parsed.setdefault(
                    node_name,
                    {
                        "type": node.get("type"),
                        "state": node.get("running"),
                        "disk_free_alarm": node.get("disk_free_alarm"),
                        "mem_alarm": node.get("mem_alarm"),
                        "fd": fd_stats,
                        "sockets": sockets,
                        "proc": proc,
                        "mem": mem,
                        "gc": gc_stats,
                        "uptime": uptime,
                    },
                )

    return parsed


def discover_rabbitmq_nodes(section: Section) -> Iterable[tuple[str, dict]]:
    yield from ((item, {}) for item in section)


def check_rabbitmq_nodes(item, params, parsed):
    if not (data := parsed.get(item)):
        return

    node_type = data.get("type")
    if node_type is not None:
        yield 0, "Type: %s" % node_type.title()

    node_state = data.get("state")
    if node_state is not None:
        state = 0
        if not node_state:
            state = params.get("state")
        yield state, "Is running: %s" % str(node_state).replace("True", "yes").replace(
            "False", "no"
        )

    for alarm_key, alarm_infotext in [
        ("disk_free_alarm", "Disk alarm in effect"),
        ("mem_alarm", "Memory alarm in effect"),
    ]:
        alarm_value = data.get(alarm_key)
        if alarm_value is None:
            continue

        alarm_state = 0
        if alarm_value:
            alarm_state = params.get(alarm_key)

            yield alarm_state, "{}: {}".format(
                alarm_infotext,
                str(alarm_value).replace("True", "yes").replace("False", "no"),
            )


check_info["rabbitmq_nodes"] = LegacyCheckDefinition(
    parse_function=parse_rabbitmq_nodes,
    service_name="RabbitMQ Node %s",
    discovery_function=discover_rabbitmq_nodes,
    check_function=check_rabbitmq_nodes,
    check_ruleset_name="rabbitmq_nodes",
    check_default_parameters={
        "state": 2,
        "disk_free_alarm": 2,
        "mem_alarm": 2,
    },
)


def check_rabbitmq_nodes_filedesc(item, params, parsed):
    fd_data = parsed.get(item, {}).get("fd")
    if not fd_data:
        return

    value = fd_data.get("fd_used")
    if value is None:
        return

    total = fd_data.get("fd_total")
    if total is None:
        return

    yield _handle_output(params, value, total, "File descriptors used", "open_file_descriptors")

    open_fd = fd_data.get("fd_open")
    if open_fd is not None:
        levels_upper = params.get("fd_open_upper", (None, None))

        yield check_levels(
            open_fd,
            "file_descriptors_open_attempts",
            levels_upper,
            human_readable_func=int,
            infoname="File descriptor open attempts",
        )

    open_fd_rate = fd_data.get("fd_open_rate")
    if open_fd_rate is not None:
        levels_upper = params.get("fd_open_rate_upper", (None, None))
        levels_lower = params.get("fd_open_rate_lower", (None, None))

        yield check_levels(
            open_fd_rate,
            "file_descriptors_open_attempts_rate",
            levels_upper + levels_lower,
            human_readable_func=float,
            unit="1/s",
            infoname="Rate",
        )


check_info["rabbitmq_nodes.filedesc"] = LegacyCheckDefinition(
    service_name="RabbitMQ Node %s Filedesc",
    sections=["rabbitmq_nodes"],
    discovery_function=discover_key("fd"),
    check_function=check_rabbitmq_nodes_filedesc,
    check_ruleset_name="rabbitmq_nodes_filedesc",
)


def check_rabbitmq_nodes_sockets(item, params, parsed):
    socket_data = parsed.get(item, {}).get("sockets")
    if not socket_data:
        return None

    value = socket_data.get("sockets_used")
    if value is None:
        return None

    total = socket_data.get("sockets_total")
    if total is None:
        return None

    return _handle_output(params, value, total, "Sockets used", "sockets")


check_info["rabbitmq_nodes.sockets"] = LegacyCheckDefinition(
    service_name="RabbitMQ Node %s Sockets",
    sections=["rabbitmq_nodes"],
    discovery_function=discover_key("sockets"),
    check_function=check_rabbitmq_nodes_sockets,
    check_ruleset_name="rabbitmq_nodes_sockets",
)


def check_rabbitmq_nodes_proc(item, params, parsed):
    proc_data = parsed.get(item, {}).get("proc")
    if not proc_data:
        return None

    used = proc_data.get("proc_used")
    if used is None:
        return None

    total = proc_data.get("proc_total")
    if total is None:
        return None

    return _handle_output(params, used, total, "Erlang processes used", "processes")


check_info["rabbitmq_nodes.proc"] = LegacyCheckDefinition(
    service_name="RabbitMQ Node %s Processes",
    sections=["rabbitmq_nodes"],
    discovery_function=discover_key("proc"),
    check_function=check_rabbitmq_nodes_proc,
    check_ruleset_name="rabbitmq_nodes_proc",
)


def check_rabbitmq_nodes_mem(item, params, parsed):
    mem_data = parsed.get(item, {}).get("mem")
    if not mem_data:
        return

    mem_used = mem_data.get("mem_used")
    if mem_used is None:
        return

    mem_mark = mem_data.get("mem_limit")
    if mem_mark is None:
        return

    warn, crit = params.get("levels", (None, None))
    mode = "abs_used" if isinstance(warn, int) else "perc_used"

    yield check_memory_element(
        "Memory used",
        mem_used,
        mem_mark,
        (mode, (warn, crit)),
        label_total="High watermark",
        metric_name="mem_used",
    )


check_info["rabbitmq_nodes.mem"] = LegacyCheckDefinition(
    service_name="RabbitMQ Node %s Memory",
    sections=["rabbitmq_nodes"],
    discovery_function=discover_key("mem"),
    check_function=check_rabbitmq_nodes_mem,
    check_ruleset_name="memory_multiitem",
)

_UNITS_NODES_GC = {"gc_num_rate": "1/s"}


_METRIC_SPECS: Sequence[tuple[str, str, Callable, str]] = [
    ("gc_num", "GC runs", int, "gc_runs"),
    ("gc_num_rate", "Rate", float, "gc_runs_rate"),
    ("gc_bytes_reclaimed", "Bytes reclaimed by GC", get_bytes_human_readable, "gc_bytes"),
    ("gc_bytes_reclaimed_rate", "Rate", render.iobandwidth, "gc_bytes_rate"),
    ("run_queue", "Runtime run queue", int, "runtime_run_queue"),
]


def check_rabbitmq_nodes_gc(item, params, parsed):
    gc_data = parsed.get(item, {}).get("gc")
    if not gc_data:
        return

    for key, infotext, hr_func, perf_key in _METRIC_SPECS:
        value = gc_data.get(key)
        if value is None:
            continue

        levels_upper = params.get("%s_upper" % key, (None, None))
        levels_lower = params.get("%s_lower" % key, (None, None))

        yield check_levels(
            value,
            perf_key,
            levels_upper + levels_lower,
            human_readable_func=hr_func,
            unit=_UNITS_NODES_GC.get(key, ""),
            infoname=infotext,
        )


def check_rabbitmq_nodes_uptime(item, params, parsed):
    uptime_data = parsed.get(item, {}).get("uptime")
    if not uptime_data:
        return

    node_uptime = uptime_data.get("uptime")
    if node_uptime is not None:
        uptime_sec = float(node_uptime) / 1000.0

        yield check_uptime_seconds(params, uptime_sec)


check_info["rabbitmq_nodes.uptime"] = LegacyCheckDefinition(
    service_name="RabbitMQ Node %s Uptime",
    sections=["rabbitmq_nodes"],
    discovery_function=discover_key("uptime"),
    check_function=check_rabbitmq_nodes_uptime,
    check_ruleset_name="rabbitmq_nodes_uptime",
)


def _handle_output(params, value, total, info_text, perf_key):
    levels = params.get("levels")
    if levels is None:
        warn, crit = (None, None)
    else:
        warn, crit = levels[1]

    perc_value = 100.0 * value / total

    if isinstance(warn, float) and isinstance(crit, float):
        value_check = perc_value
        warn_abs: int | None = int((warn / 100.0) * total)
        crit_abs: int | None = int((crit / 100.0) * total)
        level_msg = " (warn/crit at {}/{})".format(
            render.percent(warn),
            render.percent(crit),
        )
    else:
        value_check = value
        warn_abs = warn
        crit_abs = crit
        level_msg = f" (warn/crit at {warn}/{crit})"

    state, _info, _perf = check_levels(
        value_check,
        None,
        (warn, crit),
    )

    infotext = "{}: {} of {}, {}".format(
        info_text,
        value,
        total,
        render.percent(perc_value),
    )

    if state:
        infotext += level_msg

    # construct perfdata for absolut values even perc levels are set
    return state, infotext, [(perf_key, value, warn_abs, crit_abs, 0, total)]


check_info["rabbitmq_nodes.gc"] = LegacyCheckDefinition(
    service_name="RabbitMQ Node %s GC",
    sections=["rabbitmq_nodes"],
    discovery_function=discover_key("gc"),
    check_function=check_rabbitmq_nodes_gc,
    check_ruleset_name="rabbitmq_nodes_gc",
)
