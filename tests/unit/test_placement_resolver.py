from math import radians

import pytest

from fireplanner.firecomponent import (
    Elbow,
    Reducer,
    SteelConnection,
    SteelDims,
    SteelMaterial,
    SteelSchedule,
    SteelSpecs,
    Tee,
)
from fireplanner.geometry.components import (
    GeometricElbow,
    GeometricReducer,
    GeometricTee,
)
from fireplanner.geometry.components.base import ViewType
from fireplanner.geometry.primitives import Line, Point
from fireplanner.geometry.primitives.transform import Transform2D
from fireplanner.networks.junction import Junction, JunctionType
from fireplanner.networks.junction_assembly import JunctionAssembly, PipeAssembly
from fireplanner.networks.junction_info import (
    EdgeInfo,
    ThreeWayJunctionInfo,
    TwoWayJunctionInfo,
)
from fireplanner.networks.placement import PlacementContext, PlacementResolver
from fireplanner.networks.placement.assembly_builder import PlacementAssemblyBuilder
from fireplanner.networks.placement.strategy import (
    SingleElbowPlacementStrategy,
    SingleReducerPlacementStrategy,
    SingleTeePlacementStrategy,
    TeeElbowRisePlacementStrategy,
    TeeReducerPlacementStrategy,
)


def geometric_tee_builder(
    run_diameter: SteelDims = SteelDims.DIM_1_INCHES,
    branch_diameter: SteelDims | None = None,
):
    if branch_diameter is None:
        branch_diameter = run_diameter
    tee = Tee(
        run_diameter=run_diameter,
        branch_diameter=branch_diameter,
        material=SteelMaterial.ERW,
        schedule=SteelSchedule.SCD40,
        specs=SteelSpecs.ASTM,
        connection_type=SteelConnection.Welded,
    )
    return GeometricTee(tee)


def geometric_reducer_builder(
    diameter1: SteelDims = SteelDims.DIM_1_INCHES,
    diameter2: SteelDims = SteelDims.DIM_0_75_INCHES,
):
    reducer = Reducer(
        diameter1=diameter1,
        diameter2=diameter2,
        material=SteelMaterial.ERW,
        schedule=SteelSchedule.SCD40,
        specs=SteelSpecs.ASTM,
        connection_type=SteelConnection.Welded,
    )
    return GeometricReducer(reducer)


def geometric_elbow_builder(
    diameter: SteelDims = SteelDims.DIM_1_INCHES, angle: float = 90.0
):
    elbow = Elbow(
        diameter=diameter,
        angle=angle,
        material=SteelMaterial.ERW,
        schedule=SteelSchedule.SCD40,
        specs=SteelSpecs.ASTM,
        connection_type=SteelConnection.Welded,
    )
    return GeometricElbow(elbow)


def _build_junction_assembly(
    junction: Junction,
    edge_id_line_map: dict[int, Line],
    edge_pipe_dim_map: dict[int, SteelDims],
) -> JunctionAssembly:
    edge_infos = [
        EdgeInfo(
            edge_id=edge_id,
            line=line,
            length=line.length(),
            sprinkler_count=0,
        )
        for edge_id, line in edge_id_line_map.items()
    ]

    if junction.junction_type == JunctionType.THREE_WAY:
        junction_info = ThreeWayJunctionInfo(
            junction_id=junction.id,
            origin=junction.origin,
            run=edge_infos[:2],
            branch=edge_infos[2] if len(edge_infos) > 2 else None,
        )
    else:
        junction_info = TwoWayJunctionInfo(
            junction_id=junction.id,
            origin=junction.origin,
            edges=edge_infos[:2],
            angle=junction.angle or 0.0,
        )

    return JunctionAssembly(
        junction_info=junction_info,
        pipes=[
            PipeAssembly(
                edge_info=edge_info,
                diameter=edge_pipe_dim_map[edge_info.edge_id],
                pipe=None,
            )
            for edge_info in edge_infos
            if edge_info.edge_id in edge_pipe_dim_map
        ],
    )


def _build_placement_assembly(junction_assembly: JunctionAssembly, components):
    return PlacementAssemblyBuilder().build(junction_assembly, list(components))


