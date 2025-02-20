#!/usr/bin/env python3
# Copyright (C) 2020 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.
"""Downtimes

A (scheduled) downtime is a planned maintenance period.
Hosts and services are handled differently by Checkmk during a downtime, for example,
notifications are disabled.

### Related documentation

How to use the query DSL used in the `query` parameters of these endpoints, have a look at the
[Querying Status Data](#section/Querying-Status-Data) section of this documentation.

These endpoints support all [Livestatus filter operators](https://docs.checkmk.com/latest/en/livestatus_references.html#heading_filter),
which you can look up in the Checkmk documentation.

For a detailed list of columns, please take a look at the [downtimes table](https://github.com/checkmk/checkmk/blob/master/cmk/utils/livestatus_helpers/tables/downtimes.py)
definition on GitHub.

### Relations

Downtime object can have the following relations:

 * `self` - The downtime itself.
 * `urn:com.checkmk:rels/host_config` - The host the downtime applies to.
 * `urn:org.restfulobjects/delete` - The endpoint to delete downtimes.

"""
import datetime as dt
import json
from collections.abc import Callable, Mapping
from typing import Any, Literal

from livestatus import SiteId

from cmk.utils.livestatus_helpers.expressions import And, Or, QueryExpression
from cmk.utils.livestatus_helpers.queries import detailed_connection, Query
from cmk.utils.livestatus_helpers.tables import Hosts
from cmk.utils.livestatus_helpers.tables.downtimes import Downtimes

from cmk.gui import fields as gui_fields
from cmk.gui import sites
from cmk.gui.fields.utils import BaseSchema
from cmk.gui.http import Response
from cmk.gui.livestatus_utils.commands import downtimes as downtime_commands
from cmk.gui.livestatus_utils.commands.downtimes import QueryException
from cmk.gui.logged_in import user
from cmk.gui.openapi.endpoints.downtime.request_schemas import (
    CreateHostRelatedDowntime,
    CreateServiceRelatedDowntime,
    DeleteDowntime,
)
from cmk.gui.openapi.endpoints.downtime.response_schemas import DowntimeCollection, DowntimeObject
from cmk.gui.openapi.restful_objects import constructors, Endpoint, permissions
from cmk.gui.openapi.restful_objects.registry import EndpointRegistry
from cmk.gui.openapi.utils import problem, serve_json

from cmk import fields

DowntimeType = Literal[
    "host", "service", "hostgroup", "servicegroup", "host_by_query", "service_by_query"
]

SERVICE_DESCRIPTION_SHOW = {
    "service_description": fields.String(
        description="The service description. No exception is raised when the specified service "
        "description does not exist. This parameter can be combined with the host_name parameter "
        "to only filter for service downtimes of on a specific host. Cannot be used "
        "together with the query parameter.",
        example="Memory",
        required=False,
    )
}

HOST_NAME_SHOW = {
    "host_name": gui_fields.HostField(
        description="The host name. No exception is raised when the specified host name does not "
        "exist. Using this parameter only will filter for host downtimes only. Cannot "
        "be used together with the query parameter.",
        should_exist=None,  # we do not care
        example="example.com",
        required=False,
    )
}

DOWNTIME_TYPE = {
    "downtime_type": fields.String(
        description="The type of the downtime to be listed. Only filters the result when using "
        "the host_name or service_description parameter.",
        enum=["host", "service", "both"],
        example="host",
        load_default="both",
        required=False,
    )
}

PERMISSIONS = permissions.Undocumented(
    permissions.AnyPerm(
        [
            permissions.Perm("general.see_all"),
            permissions.OkayToIgnorePerm("bi.see_all"),
            permissions.OkayToIgnorePerm("mkeventd.seeall"),
            permissions.Perm("wato.see_all_folders"),
        ]
    )
)


RW_PERMISSIONS = permissions.AllPerm(
    [
        permissions.Perm("action.downtimes"),
        PERMISSIONS,
    ]
)


class DowntimeParameter(BaseSchema):
    query = gui_fields.query_field(
        Downtimes,
        required=False,
        example=json.dumps(
            {
                "op": "and",
                "expr": [
                    {"op": "=", "left": "host_name", "right": "example.com"},
                    {"op": "=", "left": "type", "right": "0"},
                ],
            }
        ),
    )


