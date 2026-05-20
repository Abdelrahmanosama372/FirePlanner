from fireplanner.geometry.primitives import Block, Line, Point
from fireplanner.networks import (
    CoreNetwork,
    CoreNetworkConfig,
    EdgeInfo,
    SprinklerJunctionInfo,
    ThreeWayJunctionInfo,
    TwoWayJunctionInfo,
)
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
