from math import radians
import pytest

from fireplanner.firecomponent import (
    SteelDims,
    SteelConnection,
    SteelMaterial,
    SteelSchedule,
    SteelSpecs,
    Tee,
    Reducer,
    Elbow,
)
from fireplanner.geometry.components.geometric_component import GeometricComponent
from fireplanner.geometry.components import (
    GeometricElbow,
    GeometricReducer,
    GeometricTee,
)
from fireplanner.geometry.primitives import Line, Point
from fireplanner.geometry.primitives.transform import Transform2D
from fireplanner.networks.junction import Junction, JunctionType
from fireplanner.networks.placement_resolver import (
    PlacementResolver,
    PlacementResolverConfig,
    PlacementUnit,
)


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


@pytest.mark.parametrize(
    "edge_id_line_map, expected_transform",
    [
        (
            {
                1: Line(start=Point(x=-1, y=0), end=Point(x=0, y=0), id=1),
                2: Line(start=Point(x=0, y=0), end=Point(x=1, y=0), id=2),
                3: Line(start=Point(x=0, y=0), end=Point(x=0, y=1), id=3),
            },
            Transform2D(Point(x=0, y=0), radians(0)),
        ),
        (
            # reversed main lines
            {
                1: Line(end=Point(x=-1, y=0), start=Point(x=0, y=0), id=1),
                2: Line(end=Point(x=0, y=0), start=Point(x=1, y=0), id=2),
                3: Line(start=Point(x=0, y=0), end=Point(x=0, y=1), id=3),
            },
            Transform2D(Point(x=0, y=0), radians(0)),
        ),
        (
            # reversed branch line
            {
                1: Line(start=Point(x=0, y=0), end=Point(x=-1, y=0), id=1),
                2: Line(start=Point(x=1, y=0), end=Point(x=0, y=0), id=2),
                3: Line(start=Point(x=0, y=1), end=Point(x=0, y=0), id=3),
            },
            Transform2D(Point(x=0, y=0), radians(0)),
        ),
        (
            # 2nd quadrant main line
            {
                1: Line(start=Point(x=-1, y=1), end=Point(x=0, y=0), id=1),
                2: Line(start=Point(x=0, y=0), end=Point(x=1, y=-1), id=2),
                3: Line(start=Point(x=0, y=0), end=Point(x=-1, y=-1), id=3),
            },
            Transform2D(Point(x=0, y=0), radians(135)),
        ),
        (
            # 2nd quadrant reversed main line
            {
                1: Line(end=Point(x=-1, y=1), start=Point(x=0, y=0), id=1),
                2: Line(end=Point(x=0, y=0), start=Point(x=1, y=-1), id=2),
                3: Line(start=Point(x=0, y=0), end=Point(x=-1, y=-1), id=3),
            },
            Transform2D(Point(x=0, y=0), radians(135)),
        ),
    ],
)
def test_resolve_transform_for_tee(geometric_tee, edge_id_line_map, expected_transform):
    resolver = PlacementResolver()
    junction = Junction(
        id=1,
        origin=Point(x=0, y=0),
        junction_type=JunctionType.THREE_WAY,
        connected_edges_ids=[1, 2, 3],
    )
    transform = resolver.resolve_transform(
        junction=junction,
        edge_id_line_map=edge_id_line_map,
        edge_pipe_dim_map={
            1: SteelDims.DIM_1_INCHES,
            2: SteelDims.DIM_1_INCHES,
            3: SteelDims.DIM_1_INCHES,
        },
        geometric_component=geometric_tee,
    )

    assert transform.origin == expected_transform.origin
    assert transform.angle == expected_transform.angle


