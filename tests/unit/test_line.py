import pytest
from fireplanner.geometry.primitives import Line, Point, LineType, PrimitiveStyle


def test_line_construction():
    start = Point(x=0, y=0)
    end = Point(x=10, y=0)

    line = Line(start=start, end=end)

    assert line.start == start
    assert line.end == end
    assert line.line_type == LineType.Normal
    assert line.style is None


def test_line_style_setter_and_getter():
    line = Line(start=Point(x=0, y=0), end=Point(x=10, y=0))
    style = PrimitiveStyle(layer="A-LINE", color="green", category="pipe")

    line.style = style

    assert line.style == style


def test_pass_through_point_on_line():
    line = Line(start=Point(x=0, y=0), end=Point(x=10, y=0))

    point = Point(x=5, y=0)

    assert line.pass_through_point(point) is True


def test_pass_through_point_not_on_line():
    line = Line(start=Point(x=0, y=0), end=Point(x=10, y=0))

    point = Point(x=5, y=1)

    assert line.pass_through_point(point) is False


def test_pass_through_point_at_start():
    start = Point(x=2, y=3)
    end = Point(x=8, y=3)

    line = Line(start=start, end=end)

    assert line.pass_through_point(start) is True


def test_pass_through_point_at_end():
    start = Point(x=2, y=3)
    end = Point(x=8, y=3)

    line = Line(start=start, end=end)

    assert line.pass_through_point(end) is True


def test_lines_intersect_at_point():
    line1 = Line(start=Point(x=0, y=0), end=Point(x=10, y=0))
    line2 = Line(start=Point(x=5, y=-5), end=Point(x=5, y=5))

    intersects, point = line1.intersects_line_2D(line2)

    assert intersects is True
    assert point == Point(x=5, y=0)


def test_lines_not_intersect():
    line1 = Line(start=Point(x=0, y=0), end=Point(x=10, y=0))
    line2 = Line(start=Point(x=0, y=5), end=Point(x=10, y=5))

    intersects, point = line1.intersects_line_2D(line2)

    assert intersects is False
    assert point is None


# =================================================
# 3️⃣ Collinear Intersection Cases
# =================================================


# Case 1:
# A------------------B
#       C-----------------D
def test_collinear_overlap_case_1():
    A = Point(x=0, y=0)
    B = Point(x=10, y=0)
    C = Point(x=5, y=0)
    D = Point(x=15, y=0)

    line1 = Line(start=A, end=B)
    line2 = Line(start=C, end=D)

    intersects, point = line1.intersects_line_2D(line2)

    assert intersects is True
    assert point == C


# Case 2:
#       A------------------B
# C-----------------D
def test_collinear_overlap_case_2():
    A = Point(x=5, y=0)
    B = Point(x=15, y=0)
    C = Point(x=0, y=0)
    D = Point(x=10, y=0)

    line1 = Line(start=A, end=B)
    line2 = Line(start=C, end=D)

    intersects, point = line1.intersects_line_2D(line2)

    assert intersects is True
    assert point == D


# Case 3:
# A--------------------B
# C--------------------------------------D
def test_collinear_overlap_case_3():
    A = Point(x=5, y=0)
    B = Point(x=10, y=0)
    C = Point(x=5, y=0)
    D = Point(x=20, y=0)

    line1 = Line(start=A, end=B)
    line2 = Line(start=C, end=D)

    intersects, point = line1.intersects_line_2D(line2)

    assert intersects is True
    assert point == C


# Case 4:
#         A------B
# C------------------D
def test_collinear_overlap_case_4():
    A = Point(x=5, y=0)
    B = Point(x=10, y=0)
    C = Point(x=0, y=0)
    D = Point(x=20, y=0)

    line1 = Line(start=A, end=B)
    line2 = Line(start=C, end=D)

    intersects, point = line1.intersects_line_2D(line2)

    assert intersects is True
    assert point == A


def test_line_to_json():
    line = Line(
        start=Point(x=1.0, y=2.0, z=3.0),
        end=Point(x=4.0, y=5.0, z=6.0),
        line_type=LineType.CenterLine,
    )

    data = line.to_json()

    assert data == {
        "Line": {
            "start": {"Point": "1.0, 2.0, 3.0"},
            "end": {"Point": "4.0, 5.0, 6.0"},
            "line type": str(LineType.CenterLine),
        }
    }


def test_line_from_json():
    data = {
        "Line": {
            "start": {"Point": "1.0, 2.0, 3.0"},
            "end": {"Point": "4.0, 5.0, 6.0"},
            "line type": str(LineType.CenterLine),
        }
    }

    line = Line.from_json(data)

    assert line.start.x == 1.0
    assert line.start.y == 2.0
    assert line.start.z == 3.0

    assert line.end.x == 4.0
    assert line.end.y == 5.0
    assert line.end.z == 6.0

    assert line.line_type == LineType.CenterLine


def test_line_to_json_and_from_json_with_style():
    style = PrimitiveStyle(layer="A-LINE", color="yellow", category="route")
    line = Line(
        start=Point(x=1.0, y=2.0, z=3.0),
        end=Point(x=4.0, y=5.0, z=6.0),
        line_type=LineType.CenterLine,
        style=style,
    )

    data = line.to_json()

    assert data == {
        "Line": {
            "start": {"Point": "1.0, 2.0, 3.0"},
            "end": {"Point": "4.0, 5.0, 6.0"},
            "line type": str(LineType.CenterLine),
            "style": {
                "layer": "A-LINE",
                "color": "yellow",
                "category": "route",
            },
        }
    }
    assert Line.from_json(data).style == style
