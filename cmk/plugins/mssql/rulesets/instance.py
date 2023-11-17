#!/usr/bin/env python3
# Copyright (C) 2023 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from cmk.rulesets.v1 import (
    CheckParameterRuleSpecWithItem,
    DictElement,
    Dictionary,
    Localizable,
    MonitoringState,
    State,
    TextInput,
    Topic,
)


def _parameter_form_mssql_instance() -> Dictionary:
    return Dictionary(
        elements={
            "map_connection_state": DictElement(
                MonitoringState(title=Localizable("Connection status"), prefill_value=State.CRIT)
            ),
        }
    )


rule_spec_mssql_instance = CheckParameterRuleSpecWithItem(
    name="mssql_instance",
    title=Localizable("MSSQL Instance"),
    topic=Topic.APPLICATIONS,
    item_form=TextInput(title=Localizable("Instance identifier")),
    parameter_form=_parameter_form_mssql_instance,
)
