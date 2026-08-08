import pytest

from fireplanner.firecomponent import Elbow, Reducer, SteelConnection, SteelDims, Tee
from fireplanner.geometry.primitives import Line, Point, PrimitiveStyle
from fireplanner.networks import CoreNetwork, ModelNetwork, ModelNetworkConfig
from fireplanner.networks.junction_info import (
    EdgeInfo,
    FourWayJunctionInfo,
    SprinklerInfo,
    SprinklerJunctionInfo,
    TerminalSprinklerInfo,
    ThreeWayJunctionInfo,
    TwoWayJunctionInfo,
)


class _FakeCoreNetwork:
    def __init__(
        self,
        edges_info: list[EdgeInfo],
        junctions_info: list[
            TwoWayJunctionInfo
            | ThreeWayJunctionInfo
            | FourWayJunctionInfo
            | SprinklerJunctionInfo
        ],
        terminal_sprinkler_infos: list[TerminalSprinklerInfo] | None = None,
    ) -> None:
        self._edges_info = edges_info
        self._junctions_info = junctions_info
        self._terminal_sprinkler_infos = terminal_sprinkler_infos or []

    def get_edges_info(self) -> list[EdgeInfo]:
        return list(self._edges_info)

    def get_junctions_info(
        self,
    ) -> list[
        TwoWayJunctionInfo
        | ThreeWayJunctionInfo
        | FourWayJunctionInfo
        | SprinklerJunctionInfo
    ]:
        return list(self._junctions_info)

    def get_terminal_sprinkler_infos(self) -> list[TerminalSprinklerInfo]:
        return list(self._terminal_sprinkler_infos)


@pytest.fixture
def defaultModelNetwork():
    return ModelNetwork(CoreNetwork())


@pytest.mark.parametrize(
    "pipe1, pipe2, angle, expected_types",
    [
        # same diameter + straight
        (
            SteelDims.DIM_2_INCHES,
            SteelDims.DIM_2_INCHES,
            0.0,
            [],
        ),
        # different diameter + straight -> reducer
        (
            SteelDims.DIM_2_INCHES,
            SteelDims.DIM_1_INCHES,
            0.0,
            [Reducer],
        ),
        # angled -> elbow
        (
            SteelDims.DIM_2_INCHES,
            SteelDims.DIM_1_INCHES,
            90.0,
            [Elbow],
        ),
    ],
)
def test_create_fire_connection_for_two_way_junction(
    defaultModelNetwork,
    pipe1,
    pipe2,
    angle,
    expected_types,
):

    connections = defaultModelNetwork._create_fire_connection_for_two_way_junction(
        pipe1,
        pipe2,
        angle,
    )

    assert len(connections) == len(expected_types)

    for connection, expected_type in zip(connections, expected_types):
        assert isinstance(connection, expected_type)


@pytest.mark.parametrize(
    "run1, run2, branch, expected_types",
    [
        # equal runs + smaller branch
        (
            SteelDims.DIM_4_INCHES,
            SteelDims.DIM_4_INCHES,
            SteelDims.DIM_2_INCHES,
            [Tee],
        ),
        # unequal runs + smaller branch
        (
            SteelDims.DIM_4_INCHES,
            SteelDims.DIM_2_INCHES,
            SteelDims.DIM_1_INCHES,
            [Tee, Reducer],
        ),
        # branch is largest
        (
            SteelDims.DIM_2_INCHES,
            SteelDims.DIM_3_INCHES,
            SteelDims.DIM_6_INCHES,
            [Tee, Reducer, Reducer],
        ),
    ],
)
def test_create_fire_connection_for_three_way_junction(
    defaultModelNetwork,
    run1,
    run2,
    branch,
    expected_types,
):

    connections = defaultModelNetwork._create_fire_connection_for_three_way_junction(
        run1,
        run2,
        branch,
    )

    assert len(connections) == len(expected_types)

    for connection, expected_type in zip(connections, expected_types):
        assert isinstance(connection, expected_type)


