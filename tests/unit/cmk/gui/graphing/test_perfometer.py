#!/usr/bin/env python3
# Copyright (C) 2023 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from collections.abc import Callable, Mapping, Sequence

import numpy as np
import pytest

from cmk.gui.graphing import (
    get_first_matching_perfometer,
    MetricometerRendererLegacyLogarithmic,
    perfometer_info,
    PerfometerSpec,
    renderer_registry,
)
from cmk.gui.graphing._perfometer import (
    _make_projection,
    _perfometer_possible,
    _PERFOMETER_PROJECTION_PARAMETERS,
    MetricometerRendererLegacyLinear,
    MetricometerRendererPerfometer,
    MetricRendererStack,
)
from cmk.gui.graphing._type_defs import TranslatedMetric, UnitInfo

from cmk.graphing.v1 import metric as metric_api
from cmk.graphing.v1 import perfometer as perfometer_api


@pytest.mark.parametrize(
    "perfometer, translated_metrics",
    [
        pytest.param(
            {
                "type": "linear",
                "segments": ["m1", "m2,m3,+", "m4,10,*"],
                "total": 100.0,
                "label": ("m1,m2,/", "%"),
            },
            {
                "m1": {"value": 1, "unit": "", "color": "#111111"},
                "m2": {"value": 2, "unit": "", "color": "#222222"},
                "m3": {"value": 3, "unit": "", "color": "#333333"},
                "m4": {"value": 4, "unit": "", "color": "#444444"},
            },
            id="linear with total float",
        ),
        pytest.param(
            {
                "type": "linear",
                "segments": ["m1", "m2,m3,+", "m4,10,*"],
                "total": "m5:max",
                "label": ("m1,m2,/", "%"),
            },
            {
                "m1": {"value": 1, "unit": "", "color": "#111111"},
                "m2": {"value": 2, "unit": "", "color": "#222222"},
                "m3": {"value": 3, "unit": "", "color": "#333333"},
                "m4": {"value": 4, "unit": "", "color": "#444444"},
                "m5": {"value": 5, "unit": "", "color": "#555555", "scalar": {"max": 5}},
            },
            id="linear with total RPN expression",
        ),
        pytest.param(
            {
                "type": "linear",
                "segments": ["m1", "m2,m3,+", "m4,10,*"],
                "total": 100.0,
                "condition": "m1,m2,<",
            },
            {
                "m1": {"value": 1, "unit": "", "color": "#111111"},
                "m2": {"value": 2, "unit": "", "color": "#222222"},
                "m3": {"value": 3, "unit": "", "color": "#333333"},
                "m4": {"value": 4, "unit": "", "color": "#444444"},
            },
            id="linear with condition",
        ),
        pytest.param(
            {
                "type": "logarithmic",
                "metric": "m1",
                "half_value": 5,
                "exponent": 2,
            },
            {
                "m1": {"value": 1, "unit": "", "color": "#111111"},
            },
            id="logarithmic with metric name",
        ),
        pytest.param(
            {
                "type": "logarithmic",
                "metric": "m1,m2,+",
                "half_value": 5,
                "exponent": 2,
            },
            {
                "m1": {"value": 1, "unit": "", "color": "#111111"},
                "m2": {"value": 2, "unit": "", "color": "#222222"},
            },
            id="logarithmic with RPN expression",
        ),
    ],
)
def test__perfometer_possible(
    perfometer: PerfometerSpec,
    translated_metrics: Mapping[str, TranslatedMetric],
) -> None:
    assert _perfometer_possible(perfometer, translated_metrics)


@pytest.mark.parametrize(
    "translated_metrics, perfometer",
    [
        pytest.param(
            {"active_connections": {}},
            perfometer_api.Perfometer(
                name="active_connections",
                focus_range=perfometer_api.FocusRange(
                    lower=perfometer_api.Closed(value=0),
                    upper=perfometer_api.Open(value=2500.0),
                ),
                segments=["active_connections"],
            ),
            id="very first perfometer",
        ),
    ],
)
def test_get_first_matching_perfometer(
    translated_metrics: Mapping[str, TranslatedMetric],
    perfometer: perfometer_api.Perfometer | perfometer_api.Bidirectional | perfometer_api.Stacked,
) -> None:
    assert get_first_matching_perfometer(translated_metrics) == perfometer


