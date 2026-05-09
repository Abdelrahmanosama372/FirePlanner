from fireplanner.firecomponent.base import (
    SteelDims,
    SteelMaterial,
    SteelSpecs,
    SteelSchedule,
    SteelConnection,
)
from enum import StrEnum
from dataclasses import dataclass


class Unit(StrEnum):
    MM = "milimeter"
    CM = "centimeter"
    M = "meter"
    LUMPSUM = "lumpsum"
    Gallon = "gallons"
    Liter = "liters"
    Num = "number"


@dataclass(frozen=True)
class SteelSpec:
    material: SteelMaterial
    schedule: SteelSchedule
    specs: SteelSpecs


@dataclass(frozen=True)
class PipeSpec:
    diameter: SteelDims
    steel: SteelSpec


@dataclass(frozen=True)
class PipeBOQ:
    lengths_by_spec: dict[PipeSpec, float]
    unit: Unit


@dataclass(frozen=True)
class ConnectionKey:
    pass


@dataclass(frozen=True)
class TeeKey(ConnectionKey):
    run_diameter: SteelDims
    branch_diameter: SteelDims
    steel: SteelSpec
    connection: SteelConnection


@dataclass(frozen=True)
class ElbowKey(ConnectionKey):
    diameter: SteelDims
    steel: SteelSpec
    connection: SteelConnection


@dataclass(frozen=True)
class ReducerKey(ConnectionKey):
    large_diameter: SteelDims
    small_diameter: SteelDims
    steel: SteelSpec
    connection: SteelConnection


@dataclass(frozen=True)
class HangerKey(ConnectionKey):
    pipe_diameter: SteelDims
    steel: SteelSpec


@dataclass(frozen=True)
class ConnectionBOQ:
    fittings_counts: dict[ConnectionKey, int]
    unit: Unit


@dataclass(frozen=True)
class PaintBOQ:
    primer: float
    lacque: float
    thinner: float
    unit: Unit


@dataclass(frozen=True)
class BOQReport:
    pipes: PipeBOQ
    connections: ConnectionBOQ
    paint: PaintBOQ


@dataclass(frozen=True)
class PaintConfig:
    thickness: int
    scrap_precentage: float
    volume_solids_precentage: float
