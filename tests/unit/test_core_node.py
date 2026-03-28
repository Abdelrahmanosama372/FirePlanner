import pytest

from fireplanner.geometry.primitives import Block, Line, Point
from fireplanner.networks import CoreNode


def build_node_with_intersections() -> tuple[CoreNode, CoreNode, CoreNode]:
    node = CoreNode(
        Line(id=100, start=Point(x=0, y=0), end=Point(x=0, y=10)),
    )
    child_near = CoreNode(
        Line(id=101, start=Point(x=0, y=3), end=Point(x=2, y=3)),
    )
    child_far = CoreNode(
        Line(id=102, start=Point(x=0, y=7), end=Point(x=2, y=7)),
    )

    node.add_node(child_far, Point(x=0, y=7))
    node.add_node(child_near, Point(x=0, y=3))

    return node, child_near, child_far


def test_core_node_line_property_returns_assigned_line():
    line = Line(id=1, start=Point(x=0, y=0), end=Point(x=4, y=0))
    node = CoreNode(line)

    assert node.line == line


def test_add_block_appends_block_to_blocks_property():
    node = CoreNode(Line(id=1, start=Point(x=0, y=0), end=Point(x=4, y=0)))
    block = Block(id=5, name="SPR", center=Point(x=2, y=0))

    node.add_block(block)

    assert node.blocks == [block]


def test_add_block_rejects_non_block_values():
    node = CoreNode(Line(id=1, start=Point(x=0, y=0), end=Point(x=4, y=0)))

    with pytest.raises(TypeError, match="block must be an instance of Block"):
        node.add_block("not-a-block")


def test_add_node_stores_connected_nodes_and_intersection_mapping():
    node, child_near, child_far = build_node_with_intersections()

    assert node.connected_nodes == [child_far, child_near]
    assert node.intersection_points == {
        Point(x=0, y=7): child_far,
        Point(x=0, y=3): child_near,
    }


def test_add_node_rejects_invalid_node_or_intersection_point():
    node = CoreNode(Line(id=1, start=Point(x=0, y=0), end=Point(x=4, y=0)))
    child = CoreNode(Line(id=2, start=Point(x=1, y=0), end=Point(x=1, y=2)))

    with pytest.raises(TypeError, match="node must be an instance of CoreNode"):
        node.add_node("not-a-node", Point(x=1, y=0))

    with pytest.raises(
        TypeError,
        match="intersection_point must be an instance of Point",
    ):
        node.add_node(child, "not-a-point")


def test_find_intersection_points_returns_only_points():
    node, _, _ = build_node_with_intersections()

    assert node.find_intersection_points() == [
        Point(x=0, y=7),
        Point(x=0, y=3),
    ]


def test_find_intersection_points_with_nodes_returns_mapping():
    node, child_near, child_far = build_node_with_intersections()

    assert node.find_intersection_points_with_nodes() == {
        Point(x=0, y=7): child_far,
        Point(x=0, y=3): child_near,
    }


def test_edges_are_lazily_constructed_sorted_from_line_start_and_cached():
    node, _, _ = build_node_with_intersections()

    edges = node.edges

    assert edges is node.edges
    assert [(edge.id, edge.start, edge.end) for edge in edges] == [
        (1, Point(x=0, y=0), Point(x=0, y=3)),
        (2, Point(x=0, y=3), Point(x=0, y=7)),
        (3, Point(x=0, y=7), Point(x=0, y=10)),
    ]


def test_edges_returns_single_edge_when_no_intersections_exist():
    node = CoreNode(Line(id=9, start=Point(x=1, y=1), end=Point(x=5, y=1)))

    assert [(edge.id, edge.start, edge.end) for edge in node.edges] == [
        (1, Point(x=1, y=1), Point(x=5, y=1)),
    ]


def test_find_intersected_edges_returns_matching_edges_for_intersection_point():
    node, _, _ = build_node_with_intersections()

    intersected_edges = node.find_intersected_edges(Point(x=0, y=3))

    assert intersected_edges is not None
    assert [(edge.id, edge.start, edge.end) for edge in intersected_edges] == [
        (1, Point(x=0, y=0), Point(x=0, y=3)),
        (2, Point(x=0, y=3), Point(x=0, y=7)),
    ]


def test_find_intersected_edges_returns_none_for_non_intersection_point():
    node, _, _ = build_node_with_intersections()

    assert node.find_intersected_edges(Point(x=0, y=5)) is None