@pytest.mark.parametrize(
    "translated_metrics, perfometer_index",
    [
        pytest.param(
            {
                "delivered_notifications": {"value": 0, "unit": "", "color": "#123456"},
                "failed_notifications": {"value": 0, "unit": "", "color": "#456789"},
            },
            -4,
            id="fourth from last",
        ),
        pytest.param(
            {
                "delivered_notifications": {"value": 0, "unit": "", "color": "#123456"},
                "failed_notifications": {"value": 1, "unit": "", "color": "#456789"},
            },
            -3,
            id="third from last",
        ),
        pytest.param(
            {"robotmk_suite_runtime": {}},
            -2,
            id="second from last",
        ),
        pytest.param(
            {"robotmk_test_runtime": {}},
            -1,
            id="very last perfometer",
        ),
        pytest.param(
            {
                "fs_used": {"value": 10, "scalar": {"max": 30}, "unit": "", "color": "#123456"},
                "uncommitted": {"value": 4, "unit": "", "color": "#123456"},
                "fs_size": {"value": 15, "unit": "", "color": "#123456"},
            },
            61,
            id="filesystem check without overcommittment",
        ),
        pytest.param(
            {
                "fs_used": {"value": 10, "scalar": {"max": 100}, "unit": "", "color": "#123456"},
                "uncommitted": {"value": 4, "unit": "", "color": "#123456"},
                "fs_size": {"value": 15, "unit": "", "color": "#123456"},
                "overprovisioned": {"value": 7, "unit": "", "color": "#123456"},
            },
            61,
            id="filesystem check without overcommittment (+overprovisioned)",
        ),
        pytest.param(
            {
                "fs_used": {"value": 10, "scalar": {"max": 100}, "unit": "", "color": "#123456"},
                "uncommitted": {"value": 5, "unit": "", "color": "#123456"},
                "fs_size": {"value": 15, "unit": "", "color": "#123456"},
                "overprovisioned": {"value": 7, "unit": "", "color": "#123456"},
            },
            62,
            id="filesystem check with overcommittment",
        ),
    ],
)
def test_get_first_matching_legacy_perfometer(
    translated_metrics: Mapping[str, TranslatedMetric], perfometer_index: int
) -> None:
    assert get_first_matching_perfometer(translated_metrics) == perfometer_info[perfometer_index]


def test_registered_renderers() -> None:
    registered_plugins = sorted(renderer_registry.keys())
    assert registered_plugins == sorted(
        [
            "perfometer",
            "bidirectional",
            "stacked",
            "legacy_dual",
            "legacy_linear",
            "legacy_logarithmic",
            "legacy_stacked",
        ]
    )


class TestMetricometerRendererLegacyLinear:
    def _renderer(
        self,
        unit_info: UnitInfo,
    ) -> MetricometerRendererLegacyLinear:
        return MetricometerRendererLegacyLinear(
            {
                "type": "linear",
                "segments": ["my_metric"],
                "total": 100.0,
            },
            {
                "my_metric": {
                    "orig_name": ["my_metric"],
                    "value": 60.0,
                    "scalar": {"warn": 80.0, "crit": 90.0},
                    "scale": [1.0],
                    "auto_graph": True,
                    "title": "My metric",
                    "unit": unit_info,
                    "color": "#ffa000",
                }
            },
        )

    @pytest.mark.parametrize(
        ["unit_info", "expected_result"],
        [
            pytest.param(
                {
                    "title": "My unit",
                    "symbol": "U",
                    "render": str,
                    "js_render": "v => cmk.number_format.drop_dotzero(v) + ' U'",
                    "id": "u",
                    "description": "My unit",
                },
                [[(60.0, "#ffa000"), (40.0, "#bdbdbd")]],
                id="no unit conversion",
            ),
            pytest.param(
                {
                    "title": "My unit",
                    "symbol": "U",
                    "render": str,
                    "js_render": "v => cmk.number_format.drop_dotzero(v) + ' U'",
                    "id": "u",
                    "description": "My unit",
                    "conversion": lambda v: 2 * v - 10,
                },
                [
                    [
                        (60.0 / (2 * 100 - 10) * 100, "#ffa000"),
                        (100 - 60.0 / (2 * 100 - 10) * 100, "#bdbdbd"),
                    ]
                ],
                id="with unit conversion",
            ),
        ],
    )
    def test_get_stack(
        self,
        unit_info: UnitInfo,
        expected_result: MetricRendererStack,
    ) -> None:
        assert self._renderer(unit_info).get_stack() == expected_result

    @pytest.mark.parametrize(
        ["perfometer_render", "expected_result"],
        [
            pytest.param(
                None,
                "60.0",
                id="no dedicated perfometer renderer",
            ),
            pytest.param(
                lambda v: f"{2*v} U",
                "120.0 U",
                id="dedicated perfometer renderer",
            ),
        ],
    )
    def test_get_label(
        self,
        perfometer_render: Callable[[float], str] | None,
        expected_result: str,
    ) -> None:
        unit_info: UnitInfo = {
            "title": "My unit",
            "symbol": "U",
            "render": str,
            "js_render": "v => cmk.number_format.drop_dotzero(v) + ' U'",
            "id": "u",
            "description": "My unit",
        }
        if perfometer_render:
            unit_info["perfometer_render"] = perfometer_render
        assert self._renderer(unit_info).get_label() == expected_result


