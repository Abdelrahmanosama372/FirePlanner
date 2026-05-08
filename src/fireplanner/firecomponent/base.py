from enum import StrEnum, Enum, auto
from typing import final, Any, TypeVar
from abc import ABC, abstractmethod


class SteelMaterial(StrEnum):
    Seamless = auto()
    ERW = auto()


class SteelSchedule(StrEnum):
    SCD40 = auto()
    SCD80 = auto()


class SteelSpecs(StrEnum):
    ASTM = auto()
    ISO = auto()


class SteelConnection(StrEnum):
    Grooved = auto()
    Welded = auto()
    Threaded = auto()


class SteelDims(Enum):
    DIM_0_5_INCHES = 0.5
    DIM_0_75_INCHES = 0.75
    DIM_1_INCHES = 1.0
    DIM_1_25_INCHES = 1.25
    DIM_1_5_INCHES = 1.5
    DIM_2_INCHES = 2.0
    DIM_2_5_INCHES = 2.5
    DIM_3_INCHES = 3.0
    DIM_4_INCHES = 4.0
    DIM_6_INCHES = 6.0
    DIM_8_INCHES = 8.0
    DIM_10_INCHES = 10.0
    DIM_12_INCHES = 12.0


T = TypeVar("T", bound="FireComponent")


class FireComponent(ABC):
    def __init__(
        self,
        material: SteelMaterial,
        schedule: SteelSchedule,
        specs: SteelSpecs,
        connection_type: SteelConnection,
    ) -> None:

        self._material: SteelMaterial = material
        self._schedule: SteelSchedule = schedule
        self._specs: SteelSpecs = specs
        self._connection_type: SteelConnection = connection_type

    @property
    @final
    def material(self) -> SteelMaterial:
        return self._material

    @property
    @final
    def schedule(self) -> SteelSchedule:
        return self._schedule

    @property
    @final
    def specs(self) -> SteelSpecs:
        return self._specs

    @property
    @final
    def connection_type(self) -> SteelConnection:
        return self._connection_type

    @abstractmethod
    def to_json(self) -> dict[Any, Any]:
        return {
            "material": self.material.value,
            "schedule": self.schedule.value,
            "specs": self.specs.value,
            "connection_type": self.connection_type.value,
        }

    @abstractmethod
    @classmethod
    def from_json(cls: type[T], data: dict[Any, Any]) -> T:
        pass
