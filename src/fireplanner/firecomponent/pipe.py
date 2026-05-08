from __future__ import annotations
from typing import override, final, Any
from .base import (
    FireComponent,
    SteelConnection,
    SteelDims,
    SteelMaterial,
    SteelSchedule,
    SteelSpecs,
)


class Pipe(FireComponent):
    def __init__(
        self,
        diameter: SteelDims,
        material: SteelMaterial,
        schedule: SteelSchedule,
        specs: SteelSpecs,
        connection_type: SteelConnection,
    ) -> None:

        self._diameter: SteelDims = diameter
        super().__init__(material, schedule, specs, connection_type)

    @property
    @final
    def diameter(self) -> SteelDims:
        return self._diameter

    @override
    def to_json(self) -> dict[Any, Any]:
        component_json = super().to_json()
        component_json["diameter"] = str(self._diameter.value)
        return {"Pipe": component_json}

    @classmethod
    @override
    def from_json(cls, data: dict[Any, Any]) -> Pipe:
        pipe_data: dict[str, str] = data["Pipe"]
        return Pipe(
            diameter=SteelDims(float(pipe_data["diameter"])),
            material=SteelMaterial(pipe_data["material"]),
            schedule=SteelSchedule(pipe_data["schedule"]),
            specs=SteelSpecs(pipe_data["specs"]),
            connection_type=SteelConnection(pipe_data["connection_type"]),
        )