def test_short_transition_edge_collapses_on_inline_two_way_chain():
    edges_info = [
        EdgeInfo(
            edge_id=1,
            line=Line(start=Point(x=0, y=0), end=Point(x=1000, y=0), id=1),
            length=1000.0,
            sprinkler_count=2,
        ),
        EdgeInfo(
            edge_id=2,
            line=Line(start=Point(x=1000, y=0), end=Point(x=1300, y=0), id=2),
            length=300.0,
            sprinkler_count=3,
        ),
        EdgeInfo(
            edge_id=3,
            line=Line(start=Point(x=1300, y=0), end=Point(x=2300, y=0), id=3),
            length=1000.0,
            sprinkler_count=5,
        ),
    ]
    junctions_info = [
        TwoWayJunctionInfo(
            junction_id=1,
            origin=Point(x=1000, y=0),
            edges=[edges_info[0], edges_info[1]],
            angle=0.0,
        ),
        TwoWayJunctionInfo(
            junction_id=2,
            origin=Point(x=1300, y=0),
            edges=[edges_info[1], edges_info[2]],
            angle=0.0,
        ),
    ]

    network = ModelNetwork(
        _FakeCoreNetwork(edges_info, junctions_info),
        config=ModelNetworkConfig(
            short_transition_edges_enabled=True,
            short_transition_edges_max_length_mm=400.0,
        ),
    )

    diameters = network.get_edge_id_to_pipe_diameter_map()
    assert diameters[1] == SteelDims.DIM_1_INCHES
    assert diameters[2] == SteelDims.DIM_1_5_INCHES
    assert diameters[3] == SteelDims.DIM_1_5_INCHES


def test_short_transition_edge_collapses_on_three_way_run_chain_not_branch():
    edges_info = [
        EdgeInfo(
            edge_id=1,
            line=Line(start=Point(x=0, y=0), end=Point(x=1000, y=0), id=1),
            length=1000.0,
            sprinkler_count=2,
        ),
        EdgeInfo(
            edge_id=2,
            line=Line(start=Point(x=1000, y=0), end=Point(x=1300, y=0), id=2),
            length=300.0,
            sprinkler_count=3,
        ),
        EdgeInfo(
            edge_id=3,
            line=Line(start=Point(x=1300, y=0), end=Point(x=2300, y=0), id=3),
            length=1000.0,
            sprinkler_count=5,
        ),
        EdgeInfo(
            edge_id=4,
            line=Line(start=Point(x=1300, y=0), end=Point(x=1300, y=1000), id=4),
            length=1000.0,
            sprinkler_count=1,
        ),
    ]
    junctions_info = [
        TwoWayJunctionInfo(
            junction_id=1,
            origin=Point(x=1000, y=0),
            edges=[edges_info[0], edges_info[1]],
            angle=0.0,
        ),
        ThreeWayJunctionInfo(
            junction_id=2,
            origin=Point(x=1300, y=0),
            run=[edges_info[1], edges_info[2]],
            branch=edges_info[3],
        ),
    ]

    network = ModelNetwork(
        _FakeCoreNetwork(edges_info, junctions_info),
        config=ModelNetworkConfig(
            short_transition_edges_enabled=True,
            short_transition_edges_max_length_mm=400.0,
        ),
    )

    diameters = network.get_edge_id_to_pipe_diameter_map()
    assert diameters[1] == SteelDims.DIM_1_INCHES
    assert diameters[2] == SteelDims.DIM_1_5_INCHES
    assert diameters[3] == SteelDims.DIM_1_5_INCHES
    assert diameters[4] == SteelDims.DIM_1_INCHES


def test_layer_name_to_pipe_diameter_overrides_sprinkler_based_sizing():
    edges_info = [
        EdgeInfo(
            edge_id=1,
            line=Line(
                start=Point(x=0, y=0),
                end=Point(x=1000, y=0),
                id=1,
                style=PrimitiveStyle(layer="fire-cabinet"),
            ),
            length=1000.0,
            sprinkler_count=0,
        )
    ]

    network = ModelNetwork(
        _FakeCoreNetwork(edges_info, []),
        config=ModelNetworkConfig(
            layer_name_to_pipe_diameter={"fire-cabinet": 1.0},
        ),
    )

    diameters = network.get_edge_id_to_pipe_diameter_map()
    assert diameters[1] == SteelDims.DIM_1_INCHES