@Endpoint(
    constructors.collection_href("downtime", "host"),
    "cmk/create_host",
    method="post",
    tag_group="Monitoring",
    skip_locking=True,
    request_schema=CreateHostRelatedDowntime,
    additional_status_codes=[422],
    output_empty=True,
    permissions_required=RW_PERMISSIONS,
    update_config_generation=False,
)
def create_host_related_downtime(params: Mapping[str, Any]) -> Response:
    """Create a host related scheduled downtime"""
    body = params["body"]
    live = sites.live()

    downtime_type: DowntimeType = body["downtime_type"]

    if downtime_type == "host":
        downtime_commands.schedule_host_downtime(
            live,
            host_entry=body["host_name"],
            start_time=body["start_time"],
            end_time=body["end_time"],
            recur=body["recur"],
            duration=body["duration"],
            user_id=user.ident,
            comment=body.get("comment", f"Downtime for host {body['host_name']!r}"),
        )
    elif downtime_type == "hostgroup":
        downtime_commands.schedule_hostgroup_host_downtime(
            live,
            hostgroup_name=body["hostgroup_name"],
            start_time=body["start_time"],
            end_time=body["end_time"],
            recur=body["recur"],
            duration=body["duration"],
            user_id=user.ident,
            comment=body.get("comment", f"Downtime for hostgroup {body['hostgroup_name']!r}"),
        )

    elif downtime_type == "host_by_query":
        try:
            downtime_commands.schedule_hosts_downtimes_with_query(
                live,
                body["query"],
                start_time=body["start_time"],
                end_time=body["end_time"],
                recur=body["recur"],
                duration=body["duration"],
                user_id=user.ident,
                comment=body.get("comment", ""),
            )
        except QueryException:
            return problem(
                status=422,
                title="Query did not match any host",
                detail="The provided query returned an empty list so no downtime was set",
            )
    else:
        return problem(
            status=400,
            title="Unhandled downtime-type.",
            detail=f"The downtime-type {downtime_type!r} is not supported.",
        )

    return Response(status=204)


def _with_defaulted_timezone(
    date: dt.datetime,
    _get_local_timezone: Callable[[], dt.tzinfo | None] = lambda: dt.datetime.now(dt.timezone.utc)
    .astimezone()
    .tzinfo,
) -> dt.datetime:
    """Default a datetime to the local timezone.

    Params:
        date: a datetime that might not have a timezone

    Returns: The input datetime if it had a timezone set or
             the input datetime with the local timezone if no timezone was set.
    """
    if date.tzinfo is None:
        date = date.replace(tzinfo=_get_local_timezone())
    return date


@Endpoint(
    constructors.collection_href("downtime", "service"),
    "cmk/create_service",
    method="post",
    tag_group="Monitoring",
    skip_locking=True,
    request_schema=CreateServiceRelatedDowntime,
    additional_status_codes=[422],
    output_empty=True,
    permissions_required=RW_PERMISSIONS,
    update_config_generation=False,
)
def create_service_related_downtime(params: Mapping[str, Any]) -> Response:
    """Create a service related scheduled downtime"""
    body = params["body"]
    live = sites.live()

    downtime_type: DowntimeType = body["downtime_type"]

    if downtime_type == "service":
        host_name = body["host_name"]
        with detailed_connection(live) as conn:
            try:
                site_id = Query(
                    columns=[Hosts.name], filter_expr=Hosts.name.op("=", host_name)
                ).value(conn)
            except ValueError:
                # Request user can't see the host (but may still be able to access the service)
                site_id = None
        start_time = _with_defaulted_timezone(body["start_time"])
        end_time = _with_defaulted_timezone(body["end_time"])
        downtime_commands.schedule_service_downtime(
            live,
            site_id,
            host_name=body["host_name"],
            service_description=body["service_descriptions"],
            start_time=start_time,
            end_time=end_time,
            recur=body["recur"],
            duration=body["duration"],
            user_id=user.ident,
            comment=body.get(
                "comment",
                f"Downtime for services {', '.join(body['service_descriptions'])!r}@{body['host_name']!r}",
            ),
        )
    elif downtime_type == "servicegroup":
        downtime_commands.schedule_servicegroup_service_downtime(
            live,
            servicegroup_name=body["servicegroup_name"],
            start_time=body["start_time"],
            end_time=body["end_time"],
            recur=body["recur"],
            duration=body["duration"],
            user_id=user.ident,
            comment=body.get("comment", f"Downtime for servicegroup {body['servicegroup_name']!r}"),
        )
    elif downtime_type == "service_by_query":
        try:
            downtime_commands.schedule_services_downtimes_with_query(
                live,
                query=body["query"],
                start_time=body["start_time"],
                end_time=body["end_time"],
                recur=body["recur"],
                duration=body["duration"],
                user_id=user.ident,
                comment=body.get("comment", ""),
            )
        except QueryException:
            return problem(
                status=422,
                title="Query did not match any service",
                detail="The provided query returned an empty list so no downtime was set",
            )
    else:
        return problem(
            status=400,
            title="Unhandled downtime-type.",
            detail=f"The downtime-type {downtime_type!r} is not supported.",
        )

    return Response(status=204)


