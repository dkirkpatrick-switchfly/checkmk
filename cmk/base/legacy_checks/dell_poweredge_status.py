#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.


from cmk.base.check_api import LegacyCheckDefinition
from cmk.base.check_legacy_includes.dell_poweredge import check_dell_poweredge_status
from cmk.base.config import check_info
from cmk.base.plugins.agent_based.agent_based_api.v1 import SNMPTree

from cmk.plugins.lib.dell import DETECT_IDRAC_POWEREDGE


def inventory_dell_poweredge_status(info):
    if info:
        return [(None, None)]
    return []


check_info["dell_poweredge_status"] = LegacyCheckDefinition(
    detect=DETECT_IDRAC_POWEREDGE,
    fetch=SNMPTree(
        base=".1.3.6.1.4.1.674.10892.5",
        oids=[
            "1.1.6.0",
            "1.2.2.0",
            "1.3.5.0",
            "1.3.12.0",
            "2.1.0",
            "4.300.10.1.11.1",
            "4.300.10.1.49.1",
        ],
    ),
    service_name="PowerEdge Health",
    discovery_function=inventory_dell_poweredge_status,
    check_function=check_dell_poweredge_status,
)
