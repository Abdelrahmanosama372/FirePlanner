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


# todo: support reducing elbow also
class Elbow(FireComponent, FireConnection):
    def __init__(
        self,
        diameter: SteelDims,
        angle: float,
        material: SteelMaterial,
        schedule: SteelSchedule,
        specs: SteelSpecs,
        connection_type: SteelConnection,
    ) -> None:
        self._diameter: SteelDims = diameter
        self._angle: float = angle
        super().__init__(material, schedule, specs, connection_type)

    @property
    @final
    def diameter(self) -> SteelDims:
        return self._diameter

    @property
    @final
    def angle(self) -> float:
        return self._angle

    @override
    def to_json(self) -> dict[Any, Any]:
        component_json = super().to_json()
        component_json["diameter"] = str(self._diameter.value)
        component_json["angle"] = str(self._angle)
        return {"Elbow": component_json}

    @classmethod
    @override
    def from_json(cls, data: dict[Any, Any]) -> Elbow:
        elbow_data: dict[str, str] = data["Elbow"]
        return Elbow(
            diameter=SteelDims(float(elbow_data["diameter"])),
            angle=SteelDims(float(elbow_data["angle"])),
            material=SteelMaterial(elbow_data["material"]),
            schedule=SteelSchedule(elbow_data["schedule"]),
            specs=SteelSpecs(elbow_data["specs"]),
            connection_type=SteelConnection(elbow_data["connection_type"]),
        )

    @override
    def ports_number(self) -> SteelPortsNum:
        return SteelPortsNum.ST_PORTS_2

    @override
    def ports_diameter(self) -> tuple[SteelDims, SteelDims]:
        return (self._diameter, self._diameter)
