from math import radians

from fireplanner.firecomponent import (
    Elbow,
    Hanger,
    Pipe,
    Reducer,
    SteelConnection,
    SteelDims,
    SteelMaterial,
    SteelPortsNum,
    SteelSchedule,
    SteelSpecs,
    Tee,
)


def test_pipe():
    pipe = Pipe(
        SteelDims.DIM_2_INCHES,
        SteelMaterial.ERW,
        SteelSchedule.SCD40,
        SteelSpecs.ASTM,
        SteelConnection.Grooved,
    )
    assert pipe.diameter == SteelDims.DIM_2_INCHES
    assert pipe.material == SteelMaterial.ERW
    assert pipe.schedule == SteelSchedule.SCD40
    assert pipe.specs == SteelSpecs.ASTM
    assert pipe.connection_type == SteelConnection.Grooved


def test_elbow():
    elbow = Elbow(
        SteelDims.DIM_12_INCHES,
        radians(90),
        SteelMaterial.Seamless,
        SteelSchedule.SCD80,
        SteelSpecs.ASTM,
        SteelConnection.Welded,
    )

    assert elbow.diameter == SteelDims.DIM_12_INCHES
    assert elbow.material == SteelMaterial.Seamless
    assert elbow.schedule == SteelSchedule.SCD80
    assert elbow.specs == SteelSpecs.ASTM
    assert elbow.connection_type == SteelConnection.Welded

    assert elbow.ports_number() == SteelPortsNum.ST_PORTS_2
    assert elbow.ports_diameter() == (
        SteelDims.DIM_12_INCHES,
        SteelDims.DIM_12_INCHES,
    )


def test_reducer_orders_diameters_correctly():
    reducer = Reducer(
        SteelDims.DIM_4_INCHES,
        SteelDims.DIM_2_INCHES,
        SteelMaterial.ERW,
        SteelSchedule.SCD40,
        SteelSpecs.ASTM,
        SteelConnection.Grooved,
    )

    assert reducer.large_diameter == SteelDims.DIM_4_INCHES
    assert reducer.small_diameter == SteelDims.DIM_2_INCHES


def test_reducer():
    reducer = Reducer(
        SteelDims.DIM_2_INCHES,
        SteelDims.DIM_6_INCHES,  # reversed on purpose
        SteelMaterial.ERW,
        SteelSchedule.SCD40,
        SteelSpecs.ASTM,
        SteelConnection.Welded,
    )

    assert reducer.large_diameter == SteelDims.DIM_6_INCHES
    assert reducer.small_diameter == SteelDims.DIM_2_INCHES

    assert reducer.material == SteelMaterial.ERW
    assert reducer.schedule == SteelSchedule.SCD40
    assert reducer.specs == SteelSpecs.ASTM
    assert reducer.connection_type == SteelConnection.Welded

    assert reducer.ports_number() == SteelPortsNum.ST_PORTS_2
    assert reducer.ports_diameter() == (
        SteelDims.DIM_6_INCHES,
        SteelDims.DIM_2_INCHES,
    )


def test_hanger():
    hanger = Hanger(
        SteelDims.DIM_1_5_INCHES,
        SteelMaterial.Seamless,
        SteelSchedule.SCD80,
        SteelSpecs.ISO,
        SteelConnection.Grooved,
    )

    assert hanger.diameter == SteelDims.DIM_1_5_INCHES
    assert hanger.material == SteelMaterial.Seamless
    assert hanger.schedule == SteelSchedule.SCD80
    assert hanger.specs == SteelSpecs.ISO
    assert hanger.connection_type == SteelConnection.Grooved


def test_tee():
    tee = Tee(
        SteelDims.DIM_4_INCHES,
        SteelDims.DIM_2_INCHES,
        SteelMaterial.ERW,
        SteelSchedule.SCD40,
        SteelSpecs.ASTM,
        SteelConnection.Grooved,
    )

    assert tee.run_diameter == SteelDims.DIM_4_INCHES
    assert tee.branch_diameter == SteelDims.DIM_2_INCHES

    assert tee.material == SteelMaterial.ERW
    assert tee.schedule == SteelSchedule.SCD40
    assert tee.specs == SteelSpecs.ASTM
    assert tee.connection_type == SteelConnection.Grooved

    assert tee.ports_number() == SteelPortsNum.ST_PORTS_3
    assert tee.ports_diameter() == (
        SteelDims.DIM_4_INCHES,
        SteelDims.DIM_4_INCHES,
        SteelDims.DIM_2_INCHES,
    )
