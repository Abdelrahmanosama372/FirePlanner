from fireplanner.geometry.primitives import Line, Point
from fireplanner.networks import CoreNode


def test_core_node_constructor_sets_line_and_empty_intersection_point():
    line = Line(id=1, start=Point(x=0, y=0), end=Point(x=0, y=4))

    node = CoreNode(line)

    assert node.edge == line
    assert node.line == line
    assert node.intersection_point is None


def test_set_intersection_point_updates_node():
    node = CoreNode(Line(id=1, start=Point(x=0, y=0), end=Point(x=0, y=4)))
    intersection_point = Point(x=0, y=0)

    node.set_intersection_point(intersection_point)

    assert node.intersection_point == intersection_point


def test_add_node_stores_connected_nodes():
    root = CoreNode(Line(id=1, start=Point(x=0, y=0), end=Point(x=0, y=4)))
    child = CoreNode(Line(id=2, start=Point(x=0, y=4), end=Point(x=4, y=4)))

    root.add_node(child)

    assert root.get_connected_nodes_number() == 1
    assert root.get_connected_nodes() == [child]
    assert root.connected_nodes == [child]