@Endpoint(
    constructors.collection_href("downtime"),
    ".../collection",
    method="get",
    tag_group="Monitoring",
    query_params=[
        HOST_NAME_SHOW,
        SERVICE_DESCRIPTION_SHOW,
        DowntimeParameter,
        DOWNTIME_TYPE,
        {
            "site_id": gui_fields.SiteField(
                description="An existing site id",
                example="heute",
                presence="should_exist",
            )
        },
    ],
    response_schema=DowntimeCollection,
    permissions_required=PERMISSIONS,
)
def show_downtimes(param):
    """Show all scheduled downtimes"""
    return _show_downtimes(param)


def _show_downtimes(param):
    """
    Examples:

        >>> import json
        >>> from cmk.gui.livestatus_utils.testing import simple_expect
        >>> from cmk.gui.openapi.restful_objects.params import to_openapi
        >>> from cmk.gui.fields.utils import tree_to_expr
        >>> with simple_expect() as live:
        ...    _ = live.expect_query("GET downtimes\\nColumns: host_name type\\nFilter: host_name = example.com\\nFilter: type = 0\\nAnd: 2")
        ...    q = Query([Downtimes.host_name, Downtimes.type])
        ...    q = q.filter(tree_to_expr(json.loads(to_openapi([DowntimeParameter], "query")[0]['example']), "downtimes"))
        ...    list(q.iterate(live))
        []

    """

    q = Query(
        [
            Downtimes.id,
            Downtimes.host_name,
            Downtimes.service_description,
            Downtimes.is_service,
            Downtimes.author,
            Downtimes.start_time,
            Downtimes.end_time,
            Downtimes.recurring,
            Downtimes.comment,
        ]
    )

    query_expr = param.get("query")
    host_name = param.get("host_name")
    service_description = param.get("service_description")

    if (downtime_type := param["downtime_type"]) != "both":
        q = q.filter(Downtimes.is_service.equals(1 if downtime_type == "service" else 0))

    if query_expr is not None:
        q = q.filter(query_expr)

    if host_name is not None:
        q = q.filter(Downtimes.host_name.op("=", host_name))

    if service_description is not None:
        q = q.filter(Downtimes.service_description.contains(service_description))

    _site_id: SiteId | None = param.get("site_id")
    return serve_json(
        _serialize_downtimes(
            q.fetchall(sites.live(), True, [_site_id] if _site_id is not None else _site_id)
        )
    )