@pytest.mark.parametrize(
    "edge_id_line_map, expected_transform",
    [
        (
            {
                1: Line(start=Point(x=-1, y=0), end=Point(x=0, y=0), id=1),
                2: Line(start=Point(x=0, y=0), end=Point(x=1, y=0), id=2),
            },
            Transform2D(Point(x=-0.25, y=0), radians(0)),
        ),
        (
            # reversed main lines
            {
                1: Line(end=Point(x=-1, y=0), start=Point(x=0, y=0), id=1),
                2: Line(end=Point(x=0, y=0), start=Point(x=1, y=0), id=2),
            },
            Transform2D(Point(x=-0.25, y=0), radians(0)),
        ),
        (
            # reversed lines order by reversing ids
            {
                2: Line(start=Point(x=-1, y=0), end=Point(x=0, y=0), id=1),
                1: Line(start=Point(x=0, y=0), end=Point(x=1, y=0), id=2),
            },
            Transform2D(Point(x=0.25, y=0), radians(180)),
        ),
        (
            # 2nd quadrant main line
            {
                1: Line(start=Point(x=-1, y=1), end=Point(x=0, y=0), id=1),
                2: Line(start=Point(x=0, y=0), end=Point(x=1, y=-1), id=2),
            },
            Transform2D(Point(x=-0.17677669, y=0.17677669), radians(-45)),
        ),
        (
            # 2nd quadrant reversed main line by reversing ids
            {
                2: Line(start=Point(x=-1, y=1), end=Point(x=0, y=0), id=1),
                1: Line(start=Point(x=0, y=0), end=Point(x=1, y=-1), id=2),
            },
            Transform2D(Point(x=0.17677669, y=-0.17677669), radians(135)),
        ),
    ],
)
def test_resolve_transform_for_reducer(
    geometric_reducer, edge_id_line_map, expected_transform
):
    resolver = PlacementResolver(
        config=PlacementResolverConfig(unit=PlacementUnit.M),
    )
    junction = Junction(
        id=2,
        origin=Point(x=0, y=0),
        junction_type=JunctionType.TWO_WAY,
        connected_edges_ids=[1, 2],
    )
    transform = resolver.resolve_transform(
        junction=junction,
        edge_id_line_map=edge_id_line_map,
        edge_pipe_dim_map={
            1: SteelDims.DIM_0_75_INCHES,
            2: SteelDims.DIM_1_INCHES,
        },
        geometric_component=geometric_reducer,
    )

    assert transform.origin == expected_transform.origin
    assert transform.angle == expected_transform.angle


@pytest.mark.parametrize(
    "edge_id_line_map, expected_transform",
    [
        (
            # simple test two lines
            {
                1: Line(start=Point(x=0, y=0), end=Point(x=1, y=0), id=1),
                2: Line(start=Point(x=0, y=0), end=Point(x=0, y=1), id=2),
            },
            Transform2D(Point(x=0.38, y=0.38), radians(180)),
        ),
        (
            # simple test but reversed endpoints of lines
            {
                1: Line(end=Point(x=0, y=0), start=Point(x=1, y=0), id=1),
                2: Line(end=Point(x=0, y=0), start=Point(x=0, y=1), id=2),
            },
            Transform2D(Point(x=0.38, y=0.38), radians(180)),
        ),
        (
            # reversed lines order by reversing ids
            {
                2: Line(start=Point(x=0, y=0), end=Point(x=1, y=0), id=1),
                1: Line(start=Point(x=0, y=0), end=Point(x=0, y=1), id=2),
            },
            Transform2D(Point(x=0.38, y=0.38), radians(180)),
        ),
        (
            # 2nd quadrant lines
            {
                1: Line(start=Point(x=-1, y=1), end=Point(x=0, y=0), id=1),
                2: Line(start=Point(x=0, y=0), end=Point(x=-1, y=-1), id=2),
            },
            Transform2D(Point(x=-0.537401, y=0.0), radians(-45)),
        ),
        (
            # 2nd quadrant reversed line by reversing ids
            {
                2: Line(start=Point(x=-1, y=-1), end=Point(x=0, y=0), id=1),
                1: Line(start=Point(x=0, y=0), end=Point(x=-1, y=-1), id=2),
            },
            Transform2D(Point(x=-0.537401, y=0.0), radians(45)),
        ),
    ],
)
def test_resolve_transform_for_elbow(
    geometric_elbow, edge_id_line_map, expected_transform
):
    resolver = PlacementResolver(
        config=PlacementResolverConfig(unit=PlacementUnit.M),
    )
    junction = Junction(
        id=3,
        origin=Point(x=0, y=0),
        junction_type=JunctionType.TWO_WAY,
        connected_edges_ids=[1, 2],
    )
    transform = resolver.resolve_transform(
        junction=junction,
        edge_id_line_map=edge_id_line_map,
        edge_pipe_dim_map={
            2: SteelDims.DIM_1_INCHES,
            3: SteelDims.DIM_1_INCHES,
        },
        geometric_component=geometric_elbow,
    )

    # assert transform.origin == expected_transform.origin
    assert transform.angle == expected_transform.angle