class TestMetricometerRendererLegacyLogarithmic:
    def _renderer(
        self,
        unit_info: UnitInfo,
    ) -> MetricometerRendererLegacyLogarithmic:
        return MetricometerRendererLegacyLogarithmic(
            {
                "type": "logarithmic",
                "metric": "my_metric",
                "half_value": 40.0,
                "exponent": 1.2,
            },
            {
                "my_metric": {
                    "orig_name": ["my_metric"],
                    "value": 123.0,
                    "scalar": {"warn": 158.0, "crit": 176.0},
                    "scale": [1.0],
                    "auto_graph": True,
                    "title": "My metric",
                    "unit": unit_info,
                    "color": "#ffa000",
                }
            },
        )

    @pytest.mark.parametrize(
        ["conversion", "expected_result"],
        [
            pytest.param(
                lambda v: v,
                (40, 1.2),
                id="no-op conversion",
            ),
            # a purely multiplicate conversion should not lead to change in the 10%-factor
            pytest.param(
                lambda v: 0.7 * v,
                (0.7 * 40, 1.2),
                id="multiplicative stretch only",
            ),
            # a huge additive offset should lead to a multiplicate 10%-factor very close to 1
            pytest.param(
                lambda v: v + 1000000,
                (40 + 1000000, 1.0),
                id="huge additive offset",
            ),
        ],
    )
    def test_estimate_parameters_for_converted_units(
        self,
        conversion: Callable[[float], float],
        expected_result: tuple[float, float],
    ) -> None:
        assert np.allclose(
            self._renderer(
                {
                    "title": "My unit",
                    "symbol": "U",
                    "render": str,
                    "js_render": "v => cmk.number_format.drop_dotzero(v) + ' U'",
                    "id": "u",
                    "description": "My unit",
                    "perfometer_render": lambda _v: "testing",
                }
            ).estimate_parameters_for_converted_units(conversion),
            expected_result,
        )

    @pytest.mark.parametrize(
        ["perfometer_render", "expected_result"],
        [
            pytest.param(
                None,
                "123.0",
                id="no dedicated perfometer renderer",
            ),
            pytest.param(
                lambda v: f"{2*v} U",
                "246.0 U",
                id="dedicated perfometer renderer",
            ),
        ],
    )
    def test_get_label(
        self,
        perfometer_render: Callable[[float], str] | None,
        expected_result: str,
    ) -> None:
        unit_info: UnitInfo = {
            "title": "My unit",
            "symbol": "U",
            "render": str,
            "js_render": "v => cmk.number_format.drop_dotzero(v) + ' U'",
            "id": "u",
            "description": "My unit",
        }
        if perfometer_render:
            unit_info["perfometer_render"] = perfometer_render
        assert self._renderer(unit_info).get_label() == expected_result


@pytest.mark.parametrize(
    "focus_range",
    [
        pytest.param(
            perfometer_api.FocusRange(perfometer_api.Closed(10), perfometer_api.Closed(-10)),
            id="closed-closed",
        ),
        pytest.param(
            perfometer_api.FocusRange(perfometer_api.Open(10), perfometer_api.Closed(-10)),
            id="open-closed",
        ),
        pytest.param(
            perfometer_api.FocusRange(perfometer_api.Closed(10), perfometer_api.Open(-10)),
            id="closed-open",
        ),
        pytest.param(
            perfometer_api.FocusRange(perfometer_api.Open(10), perfometer_api.Open(-10)),
            id="open-open",
        ),
    ],
)
def test_perfometer_projection_error(focus_range: perfometer_api.FocusRange) -> None:
    with pytest.raises(ValueError):
        _make_projection(focus_range, _PERFOMETER_PROJECTION_PARAMETERS, {})


