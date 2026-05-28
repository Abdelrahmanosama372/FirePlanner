from math import pi

from fireplanner.geometry.primitives import Arc, Circle, Line, Point, Rectangle
from fireplanner.geometry.primitives.line import LineType
from fireplanner.resolvers import PrimitiveVisibilityResolver


def test_visibility_resolver_line_crossing_rectangle():
    resolver = PrimitiveVisibilityResolver()
    rect = Rectangle.from_bounds(point1=Point(x=0, y=0), point2=Point(x=10, y=10))
    line = Line(start=Point(x=-5, y=5), end=Point(x=15, y=5))

    partition = resolver.resolve(rect, line)

    assert len(partition.hidden) == 1
    assert len(partition.visible) == 2
    hidden = partition.hidden[0]
    assert isinstance(hidden, Line)
    assert hidden.start == Point(x=0, y=5)
    assert hidden.end == Point(x=10, y=5)
    assert hidden.line_type == LineType.Hidden


def test_visibility_resolver_line_outside_rectangle():
    resolver = PrimitiveVisibilityResolver()
    rect = Rectangle.from_bounds(point1=Point(x=0, y=0), point2=Point(x=10, y=10))
    line = Line(start=Point(x=-5, y=-5), end=Point(x=-1, y=-1))

    partition = resolver.resolve(rect, line)

    assert len(partition.hidden) == 0
    assert len(partition.visible) == 1
    assert partition.visible[0] == line


def test_visibility_resolver_circle_fully_inside_rectangle():
    resolver = PrimitiveVisibilityResolver()
    rect = Rectangle.from_bounds(point1=Point(x=0, y=0), point2=Point(x=10, y=10))
    circle = Circle(center=Point(x=5, y=5), radius=2)

    partition = resolver.resolve(rect, circle)

    assert len(partition.visible) == 0
    assert len(partition.hidden) == 1
    assert isinstance(partition.hidden[0], Circle)
    assert partition.hidden[0].line_type == LineType.Hidden


def test_visibility_resolver_arc_fully_outside_rectangle():
    resolver = PrimitiveVisibilityResolver()
    rect = Rectangle.from_bounds(point1=Point(x=0, y=0), point2=Point(x=2, y=2))
    arc = Arc(start=Point(x=10, y=0), center=Point(x=0, y=0), angle=pi / 4)

    partition = resolver.resolve(rect, arc)

    assert len(partition.hidden) == 0
    assert len(partition.visible) == 1
    assert isinstance(partition.visible[0], Arc)
