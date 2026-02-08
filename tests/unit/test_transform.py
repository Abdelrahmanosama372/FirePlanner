import numpy as np
import pytest
from math import cos, sin, pi, isclose
from fireplanner.geometry.primitives import Point, Transform2D


TOL = 1e-9


def assert_point(p: Point, x: float, y: float):
    assert isclose(p.x, x, abs_tol=TOL)
    assert isclose(p.y, y, abs_tol=TOL)


def assert_angle(a: float, b: float):
    assert isclose(a, b, abs_tol=TOL)


def assert_matrix(a: np.ndarray, b: np.ndarray):
    assert np.allclose(a, b, atol=TOL)


def test_identity_transform_matrix():
    t = Transform2D(Point(x=0.0, y=0.0, z=0.0), 0.0)

    expected = np.array([
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
        [0.0, 0.0, 1.0],
    ])

    assert_matrix(t.transform, expected)


def test_transform_matrix_with_rotation_and_translation():
    angle = pi / 2
    t = Transform2D(Point(x=1.0, y=2.0, z=0.0), angle)

    expected = np.array([
        [cos(angle), -sin(angle), 1.0],
        [sin(angle),  cos(angle), 2.0],
        [0.0,         0.0,        1.0],
    ])

    assert_matrix(t.transform, expected)


def test_translated_local_no_rotation():
    t = Transform2D(Point(x=1.0, y=2.0, z=0.0), 0.0)
    t2 = t.translated_local(3.0, 4.0)

    assert_point(t2.origin, 4.0, 6.0)
    assert_angle(t2.angle, 0.0)


def test_translated_local_with_rotation():
    t = Transform2D(Point(x=0.0, y=0.0, z=0.0), pi / 2)
    t2 = t.translated_local(1.0, 0.0)

    # Local x points along global +Y
    assert_point(t2.origin, 0.0, 1.0)
    assert_angle(t2.angle, pi / 2)


def test_translate_local_mutates():
    t = Transform2D(Point(x=0.0, y=0.0, z=0.0), pi / 2)
    t.translate_local(1.0, 0.0)

    assert_point(t.origin, 0.0, 1.0)


def test_rotated_local():
    t = Transform2D(Point(x=1.0, y=2.0,z=0.0), pi / 4)
    t2 = t.rotated_local(pi / 4)

    assert_point(t2.origin, 1.0, 2.0)
    assert_angle(t2.angle, pi / 2)


def test_rotate_local_mutates():
    t = Transform2D(Point(x=0.0, y=0.0, z=0.0), 0.0)
    t.rotate_local(pi / 2)

    assert_angle(t.angle, pi / 2)


def test_matmul_composition():
    t1 = Transform2D(Point(x=1.0, y=0.0, z=0.0), pi / 2)
    t2 = Transform2D(Point(x=1.0, y=0.0, z=0.0), 0.0)

    t = t1 @ t2

    # t2 translated along its local x, which becomes global +Y after t1
    assert_point(t.origin, 1.0, 1.0)
    assert_angle(t.angle, pi / 2)


def test_from_array_round_trip():
    t = Transform2D(Point(x=3.0, y=4.0, z=0.0), pi / 3)
    mat = t.transform

    t2 = Transform2D.from_array(mat)

    assert_point(t2.origin, 3.0, 4.0)
    assert_angle(t2.angle, pi / 3)


def test_from_array_extracts_angle_correctly():
    angle = -pi / 2
    mat = np.array([
        [cos(angle), -sin(angle), 5.0],
        [sin(angle),  cos(angle), 6.0],
        [0.0,         0.0,        1.0],
    ])

    t = Transform2D.from_array(mat)

    assert_point(t.origin, 5.0, 6.0)
    assert_angle(t.angle, angle)
