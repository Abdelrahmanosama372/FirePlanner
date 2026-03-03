from fireplanner.geometry.primitives import Arc, Point


def test_arc_construction():
    start = Point(x=1.0, y=2.0, z=3.0)
    center = Point(x=4.0, y=5.0, z=6.0)

    arc = Arc(start=start, center=center, angle=90.0)

    assert arc.start == start
    assert arc.center == center
    assert arc.angle == 90.0


def test_arc_to_json():
    arc = Arc(
        start=Point(x=1.0, y=2.0, z=3.0),
        center=Point(x=4.0, y=5.0, z=6.0),
        angle=90.0,
    )

    data = arc.to_json()

    assert data == {
        "Arc": {
            "start": {"Point": "1.0, 2.0, 3.0"},
            "center": {"Point": "4.0, 5.0, 6.0"},
            "angle": "90.0",
        }
    }


def test_arc_from_json():
    data = {
        "Arc": {
            "start": {"Point": "1.0, 2.0, 3.0"},
            "center": {"Point": "4.0, 5.0, 6.0"},
            "angle": "90.0",
        }
    }

    arc = Arc.from_json(data)

    assert arc == Arc(
        start=Point(x=1.0, y=2.0, z=3.0),
        center=Point(x=4.0, y=5.0, z=6.0),
        angle=90.0,
    )
