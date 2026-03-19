from typing import override
from ...base import (
    FireComponent,
    SteelConnection,
    SteelDims,
    SteelMaterial,
    SteelSchedule,
    SteelSpecs,
)
from . import FireConnection, SteelPortsNum
from typing_extensions import final


# todo: handle case if rundiameter is less than branch diameter
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
    def ports_number(self) -> SteelPortsNum:
        return SteelPortsNum.ST_PORTS_3

    @override
    def ports_diameter(self) -> tuple[SteelDims, SteelDims, SteelDims]:
        return (self._run_diameter, self._run_diameter, self._branch_diameter)
