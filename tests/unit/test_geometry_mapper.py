"""Tests for the GeometryMapper class."""

import pytest

from fireplanner.firecomponent.base import (
    FireComponent,
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
    GeometricComponent,
    GeometricElbow,
    GeometricPipe,
    GeometricReducer,
    GeometricTee,
    GeometricWeldedBranch,
)
from fireplanner.networks.geometry_mapper import GeometryMapper, GeometryMapperConfig


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


@pytest.mark.parametrize(
    "run_diameter, branch_diameter,expected_class",
    [
        (SteelDims.DIM_2_5_INCHES, SteelDims.DIM_1_INCHES, GeometricWeldedBranch),
        (SteelDims.DIM_1_5_INCHES, SteelDims.DIM_0_5_INCHES, GeometricTee),
        (SteelDims.DIM_4_INCHES, SteelDims.DIM_2_5_INCHES, GeometricTee),
    ],
)
def test_tee_mapping_uses_welded_branch_when_config_enabled(
    run_diameter, branch_diameter, expected_class
):
    mapper = GeometryMapper(
        config=GeometryMapperConfig(
            welded_connection_enabled=True,
            welded_connection_min_main_pipe_diameter=SteelDims.DIM_2_INCHES,
        )
    )
    tee = Tee(
        run_diameter=run_diameter,
        branch_diameter=branch_diameter,
        material=SteelMaterial.ERW,
        schedule=SteelSchedule.SCD40,
        specs=SteelSpecs.ASTM,
        connection_type=SteelConnection.Grooved,
    )

    result = mapper.get_geometry(tee)

    assert isinstance(result, expected_class)


def test_reducer_mapping(mapper, reducer):
    result = mapper.get_geometry(reducer)
    assert isinstance(result, GeometricReducer)


def test_unsupported_component_raises_key_error(mapper):
    unsupported = "not a firecomponent"
    with pytest.raises(KeyError):
        mapper.get_geometry(unsupported)