@pytest.mark.parametrize(
    "component, junction, edge_id_line_map, edge_pipe_dim_map, expected_strategy",
    [
        (
            geometric_tee_builder(),
            Junction(
                id=1,
                origin=Point(x=0, y=0),
                junction_type=JunctionType.THREE_WAY,
                connected_edges_ids=[1, 2, 3],
            ),
            {
                1: Line(start=Point(x=-100, y=0), end=Point(x=0, y=0), id=1),
                2: Line(start=Point(x=0, y=0), end=Point(x=100, y=0), id=2),
                3: Line(start=Point(x=0, y=0), end=Point(x=0, y=100), id=3),
            },
            {
                1: SteelDims.DIM_1_INCHES,
                2: SteelDims.DIM_1_INCHES,
                3: SteelDims.DIM_1_INCHES,
            },
            SingleTeePlacementStrategy,
        ),
        (
            geometric_reducer_builder(),
            Junction(
                id=2,
                origin=Point(x=0, y=0),
                junction_type=JunctionType.TWO_WAY,
                connected_edges_ids=[1, 2],
            ),
            {
                1: Line(start=Point(x=-100, y=0), end=Point(x=0, y=0), id=1),
                2: Line(start=Point(x=0, y=0), end=Point(x=100, y=0), id=2),
            },
            {
                1: SteelDims.DIM_0_75_INCHES,
                2: SteelDims.DIM_1_INCHES,
            },
            SingleReducerPlacementStrategy,
        ),
        (
            geometric_elbow_builder(),
            Junction(
                id=2,
                origin=Point(x=0, y=0),
                junction_type=JunctionType.TWO_WAY,
                connected_edges_ids=[1, 2],
            ),
            {
                1: Line(start=Point(x=-100, y=0), end=Point(x=0, y=0), id=1),
                2: Line(start=Point(x=0, y=0), end=Point(x=100, y=0), id=2),
            },
            {
                1: SteelDims.DIM_1_INCHES,
                2: SteelDims.DIM_1_INCHES,
            },
            SingleElbowPlacementStrategy,
        ),
    ],
)
def test_resolver_strategy_and_context(
    component,
    junction,
    edge_id_line_map,
    edge_pipe_dim_map,
    expected_strategy,
):
    resolver = PlacementResolver()
    junction_assembly = _build_junction_assembly(
        junction=junction,
        edge_id_line_map=edge_id_line_map,
        edge_pipe_dim_map=edge_pipe_dim_map,
    )

    strategy = resolver.resolve(
        _build_placement_assembly(junction_assembly, [component])
    )

    assert isinstance(strategy, expected_strategy)


@pytest.mark.parametrize(
    "edge_id_line_map, expected_transform",
    [
        (
            {
                1: Line(start=Point(x=-100, y=0), end=Point(x=0, y=0), id=1),
                2: Line(start=Point(x=0, y=0), end=Point(x=100, y=0), id=2),
                3: Line(start=Point(x=0, y=0), end=Point(x=0, y=100), id=3),
            },
            Transform2D(Point(x=0, y=0), radians(0)),
        ),
        (
            {
                1: Line(end=Point(x=-100, y=0), start=Point(x=0, y=0), id=1),
                2: Line(end=Point(x=0, y=0), start=Point(x=100, y=0), id=2),
                3: Line(start=Point(x=0, y=0), end=Point(x=0, y=100), id=3),
            },
            Transform2D(Point(x=0, y=0), radians(0)),
        ),
        (
            {
                1: Line(start=Point(x=0, y=0), end=Point(x=-100, y=0), id=1),
                2: Line(start=Point(x=100, y=0), end=Point(x=0, y=0), id=2),
                3: Line(start=Point(x=0, y=100), end=Point(x=0, y=0), id=3),
            },
            Transform2D(Point(x=0, y=0), radians(0)),
        ),
        (
            {
                1: Line(start=Point(x=-100, y=100), end=Point(x=0, y=0), id=1),
                2: Line(start=Point(x=0, y=0), end=Point(x=100, y=-100), id=2),
                3: Line(start=Point(x=0, y=0), end=Point(x=-100, y=-100), id=3),
            },
            Transform2D(Point(x=0, y=0), radians(135)),
        ),
        (
            {
                1: Line(end=Point(x=-100, y=100), start=Point(x=0, y=0), id=1),
                2: Line(end=Point(x=0, y=0), start=Point(x=100, y=-100), id=2),
                3: Line(start=Point(x=0, y=0), end=Point(x=-100, y=-100), id=3),
            },
            Transform2D(Point(x=0, y=0), radians(135)),
        ),
    ],
)
def test_single_tee_strategy_matches_legacy_cases(
    edge_id_line_map,
    expected_transform,
):
    geometric_tee = geometric_tee_builder(run_diameter=SteelDims.DIM_1_INCHES)
    junction = Junction(
        id=1,
        origin=Point(x=0, y=0),
        junction_type=JunctionType.THREE_WAY,
        connected_edges_ids=[1, 2, 3],
    )
    edge_pipe_dim_map = {
        1: SteelDims.DIM_1_INCHES,
        2: SteelDims.DIM_1_INCHES,
        3: SteelDims.DIM_1_INCHES,
    }
    resolver = PlacementResolver()
    junction_assembly = _build_junction_assembly(
        junction=junction,
        edge_id_line_map=edge_id_line_map,
        edge_pipe_dim_map=edge_pipe_dim_map,
    )

    strategy = resolver.resolve(
        _build_placement_assembly(junction_assembly, [geometric_tee])
    )
    assert isinstance(strategy, SingleTeePlacementStrategy)
    context = strategy.get_placement_context(geometric_tee)

    assert context.transform.origin == expected_transform.origin
    assert context.transform.angle == expected_transform.angle


