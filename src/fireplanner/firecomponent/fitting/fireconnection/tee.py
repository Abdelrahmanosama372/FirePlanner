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


class Tee(FireComponent, FireConnection):
    def __init__(
        self,
        run_diameter: SteelDims,
        branch_diameter: SteelDims,
        material: SteelMaterial,
        schedule: SteelSchedule,
        specs: SteelSpecs,
        connection_type: SteelConnection,
    ) -> None:
        if branch_diameter.value > run_diameter.value:
            raise ValueError("Incorrect branch and run diameters assignment of Tee")
        self._run_diameter: SteelDims = run_diameter
        self._branch_diameter: SteelDims = branch_diameter
        super().__init__(material, schedule, specs, connection_type)

    @property
    @final
    def run_diameter(self) -> SteelDims:
        return self._run_diameter

    @property
    @final
    def branch_diameter(self) -> SteelDims:
        return self._branch_diameter

    @override
    def to_json(self) -> dict[Any, Any]:
        component_json = super().to_json()
        component_json["run_diameter"] = str(self._run_diameter.value)
        component_json["branch_diameter"] = str(self._branch_diameter.value)
        return {"Tee": component_json}

    @classmethod
    @override
    def from_json(cls, data: dict[Any, Any]) -> Tee:
        tee_data: dict[str, str] = data["Tee"]
        return Tee(
            run_diameter=SteelDims(float(tee_data["run_diameter"])),
            branch_diameter=SteelDims(float(tee_data["branch_diameter"])),
            material=SteelMaterial(tee_data["material"]),
            schedule=SteelSchedule(tee_data["schedule"]),
            specs=SteelSpecs(tee_data["specs"]),
            connection_type=SteelConnection(tee_data["connection_type"]),
        )

    @override
    def ports_number(self) -> SteelPortsNum:
        return SteelPortsNum.ST_PORTS_3

    @override
    def ports_diameter(self) -> tuple[SteelDims, SteelDims, SteelDims]:
        return (self._run_diameter, self._run_diameter, self._branch_diameter)
