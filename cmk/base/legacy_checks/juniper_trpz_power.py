#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.


from cmk.base.check_api import LegacyCheckDefinition, saveint
from cmk.base.config import check_info
from cmk.base.plugins.agent_based.agent_based_api.v1 import SNMPTree

from cmk.plugins.lib.juniper import DETECT_JUNIPER_TRPZ


def inventory_juniper_trpz_power(info):
    return [(line[0], None) for line in info]


def check_juniper_trpz_power(item, _no_params, info):
    states = {
        1: "other",
        2: "unknown",
        3: "ac-failed",
        4: "dc-failed",
        5: "ac-ok-dc-ok",
    }
    for line in info:
        if line[0] == item:
            state = saveint(line[1])
            message = "Current state: %s" % states[state]
            if state in [2, 3, 4]:
                return 2, message
            if state == 1:
                return 1, message
            return 0, message
    return None


check_info["juniper_trpz_power"] = LegacyCheckDefinition(
    detect=DETECT_JUNIPER_TRPZ,
    fetch=SNMPTree(
        base=".1.3.6.1.4.1.14525.4.8.1.1.13.1.2.1",
        oids=["3", "2"],
    ),
    service_name="PSU %s",
    discovery_function=inventory_juniper_trpz_power,
    check_function=check_juniper_trpz_power,
)
