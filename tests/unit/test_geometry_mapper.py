"""Tests for the GeometryMapper class."""

import pytest
from fireplanner.firecomponent.base import (
    FireComponent,
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
from fireplanner.networks.geometry_mapper import GeometryMapper
from fireplanner.geometry.components import (
    GeometricPipe,
    GeometricElbow,
    GeometricTee,
    GeometricReducer,
    GeometricComponent,
)


@pytest.fixture
def mapper():
    return GeometryMapper()


@pytest.fixture
def pipe():
    return Pipe(
        diameter=SteelDims.DIM_1_INCHES,
        material=SteelMaterial.ERW,
        schedule=SteelSchedule.SCD40,
        specs=SteelSpecs.ASTM,
        connection_type=SteelConnection.Grooved,
    )


@pytest.fixture
def elbow():
    return Elbow(
        diameter=SteelDims.DIM_1_INCHES,
        angle=90.0,
        material=SteelMaterial.ERW,
        schedule=SteelSchedule.SCD40,
        specs=SteelSpecs.ASTM,
        connection_type=SteelConnection.Grooved,
    )


@pytest.fixture
def tee():
    return Tee(
        run_diameter=SteelDims.DIM_1_INCHES,
        branch_diameter=SteelDims.DIM_1_INCHES,
        material=SteelMaterial.ERW,
        schedule=SteelSchedule.SCD40,
        specs=SteelSpecs.ASTM,
        connection_type=SteelConnection.Grooved,
    )


@pytest.fixture
def reducer():
    return Reducer(
        diameter1=SteelDims.DIM_1_INCHES,
        diameter2=SteelDims.DIM_0_75_INCHES,
        material=SteelMaterial.ERW,
        schedule=SteelSchedule.SCD40,
        specs=SteelSpecs.ASTM,
        connection_type=SteelConnection.Grooved,
    )


def test_pipe_mapping(mapper, pipe):
    result = mapper.get_geometry(pipe)
    assert isinstance(result, GeometricPipe)


def test_elbow_mapping(mapper, elbow):
    result = mapper.get_geometry(elbow)
    assert isinstance(result, GeometricElbow)


def test_tee_mapping(mapper, tee):
    result = mapper.get_geometry(tee)
    assert isinstance(result, GeometricTee)


def test_reducer_mapping(mapper, reducer):
    result = mapper.get_geometry(reducer)
    assert isinstance(result, GeometricReducer)


def test_unsupported_component_raises_key_error(mapper):
    unsupported = "not a firecomponent"
    with pytest.raises(KeyError):
        mapper.get_geometry(unsupported)
