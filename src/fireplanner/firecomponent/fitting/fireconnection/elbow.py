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


# todo: support reducing elbow also
class Elbow(FireComponent, FireConnection):
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
    def ports_number(self) -> SteelPortsNum:
        return SteelPortsNum.ST_PORTS_2

    @override
    def ports_diameter(self) -> tuple[SteelDims, SteelDims]:
        return (self._diameter, self._diameter)
