from math import pi, radians
from typing import List

import pytest

from fireplanner.firecomponent.base import (
    SteelConnection,
    SteelDims,
    SteelMaterial,
    SteelSchedule,
    SteelSpecs,
)
from fireplanner.firecomponent.fitting.fireconnection.elbow import Elbow
from fireplanner.firecomponent.fitting.fireconnection.reducer import Reducer
from fireplanner.firecomponent.fitting.fireconnection.tee import Tee
from fireplanner.firecomponent.fitting.hanger import Hanger
from fireplanner.firecomponent.pipe import Pipe
from fireplanner.geometry.components import (
    GeometricElbow,
    GeometricHanger,
    GeometricPipe,
    GeometricReducer,
    GeometricTee,
    GeometricWeldedBranch,
    ViewType,
)
from fireplanner.geometry.primitives import (
    Arc,
    Line,
    LineType,
    Point,
    Primitive2D,
    Rectangle,
    Transform2D,
)
from fireplanner.networks.placement.context import PlacementContext


@pytest.fixture
def geometric_pipe():
    pipe = Pipe(
        diameter=SteelDims.DIM_1_INCHES,
        material=SteelMaterial.ERW,
        schedule=SteelSchedule.SCD40,
        specs=SteelSpecs.ASTM,
        connection_type=SteelConnection.Grooved,
    )
    return GeometricPipe(pipe)


@pytest.fixture
def geometric_elbow():
    elbow = Elbow(
        diameter=SteelDims.DIM_1_INCHES,
        angle=90.0,
        material=SteelMaterial.ERW,
        schedule=SteelSchedule.SCD40,
        specs=SteelSpecs.ASTM,
        connection_type=SteelConnection.Grooved,
    )
    return GeometricElbow(elbow)


@pytest.fixture
def geometric_tee():
    tee = Tee(
        run_diameter=SteelDims.DIM_1_INCHES,
        branch_diameter=SteelDims.DIM_1_INCHES,
        material=SteelMaterial.ERW,
        schedule=SteelSchedule.SCD40,
        specs=SteelSpecs.ASTM,
        connection_type=SteelConnection.Grooved,
    )
    return GeometricTee(tee)


@pytest.fixture
def geometric_welded_branch():
    tee = Tee(
        run_diameter=SteelDims.DIM_2_5_INCHES,
        branch_diameter=SteelDims.DIM_1_INCHES,
        material=SteelMaterial.ERW,
        schedule=SteelSchedule.SCD40,
        specs=SteelSpecs.ASTM,
        connection_type=SteelConnection.Grooved,
    )
    return GeometricWeldedBranch(tee)


@pytest.fixture
def geometric_reducer():
    reducer = Reducer(
        diameter1=SteelDims.DIM_1_INCHES,
        diameter2=SteelDims.DIM_0_75_INCHES,
        material=SteelMaterial.ERW,
        schedule=SteelSchedule.SCD40,
        specs=SteelSpecs.ASTM,
        connection_type=SteelConnection.Grooved,
    )
    return GeometricReducer(reducer)


@pytest.fixture
def geometric_hanger():
    hanger = Hanger(
        diameter=SteelDims.DIM_1_INCHES,
        material=SteelMaterial.ERW,
        schedule=SteelSchedule.SCD40,
        specs=SteelSpecs.ASTM,
        connection_type=SteelConnection.Grooved,
    )
    return GeometricHanger(hanger)


@pytest.mark.parametrize(
    "transform, expected_primitives",
    [
        (
            Transform2D(Point(x=3, y=3), radians(90)),
            {
                Line(
                    start=Point(x=-13.7, y=-35), end=Point(x=-13.7, y=-13.7)
                ),  # top left
                Line(
                    start=Point(x=-13.7, y=19.7), end=Point(x=-13.7, y=41)
                ),  # top right
                Line(
                    start=Point(x=19.7, y=41.0), end=Point(x=-13.7, y=41.0)
                ),  # right run
                Line(
                    start=Point(x=-13.7, y=-35), end=Point(x=19.7, y=-35.0)
                ),  # left run
                Line(start=Point(x=19.7, y=-35), end=Point(x=19.7, y=41)),  # bottom
                Line(
                    start=Point(x=-35, y=-13.7), end=Point(x=-35, y=19.7)
                ),  # bottom branch
                Line(
                    start=Point(x=-35, y=19.7), end=Point(x=-13.7, y=19.7)
                ),  # right branch
                Line(
                    start=Point(x=-35, y=-13.7), end=Point(x=-13.7, y=-13.7)
                ),  # left branch
                Line(
                    start=Point(x=3.0, y=3.0), end=Point(x=-13.7, y=-13.7)
                ),  # center left
                Line(
                    start=Point(x=3.0, y=3.0), end=Point(x=-13.7, y=19.7)
                ),  # center right
            },
        ),
    ],
)
def test_tee_build_primitives_2d(
    geometric_tee, transform: Transform2D, expected_primitives: List[Primitive2D]
):
    geometric_tee.placement_context = PlacementContext(
        transform=transform, view_type=ViewType.ELEVATION
    )
    geometric_tee.build_primitives_2d()
    primitives = [
        prim
        for prim in geometric_tee.get_primitives_2d()
        if prim.line_type != LineType.CenterLine
    ]
    assert len(primitives) == len(expected_primitives)
    assert {prim for prim in primitives} == expected_primitives


