from math import isclose

from fireplanner.geometry.primitives import LineType, Point, PrimitiveStyle, Rectangle
from fireplanner.geometry.primitives.transform import Transform2D


def test_rectangle_construction():
    rectangle = Rectangle.from_bounds(
        point1=Point(x=1.0, y=2.0, z=0.0),
        point2=Point(x=4.0, y=6.0, z=0.0),
        line_type=LineType.CenterLine,
    )

    assert rectangle.point1 == Point(x=1.0, y=2.0, z=0.0)
    assert rectangle.point2 == Point(x=4.0, y=2.0, z=0.0)
    assert rectangle.point3 == Point(x=4.0, y=6.0, z=0.0)
    assert rectangle.point4 == Point(x=1.0, y=6.0, z=0.0)
    assert rectangle.line_type == LineType.CenterLine


def test_rectangle_transform_2d():
    rectangle = Rectangle.from_bounds(
        point1=Point(x=1.0, y=2.0),
        point2=Point(x=4.0, y=6.0),
    )
    transform = Transform2D(origin=Point(x=10.0, y=20.0), rotation=0.0)

    transformed = rectangle.transform_2d(transform)

    assert transformed.point1 == Point(x=11.0, y=22.0)
    assert transformed.point2 == Point(x=14.0, y=22.0)
    assert transformed.point3 == Point(x=14.0, y=26.0)
    assert transformed.point4 == Point(x=11.0, y=26.0)
    assert transformed.line_type == LineType.Normal


def test_rectangle_to_json_and_from_json_with_style():
    style = PrimitiveStyle(layer="A-RECT", color="yellow", category="shape")
    rectangle = Rectangle.from_bounds(
        point1=Point(x=1.0, y=2.0, z=0.0),
        point2=Point(x=4.0, y=6.0, z=0.0),
        line_type=LineType.CenterLine,
        style=style,
    )

    data = rectangle.to_json()

    assert data == {
        "Rectangle": {
            "point1": {"Point": "1.0, 2.0, 0.0"},
            "point2": {"Point": "4.0, 2.0, 0.0"},
            "point3": {"Point": "4.0, 6.0, 0.0"},
            "point4": {"Point": "1.0, 6.0, 0.0"},
            "line type": "CenterLine",
            "style": {
                "layer": "A-RECT",
                "color": "yellow",
                "category": "shape",
            },
        }
    }

    restored = Rectangle.from_json(data)
    assert restored.point1 == rectangle.point1
    assert restored.point2 == rectangle.point2
    assert restored.point3 == rectangle.point3
    assert restored.point4 == rectangle.point4
    assert restored.line_type == rectangle.line_type
    assert restored.style == rectangle.style


def test_rectangle_intersection_returns_overlap():
    rect1 = Rectangle.from_bounds(point1=Point(x=0, y=0), point2=Point(x=10, y=10))
    rect2 = Rectangle.from_bounds(point1=Point(x=5, y=5), point2=Point(x=15, y=12))

    intersection = rect1.intersection(rect2)

    assert intersection is not None
    assert intersection.point1 == Point(x=5, y=5)
    assert intersection.point3 == Point(x=10, y=10)


def test_rectangle_intersection_returns_none_when_disjoint():
    rect1 = Rectangle.from_bounds(point1=Point(x=0, y=0), point2=Point(x=2, y=2))
    rect2 = Rectangle.from_bounds(point1=Point(x=3, y=3), point2=Point(x=5, y=5))

    assert rect1.intersection(rect2) is None


def test_rectangle_intersection_handles_unordered_points():
    rect1 = Rectangle.from_bounds(point1=Point(x=10, y=10), point2=Point(x=0, y=0))
    rect2 = Rectangle.from_bounds(point1=Point(x=8, y=8), point2=Point(x=6, y=6))

    intersection = rect1.intersection(rect2)

    assert intersection is not None
    assert intersection.point1 == Point(x=6, y=6)
    assert intersection.point3 == Point(x=8, y=8)


def test_tee_and_elbow_plan_occupancy_intersection_with_rotation():
    tee_region = Rectangle(
        point1=Point(x=-15.061374439273465, y=-38.67874093090415),
        point2=Point(x=38.67874093090415, y=15.06137443927346),
        point3=Point(x=15.061374439273465, y=38.67874093090415),
        point4=Point(x=-38.67874093090415, y=-15.06137443927346),
    )
    elbow_region = Rectangle(
        point1=Point(x=-1.7763568394002505e-15, y=-23.617366491630683),
        point2=Point(x=23.617366491630683, y=-1.7763568394002505e-15),
        point3=Point(x=-15.06137443927346, y=38.67874093090415),
        point4=Point(x=-38.67874093090415, y=15.061374439273465),
    )

    intersection = tee_region.intersection(elbow_region)

    assert intersection is not None
    assert isclose(intersection.point1.x, 3.552713678800501e-15, rel_tol=1e-9)
    assert isclose(intersection.point1.y, -23.617366491630683, rel_tol=1e-9)
    assert isclose(intersection.point2.x, 23.617366491630683, rel_tol=1e-9)
    assert isclose(intersection.point2.y, -7.105427357601002e-15, rel_tol=1e-9)
    assert isclose(intersection.point3.x, 0.0, rel_tol=1e-9)
    assert isclose(intersection.point3.y, 23.617366491630683, rel_tol=1e-9)
    assert isclose(intersection.point4.x, -23.617366491630687, rel_tol=1e-9)
    assert isclose(intersection.point4.y, 0.0, rel_tol=1e-9)
