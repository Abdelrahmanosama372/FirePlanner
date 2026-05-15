from copy import deepcopy
from math import pi, radians
from typing import List
from fireplanner.networks import CoreNetwork, ModelNetwork, GeometryNetwork
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
def geometric_network():
    core_network = CoreNetwork()
    model_network = ModelNetwork(core_network)
    return GeometryNetwork(core_network, model_network)


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


def test_correct_geometric_pipes_segmenting_for_two_tees_on_main(
    geometric_network,
    geometric_tee,
):
    pipe_line = Line(start=Point(x=0, y=0), end=Point(1000, 0))

    tee1 = deepcopy(geometric_tee)
    tee2 = geometric_tee

    tee1_transform = Transform2D(origin=pipe_line.start, rotation=0.0)
    tee1.transform = tee1_transform

    tee2_transform = Transform2D(origin=pipe_line.end, rotation=0.0)
    tee2.transform = tee2_transform

    connections = [tee1, tee2]

    free_lines = geometric_network.find_free_pipes_lines(
        pipe_line,
        connections,
    )

    expected_lines = [
        Line(start=Point(x=38, y=0), end=Point(962, 0)),
    ]

    assert free_lines == expected_lines


def test_correct_geometric_pipes_segmenting_for_one_tees(
    geometric_network,
    geometric_tee,
):
    pipe_line = Line(start=Point(x=0, y=0), end=Point(1000, 0))

    tee1 = geometric_tee

    tee1_transform = Transform2D(origin=pipe_line.start, rotation=0.0)
    tee1.transform = tee1_transform

    free_lines = geometric_network.find_free_pipes_lines(
        pipe_line,
        [tee1],
    )

    expected_lines = [
        Line(start=Point(x=38, y=0), end=Point(1000, 0)),
    ]

    assert free_lines == expected_lines


def test_correct_geometric_pipes_segmenting_for_two_tees_on_branch(
    geometric_network,
    geometric_tee,
):
    pipe_line = Line(start=Point(x=0, y=0), end=Point(1000, 0))

    tee1 = deepcopy(geometric_tee)
    tee2 = geometric_tee

    tee1_transform = Transform2D(origin=pipe_line.start, rotation=-pi / 2)
    tee1.transform = tee1_transform

    tee2_transform = Transform2D(origin=pipe_line.end, rotation=pi / 2)
    tee2.transform = tee2_transform

    connections = [tee1, tee2]

    free_lines = geometric_network.find_free_pipes_lines(
        pipe_line,
        connections,
    )

    expected_lines = [
        Line(start=Point(x=38, y=0), end=Point(962, 0)),
    ]

    assert free_lines == expected_lines


def test_correct_geometric_pipes_segmenting_for_tee_and_elbow(
    geometric_network,
    geometric_tee,
    geometric_elbow,
):
    pipe_line = Line(start=Point(x=0, y=0), end=Point(1000, 0))

    tee_transform = Transform2D(origin=pipe_line.start, rotation=0.0)
    geometric_tee.transform = tee_transform

    elbow_transform = Transform2D(
        origin=Point(x=pipe_line.end.x - 38.1, y=38), rotation=-pi / 2
    )
    geometric_elbow.transform = elbow_transform

    connections = [geometric_tee, geometric_elbow]

    for line in geometric_elbow.center_line_model():
        print(f"line: start: {line.start}, {line.end}")

    free_lines = geometric_network.find_free_pipes_lines(
        pipe_line,
        connections,
    )

    for line in free_lines:
        print(f"line: start: {line.start}, {line.end}")

    expected_lines = [
        Line(start=Point(x=38, y=0), end=Point(961.9, 0)),
    ]

    assert free_lines == expected_lines