@Endpoint(
    constructors.object_href("downtime", "{downtime_id}"),
    "cmk/show",
    method="get",
    tag_group="Monitoring",
    path_params=[
        {
            "downtime_id": fields.Integer(
                description="The id of the downtime",
                example="1",
            )
        }
    ],
    query_params=[
        {
            "site_id": gui_fields.SiteField(
                description="An existing site id",
                example="heute",
                presence="should_exist",
                required=True,
            )
        }
    ],
    response_schema=DowntimeObject,
    permissions_required=PERMISSIONS,
)
def show_downtime(params: Mapping[str, Any]) -> Response:
    """Show downtime"""
    live = sites.live()
    downtime_id = params["downtime_id"]
    q = Query(
        columns=[
            Downtimes.id,
            Downtimes.host_name,
            Downtimes.service_description,
            Downtimes.is_service,
            Downtimes.author,
            Downtimes.start_time,
            Downtimes.end_time,
            Downtimes.recurring,
            Downtimes.comment,
        ],
        filter_expr=Downtimes.id.op("=", downtime_id),
    )

    try:
        downtime = q.fetchone(live, True, SiteId(params["site_id"]))
    except ValueError:
        return problem(
            status=404,
            title="The requested downtime was not found",
            detail=f"The downtime id {downtime_id} did not match any downtime",
        )
    return serve_json(_serialize_single_downtime(downtime))


@Endpoint(
    constructors.domain_type_action_href("downtime", "delete"),
    ".../delete",
    method="post",
    tag_group="Monitoring",
    skip_locking=True,
    request_schema=DeleteDowntime,
    output_empty=True,
    permissions_required=RW_PERMISSIONS,
    update_config_generation=False,
)
def delete_downtime(params: Mapping[str, Any]) -> Response:
    """Delete a scheduled downtime"""
    body = params["body"]
    delete_type: Literal["query", "by_id", "params"] = body["delete_type"]

    query_expr: QueryExpression

    site_id: SiteId | None = None
    if delete_type == "query":
        query_expr = body["query"]

    elif delete_type == "by_id":
        query_expr = Downtimes.id == body["downtime_id"]
        site_id = SiteId(body["site_id"])
    else:
        hostname = body["host_name"]
        if "service_descriptions" not in body:
            query_expr = And(Downtimes.host_name.op("=", hostname), Downtimes.is_service.op("=", 0))
        else:
            query_expr = And(
                Downtimes.host_name.op("=", hostname),
                Or(
                    *[
                        Downtimes.service_description == svc_desc
                        for svc_desc in body["service_descriptions"]
                    ]
                ),
            )

    downtime_commands.delete_downtime(sites.live(), query_expr, site_id)
    return Response(status=204)


def _serialize_downtimes(downtimes):
    entries = []
    for downtime in downtimes:
        entries.append(_serialize_single_downtime(downtime))

    return constructors.collection_object(
        "downtime",
        value=entries,
    )


def _serialize_single_downtime(downtime):
    links = []
    if downtime["is_service"]:
        downtime_detail = f"service: {downtime['service_description']}"
    else:
        host_name = downtime["host_name"]
        downtime_detail = f"host: {host_name}"
        links.append(
            constructors.link_rel(
                rel="cmk/host_config",
                href=constructors.object_href("host_config", host_name),
                title="This host of this downtime.",
                method="get",
            )
        )

    downtime_id = downtime["id"]
    return constructors.domain_object(
        domain_type="downtime",
        identifier=str(downtime_id),
        title="Downtime for %s" % downtime_detail,
        extensions=_downtime_properties(downtime),
        links=[
            constructors.link_rel(
                rel=".../delete",
                href=constructors.domain_type_action_href("downtime", "delete"),
                method="post",
                title="Delete the downtime",
                body_params={"delete_type": "by_id", "downtime_id": downtime_id},
            ),
        ],
        editable=False,
        deletable=False,
    )


def _downtime_properties(info):
    return {
        "site_id": info["site"],
        "host_name": info["host_name"],
        "author": info["author"],
        "is_service": "yes" if info["is_service"] else "no",
        "start_time": info["start_time"],
        "end_time": info["end_time"],
        "recurring": "yes" if info["recurring"] else "no",
        "comment": info["comment"],
    }


def register(endpoint_registry: EndpointRegistry) -> None:
    endpoint_registry.register(create_host_related_downtime)
    endpoint_registry.register(create_service_related_downtime)
    endpoint_registry.register(show_downtimes)
    endpoint_registry.register(show_downtime)
    endpoint_registry.register(delete_downtime)