@pytest.mark.parametrize(
    "transform, expected_primitives",
    [
        (
            Transform2D(Point(x=3, y=3), radians(90)),
            {
                Line(
                    start=Point(x=-10.335, y=-22.4), end=Point(x=-13.7, y=28.4)
                ),  # top
                Line(start=Point(x=-13.7, y=28.4), end=Point(x=19.7, y=28.4)),  # right
                Line(
                    start=Point(x=19.7, y=28.4), end=Point(x=16.335, y=-22.4)
                ),  # bottom
                Line(
                    start=Point(x=16.335, y=-22.4), end=Point(x=-10.335, y=-22.4)
                ),  # left
            },
        ),
    ],
)
def test_reducer_build_primitives_2d(
    geometric_reducer, transform: Transform2D, expected_primitives: List[Primitive2D]
):
    geometric_reducer.placement_context = PlacementContext(
        transform=transform, view_type=ViewType.ELEVATION
    )
    geometric_reducer.build_primitives_2d()
    primitives = [
        prim
        for prim in geometric_reducer.get_primitives_2d()
        if prim.line_type != LineType.CenterLine
    ]
    assert len(primitives) == len(expected_primitives)
    assert {prim for prim in primitives} == expected_primitives


@pytest.mark.parametrize(
    "transform, expected_primitives",
    [
        (
            Transform2D(Point(x=3, y=3), radians(90)),
            {
                Arc(
                    start=Point(x=3, y=24.3),
                    center=Point(x=3, y=3),
                    angle=pi / 2,
                ),  # inner arc
                Arc(
                    start=Point(x=3, y=57.7),
                    center=Point(x=3, y=3),
                    angle=pi / 2,
                ),  # outer arc
                Line(start=Point(x=3, y=24.3), end=Point(x=3, y=57.7)),  # vertical line
                Line(
                    start=Point(x=-18.3, y=3), end=Point(x=-51.7, y=3)
                ),  # horizontal line
            },
        ),
    ],
)
def test_elbow_build_primitives_2d(
    geometric_elbow, transform: Transform2D, expected_primitives: List[Primitive2D]
):
    geometric_elbow.placement_context = PlacementContext(
        transform=transform, view_type=ViewType.ELEVATION
    )
    geometric_elbow.build_primitives_2d()
    primitives = [
        prim
        for prim in geometric_elbow.get_primitives_2d()
        if prim.line_type != LineType.CenterLine
    ]
    assert len(primitives) == len(expected_primitives)
    assert {prim for prim in primitives} == expected_primitives


@pytest.mark.parametrize(
    "transform, expected_primitives",
    [
        (
            Transform2D(Point(x=3, y=3), radians(90)),
            {
                Arc(
                    start=Point(x=-33.515, y=-13.699999999999996),
                    center=Point(x=-65.98737633743491, y=3.0000000000000044),
                    angle=0.9500176519640574,
                )
            },
        ),
    ],
)
def test_geometric_welded_branch_build_primitives_2d(
    geometric_welded_branch,
    transform: Transform2D,
    expected_primitives: List[Primitive2D],
):
    geometric_welded_branch.placement_context = PlacementContext(
        transform=transform, view_type=ViewType.ELEVATION
    )
    geometric_welded_branch.build_primitives_2d()
    primitives = [
        prim
        for prim in geometric_welded_branch.get_primitives_2d()
        if prim.line_type != LineType.CenterLine
    ]
    assert len(primitives) == len(expected_primitives)
    assert {prim for prim in primitives} == expected_primitives
    geometric_welded_branch.transform = transform


@pytest.mark.parametrize(
    "component_fixture_name",
    [
        "geometric_pipe",
        "geometric_elbow",
        "geometric_reducer",
        "geometric_tee",
        "geometric_welded_branch",
        "geometric_hanger",
    ],
)
def test_geometric_component_local_occupancy_regions_returns_rectangles(
    request, component_fixture_name: str
):
    component = request.getfixturevalue(component_fixture_name)
    component.placement_context = PlacementContext(
        transform=Transform2D(origin=Point(x=0, y=0), rotation=0),
        view_type=ViewType.ELEVATION,
    )
    if isinstance(component, GeometricPipe):
        component.start = Point(x=0, y=0)
        component.end = Point(x=100, y=0)
    regions = component.local_occupancy_regions()

    assert len(regions) >= 1
    assert all(isinstance(region, Rectangle) for region in regions)


def test_geometric_component_occupied_regions_applies_transform(geometric_pipe):
    geometric_pipe.start = Point(x=0, y=0)
    geometric_pipe.end = Point(x=100, y=0)
    geometric_pipe.placement_context = PlacementContext(
        transform=Transform2D(origin=Point(x=10, y=20), rotation=0),
        view_type=ViewType.ELEVATION,
    )

    local_region = geometric_pipe.local_occupancy_regions()[0]
    world_region = geometric_pipe.occupied_regions()[0]

    assert world_region.point1 == local_region.point1.transform_2d(
        geometric_pipe.placement_context.transform
    )
    assert world_region.point2 == local_region.point2.transform_2d(
        geometric_pipe.placement_context.transform
    )
