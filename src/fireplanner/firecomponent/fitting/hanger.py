from __future__ import annotations
from ..base import (
    FireComponent,
    SteelConnection,
    SteelDims,
    SteelMaterial,
    SteelSchedule,
    SteelSpecs,
)
from typing import final, override, Any


class Hanger(FireComponent):
    def __init__(
        self,
        diameter: SteelDims,
        material: SteelMaterial,
        schedule: SteelSchedule,
        specs: SteelSpecs,
        connection_type: SteelConnection,
    ) -> None:
        self._diameter = diameter
        super().__init__(material, schedule, specs, connection_type)

    @property
    @final
    def diameter(self) -> SteelDims:
        return self._diameter

    @override
    def to_json(self) -> dict[Any, Any]:
        component_json = super().to_json()
        component_json["diameter"] = str(self._diameter.value)
        return {"Hanger": component_json}

    @classmethod
    @override
    def from_json(cls, data: dict[Any, Any]) -> Hanger:
        hanger_data: dict[str, str] = data["Hanger"]
        return Hanger(
            diameter=SteelDims(float(hanger_data["diameter"])),
            material=SteelMaterial(hanger_data["material"]),
            schedule=SteelSchedule(hanger_data["schedule"]),
            specs=SteelSpecs(hanger_data["specs"]),
            connection_type=SteelConnection(hanger_data["connection_type"]),
        )