def test_inline_sprinkler_adds_branch_connection_and_reducer_to_boq_only():
    edges_info = [
        EdgeInfo(
            edge_id=1,
            line=Line(start=Point(x=0, y=0), end=Point(x=500, y=0), id=1),
            length=500.0,
            sprinkler_count=2,
        ),
        EdgeInfo(
            edge_id=2,
            line=Line(start=Point(x=500, y=0), end=Point(x=1000, y=0), id=2),
            length=500.0,
            sprinkler_count=2,
        ),
    ]
    junctions_info = [
        SprinklerJunctionInfo(
            junction_id=1,
            origin=Point(x=500, y=0),
            edges=edges_info,
            angle=0.0,
            sprinkler_info=SprinklerInfo(k_factor=5.6, temperature=68.0),
        )
    ]

    network = ModelNetwork(_FakeCoreNetwork(edges_info, junctions_info))

    assert network.get_fire_connections_with_junctions_ids() == {}

    connections = network.get_boq_only_fire_connections()
    assert len(connections) == 2
    assert isinstance(connections[0], Tee)
    assert connections[0].branch_diameter == SteelDims.DIM_1_INCHES
    assert isinstance(connections[1], Reducer)
    assert connections[1].large_diameter == SteelDims.DIM_1_INCHES
    assert connections[1].small_diameter == SteelDims.DIM_0_5_INCHES


def test_terminal_sprinkler_connections_are_boq_only():
    edge_info = EdgeInfo(
        edge_id=1,
        line=Line(start=Point(x=0, y=0), end=Point(x=500, y=0), id=1),
        length=500.0,
        sprinkler_count=2,
    )

    network = ModelNetwork(
        _FakeCoreNetwork(
            [edge_info],
            [],
            terminal_sprinkler_infos=[
                TerminalSprinklerInfo(
                    origin=Point(x=500, y=0),
                    edge=edge_info,
                    sprinkler_info=SprinklerInfo(k_factor=8.0, temperature=68.0),
                )
            ],
        )
    )

    assert network.get_fire_connections_with_junctions_ids() == {}
    connections = network.get_boq_only_fire_connections()
    assert len(connections) == 2
    assert isinstance(connections[0], Elbow)
    assert connections[0].diameter == SteelDims.DIM_1_INCHES
    assert isinstance(connections[1], Reducer)
    assert connections[1].large_diameter == SteelDims.DIM_1_INCHES
    assert connections[1].small_diameter == SteelDims.DIM_0_75_INCHES
    assert network.get_junctions_assembly() == []


def test_terminal_sprinkler_with_k11_has_no_reducer():
    edge_info = EdgeInfo(
        edge_id=1,
        line=Line(start=Point(x=0, y=0), end=Point(x=500, y=0), id=1),
        length=500.0,
        sprinkler_count=2,
    )

    network = ModelNetwork(
        _FakeCoreNetwork(
            [edge_info],
            [],
            terminal_sprinkler_infos=[
                TerminalSprinklerInfo(
                    origin=Point(x=500, y=0),
                    edge=edge_info,
                    sprinkler_info=SprinklerInfo(k_factor=11.0, temperature=68.0),
                )
            ],
        )
    )

    connections = network.get_boq_only_fire_connections()
    assert len(connections) == 1
    assert isinstance(connections[0], Elbow)
    assert connections[0].diameter == SteelDims.DIM_1_INCHES


