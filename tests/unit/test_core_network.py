import pytest

from fireplanner.geometry.primitives import Line
from fireplanner.networks.core_network import CoreNetwork, CoreNetworkConfig, FlowRoute
from fireplanner.networks.junction import JunctionType
from tests.unit.core_network import (
    build_complex_network_blocks,
    build_complex_network_core_network,
    build_complex_network_lines,
    build_loop_network_blocks,
    build_loop_network_lines,
    build_simple_network_blocks,
    build_simple_network_core_network,
    build_simple_network_inverted_lines,
    build_simple_network_lines,
)


def line_signature(line: Line) -> tuple[float, float, float, float]:
    return (line.start.x, line.start.y, line.end.x, line.end.y)


def flatten_serialized_core_node(node_data: dict) -> list[dict]:
    nodes = [node_data["CoreNode"]]
    for child_node in node_data["CoreNode"]["connected_nodes"]:
        nodes.extend(flatten_serialized_core_node(child_node))
    return nodes


def get_serialized_simple_network_nodes() -> list[dict]:
    network = build_simple_network_core_network()
    root_data = network.to_json()["CoreNetwork"]["root"]
    assert root_data is not None
    return flatten_serialized_core_node(root_data)


def get_serialized_complex_network_nodes() -> list[dict]:
    network = build_complex_network_core_network()
    root_data = network.to_json()["CoreNetwork"]["root"]
    assert root_data is not None
    return flatten_serialized_core_node(root_data)


@pytest.mark.parametrize(
    ("build_lines", "build_blocks", "expected_lines", "expected_ids"),
    [
        (
            build_simple_network_lines,
            build_simple_network_blocks,
            {
                1: (0.0, 3000.0, 4000.0, 3000.0),
                2: (0.0, 4000.0, -6000.0, 4000.0),
                3: (0.0, 5000.0, 0.0, 9000.0),
                4: (0.0, 9000.0, 6000.0, 9000.0),
            },
            {1, 2, 3, 4},
        ),
        (
            build_simple_network_inverted_lines,
            build_simple_network_blocks,
            {
                1: (0.0, 3000.0, 4000.0, 3000.0),
                2: (0.0, 4000.0, -6000.0, 4000.0),
                3: (0.0, 5000.0, 0.0, 9000.0),
                4: (0.0, 9000.0, 6000.0, 9000.0),
            },
            {1, 2, 3, 4},
        ),
        (
            build_complex_network_lines,
            build_complex_network_blocks,
            {
                1: (0.0, 6000.0, 0.0, 12000.0),
                2: (0.0, 12000.0, 0.0, 15000.0),
                3: (0.0, 4000.0, 6000.0, 4000.0),
                4: (0.0, 5000.0, -6000.0, 5000.0),
                5: (0.0, 10000.0, 8000.0, 10000.0),
                6: (0.0, 9000.0, -8000.0, 9000.0),
                7: (0.0, 15000.0, 5000.0, 15000.0),
                8: (6000.0, 4000.0, 10000.0, 4000.0),
                9: (-6000.0, 5000.0, -10000.0, 5000.0),
                10: (8000.0, 10000.0, 12000.0, 10000.0),
                11: (-8000.0, 9000.0, -12000.0, 9000.0),
                12: (5000.0, 15000.0, 9000.0, 18000.0),
                13: (12000.0, 10000.0, 12000.0, 14000.0),
                14: (12000.0, 14000.0, 16000.0, 14000.0),
            },
            {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14},
        ),
        (
            build_loop_network_lines,
            build_loop_network_blocks,
            {
                1: (0.0, 2000.0, 0.0, 5000.0),
                2: (0.0, 4000.0, 4000.0, 4000.0),
                3: (4000.0, 4000.0, 4000.0, 8000.0),
                4: (4000.0, 8000.0, 0.0, 8000.0),
                5: (0.0, 5000.0, 0.0, 9000.0),
                6: (0.0, 9000.0, 0.0, 12000.0),
            },
            {1, 2, 3, 4, 5, 6},
        ),
    ],
)
def test_preprocessing_orients_fixture_lines(
    build_lines,
    build_blocks,
    expected_lines,
    expected_ids,
):
    lines = build_lines()
    blocks = build_blocks()
    network = CoreNetwork(config=CoreNetworkConfig(sprinkler_blocks=blocks, lines=[]))

    processed_lines = network._preprocessing(lines[0], lines[1:])

    assert {line.id for line in processed_lines} == expected_ids
    assert {line.id: line_signature(line) for line in processed_lines} == expected_lines


