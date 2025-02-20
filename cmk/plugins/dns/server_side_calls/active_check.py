#!/usr/bin/env python3
# Copyright (C) 2023 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

# {} -> Default was 'This host'
# server: None -> 'This host'
# server: "default DNS server" -> will omit the option "-s" for check_dns
# server: "str"

from collections.abc import Iterator

from pydantic import BaseModel

from cmk.server_side_calls.v1 import ActiveCheckCommand, ActiveCheckConfig, HostConfig


class Params(BaseModel, frozen=True):
    name: str | None = None
    server: str | None = None
    expect_all_addresses: bool = True
    expected_addresses_list: tuple[str, ...] = ()
    expected_authority: bool | None = None
    response_time: tuple[float, float] | None = None
    timeout: int | None = None


def commands_function(
    params: Params,
    host_config: HostConfig,
    _http_proxies: object,
) -> Iterator[ActiveCheckCommand]:
    command_arguments = ["-H", host_config.name]

    if params.server is None:
        if not host_config.address:
            raise ValueError("No IP address available")
        command_arguments += ["-s", host_config.address]
    elif params.server and params.server != "default DNS server":
        command_arguments += ["-s", params.server]

    if params.expect_all_addresses:
        command_arguments.append("-L")

    for address in params.expected_addresses_list:
        command_arguments += ["-a", address]

    if params.expected_authority:
        command_arguments.append("-A")

    if params.response_time:
        warn, crit = params.response_time
        command_arguments += ["-w", "%f" % warn]
        command_arguments += ["-c", "%f" % crit]

    if params.timeout:
        command_arguments += ["-t", str(params.timeout)]

    yield ActiveCheckCommand(
        service_description=(params.name if params.name else f"DNS {host_config.name}"),
        command_arguments=command_arguments,
    )


active_check_dns = ActiveCheckConfig(
    name="dns",
    parameter_parser=Params.model_validate,
    commands_function=commands_function,
)