def test_inline_sprinkler_branch_connection_uses_run_connection_type():
    network = ModelNetwork(
        _FakeCoreNetwork([], []),
        config=ModelNetworkConfig(
            connection_type_by_diameter={
                SteelDims.DIM_1_5_INCHES: SteelConnection.Threaded,
                SteelDims.DIM_2_5_INCHES: SteelConnection.Welded,
            }
        ),
    )

    threaded_branch = network._create_inline_sprinkler_branch_connection(
        pipe1_dim=SteelDims.DIM_1_5_INCHES,
        pipe2_dim=SteelDims.DIM_1_5_INCHES,
    )
    welded_branch = network._create_inline_sprinkler_branch_connection(
        pipe1_dim=SteelDims.DIM_2_5_INCHES,
        pipe2_dim=SteelDims.DIM_2_5_INCHES,
    )

    assert threaded_branch.run_diameter == SteelDims.DIM_1_5_INCHES
    assert threaded_branch.branch_diameter == SteelDims.DIM_1_INCHES
    assert threaded_branch.connection_type == SteelConnection.Threaded

    assert welded_branch.run_diameter == SteelDims.DIM_2_5_INCHES
    assert welded_branch.branch_diameter == SteelDims.DIM_1_INCHES
    assert welded_branch.connection_type == SteelConnection.Welded


@pytest.mark.parametrize(
    "pipe1, pipe2, expected_types",
    [
        (
            SteelDims.DIM_2_INCHES,
            SteelDims.DIM_2_INCHES,
            [Elbow, Elbow],
        ),
        (
            SteelDims.DIM_2_INCHES,
            SteelDims.DIM_1_INCHES,
            [Elbow, Elbow, Reducer],
        ),
    ],
)
def test_create_fire_connections_for_two_way_elevation_change(
    defaultModelNetwork,
    pipe1,
    pipe2,
    expected_types,
):
    connections = (
        defaultModelNetwork._create_fire_connections_for_two_way_elevation_change(
            pipe1,
            pipe2,
        )
    )

    assert [type(connection) for connection in connections] == expected_types
    assert [connection.diameter for connection in connections[:2]] == [pipe1, pipe2]
    assert all(connection.angle == 90 for connection in connections[:2])


def test_two_way_elevation_change_constructs_double_elbow():
    edges_info = [
        EdgeInfo(
            edge_id=1,
            line=Line(start=Point(x=-100, y=0), end=Point(x=0, y=0), id=1),
            length=100,
            sprinkler_count=1,
            elevation=10,
        ),
        EdgeInfo(
            edge_id=2,
            line=Line(start=Point(x=0, y=0), end=Point(x=100, y=0), id=2),
            length=100,
            sprinkler_count=1,
            elevation=0,
        ),
    ]
    network = ModelNetwork(
        _FakeCoreNetwork(
            edges_info,
            [
                TwoWayJunctionInfo(
                    junction_id=1,
                    origin=Point(x=0, y=0),
                    edges=edges_info,
                    angle=0,
                )
            ],
        )
    )

    connections = network.get_fire_connections_with_junctions_ids()[1]

    assert [type(connection) for connection in connections] == [Elbow, Elbow]


def test_four_way_junction_constructs_double_tee_and_reducers():
    origin = Point(x=0, y=0)
    edges_info = [
        EdgeInfo(1, Line(Point(x=-100, y=0), origin, id=1), 100, 10, 100),
        EdgeInfo(2, Line(origin, Point(x=100, y=0), id=2), 100, 2, 100),
        EdgeInfo(3, Line(Point(x=0, y=-100), origin, id=3), 100, 2, 200),
        EdgeInfo(4, Line(origin, Point(x=0, y=100), id=4), 100, 1, 200),
    ]
    junction_info = FourWayJunctionInfo(
        junction_id=1,
        origin=origin,
        lower_run=edges_info[:2],
        upper_run=edges_info[2:],
    )

    network = ModelNetwork(_FakeCoreNetwork(edges_info, [junction_info]))
    connections = network.get_fire_connections_with_junctions_ids()[1]

    assert [type(connection) for connection in connections] == [
        Tee,
        Tee,
        Reducer,
        Reducer,
        Reducer,
    ]
    lower_tee, upper_tee = connections[:2]
    assert lower_tee.run_diameter == SteelDims.DIM_2_INCHES
    assert lower_tee.branch_diameter == SteelDims.DIM_1_25_INCHES
    assert upper_tee.run_diameter == SteelDims.DIM_1_25_INCHES
    assert upper_tee.branch_diameter == SteelDims.DIM_1_25_INCHES