@pytest.mark.parametrize(
    ("get_nodes", "expected"),
    [
        (
            get_serialized_simple_network_nodes,
            {
                1: None,
                2: {"Point": "0.0, 2000.0, 0.0"},
                3: {"Point": "0.0, 3000.0, 0.0"},
                4: {"Point": "0.0, 4000.0, 0.0"},
                5: {"Point": "0.0, 3000.0, 0.0"},
                6: {"Point": "2000.0, 3000.0, 0.0"},
                7: {"Point": "0.0, 4000.0, 0.0"},
                8: {"Point": "-4000.0, 4000.0, 0.0"},
                9: {"Point": "0.0, 5000.0, 0.0"},
                10: {"Point": "0.0, 8000.0, 0.0"},
                11: {"Point": "0.0, 9000.0, 0.0"},
                12: {"Point": "1000.0, 9000.0, 0.0"},
            },
        ),
        (
            get_serialized_complex_network_nodes,
            {
                1: None,
                2: {"Point": "0.0, 3000.0, 0.0"},
                3: {"Point": "0.0, 4000.0, 0.0"},
                4: {"Point": "0.0, 5000.0, 0.0"},
                5: {"Point": "0.0, 4000.0, 0.0"},
                6: {"Point": "6000.0, 4000.0, 0.0"},
                7: {"Point": "0.0, 5000.0, 0.0"},
                8: {"Point": "-3000.0, 5000.0, 0.0"},
                9: {"Point": "-6000.0, 5000.0, 0.0"},
                10: {"Point": "0.0, 6000.0, 0.0"},
                11: {"Point": "0.0, 8000.0, 0.0"},
                12: {"Point": "0.0, 9000.0, 0.0"},
                13: {"Point": "0.0, 10000.0, 0.0"},
                14: {"Point": "0.0, 9000.0, 0.0"},
                15: {"Point": "-8000.0, 9000.0, 0.0"},
                16: {"Point": "0.0, 10000.0, 0.0"},
                17: {"Point": "6000.0, 10000.0, 0.0"},
                18: {"Point": "8000.0, 10000.0, 0.0"},
                19: {"Point": "9000.0, 10000.0, 0.0"},
                20: {"Point": "12000.0, 10000.0, 0.0"},
                21: {"Point": "12000.0, 12000.0, 0.0"},
                22: {"Point": "12000.0, 14000.0, 0.0"},
                23: {"Point": "15000.0, 14000.0, 0.0"},
                24: {"Point": "0.0, 12000.0, 0.0"},
                25: {"Point": "0.0, 13000.0, 0.0"},
                26: {"Point": "0.0, 15000.0, 0.0"},
                27: {"Point": "5000.0, 15000.0, 0.0"},
            },
        ),
    ],
)
def test_core_network_has_correct_intersection_points(get_nodes, expected):
    nodes = get_nodes()

    assert {node["id"]: node["intersection_point"] for node in nodes} == expected


