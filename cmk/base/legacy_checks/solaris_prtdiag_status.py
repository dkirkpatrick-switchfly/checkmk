#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

# Example output from agent:
# <<<solaris_prtdiag_status>>>
# 0


from cmk.base.check_api import LegacyCheckDefinition
from cmk.base.config import check_info


def inventory_solaris_prtdiag_status(info):
    if info:
        return [(None, None)]
    return []


def check_solaris_prtdiag_status(_no_item, _no_params, info):
    if not info:
        return None

    # 0 No failures or errors are detected in the system.
    # 1 Failures or errors are detected in the system.
    if int(info[0][0]) == 0:
        return 0, "No failures or errors are reported"
    return (
        2,
        "Failures or errors are reported by the system. "
        'Please check the output of "prtdiag -v" for details.',
    )


check_info["solaris_prtdiag_status"] = LegacyCheckDefinition(
    service_name="Hardware Overall State",
    discovery_function=inventory_solaris_prtdiag_status,
    check_function=check_solaris_prtdiag_status,
)
