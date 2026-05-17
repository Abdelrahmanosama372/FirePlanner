from math import degrees, isclose, radians

import numpy as np

from fireplanner.geometry.primitives import Point, PrimitiveStyle, Transform2D

TOL = 1e-9


def test_point_construction():
    point = Point(x=1.5, y=2.5, z=3.5)

    assert point.x == 1.5
    assert point.y == 2.5
    assert point.z == 3.5
    assert point.style is None


def test_point_style_setter_and_getter():
    point = Point(x=1.0, y=2.0)
    style = PrimitiveStyle(layer="A-WALL", color="red", category="annotation")

    point.style = style

    assert point.style == style


def test_point_distance():
    p1 = Point(x=1.0, y=2.0, z=3.0)
    p2 = Point(x=4.0, y=6.0, z=3.0)

    result = p1.distance(p2)

    assert isclose(result, 5.0, abs_tol=TOL)


def test_point_add():
    p1 = Point(x=1.0, y=2.0, z=3.0)
    p2 = Point(x=4.0, y=5.0, z=6.0)

    result = p1 + p2

    assert result == Point(x=5.0, y=7.0, z=9.0)


def test_point_subtract():
    p1 = Point(x=10.0, y=8.0, z=6.0)
    p2 = Point(x=1.0, y=2.0, z=3.0)

    result = p1 - p2

    assert result == Point(x=9.0, y=6.0, z=3.0)


def test_point_array():
    point = Point(x=1.0, y=2.0, z=3.0)

    result = point.array()

    assert isinstance(result, np.ndarray)
    assert np.array_equal(result, np.array([1.0, 2.0, 3.0]))


def test_point_transform_2d():
    point = Point(x=1.0, y=2.0, z=3.0)
    trans = Transform2D(Point(x=3, y=3), radians(90))

    result = point.transform_2d(trans)

    assert np.array_equal(result.array(), np.array([1.0, 4.0, 0.0]))


def test_point_to_json():
    point = Point(x=1.0, y=2.0, z=3.0)

    data = point.to_json()

    assert data == {"Point": "1.0, 2.0, 3.0"}


def test_point_from_json():
    data = {"Point": "1.0, 2.0, 3.0"}

    point = Point.from_json(data)

    assert point == Point(x=1.0, y=2.0, z=3.0)


def test_point_to_json_and_from_json_with_style():
    style = PrimitiveStyle(layer="A-POINT", color="blue", category="marker")
    point = Point(x=1.0, y=2.0, z=3.0, style=style)

    data = point.to_json()

    assert data == {
        "Point": "1.0, 2.0, 3.0",
        "style": {
            "layer": "A-POINT",
            "color": "blue",
            "category": "marker",
        },
    }
    assert Point.from_json(data).style == style
