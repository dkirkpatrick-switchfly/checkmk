#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.
from collections.abc import Iterable
from typing import Literal

from typing_extensions import TypedDict

Scope = list[str]
UnixTimeStamp = int  # restrict to positive numbers
Audience = str | list[str]
TokenType = Literal["access_token", "refresh_token"]


class HostGroup(TypedDict):
    alias: str


WSGIResponse = Iterable[bytes]