@pytest.mark.parametrize(
    "value, result",
    [
        pytest.param(-10, 0.0, id="left"),
        pytest.param(5, 50.0, id="middle"),
        pytest.param(20, 100.0, id="right"),
    ],
)
def test_perfometer_projection_closed_closed(value: int | float, result: float) -> None:
    projection = _make_projection(
        perfometer_api.FocusRange(perfometer_api.Closed(-10), perfometer_api.Closed(20)),
        _PERFOMETER_PROJECTION_PARAMETERS,
        {},
    )
    assert projection(value) == result


@pytest.mark.parametrize(
    "value",
    [
        pytest.param(-11, id="left-too-low"),
        pytest.param(21, id="right-too-high"),
    ],
)
def test_perfometer_projection_closed_closed_error(value: int | float) -> None:
    projection = _make_projection(
        perfometer_api.FocusRange(perfometer_api.Closed(-10), perfometer_api.Closed(20)),
        _PERFOMETER_PROJECTION_PARAMETERS,
        {},
    )
    with pytest.raises(ValueError):
        projection(value)


@pytest.mark.parametrize(
    "value, result",
    [
        pytest.param(-11, 14.777817878976812, id="left-lower"),
        pytest.param(-10, 15.0, id="left"),
        pytest.param(5, 57.5, id="middle"),
        pytest.param(20, 100.0, id="right"),
    ],
)
def test_perfometer_projection_open_closed(value: int | float, result: float) -> None:
    projection = _make_projection(
        perfometer_api.FocusRange(perfometer_api.Open(-10), perfometer_api.Closed(20)),
        _PERFOMETER_PROJECTION_PARAMETERS,
        {},
    )
    assert projection(value) == result


@pytest.mark.parametrize(
    "value",
    [
        pytest.param(21, id="right-too-high"),
    ],
)
def test_perfometer_projection_open_closed_error(value: int | float) -> None:
    projection = _make_projection(
        perfometer_api.FocusRange(perfometer_api.Open(-10), perfometer_api.Closed(20)),
        _PERFOMETER_PROJECTION_PARAMETERS,
        {},
    )
    with pytest.raises(ValueError):
        projection(value)


@pytest.mark.parametrize(
    "value, result",
    [
        pytest.param(-10, 0.0, id="left"),
        pytest.param(5, 42.5, id="middle"),
        pytest.param(20, 85.0, id="right"),
        pytest.param(21, 85.2221821210232, id="right-higher"),
    ],
)
def test_perfometer_projection_closed_open(value: int | float, result: float) -> None:
    projection = _make_projection(
        perfometer_api.FocusRange(perfometer_api.Closed(-10), perfometer_api.Open(20)),
        _PERFOMETER_PROJECTION_PARAMETERS,
        {},
    )
    assert projection(value) == result


@pytest.mark.parametrize(
    "value",
    [
        pytest.param(-11, id="left-too-low"),
    ],
)
def test_perfometer_projection_closed_open_error(value: int | float) -> None:
    projection = _make_projection(
        perfometer_api.FocusRange(perfometer_api.Closed(-10), perfometer_api.Open(20)),
        _PERFOMETER_PROJECTION_PARAMETERS,
        {},
    )
    with pytest.raises(ValueError):
        projection(value)


@pytest.mark.parametrize(
    "value, result",
    [
        pytest.param(-11, 14.777817878976812, id="left-lower"),
        pytest.param(-10, 15.0, id="left"),
        pytest.param(5, 50.0, id="middle"),
        pytest.param(20, 85.0, id="right"),
        pytest.param(21, 85.2221821210232, id="right-higher"),
    ],
)
def test_perfometer_projection_open_open(value: int | float, result: float) -> None:
    projection = _make_projection(
        perfometer_api.FocusRange(perfometer_api.Open(-10), perfometer_api.Open(20)),
        _PERFOMETER_PROJECTION_PARAMETERS,
        {},
    )
    assert projection(value) == result


