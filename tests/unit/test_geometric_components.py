from math import pi, radians
from typing import List
import pytest
from fireplanner.geometry.primitives import Primitive2D, Transform2D, Point, Line, Arc
from fireplanner.firecomponent.base import (
    SteelMaterial,
    SteelSchedule,
    SteelSpecs,
    SteelConnection,
    SteelDims,
)

from fireplanner.firecomponent.pipe import Pipe
from fireplanner.firecomponent.fitting.fireconnection.elbow import Elbow
from fireplanner.firecomponent.fitting.fireconnection.tee import Tee
from fireplanner.firecomponent.fitting.fireconnection.reducer import Reducer
from fireplanner.geometry.components import (
    GeometricPipe,
    GeometricElbow,
    GeometricTee,
    GeometricReducer,
)


@pytest.fixture
def geometric_pipe():
    pipe = Pipe(
        diameter=SteelDims.DIM_1_INCHES,
        material=SteelMaterial.ERW,
        schedule=SteelSchedule.SCD40,
        specs=SteelSpecs.ASTM,
        connection_type=SteelConnection.Grooved,
    )
    return GeometricPipe(pipe)


@pytest.fixture
def geometric_elbow():
    elbow = Elbow(
        diameter=SteelDims.DIM_1_INCHES,
        angle=90.0,
        material=SteelMaterial.ERW,
        schedule=SteelSchedule.SCD40,
        specs=SteelSpecs.ASTM,
        connection_type=SteelConnection.Grooved,
    )
    return GeometricElbow(elbow)


@pytest.fixture
def geometric_tee():
    tee = Tee(
        run_diameter=SteelDims.DIM_1_INCHES,
        branch_diameter=SteelDims.DIM_1_INCHES,
        material=SteelMaterial.ERW,
        schedule=SteelSchedule.SCD40,
        specs=SteelSpecs.ASTM,
        connection_type=SteelConnection.Grooved,
    )
    return GeometricTee(tee)


@pytest.fixture
def geometric_reducer():
    reducer = Reducer(
        diameter1=SteelDims.DIM_1_INCHES,
        diameter2=SteelDims.DIM_0_75_INCHES,
        material=SteelMaterial.ERW,
        schedule=SteelSchedule.SCD40,
        specs=SteelSpecs.ASTM,
        connection_type=SteelConnection.Grooved,
    )
    return GeometricReducer(reducer)


@pytest.mark.parametrize(
    "transform, expected_primitives",
    [
        (
            Transform2D(Point(x=3, y=3), radians(90)),
            {
                Line(
                    start=Point(x=-13.7, y=-35), end=Point(x=-13.7, y=-13.7)
                ),  # top left
                Line(
                    start=Point(x=-13.7, y=19.7), end=Point(x=-13.7, y=41)
                ),  # top right
                Line(
                    start=Point(x=19.7, y=41.0), end=Point(x=-13.7, y=41.0)
                ),  # right run
                Line(
                    start=Point(x=-13.7, y=-35), end=Point(x=19.7, y=-35.0)
                ),  # left run
                Line(start=Point(x=19.7, y=-35), end=Point(x=19.7, y=41)),  # bottom
                Line(
                    start=Point(x=-35, y=-13.7), end=Point(x=-35, y=19.7)
                ),  # bottom branch
                Line(
                    start=Point(x=-35, y=19.7), end=Point(x=-13.7, y=19.7)
                ),  # right branch
                Line(
                    start=Point(x=-35, y=-13.7), end=Point(x=-13.7, y=-13.7)
                ),  # left branch
                Line(
                    start=Point(x=3.0, y=3.0), end=Point(x=-13.7, y=-13.7)
                ),  # center left
                Line(
                    start=Point(x=3.0, y=3.0), end=Point(x=-13.7, y=19.7)
                ),  # center right
            },
        ),
    ],
)
def test_tee_build_primitives_2d(
    geometric_tee, transform: Transform2D, expected_primitives: List[Primitive2D]
):
    geometric_tee.transform = transform
    primitives = geometric_tee.get_primitives_2d()
    assert len(primitives) == len(expected_primitives)
    assert {prim for prim in primitives} == expected_primitives


@pytest.mark.parametrize(
    "transform, expected_primitives",
    [
        (
            Transform2D(Point(x=3, y=3), radians(90)),
            {
                Line(
                    start=Point(x=-10.335, y=-22.4), end=Point(x=-13.7, y=28.4)
                ),  # top
                Line(start=Point(x=-13.7, y=28.4), end=Point(x=19.7, y=28.4)),  # right
                Line(
                    start=Point(x=19.7, y=28.4), end=Point(x=16.335, y=-22.4)
                ),  # bottom
                Line(
                    start=Point(x=16.335, y=-22.4), end=Point(x=-10.335, y=-22.4)
                ),  # left
            },
        ),
    ],
)
def test_reducer_build_primitives_2d(
    geometric_reducer, transform: Transform2D, expected_primitives: List[Primitive2D]
):
    geometric_reducer.transform = transform
    primitives = geometric_reducer.get_primitives_2d()
    assert len(primitives) == len(expected_primitives)
    assert {prim for prim in primitives} == expected_primitives


@pytest.mark.parametrize(
    "transform, expected_primitives",
    [
        (
            Transform2D(Point(x=3, y=3), radians(90)),
            {
                Arc(
                    start=Point(x=3, y=24.3),
                    center=Point(x=3, y=3),
                    angle=pi / 2,
                ),  # inner arc
                Arc(
                    start=Point(x=3, y=57.7),
                    center=Point(x=3, y=3),
                    angle=pi / 2,
                ),  # outer arc
                Line(start=Point(x=3, y=24.3), end=Point(x=3, y=57.7)),  # vertical line
                Line(
                    start=Point(x=-18.3, y=3), end=Point(x=-51.7, y=3)
                ),  # horizontal line
            },
        ),
    ],
)
def test_elbow_build_primitives_2d(
    geometric_elbow, transform: Transform2D, expected_primitives: List[Primitive2D]
):
    geometric_elbow.transform = transform
    primitives = geometric_elbow.get_primitives_2d()
    assert len(primitives) == len(expected_primitives)
    assert {prim for prim in primitives} == expected_primitives