@pytest.mark.parametrize(
    "edge_id_line_map, expected_transform",
    [
        (
            {
                1: Line(start=Point(x=-100, y=0), end=Point(x=0, y=0), id=1),
                2: Line(start=Point(x=0, y=0), end=Point(x=100, y=0), id=2),
            },
            Transform2D(Point(x=-250.0, y=0.0), radians(0)),
        ),
        (
            # reversed main lines
            {
                1: Line(end=Point(x=-100, y=0), start=Point(x=0, y=0), id=1),
                2: Line(end=Point(x=0, y=0), start=Point(x=100, y=0), id=2),
            },
            Transform2D(Point(x=-250.0, y=0.0), radians(0)),
        ),
        (
            # reversed lines order by reversing ids
            {
                2: Line(start=Point(x=-100, y=0), end=Point(x=0, y=0), id=1),
                1: Line(start=Point(x=0, y=0), end=Point(x=100, y=0), id=2),
            },
            Transform2D(Point(x=250.0, y=0.0), radians(180)),
        ),
        (
            # 2nd quadrant main line
            {
                1: Line(start=Point(x=-100, y=100), end=Point(x=0, y=0), id=1),
                2: Line(start=Point(x=0, y=0), end=Point(x=100, y=-100), id=2),
            },
            Transform2D(
                Point(x=-176.7766952966369, y=176.77669529663686), radians(-45)
            ),
        ),
        (
            # 2nd quadrant reversed main line by reversing ids
            {
                2: Line(start=Point(x=-100, y=100), end=Point(x=0, y=0), id=1),
                1: Line(start=Point(x=0, y=0), end=Point(x=100, y=-100), id=2),
            },
            Transform2D(
                Point(x=176.77669529663686, y=-176.7766952966369), radians(135)
            ),
        ),
    ],
)
def test_single_reducer_strategy_matches_legacy_cases(
    edge_id_line_map,
    expected_transform,
):
    geometric_reducer = geometric_reducer_builder(
        diameter1=SteelDims.DIM_1_INCHES, diameter2=SteelDims.DIM_0_75_INCHES
    )
    junction = Junction(
        id=1,
        origin=Point(x=0, y=0),
        junction_type=JunctionType.TWO_WAY,
        connected_edges_ids=[1, 2],
    )
    edge_pipe_dim_map = {
        1: SteelDims.DIM_0_75_INCHES,
        2: SteelDims.DIM_1_INCHES,
    }
    resolver = PlacementResolver()
    junction_assembly = _build_junction_assembly(
        junction=junction,
        edge_id_line_map=edge_id_line_map,
        edge_pipe_dim_map=edge_pipe_dim_map,
    )

    strategy = resolver.resolve(
        _build_placement_assembly(junction_assembly, [geometric_reducer])
    )
    assert isinstance(strategy, SingleReducerPlacementStrategy)
    context = strategy.get_placement_context(geometric_reducer)

    assert context.transform.origin == expected_transform.origin
    assert context.transform.angle == expected_transform.angle
    assert context.view_type == ViewType.ELEVATION


