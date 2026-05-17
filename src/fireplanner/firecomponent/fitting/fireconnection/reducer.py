from __future__ import annotations

from typing import Any, final, override

from ...base import (
    FireComponent,
    SteelConnection,
    SteelDims,
    SteelMaterial,
    SteelSchedule,
    SteelSpecs,
)
from . import FireConnection, SteelPortsNum


# todo: handle case if input diameters are of same size
class Reducer(FireComponent, FireConnection):
    def __init__(
        self,
        diameter1: SteelDims,
        diameter2: SteelDims,
        material: SteelMaterial,
        schedule: SteelSchedule,
        specs: SteelSpecs,
        connection_type: SteelConnection,
    ) -> None:
        self._large_diameter, self._small_diameter = (
            (diameter1, diameter2)
            if diameter1.value > diameter2.value
            else (diameter2, diameter1)
        )
        super().__init__(material, schedule, specs, connection_type)

    @property
    @final
    def large_diameter(self) -> SteelDims:
        return self._large_diameter

    @property
    @final
    def small_diameter(self) -> SteelDims:
        return self._small_diameter

    @override
    def to_json(self) -> dict[Any, Any]:
        component_json = super().to_json()
        component_json["diameter1"] = str(self._large_diameter.value)
        component_json["diameter2"] = str(self._small_diameter.value)
        return {"Reducer": component_json}

    @classmethod
    @override
    def from_json(cls, data: dict[Any, Any]) -> Reducer:
        reducer_data: dict[str, str] = data["Reducer"]
        return Reducer(
            diameter1=SteelDims(float(reducer_data["diameter1"])),
            diameter2=SteelDims(float(reducer_data["diameter2"])),
            material=SteelMaterial(reducer_data["material"]),
            schedule=SteelSchedule(reducer_data["schedule"]),
            specs=SteelSpecs(reducer_data["specs"]),
            connection_type=SteelConnection(reducer_data["connection_type"]),
        )

    @override
    def ports_number(self) -> SteelPortsNum:
        return SteelPortsNum.ST_PORTS_2

    @override
    def ports_diameter(self) -> tuple[SteelDims, SteelDims]:
        return (self._large_diameter, self._small_diameter)
