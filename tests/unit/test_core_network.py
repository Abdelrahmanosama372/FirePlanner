import pytest

from fireplanner.geometry.primitives import Line
from fireplanner.networks.core_network import CoreNetwork
from fireplanner.networks.junction import JunctionType
from tests.unit.core_network import (
    build_complex_network_core_network,
    build_simple_network_core_network,
    build_complex_network_blocks,
    build_complex_network_lines,
    build_loop_network_blocks,
    build_loop_network_lines,
    build_simple_network_blocks,
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
                1: (0, 3, 4, 3),
                2: (0, 4, -6, 4),
                3: (0, 5, 0, 9),
                4: (0, 9, 6, 9),
            },
            {1, 2, 3, 4},
        ),
        (
            build_simple_network_inverted_lines,
            build_simple_network_blocks,
            {
                1: (0, 3, 4, 3),
                2: (0, 4, -6, 4),
                3: (0, 5, 0, 9),
                4: (0, 9, 6, 9),
            },
            {1, 2, 3, 4},
        ),
        (
            build_complex_network_lines,
            build_complex_network_blocks,
            {
                1: (0, 6, 0, 12),
                2: (0, 12, 0, 15),
                3: (0, 4, 6, 4),
                4: (0, 5, -6, 5),
                5: (0, 10, 8, 10),
                6: (0, 9, -8, 9),
                7: (0, 15, 5, 15),
                8: (6, 4, 10, 4),
                9: (-6, 5, -10, 5),
                10: (8, 10, 12, 10),
                11: (-8, 9, -12, 9),
                12: (5, 15, 9, 18),
                13: (12, 10, 12, 14),
                14: (12, 14, 16, 14),
            },
            {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14},
        ),
        (
            build_loop_network_lines,
            build_loop_network_blocks,
            {
                1: (0, 2, 0, 5),
                2: (0, 4, 4, 4),
                3: (4, 4, 4, 8),
                4: (4, 8, 0, 8),
                5: (0, 5, 0, 9),
                6: (0, 9, 0, 12),
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
    network = CoreNetwork(sprinkles=blocks, lines=[])

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
                2: {"Point": "0, 2, 0.0"},
                3: {"Point": "0.0, 3.0, 0.0"},
                4: {"Point": "0.0, 4.0, 0.0"},
                5: {"Point": "0.0, 3.0, 0.0"},
                6: {"Point": "2, 3, 0.0"},
                7: {"Point": "0.0, 4.0, 0.0"},
                8: {"Point": "-4, 4, 0.0"},
                9: {"Point": "0, 5, 0.0"},
                10: {"Point": "0, 8, 0.0"},
                11: {"Point": "0.0, 9.0, 0.0"},
                12: {"Point": "1, 9, 0.0"},
            },
        ),
        (
            get_serialized_complex_network_nodes,
            {
                1: None,
                2: {"Point": "0, 3, 0.0"},
                3: {"Point": "0.0, 4.0, 0.0"},
                4: {"Point": "0.0, 5.0, 0.0"},
                5: {"Point": "0.0, 4.0, 0.0"},
                6: {"Point": "6, 4, 0.0"},
                7: {"Point": "0.0, 5.0, 0.0"},
                8: {"Point": "-3, 5, 0.0"},
                9: {"Point": "-6, 5, 0.0"},
                10: {"Point": "0, 6, 0.0"},
                11: {"Point": "0, 8, 0.0"},
                12: {"Point": "0.0, 9.0, 0.0"},
                13: {"Point": "0.0, 10.0, 0.0"},
                14: {"Point": "0.0, 9.0, 0.0"},
                15: {"Point": "-8, 9, 0.0"},
                16: {"Point": "0.0, 10.0, 0.0"},
                17: {"Point": "6, 10, 0.0"},
                18: {"Point": "8, 10, 0.0"},
                19: {"Point": "9, 10, 0.0"},
                20: {"Point": "12.0, 10.0, 0.0"},
                21: {"Point": "12, 12, 0.0"},
                22: {"Point": "12.0, 14.0, 0.0"},
                23: {"Point": "15, 14, 0.0"},
                24: {"Point": "0, 12, 0.0"},
                25: {"Point": "0, 13, 0.0"},
                26: {"Point": "0.0, 15.0, 0.0"},
                27: {"Point": "5.0, 15.0, 0.0"},
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
                1: ("0, 0, 0.0", "0, 2, 0.0"),
                2: ("0, 2, 0.0", "0.0, 3.0, 0.0"),
                3: ("0.0, 3.0, 0.0", "0.0, 4.0, 0.0"),
                4: ("0.0, 4.0, 0.0", "0, 5, 0.0"),
                5: ("0, 3, 0.0", "2, 3, 0.0"),
                6: ("2, 3, 0.0", "4, 3, 0.0"),
                7: ("0, 4, 0.0", "-4, 4, 0.0"),
                8: ("-4, 4, 0.0", "-6, 4, 0.0"),
                9: ("0, 5, 0.0", "0, 8, 0.0"),
                10: ("0, 8, 0.0", "0.0, 9.0, 0.0"),
                11: ("0, 9, 0.0", "1, 9, 0.0"),
                12: ("1, 9, 0.0", "6, 9, 0.0"),
            },
        ),
        (
            get_serialized_complex_network_nodes,
            {
                1: ("0, 0, 0.0", "0, 3, 0.0"),
                2: ("0, 3, 0.0", "0.0, 4.0, 0.0"),
                3: ("0.0, 4.0, 0.0", "0.0, 5.0, 0.0"),
                4: ("0.0, 5.0, 0.0", "0, 6, 0.0"),
                5: ("0, 4, 0.0", "6, 4, 0.0"),
                6: ("6, 4, 0.0", "10, 4, 0.0"),
                7: ("0, 5, 0.0", "-3, 5, 0.0"),
                8: ("-3, 5, 0.0", "-6, 5, 0.0"),
                9: ("-6, 5, 0.0", "-10, 5, 0.0"),
                10: ("0, 6, 0.0", "0, 8, 0.0"),
                11: ("0, 8, 0.0", "0.0, 9.0, 0.0"),
                12: ("0.0, 9.0, 0.0", "0.0, 10.0, 0.0"),
                13: ("0.0, 10.0, 0.0", "0, 12, 0.0"),
                14: ("0, 9, 0.0", "-8, 9, 0.0"),
                15: ("-8, 9, 0.0", "-12, 9, 0.0"),
                16: ("0, 10, 0.0", "6, 10, 0.0"),
                17: ("6, 10, 0.0", "8, 10, 0.0"),
                18: ("8, 10, 0.0", "9, 10, 0.0"),
                19: ("9, 10, 0.0", "12.0, 10.0, 0.0"),
                20: ("12, 10, 0.0", "12, 12, 0.0"),
                21: ("12, 12, 0.0", "12.0, 14.0, 0.0"),
                22: ("12, 14, 0.0", "15, 14, 0.0"),
                23: ("15, 14, 0.0", "16, 14, 0.0"),
                24: ("0, 12, 0.0", "0, 13, 0.0"),
                25: ("0, 13, 0.0", "0.0, 15.0, 0.0"),
                26: ("0, 15, 0.0", "5.0, 15.0, 0.0"),
                27: ("5, 15, 0.0", "9, 18, 0.0"),
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
            },
        ),
    ],
)
def test_create_sprinkler_map_has_correct_edge_counts(build_network, expected):
    network = build_network()

    assert {
        edge_id: network.find_edge_sprinkler_count(edge_id)
        for edge_id in expected
    } == expected


def test_get_junctions_has_correct_junction_type_on_simple_network():
    junctions = build_simple_network_core_network().get_junctions()

    assert {junction_id: junction.junction_type for junction_id, junction in junctions.items()} == {
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

    assert {junction_id: junction.angle for junction_id, junction in junctions.items()} == {
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
