from copy import deepcopy
from math import cos, isclose, radians, sin

import pytest

from fireplanner.firecomponent.base import (
    SteelConnection,
    SteelDims,
    SteelMaterial,
    SteelSchedule,
    SteelSpecs,
)
from fireplanner.firecomponent.fitting.fireconnection.elbow import Elbow
from fireplanner.firecomponent.fitting.fireconnection.reducer import Reducer
from fireplanner.firecomponent.fitting.fireconnection.tee import Tee
from fireplanner.firecomponent.pipe import Pipe
from fireplanner.geometry.components import (
    GeometricElbow,
    GeometricPipe,
    GeometricReducer,
    GeometricTee,
)
from fireplanner.geometry.components.base import ViewType
from fireplanner.geometry.primitives import Point, Transform2D
from fireplanner.networks.placement.context import PlacementContext
from fireplanner.resolvers import PipeTrimmerResolver


@pytest.fixture
def geometric_pipe() -> GeometricPipe:
    return GeometricPipe(
        Pipe(
            diameter=SteelDims.DIM_1_INCHES,
            material=SteelMaterial.ERW,
            schedule=SteelSchedule.SCD40,
            specs=SteelSpecs.ASTM,
            connection_type=SteelConnection.Grooved,
        ),
    )


@pytest.fixture
def geometric_tee() -> GeometricTee:
    return GeometricTee(
        Tee(
            run_diameter=SteelDims.DIM_1_INCHES,
            branch_diameter=SteelDims.DIM_1_INCHES,
            material=SteelMaterial.ERW,
            schedule=SteelSchedule.SCD40,
            specs=SteelSpecs.ASTM,
            connection_type=SteelConnection.Grooved,
        )
    )


@pytest.fixture
def geometric_elbow() -> GeometricElbow:
    return GeometricElbow(
        Elbow(
            diameter=SteelDims.DIM_1_INCHES,
            angle=90.0,
            material=SteelMaterial.ERW,
            schedule=SteelSchedule.SCD40,
            specs=SteelSpecs.ASTM,
            connection_type=SteelConnection.Grooved,
        )
    )


def _center_reducer() -> GeometricReducer:
    center_reducer = GeometricReducer(
        Reducer(
            diameter1=SteelDims.DIM_1_INCHES,
            diameter2=SteelDims.DIM_0_75_INCHES,
            material=SteelMaterial.ERW,
            schedule=SteelSchedule.SCD40,
            specs=SteelSpecs.ASTM,
            connection_type=SteelConnection.Grooved,
        )
    )
    return center_reducer


def test_pipe_trimmer_with_tee_tee_and_center_reducer(geometric_pipe, geometric_tee):
    resolver = PipeTrimmerResolver()
    geometric_pipe.start = Point(x=0.0, y=0.0)
    geometric_pipe.end = Point(x=500.0, y=0.0)

    start_tee = deepcopy(geometric_tee)
    end_tee = deepcopy(geometric_tee)
    center_reducer = _center_reducer()

    start_tee.placement_context = PlacementContext(
        transform=Transform2D(origin=Point(x=0.0, y=0.0), rotation=0.0),
        view_type=ViewType.ELEVATION,
    )
    end_tee.placement_context = PlacementContext(
        transform=Transform2D(origin=Point(x=500.0, y=0.0), rotation=0.0),
        view_type=ViewType.ELEVATION,
    )
    center_reducer.placement_context = PlacementContext(
        transform=Transform2D(origin=Point(x=250.0, y=0.0), rotation=0.0),
        view_type=ViewType.ELEVATION,
    )

    trimmed = resolver.resolve(
        geometric_pipe=geometric_pipe,
        start_connections=[start_tee, center_reducer],
        end_connections=[end_tee],
    )

    assert len(trimmed) == 2
    assert isclose(trimmed[0].start.x, 38.0, rel_tol=1e-9)
    assert isclose(trimmed[0].end.x, 224.6, rel_tol=1e-9)
    assert isclose(trimmed[1].start.x, 275.4, rel_tol=1e-9)
    assert isclose(trimmed[1].end.x, 462.0, rel_tol=1e-9)
    assert isclose(trimmed[0].start.y, 0.0, rel_tol=1e-9)
    assert isclose(trimmed[0].end.y, 0.0, rel_tol=1e-9)
    assert isclose(trimmed[1].start.y, 0.0, rel_tol=1e-9)
    assert isclose(trimmed[1].end.y, 0.0, rel_tol=1e-9)


def test_pipe_trimmer_with_tee_tee_and_center_reducer_rotated_45(
    geometric_pipe, geometric_tee
):
    resolver = PipeTrimmerResolver()
    theta = radians(45.0)
    c = cos(theta)
    s = sin(theta)

    geometric_pipe.start = Point(x=0.0, y=0.0)
    geometric_pipe.end = Point(x=500.0 * c, y=500.0 * s)

    start_tee = deepcopy(geometric_tee)
    end_tee = deepcopy(geometric_tee)
    center_reducer = _center_reducer()

    start_tee.placement_context = PlacementContext(
        transform=Transform2D(origin=Point(x=0.0, y=0.0), rotation=theta),
        view_type=ViewType.ELEVATION,
    )
    end_tee.placement_context = PlacementContext(
        transform=Transform2D(origin=Point(x=500.0 * c, y=500.0 * s), rotation=theta),
        view_type=ViewType.ELEVATION,
    )
    center_reducer.placement_context = PlacementContext(
        transform=Transform2D(origin=Point(x=250.0 * c, y=250.0 * s), rotation=theta),
        view_type=ViewType.ELEVATION,
    )

    trimmed = resolver.resolve(
        geometric_pipe=geometric_pipe,
        start_connections=[start_tee, center_reducer],
        end_connections=[end_tee],
    )

    assert len(trimmed) == 2
    assert isclose(trimmed[0].start.x, 38.0 * c, rel_tol=1e-9)
    assert isclose(trimmed[0].start.y, 38.0 * s, rel_tol=1e-9)
    assert isclose(trimmed[0].end.x, 224.6 * c, rel_tol=1e-9)
    assert isclose(trimmed[0].end.y, 224.6 * s, rel_tol=1e-9)
    assert isclose(trimmed[1].start.x, 275.4 * c, rel_tol=1e-9)
    assert isclose(trimmed[1].start.y, 275.4 * s, rel_tol=1e-9)
    assert isclose(trimmed[1].end.x, 462.0 * c, rel_tol=1e-9)
    assert isclose(trimmed[1].end.y, 462.0 * s, rel_tol=1e-9)
