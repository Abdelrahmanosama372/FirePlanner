from fireplanner.geometry.primitives import LineType, Point, PrimitiveStyle, Rectangle
from fireplanner.geometry.primitives.transform import Transform2D


def test_rectangle_construction():
    rectangle = Rectangle(
        point1=Point(x=1.0, y=2.0, z=0.0),
        point2=Point(x=4.0, y=6.0, z=0.0),
        line_type=LineType.CenterLine,
    )

    assert rectangle.point1 == Point(x=1.0, y=2.0, z=0.0)
    assert rectangle.point2 == Point(x=4.0, y=6.0, z=0.0)
    assert rectangle.line_type == LineType.CenterLine


def test_rectangle_transform_2d():
    rectangle = Rectangle(
        point1=Point(x=1.0, y=2.0),
        point2=Point(x=4.0, y=6.0),
    )
    transform = Transform2D(origin=Point(x=10.0, y=20.0), rotation=0.0)

    transformed = rectangle.transform_2d(transform)

    assert transformed.point1 == Point(x=11.0, y=22.0)
    assert transformed.point2 == Point(x=14.0, y=26.0)
    assert transformed.line_type == LineType.Normal


def test_rectangle_to_json_and_from_json_with_style():
    style = PrimitiveStyle(layer="A-RECT", color="yellow", category="shape")
    rectangle = Rectangle(
        point1=Point(x=1.0, y=2.0, z=0.0),
        point2=Point(x=4.0, y=6.0, z=0.0),
        line_type=LineType.CenterLine,
        style=style,
    )

    data = rectangle.to_json()

    assert data == {
        "Rectangle": {
            "point1": {"Point": "1.0, 2.0, 0.0"},
            "point2": {"Point": "4.0, 6.0, 0.0"},
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
    assert restored.line_type == rectangle.line_type
    assert restored.style == rectangle.style


def test_rectangle_intersection_returns_overlap():
    rect1 = Rectangle(point1=Point(x=0, y=0), point2=Point(x=10, y=10))
    rect2 = Rectangle(point1=Point(x=5, y=5), point2=Point(x=15, y=12))

    intersection = rect1.intersection(rect2)

    assert intersection is not None
    assert intersection.point1 == Point(x=5, y=5)
    assert intersection.point2 == Point(x=10, y=10)


def test_rectangle_intersection_returns_none_when_disjoint():
    rect1 = Rectangle(point1=Point(x=0, y=0), point2=Point(x=2, y=2))
    rect2 = Rectangle(point1=Point(x=3, y=3), point2=Point(x=5, y=5))

    assert rect1.intersection(rect2) is None


def test_rectangle_intersection_handles_unordered_points():
    rect1 = Rectangle(point1=Point(x=10, y=10), point2=Point(x=0, y=0))
    rect2 = Rectangle(point1=Point(x=8, y=8), point2=Point(x=6, y=6))

    intersection = rect1.intersection(rect2)

    assert intersection is not None
    assert intersection.point1 == Point(x=6, y=6)
    assert intersection.point2 == Point(x=8, y=8)
