from fireplanner.geometry.primitives import Block, Line, Point
from fireplanner.networks import (
    CoreNetwork,
    CoreNetworkConfig,
    EdgeInfo,
    FourWayJunctionInfo,
    SprinklerJunctionInfo,
    ThreeWayJunctionInfo,
    TopologyInterpreter,
    TwoWayJunctionInfo,
)
from fireplanner.networks.junction import Junction, JunctionType
from tests.unit.test_core_network import build_simple_network_core_network


def test_core_network_returns_junction_infos():
    network = build_simple_network_core_network()

    junction_infos = network.get_junctions_info()

    assert junction_infos
    assert len(junction_infos) == len(network.get_junctions())


def test_topology_interpreter_builds_three_way_junction_info():
    network = build_simple_network_core_network()

    junction_infos = network.get_junctions_info()
    three_way_infos = [
        info for info in junction_infos if isinstance(info, ThreeWayJunctionInfo)
    ]

    assert three_way_infos
    info = three_way_infos[0]
    assert len(info.run) == 2
    assert isinstance(info.branch, EdgeInfo)


def test_topology_interpreter_builds_two_way_junction_info():
    network = build_simple_network_core_network()

    junction_infos = network.get_junctions_info()
    two_way_infos = [
        info for info in junction_infos if isinstance(info, TwoWayJunctionInfo)
    ]

    assert two_way_infos
    info = two_way_infos[0]
    assert len(info.edges) == 2
    assert all(edge_info.length > 0 for edge_info in info.edges)


def test_topology_interpreter_builds_sprinkler_junction_info():
    network = CoreNetwork(
        config=CoreNetworkConfig(
            sprinkler_block_data={"SPR": {"k_factor": 5.6, "temperature": 68}},
            sprinkler_blocks=[Block(name="SPR", center=Point(x=5, y=0))],
            lines=[Line(start=Point(x=0, y=0), end=Point(x=10, y=0), id=1)],
        )
    )

    junction_infos = network.get_junctions_info()
    sprinkler_infos = [
        info for info in junction_infos if isinstance(info, SprinklerJunctionInfo)
    ]

    assert sprinkler_infos
    first_sprinkler_info = sprinkler_infos[0]
    assert first_sprinkler_info.sprinkler_info is not None
    assert first_sprinkler_info.sprinkler_info.k_factor == 5.6
    assert first_sprinkler_info.sprinkler_info.temperature == 68


def test_topology_interpreter_reads_metadata_for_multiple_sprinkler_block_names():
    network = CoreNetwork(
        config=CoreNetworkConfig(
            sprinkler_block_data={
                "SPR56": {"k_factor": 5.6, "temperature": 68},
                "SPR8": {"k_factor": 8, "temperature": 74},
            },
            sprinkler_blocks=[
                Block(name="SPR56", center=Point(x=5, y=0)),
                Block(name="SPR8", center=Point(x=15, y=0)),
            ],
            lines=[
                Line(start=Point(x=0, y=0), end=Point(x=20, y=0), id=1),
            ],
        )
    )

    junction_infos = network.get_junctions_info()
    sprinkler_infos = [
        info for info in junction_infos if isinstance(info, SprinklerJunctionInfo)
    ]

    assert len(sprinkler_infos) == 2
    assert [info.sprinkler_info.k_factor for info in sprinkler_infos] == [5.6, 8.0]
    assert [info.sprinkler_info.temperature for info in sprinkler_infos] == [68.0, 74.0]


def test_topology_interpreter_builds_four_way_runs_ordered_by_cop():
    origin = Point(x=0, y=0)
    lines = {
        1: Line(start=Point(x=-100, y=0), end=origin, id=1),
        2: Line(start=origin, end=Point(x=100, y=0), id=2),
        3: Line(start=Point(x=0, y=-100), end=origin, id=3),
        4: Line(start=origin, end=Point(x=0, y=100), id=4),
    }
    interpreter = TopologyInterpreter(
        edge_id_line_map=lines,
        edge_id_elevation_map={1: 100, 2: 100, 3: 200, 4: 200},
        edge_id_sprinkler_map={1: 8, 2: 2, 3: 2, 4: 1},
    )

    info = interpreter.interpret_junction(
        Junction(
            id=1,
            origin=origin,
            junction_type=JunctionType.FOUR_WAY,
            connected_edges_ids=[1, 3, 2, 4],
        )
    )

    assert isinstance(info, FourWayJunctionInfo)
    assert {edge.edge_id for edge in info.lower_run} == {1, 2}
    assert {edge.edge_id for edge in info.upper_run} == {3, 4}
    assert {edge.elevation for edge in info.lower_run} == {100}
    assert {edge.elevation for edge in info.upper_run} == {200}
