import pytest

from fireplanner.firecomponent import Elbow, Reducer, SteelDims, Tee
from fireplanner.geometry.primitives import Line, Point
from fireplanner.networks import CoreNetwork, ModelNetwork, ModelNetworkConfig
from fireplanner.networks.junction_info import (
    EdgeInfo,
    ThreeWayJunctionInfo,
    TwoWayJunctionInfo,
)


class _FakeCoreNetwork:
    def __init__(
        self,
        edges_info: list[EdgeInfo],
        junctions_info: list[TwoWayJunctionInfo | ThreeWayJunctionInfo],
    ) -> None:
        self._edges_info = edges_info
        self._junctions_info = junctions_info

    def get_edges_info(self) -> list[EdgeInfo]:
        return list(self._edges_info)

    def get_junctions_info(self) -> list[TwoWayJunctionInfo | ThreeWayJunctionInfo]:
        return list(self._junctions_info)


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