@pytest.mark.parametrize(
    ("get_nodes", "expected"),
    [
        (
            get_serialized_simple_network_nodes,
            {
                1: ("0.0, 0.0, 0.0", "0.0, 2000.0, 0.0"),
                2: ("0.0, 2000.0, 0.0", "0.0, 3000.0, 0.0"),
                3: ("0.0, 3000.0, 0.0", "0.0, 4000.0, 0.0"),
                4: ("0.0, 4000.0, 0.0", "0.0, 5000.0, 0.0"),
                5: ("0.0, 3000.0, 0.0", "2000.0, 3000.0, 0.0"),
                6: ("2000.0, 3000.0, 0.0", "4000.0, 3000.0, 0.0"),
                7: ("0.0, 4000.0, 0.0", "-4000.0, 4000.0, 0.0"),
                8: ("-4000.0, 4000.0, 0.0", "-6000.0, 4000.0, 0.0"),
                9: ("0.0, 5000.0, 0.0", "0.0, 8000.0, 0.0"),
                10: ("0.0, 8000.0, 0.0", "0.0, 9000.0, 0.0"),
                11: ("0.0, 9000.0, 0.0", "1000.0, 9000.0, 0.0"),
                12: ("1000.0, 9000.0, 0.0", "6000.0, 9000.0, 0.0"),
            },
        ),
        (
            get_serialized_complex_network_nodes,
            {
                1: ("0.0, 0.0, 0.0", "0.0, 3000.0, 0.0"),
                2: ("0.0, 3000.0, 0.0", "0.0, 4000.0, 0.0"),
                3: ("0.0, 4000.0, 0.0", "0.0, 5000.0, 0.0"),
                4: ("0.0, 5000.0, 0.0", "0.0, 6000.0, 0.0"),
                5: ("0.0, 4000.0, 0.0", "6000.0, 4000.0, 0.0"),
                6: ("6000.0, 4000.0, 0.0", "10000.0, 4000.0, 0.0"),
                7: ("0.0, 5000.0, 0.0", "-3000.0, 5000.0, 0.0"),
                8: ("-3000.0, 5000.0, 0.0", "-6000.0, 5000.0, 0.0"),
                9: ("-6000.0, 5000.0, 0.0", "-10000.0, 5000.0, 0.0"),
                10: ("0.0, 6000.0, 0.0", "0.0, 8000.0, 0.0"),
                11: ("0.0, 8000.0, 0.0", "0.0, 9000.0, 0.0"),
                12: ("0.0, 9000.0, 0.0", "0.0, 10000.0, 0.0"),
                13: ("0.0, 10000.0, 0.0", "0.0, 12000.0, 0.0"),
                14: ("0.0, 9000.0, 0.0", "-8000.0, 9000.0, 0.0"),
                15: ("-8000.0, 9000.0, 0.0", "-12000.0, 9000.0, 0.0"),
                16: ("0.0, 10000.0, 0.0", "6000.0, 10000.0, 0.0"),
                17: ("6000.0, 10000.0, 0.0", "8000.0, 10000.0, 0.0"),
                18: ("8000.0, 10000.0, 0.0", "9000.0, 10000.0, 0.0"),
                19: ("9000.0, 10000.0, 0.0", "12000.0, 10000.0, 0.0"),
                20: ("12000.0, 10000.0, 0.0", "12000.0, 12000.0, 0.0"),
                21: ("12000.0, 12000.0, 0.0", "12000.0, 14000.0, 0.0"),
                22: ("12000.0, 14000.0, 0.0", "15000.0, 14000.0, 0.0"),
                23: ("15000.0, 14000.0, 0.0", "16000.0, 14000.0, 0.0"),
                24: ("0.0, 12000.0, 0.0", "0.0, 13000.0, 0.0"),
                25: ("0.0, 13000.0, 0.0", "0.0, 15000.0, 0.0"),
                26: ("0.0, 15000.0, 0.0", "5000.0, 15000.0, 0.0"),
                27: ("5000.0, 15000.0, 0.0", "9000.0, 18000.0, 0.0"),
            },
        ),
    ],
)
def test_core_network_has_correct_connected_edges(get_nodes, expected):
    nodes = get_nodes()

    assert {
        node["id"]: (
            node["edge"]["Line"]["start"]["Point"],
            node["edge"]["Line"]["end"]["Point"],
        )
        for node in nodes
    } == expected


def test_simple_network_flow_routes_assignment() -> None:
    network = build_simple_network_core_network()

    assert network.get_edge_flow_routes() == {
        1: FlowRoute.CONTINUATION,
        2: FlowRoute.CONTINUATION,
        3: FlowRoute.CONTINUATION,
        4: FlowRoute.CONTINUATION,
        5: FlowRoute.BRANCH,
        6: FlowRoute.BRANCH,
        7: FlowRoute.BRANCH,
        8: FlowRoute.BRANCH,
        9: FlowRoute.CONTINUATION,
        10: FlowRoute.CONTINUATION,
        11: FlowRoute.CONTINUATION,
        12: FlowRoute.CONTINUATION,
    }