@pytest.mark.parametrize(
    "edge_id_line_map, expected_transform",
    [
        (
            # simple test two lines
            {
                1: Line(start=Point(x=0, y=0), end=Point(x=100, y=0), id=1),
                2: Line(start=Point(x=0, y=0), end=Point(x=0, y=100), id=2),
            },
            Transform2D(Point(x=38, y=38), radians(180)),
        ),
        (
            # simple test but reversed endpoints of lines
            {
                1: Line(end=Point(x=0, y=0), start=Point(x=100, y=0), id=1),
                2: Line(end=Point(x=0, y=0), start=Point(x=0, y=100), id=2),
            },
            Transform2D(Point(x=38, y=38), radians(180)),
        ),
        (
            # reversed lines order by reversing ids
            {
                2: Line(start=Point(x=0, y=0), end=Point(x=100, y=0), id=1),
                1: Line(start=Point(x=0, y=0), end=Point(x=0, y=100), id=2),
            },
            Transform2D(Point(x=38, y=38), radians(180)),
        ),
        (
            # 2nd quadrant lines
            {
                1: Line(start=Point(x=-100, y=100), end=Point(x=0, y=0), id=1),
                2: Line(start=Point(x=0, y=0), end=Point(x=-100, y=-100), id=2),
            },
            Transform2D(Point(x=-53.7401, y=0.0), radians(-45)),
        ),
        (
            # 2nd quadrant reversed line by reversing ids
            {
                2: Line(start=Point(x=-100, y=100), end=Point(x=0, y=0), id=1),
                1: Line(start=Point(x=0, y=0), end=Point(x=-100, y=-100), id=2),
            },
            Transform2D(Point(x=-53.7401, y=0.0), radians(-45)),
        ),
    ],
)
def test_single_elbow_strategy_matches_legacy_cases(
    edge_id_line_map, expected_transform
):
    geometric_elbow = geometric_elbow_builder(
        diameter=SteelDims.DIM_1_INCHES, angle=90.0
    )
    junction = Junction(
        id=1,
        origin=Point(x=0, y=0),
        junction_type=JunctionType.TWO_WAY,
        connected_edges_ids=[1, 2],
    )
    edge_pipe_dim_map = {
        1: SteelDims.DIM_1_INCHES,
        2: SteelDims.DIM_1_INCHES,
    }
    resolver = PlacementResolver()
    junction_assembly = _build_junction_assembly(
        junction=junction,
        edge_id_line_map=edge_id_line_map,
        edge_pipe_dim_map=edge_pipe_dim_map,
    )

    strategy = resolver.resolve(
        _build_placement_assembly(junction_assembly, [geometric_elbow])
    )
    assert isinstance(strategy, SingleElbowPlacementStrategy)

    context = strategy.get_placement_context(geometric_elbow)

    assert context.transform.origin == expected_transform.origin
    assert context.transform.angle == expected_transform.angle
    assert context.view_type == ViewType.ELEVATION


@pytest.mark.parametrize(
    "geometric_components, edge_id_line_map, edge_pipe_dim_map, expected_transforms",
    [
        (
            [geometric_tee_builder(), geometric_reducer_builder()],
            {
                1: Line(start=Point(x=0, y=0), end=Point(x=100, y=0), id=1),
                2: Line(start=Point(x=0, y=0), end=Point(x=-100, y=0), id=2),
                3: Line(start=Point(x=0, y=0), end=Point(x=0, y=100), id=3),
            },
            {
                1: SteelDims.DIM_0_75_INCHES,
                2: SteelDims.DIM_1_INCHES,
                3: SteelDims.DIM_1_INCHES,
            },
            [
                Transform2D(Point(x=0, y=0), radians(0)),
                Transform2D(Point(x=138, y=0), radians(180)),
            ],
        ),
        (
            [geometric_tee_builder(), geometric_reducer_builder()],
            {
                1: Line(start=Point(x=0, y=0), end=Point(x=100, y=0), id=1),
                2: Line(start=Point(x=0, y=0), end=Point(x=-100, y=0), id=2),
                3: Line(start=Point(x=0, y=0), end=Point(x=0, y=100), id=3),
            },
            {
                1: SteelDims.DIM_1_INCHES,
                2: SteelDims.DIM_0_75_INCHES,
                3: SteelDims.DIM_1_INCHES,
            },
            [
                Transform2D(Point(x=0, y=0), radians(0)),
                Transform2D(Point(x=-138, y=0), radians(0)),
            ],
        ),
        (
            [
                geometric_tee_builder(),
                geometric_reducer_builder(),
                geometric_reducer_builder(),
            ],
            {
                1: Line(start=Point(x=0, y=0), end=Point(x=100, y=0), id=1),
                2: Line(start=Point(x=0, y=0), end=Point(x=-100, y=0), id=2),
                3: Line(start=Point(x=0, y=0), end=Point(x=0, y=100), id=3),
            },
            {
                1: SteelDims.DIM_0_75_INCHES,
                2: SteelDims.DIM_0_75_INCHES,
                3: SteelDims.DIM_1_INCHES,
            },
            [
                Transform2D(Point(x=0, y=0), radians(0)),
                Transform2D(Point(x=138, y=0), radians(180)),
                Transform2D(Point(x=-138, y=0), radians(0)),
            ],
        ),
        (
            [
                geometric_tee_builder(),
                geometric_reducer_builder(),
                geometric_reducer_builder(diameter2=SteelDims.DIM_0_5_INCHES),
            ],
            {
                1: Line(start=Point(x=0, y=0), end=Point(x=100, y=0), id=1),
                2: Line(start=Point(x=0, y=0), end=Point(x=-100, y=0), id=2),
                3: Line(start=Point(x=0, y=0), end=Point(x=0, y=100), id=3),
            },
            {
                1: SteelDims.DIM_0_5_INCHES,
                2: SteelDims.DIM_0_75_INCHES,
                3: SteelDims.DIM_1_INCHES,
            },
            [
                Transform2D(Point(x=0, y=0), radians(0)),
                Transform2D(Point(x=-138, y=0), radians(0)),
                Transform2D(Point(x=138, y=0), radians(180)),
            ],
        ),
    ],
)
def test_group_transform_resolve(
    geometric_components,
    edge_id_line_map,
    edge_pipe_dim_map,
    expected_transforms,
):
    junction = Junction(
        id=1,
        origin=Point(x=0, y=0),
        junction_type=JunctionType.THREE_WAY,
        connected_edges_ids=[1, 2, 3],
    )

    resolver = PlacementResolver()
    junction_assembly = _build_junction_assembly(
        junction=junction,
        edge_id_line_map=edge_id_line_map,
        edge_pipe_dim_map=edge_pipe_dim_map,
    )

    strategy = resolver.resolve(
        _build_placement_assembly(junction_assembly, geometric_components)
    )
    assert isinstance(strategy, TeeReducerPlacementStrategy)

    for component, expected_transform in zip(geometric_components, expected_transforms):
        context = strategy.get_placement_context(component)
        assert context.transform.origin == expected_transform.origin
        assert context.transform.angle == expected_transform.angle
        assert context.view_type == ViewType.ELEVATION