@pytest.mark.parametrize(
    "segments, translated_metrics, value_projections",
    [
        pytest.param(
            ["metric-name"],
            {
                "metric-name": {
                    "orig_name": ["metric-name"],
                    "value": 2600.0,
                    "scalar": {},
                    "scale": [1.0],
                    "auto_graph": True,
                    "title": "Metric name 1",
                    "unit": {
                        "title": "Title",
                        "symbol": "",
                        "render": lambda v: f"{v}",
                        "js_render": "v => v",
                    },
                    "color": "#111111",
                },
            },
            [(85.27, "#111111")],
            id="one-metric",
        ),
        pytest.param(
            ["metric-name1", "metric-name2"],
            {
                "metric-name1": {
                    "orig_name": ["metric-name1"],
                    "value": 2000.0,
                    "scalar": {},
                    "scale": [1.0],
                    "auto_graph": True,
                    "title": "Metric name 1",
                    "unit": {
                        "title": "Title",
                        "symbol": "",
                        "render": lambda v: f"{v}",
                        "js_render": "v => v",
                    },
                    "color": "#111111",
                },
                "metric-name2": {
                    "orig_name": ["metric-name2"],
                    "value": 600.0,
                    "scalar": {},
                    "scale": [1.0],
                    "auto_graph": True,
                    "title": "Metric name 2",
                    "unit": {
                        "title": "Title",
                        "symbol": "",
                        "render": lambda v: f"{v}",
                        "js_render": "v => v",
                    },
                    "color": "#222222",
                },
            },
            [(65.59, "#111111"), (19.68, "#222222")],
            id="two-metrics",
        ),
        pytest.param(
            ["metric-name1", "metric-name2", "metric-name3"],
            {
                "metric-name1": {
                    "orig_name": ["metric-name1"],
                    "value": 2000.0,
                    "scalar": {},
                    "scale": [1.0],
                    "auto_graph": True,
                    "title": "Metric name 1",
                    "unit": {
                        "title": "Title",
                        "symbol": "",
                        "render": lambda v: f"{v}",
                        "js_render": "v => v",
                    },
                    "color": "#111111",
                },
                "metric-name2": {
                    "orig_name": ["metric-name2"],
                    "value": 400.0,
                    "scalar": {},
                    "scale": [1.0],
                    "auto_graph": True,
                    "title": "Metric name 2",
                    "unit": {
                        "title": "Title",
                        "symbol": "",
                        "render": lambda v: f"{v}",
                        "js_render": "v => v",
                    },
                    "color": "#222222",
                },
                "metric-name3": {
                    "orig_name": ["metric-name3"],
                    "value": 200.0,
                    "scalar": {},
                    "scale": [1.0],
                    "auto_graph": True,
                    "title": "Metric name 3",
                    "unit": {
                        "title": "Title",
                        "symbol": "",
                        "render": lambda v: f"{v}",
                        "js_render": "v => v",
                    },
                    "color": "#333333",
                },
            },
            [(65.59, "#111111"), (13.12, "#222222"), (6.56, "#333333")],
            id="three-metrics",
        ),
    ],
)
def test_perfometer_renderer_stack(
    segments: Sequence[
        str
        | metric_api.Constant
        | metric_api.WarningOf
        | metric_api.CriticalOf
        | metric_api.MinimumOf
        | metric_api.MaximumOf
        | metric_api.Sum
        | metric_api.Product
        | metric_api.Difference
        | metric_api.Fraction
    ],
    translated_metrics: Mapping[str, TranslatedMetric],
    value_projections: Sequence[tuple[float, str]],
) -> None:
    assert MetricometerRendererPerfometer(
        perfometer_api.Perfometer(
            "name",
            perfometer_api.FocusRange(perfometer_api.Closed(0), perfometer_api.Open(2500.0)),
            segments,
        ),
        translated_metrics,
    ).get_stack() == [list(value_projections) + [(14.73, "#bdbdbd")]]


def test_perfometer_renderer_stack_same_values() -> None:
    assert MetricometerRendererPerfometer(
        perfometer_api.Perfometer(
            "name",
            perfometer_api.FocusRange(perfometer_api.Closed(0), perfometer_api.Open(2500.0)),
            ["metric-name1", "metric-name2"],
        ),
        {
            "metric-name1": {
                "orig_name": ["metric-name1"],
                "value": 1300.0,
                "scalar": {},
                "scale": [1.0],
                "auto_graph": True,
                "title": "Metric name 1",
                "unit": {
                    "title": "Title",
                    "symbol": "",
                    "render": lambda v: f"{v}",
                    "js_render": "v => v",
                },
                "color": "#111111",
            },
            "metric-name2": {
                "orig_name": ["metric-name2"],
                "value": 1300.0,
                "scalar": {},
                "scale": [1.0],
                "auto_graph": True,
                "title": "Metric name 2",
                "unit": {
                    "title": "Title",
                    "symbol": "",
                    "render": lambda v: f"{v}",
                    "js_render": "v => v",
                },
                "color": "#222222",
            },
        },
    ).get_stack() == [[(42.63, "#111111"), (42.63, "#222222"), (14.74, "#bdbdbd")]]