@pytest.mark.parametrize(
    ("get_nodes", "expected"),
    [
        (
            get_serialized_simple_network_nodes,
            {
                1: 1,
                2: 2,
                3: 2,
                4: 1,
                5: 1,
                6: 0,
                7: 1,
                8: 0,
                9: 1,
                10: 1,
                11: 1,
                12: 0,
            },
        ),
        (
            get_serialized_complex_network_nodes,
            {
                1: 1,
                2: 2,
                3: 2,
                4: 1,
                5: 1,
                6: 0,
                7: 1,
                8: 1,
                9: 0,
                10: 1,
                11: 2,
                12: 2,
                13: 1,
                14: 1,
                15: 0,
                16: 1,
                17: 1,
                18: 1,
                19: 1,
                20: 1,
                21: 1,
                22: 1,
                23: 0,
                24: 1,
                25: 1,
                26: 1,
                27: 0,
            },
        ),
    ],
)
def test_core_network_has_correct_number_of_connected_nodes(get_nodes, expected):
    nodes = get_nodes()

    assert {node["id"]: len(node["connected_nodes"]) for node in nodes} == expected


@pytest.mark.parametrize(
    ("build_network", "expected"),
    [
        (
            build_simple_network_core_network,
            {
                1: 5,
                2: 4,
                3: 3,
                4: 2,
                5: 1,
                6: 0,
                7: 1,
                8: 0,
                9: 2,
                10: 1,
                11: 1,
                12: 0,
            },
        ),
        (
            build_complex_network_core_network,
            {
                1: 8,
                2: 7,
                3: 7,
                4: 6,
                5: 0,
                6: 0,
                7: 1,
                8: 0,
                9: 0,
                10: 6,
                11: 5,
                12: 5,
                13: 1,
                14: 0,
                15: 0,
                16: 4,
                17: 3,
                18: 3,
                19: 2,
                20: 2,
                21: 1,
                22: 1,
                23: 0,
                24: 1,
                25: 0,
                26: 0,
                27: 0,
                28: None,
            },
        ),
    ],
)
def test_create_sprinkler_map_has_correct_edge_counts(build_network, expected):
    network = build_network()

    assert {
        edge_id: network.find_edge_sprinkler_count(edge_id) for edge_id in expected
    } == expected


def test_get_junctions_has_correct_junction_type_on_simple_network():
    junctions = build_simple_network_core_network().get_junctions()

    assert {
        junction_id: junction.junction_type
        for junction_id, junction in junctions.items()
    } == {
        1: JunctionType.TWO_WAY,
        2: JunctionType.THREE_WAY,
        3: JunctionType.THREE_WAY,
        4: JunctionType.TWO_WAY,
        5: JunctionType.TWO_WAY,
        6: JunctionType.TWO_WAY,
        7: JunctionType.TWO_WAY,
        8: JunctionType.TWO_WAY,
        9: JunctionType.TWO_WAY,
    }


def test_get_junctions_has_correct_connected_edges_ids_on_simple_network():
    junctions = build_simple_network_core_network().get_junctions()

    assert {
        junction_id: junction.connected_edges_ids
        for junction_id, junction in junctions.items()
    } == {
        1: [1, 2],
        2: [2, 3, 5],
        3: [3, 4, 7],
        4: [4, 9],
        5: [9, 10],
        6: [10, 11],
        7: [11, 12],
        8: [7, 8],
        9: [5, 6],
    }


def test_get_junctions_has_correct_angle_on_simple_network():
    junctions = build_simple_network_core_network().get_junctions()

    assert {
        junction_id: junction.angle for junction_id, junction in junctions.items()
    } == {
        1: 0.0,
        2: None,
        3: None,
        4: 0.0,
        5: 0.0,
        6: 90.0,
        7: 0.0,
        8: 0.0,
        9: 0.0,
    }


def test_get_junctions_has_correct_has_sprinkler_on_simple_network():
    junctions = build_simple_network_core_network().get_junctions()

    assert {
        junction_id: junction.has_sprinkler
        for junction_id, junction in junctions.items()
    } == {
        1: True,
        2: False,
        3: False,
        4: False,
        5: True,
        6: False,
        7: True,
        8: True,
        9: True,
    }


def test_simple_network_elevations_assignment():

    network = CoreNetwork(
        config=CoreNetworkConfig(
            sprinkler_blocks=build_simple_network_blocks(),
            lines=build_simple_network_lines(),
            line_elevations={
                0: 2000,
                1: 2200,
                2: 2200,
                3: 2000,
                4: 2000,
            },
        )
    )

    print(network.get_edges_id_elevation_map())

    assert network.get_edges_id_elevation_map() == {
        1: 2000,
        2: 2000,
        3: 2000,
        4: 2000,
        5: 2200,
        6: 2200,
        7: 2200,
        8: 2200,
        9: 2000,
        10: 2000,
        11: 2000,
        12: 2000,
    }
