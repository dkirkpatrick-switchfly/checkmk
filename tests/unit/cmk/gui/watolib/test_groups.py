#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.


from collections.abc import Callable
from typing import ContextManager

import pytest

import cmk.utils.paths

import cmk.gui.groups as gui_groups
from cmk.gui.utils.script_helpers import application_and_request_context
from cmk.gui.watolib.groups import contact_group_usage_finder_registry


@pytest.fixture(autouse=True)
def patch_config_paths(monkeypatch, tmp_path):
    cmk_confd = tmp_path / "check_mk" / "conf.d"
    monkeypatch.setattr(cmk.utils.paths, "check_mk_config_dir", str(cmk_confd))
    (cmk_confd / "wato").mkdir(parents=True)

    gui_confd = tmp_path / "check_mk" / "multisite.d"
    monkeypatch.setattr(cmk.utils.paths, "default_config_dir", str(gui_confd.parent))
    (gui_confd / "wato").mkdir(parents=True)


@pytest.mark.usefixtures("tmp_path")
def test_load_group_information_empty(run_as_superuser: Callable[[], ContextManager[None]]) -> None:
    with application_and_request_context(), run_as_superuser():
        assert gui_groups.load_contact_group_information() == {}
        assert gui_groups.load_host_group_information() == {}
        assert gui_groups.load_service_group_information() == {}


@pytest.mark.usefixtures("tmp_path")
def test_load_group_information(run_as_superuser: Callable[[], ContextManager[None]]) -> None:
    with open(cmk.utils.paths.check_mk_config_dir + "/wato/groups.mk", "w") as f:
        f.write(
            """# encoding: utf-8

define_contactgroups.update({'all': u'Everything'})
define_hostgroups.update({'all_hosts': u'All hosts :-)'})
define_servicegroups.update({'all_services': u'All särvices'})
"""
        )

    with open(cmk.utils.paths.default_config_dir + "/multisite.d/wato/groups.mk", "w") as f:
        f.write(
            """# encoding: utf-8

multisite_hostgroups = {
    "all_hosts": {
        "ding": "dong",
    },
}

multisite_servicegroups = {
    "all_services": {
        "d1ng": "dong",
    },
}

multisite_contactgroups = {
    "all": {
        "d!ng": "dong",
    },
}
"""
        )

    with application_and_request_context(), run_as_superuser():
        assert gui_groups.load_group_information() == {
            "contact": {
                "all": {
                    "alias": "Everything",
                    "d!ng": "dong",
                }
            },
            "host": {
                "all_hosts": {
                    "alias": "All hosts :-)",
                    "ding": "dong",
                }
            },
            "service": {
                "all_services": {
                    "alias": "All s\xe4rvices",
                    "d1ng": "dong",
                }
            },
        }

        assert gui_groups.load_contact_group_information() == {
            "all": {
                "alias": "Everything",
                "d!ng": "dong",
            }
        }

        assert gui_groups.load_host_group_information() == {
            "all_hosts": {
                "alias": "All hosts :-)",
                "ding": "dong",
            }
        }

        assert gui_groups.load_service_group_information() == {
            "all_services": {
                "alias": "All s\xe4rvices",
                "d1ng": "dong",
            }
        }


def test_group_usage_finder_registry_entries() -> None:
    expected = [
        "find_usages_of_contact_group_in_dashboards",
        "find_usages_of_contact_group_in_default_user_profile",
        "find_usages_of_contact_group_in_ec_rules",
        "find_usages_of_contact_group_in_hosts_and_folders",
        "find_usages_of_contact_group_in_mkeventd_notify_contactgroup",
        "find_usages_of_contact_group_in_notification_rules",
        "find_usages_of_contact_group_in_users",
    ]

    registered = [f.__name__ for f in contact_group_usage_finder_registry.values()]
    assert sorted(registered) == sorted(expected)
