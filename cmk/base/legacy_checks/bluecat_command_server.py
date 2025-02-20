#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.


from cmk.base.check_api import LegacyCheckDefinition
from cmk.base.config import check_info
from cmk.base.plugins.agent_based.agent_based_api.v1 import SNMPTree

from cmk.plugins.lib.bluecat import DETECT_BLUECAT


def inventory_bluecat_command_server(info):
    return [(None, None)]


def check_bluecat_command_server(item, params, info):
    oper_state = int(info[0][0])
    oper_states = {
        1: "running normally",
        2: "not running",
        3: "currently starting",
        4: "currently stopping",
        5: "fault",
    }
    state = 0
    if oper_state in params["oper_states"]["warning"]:
        state = 1
    elif oper_state in params["oper_states"]["critical"]:
        state = 2
    yield state, "Command Server is %s" % oper_states[oper_state]


check_info["bluecat_command_server"] = LegacyCheckDefinition(
    detect=DETECT_BLUECAT,
    fetch=SNMPTree(
        base=".1.3.6.1.4.1.13315.3.1.7.2.1",
        oids=["1"],
    ),
    service_name="Command Server",
    discovery_function=inventory_bluecat_command_server,
    check_function=check_bluecat_command_server,
    check_ruleset_name="bluecat_command_server",
    check_default_parameters={
        "oper_states": {
            "warning": [2, 3, 4],
            "critical": [5],
        },
    },
)