@pytest.mark.parametrize(
    "edge_id_line_map, edge_pipe_dim_map, expected_contexts",
    [
        (
            {
                1: Line(start=Point(x=0, y=0), end=Point(x=100, y=0), id=1),
                2: Line(start=Point(x=0, y=0), end=Point(x=-100, y=0), id=2),
                3: Line(start=Point(x=0, y=0), end=Point(x=0, y=100), id=3),
            },
            {
                1: SteelDims.DIM_1_INCHES,
                2: SteelDims.DIM_1_INCHES,
                3: SteelDims.DIM_1_INCHES,
            },
            [
                PlacementContext(
                    transform=Transform2D(Point(x=0, y=0), radians(0)),
                    view_type=ViewType.PLAN,
                ),
                PlacementContext(
                    transform=Transform2D(Point(x=0, y=0), radians(0)),
                    view_type=ViewType.PLAN,
                ),
            ],
        ),
        (
            {
                1: Line(start=Point(x=0, y=0), end=Point(x=100, y=100), id=1),
                2: Line(start=Point(x=0, y=0), end=Point(x=-100, y=-100), id=2),
                3: Line(start=Point(x=0, y=0), end=Point(x=-100, y=100), id=3),
            },
            {
                1: SteelDims.DIM_1_INCHES,
                2: SteelDims.DIM_1_INCHES,
                3: SteelDims.DIM_1_INCHES,
            },
            [
                PlacementContext(
                    transform=Transform2D(Point(x=0, y=0), radians(45)),
                    view_type=ViewType.PLAN,
                ),
                PlacementContext(
                    transform=Transform2D(Point(x=0, y=0), radians(45)),
                    view_type=ViewType.PLAN,
                ),
            ],
        ),
    ],
)
def test_tee_with_elbow_placement(
    edge_id_line_map,
    edge_pipe_dim_map,
    expected_contexts,
):
    geometric_components = [geometric_tee_builder(), geometric_elbow_builder()]
    junction = Junction(
        id=1,
        origin=Point(x=0, y=0),
        junction_type=JunctionType.THREE_WAY,
        connected_edges_ids=[1, 2, 3],
    )

    resolver = PlacementResolver()
    junction_assembly = _build_junction_assembly(
        junction=junction,
        edge_id_line_map=edge_id_line_map,
        edge_pipe_dim_map=edge_pipe_dim_map,
    )

    strategy = resolver.resolve(
        _build_placement_assembly(junction_assembly, geometric_components)
    )
    assert isinstance(strategy, TeeElbowRisePlacementStrategy)

    for component, expected_context in zip(geometric_components, expected_contexts):
        context = strategy.get_placement_context(component)
        assert context.transform.origin == expected_context.transform.origin
        assert context.transform.angle == expected_context.transform.angle
        assert context.view_type == expected_context.view_type
