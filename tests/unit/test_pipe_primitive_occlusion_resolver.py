from __future__ import annotations

from collections import Counter
from copy import deepcopy
from dataclasses import dataclass
from math import cos, radians, sin

import pytest

from fireplanner.firecomponent import (
    Elbow,
    Pipe,
    SteelConnection,
    SteelDims,
    SteelMaterial,
    SteelSchedule,
    SteelSpecs,
    Tee,
)
from fireplanner.firecomponent.fitting.fireconnection.reducer import Reducer
from fireplanner.geometry.components import (
    GeometricElbow,
    GeometricPipe,
    GeometricReducer,
    GeometricTee,
    GeometricWeldedBranch,
)
from fireplanner.geometry.components.base import ViewType
from fireplanner.geometry.primitives import Line, Point, Rectangle, Transform2D
from fireplanner.networks.placement.context import PlacementContext
from fireplanner.resolvers import PipePrimitiveOcclusionResolver


@dataclass
class _FakeOccluder:
    region: Rectangle

    def occupied_regions(self) -> list[Rectangle]:
        return [self.region]


@pytest.fixture
def geometric_pipe() -> GeometricPipe:
    return GeometricPipe(
        Pipe(
            diameter=SteelDims.DIM_1_INCHES,
            material=SteelMaterial.ERW,
            schedule=SteelSchedule.SCD40,
            specs=SteelSpecs.ASTM,
            connection_type=SteelConnection.Grooved,
        )
    )


@pytest.fixture
def geometric_tee() -> GeometricTee:
    return GeometricTee(
        Tee(
            run_diameter=SteelDims.DIM_1_INCHES,
            branch_diameter=SteelDims.DIM_1_INCHES,
            material=SteelMaterial.ERW,
            schedule=SteelSchedule.SCD40,
            specs=SteelSpecs.ASTM,
            connection_type=SteelConnection.Grooved,
        )
    )


@pytest.fixture
def geometric_elbow() -> GeometricElbow:
    return GeometricElbow(
        Elbow(
            diameter=SteelDims.DIM_1_INCHES,
            angle=90.0,
            material=SteelMaterial.ERW,
            schedule=SteelSchedule.SCD40,
            specs=SteelSpecs.ASTM,
            connection_type=SteelConnection.Grooved,
        )
    )


def _center_reducer() -> GeometricReducer:
    return GeometricReducer(
        Reducer(
            diameter1=SteelDims.DIM_1_INCHES,
            diameter2=SteelDims.DIM_0_75_INCHES,
            material=SteelMaterial.ERW,
            schedule=SteelSchedule.SCD40,
            specs=SteelSpecs.ASTM,
            connection_type=SteelConnection.Grooved,
        )
    )


def _line_tuples(lines: list[Line]) -> list[tuple[float, float, float, float]]:
    result: list[tuple[float, float, float, float]] = []
    for line in lines:
        start = line.start
        end = line.end
        if (start.x, start.y) > (end.x, end.y):
            start, end = end, start
        result.append((start.x, start.y, end.x, end.y))
    return sorted(result)


def _assert_line_tuples_close(
    actual: list[tuple[float, float, float, float]],
    expected: list[tuple[float, float, float, float]],
) -> None:
    def _quantize(values: list[tuple[float, float, float, float]]) -> Counter:
        return Counter(
            tuple(round(value, 3) for value in value_tuple) for value_tuple in values
        )

    assert _quantize(actual) == _quantize(expected)


def test_pipe_primitive_occlusion_trims_only_overlapped_lines():
    pipe = GeometricPipe(
        Pipe(
            diameter=SteelDims.DIM_1_INCHES,
            material=SteelMaterial.ERW,
            schedule=SteelSchedule.SCD40,
            specs=SteelSpecs.ASTM,
            connection_type=SteelConnection.Grooved,
        ),
        start=Point(x=0.0, y=0.0),
        end=Point(x=500.0, y=0.0),
    )
    pipe.placement_context = PlacementContext(
        transform=Transform2D(origin=Point(x=0.0, y=0.0), rotation=0.0),
        view_type=ViewType.ELEVATION,
    )

    occluder = _FakeOccluder(
        region=Rectangle.from_bounds(
            point1=Point(x=200.0, y=-25.0),
            point2=Point(x=300.0, y=0.0),
        )
    )

    drawable = PipePrimitiveOcclusionResolver().resolve(pipe, [occluder])  # type: ignore[arg-type]
    lines = [
        primitive for primitive in drawable.primitives if isinstance(primitive, Line)
    ]
    assert len(lines) == 5

    upper = [line for line in lines if line.start.y > 0 and line.end.y > 0]
    center = [line for line in lines if line.start.y == 0 and line.end.y == 0]
    lower = [line for line in lines if line.start.y < 0 and line.end.y < 0]
    assert len(upper) == 1
    assert upper[0].start == Point(x=0.0, y=16.7)
    assert upper[0].end == Point(x=500.0, y=16.7)
    assert len(center) == 2
    assert len(lower) == 2


def test_pipe_primitive_occlusion_with_tee_tee_and_center_reducer(
    geometric_pipe, geometric_tee
):
    resolver = PipePrimitiveOcclusionResolver()
    geometric_pipe.start = Point(x=0.0, y=0.0)
    geometric_pipe.end = Point(x=500.0, y=0.0)
    geometric_pipe.placement_context = PlacementContext(
        transform=Transform2D(origin=Point(x=0.0, y=0.0), rotation=0.0),
        view_type=ViewType.ELEVATION,
    )

    start_tee = deepcopy(geometric_tee)
    end_tee = deepcopy(geometric_tee)
    center_reducer = _center_reducer()
    start_tee.placement_context = PlacementContext(
        transform=Transform2D(origin=Point(x=0.0, y=0.0), rotation=0.0),
        view_type=ViewType.ELEVATION,
    )
    end_tee.placement_context = PlacementContext(
        transform=Transform2D(origin=Point(x=500.0, y=0.0), rotation=0.0),
        view_type=ViewType.ELEVATION,
    )
    center_reducer.placement_context = PlacementContext(
        transform=Transform2D(origin=Point(x=250.0, y=0.0), rotation=0.0),
        view_type=ViewType.ELEVATION,
    )

    drawable = resolver.resolve(
        pipe=geometric_pipe,
        occluding_components=[start_tee, center_reducer, end_tee],
    )
    lines = [
        primitive for primitive in drawable.primitives if isinstance(primitive, Line)
    ]

    _assert_line_tuples_close(
        _line_tuples(lines),
        [
            (38.000, -16.700, 224.600, -16.700),
            (38.000, 0.000, 224.600, 0.000),
            (38.000, 16.700, 224.600, 16.700),
            (275.400, -16.700, 462.000, -16.700),
            (275.400, 0.000, 462.000, 0.000),
            (275.400, 16.700, 462.000, 16.700),
        ],
    )


def test_pipe_primitive_occlusion_with_tee_tee_and_center_reducer_rotated_45(
    geometric_pipe, geometric_tee
):
    resolver = PipePrimitiveOcclusionResolver()
    theta = radians(45.0)
    c = cos(theta)
    s = sin(theta)
    geometric_pipe.start = Point(x=0.0, y=0.0)
    geometric_pipe.end = Point(x=500.0 * c, y=500.0 * s)
    geometric_pipe.placement_context = PlacementContext(
        transform=Transform2D(origin=Point(x=0.0, y=0.0), rotation=theta),
        view_type=ViewType.ELEVATION,
    )

    start_tee = deepcopy(geometric_tee)
    end_tee = deepcopy(geometric_tee)
    center_reducer = _center_reducer()
    start_tee.placement_context = PlacementContext(
        transform=Transform2D(origin=Point(x=0.0, y=0.0), rotation=theta),
        view_type=ViewType.ELEVATION,
    )
    end_tee.placement_context = PlacementContext(
        transform=Transform2D(origin=Point(x=500.0 * c, y=500.0 * s), rotation=theta),
        view_type=ViewType.ELEVATION,
    )
    center_reducer.placement_context = PlacementContext(
        transform=Transform2D(origin=Point(x=250.0 * c, y=250.0 * s), rotation=theta),
        view_type=ViewType.ELEVATION,
    )

    drawable = resolver.resolve(
        pipe=geometric_pipe,
        occluding_components=[start_tee, center_reducer, end_tee],
    )
    lines = [
        primitive for primitive in drawable.primitives if isinstance(primitive, Line)
    ]

    _assert_line_tuples_close(
        _line_tuples(lines),
        [
            (
                15.061,
                38.679,
                147.007,
                170.625,
            ),
            (
                38.679,
                15.061,
                170.625,
                147.007,
            ),
            (
                26.870,
                26.870,
                158.816,
                158.816,
            ),
            (
                182.929,
                206.546,
                314.875,
                338.492,
            ),
            (
                194.737,
                194.737,
                326.683,
                326.683,
            ),
            (
                206.546,
                182.929,
                338.492,
                314.875,
            ),
        ],
    )


def test_pipe_primitive_occlusion_with_elbow_plan(geometric_pipe, geometric_elbow):
    resolver = PipePrimitiveOcclusionResolver()
    geometric_pipe.diameter = SteelDims.DIM_2_5_INCHES
    geometric_pipe.start = Point(x=0.0, y=0.0)
    geometric_pipe.end = Point(x=500.0, y=0.0)
    geometric_pipe.placement_context = PlacementContext(
        transform=Transform2D(origin=Point(x=0.0, y=0.0), rotation=0.0),
        view_type=ViewType.ELEVATION,
    )

    elbow = deepcopy(geometric_elbow)
    elbow.placement_context = PlacementContext(
        transform=Transform2D(origin=Point(x=500.0, y=0.0), rotation=0.0),
        view_type=ViewType.PLAN,
    )

    drawable = resolver.resolve(
        pipe=geometric_pipe,
        occluding_components=[elbow],
    )
    lines = [
        primitive for primitive in drawable.primitives if isinstance(primitive, Line)
    ]

    _assert_line_tuples_close(
        _line_tuples(lines),
        [
            (0.000, -36.515, 500.000, -36.515),
            (0.000, 0.000, 483.300, 0.000),
            (0.000, 36.515, 483.300, 36.515),
        ],
    )


def test_pipe_primitive_occlusion_with_elbow_plan_and_welded_same_position_keeps_output(
    geometric_pipe, geometric_elbow
):
    resolver = PipePrimitiveOcclusionResolver()
    geometric_pipe.diameter = SteelDims.DIM_2_5_INCHES
    geometric_pipe.start = Point(x=0.0, y=0.0)
    geometric_pipe.end = Point(x=500.0, y=0.0)
    geometric_pipe.placement_context = PlacementContext(
        transform=Transform2D(origin=Point(x=0.0, y=0.0), rotation=0.0),
        view_type=ViewType.ELEVATION,
    )

    elbow = deepcopy(geometric_elbow)
    elbow.placement_context = PlacementContext(
        transform=Transform2D(origin=Point(x=500.0, y=0.0), rotation=0.0),
        view_type=ViewType.PLAN,
    )

    welded = GeometricWeldedBranch(
        Tee(
            run_diameter=SteelDims.DIM_1_INCHES,
            branch_diameter=SteelDims.DIM_1_INCHES,
            material=SteelMaterial.ERW,
            schedule=SteelSchedule.SCD40,
            specs=SteelSpecs.ASTM,
            connection_type=SteelConnection.Welded,
        )
    )
    welded.placement_context = PlacementContext(
        transform=Transform2D(origin=Point(x=500.0, y=0.0), rotation=0.0),
        view_type=ViewType.PLAN,
    )

    elbow_only_drawable = resolver.resolve(
        pipe=geometric_pipe,
        occluding_components=[elbow],
    )
    elbow_welded_drawable = resolver.resolve(
        pipe=geometric_pipe,
        occluding_components=[elbow, welded],
    )

    elbow_only_lines = [
        primitive
        for primitive in elbow_only_drawable.primitives
        if isinstance(primitive, Line)
    ]
    elbow_welded_lines = [
        primitive
        for primitive in elbow_welded_drawable.primitives
        if isinstance(primitive, Line)
    ]

    assert _line_tuples(elbow_welded_lines) == _line_tuples(elbow_only_lines)


def test_pipe_primitive_occlusion_with_elbow_plan_and_welded_rotated_45(
    geometric_pipe, geometric_elbow
):
    resolver = PipePrimitiveOcclusionResolver()
    theta = radians(45.0)
    c = cos(theta)
    s = sin(theta)
    geometric_pipe.diameter = SteelDims.DIM_2_5_INCHES
    geometric_pipe.start = Point(x=0.0, y=0.0)
    geometric_pipe.end = Point(x=500.0 * c, y=500.0 * s)
    geometric_pipe.placement_context = PlacementContext(
        transform=Transform2D(origin=Point(x=0.0, y=0.0), rotation=theta),
        view_type=ViewType.ELEVATION,
    )

    elbow = deepcopy(geometric_elbow)
    elbow.placement_context = PlacementContext(
        transform=Transform2D(origin=Point(x=500.0 * c, y=500.0 * s), rotation=theta),
        view_type=ViewType.PLAN,
    )

    welded = GeometricWeldedBranch(
        Tee(
            run_diameter=SteelDims.DIM_1_INCHES,
            branch_diameter=SteelDims.DIM_1_INCHES,
            material=SteelMaterial.ERW,
            schedule=SteelSchedule.SCD40,
            specs=SteelSpecs.ASTM,
            connection_type=SteelConnection.Welded,
        )
    )
    welded.placement_context = PlacementContext(
        transform=Transform2D(origin=Point(x=500.0 * c, y=500.0 * s), rotation=theta),
        view_type=ViewType.PLAN,
    )

    drawable = resolver.resolve(
        pipe=geometric_pipe,
        occluding_components=[elbow, welded],
    )
    lines = [
        primitive for primitive in drawable.primitives if isinstance(primitive, Line)
    ]

    _assert_line_tuples_close(
        _line_tuples(lines),
        [
            (
                0.000 * c + 36.515 * s,
                0.000 * s - 36.515 * c,
                500.000 * c + 36.515 * s,
                500.000 * s - 36.515 * c,
            ),
            (
                0.000 * c,
                0.000 * s,
                483.300 * c,
                483.300 * s,
            ),
            (
                0.000 * c - 36.515 * s,
                0.000 * s + 36.515 * c,
                483.300 * c - 36.515 * s,
                483.300 * s + 36.515 * c,
            ),
        ],
    )
