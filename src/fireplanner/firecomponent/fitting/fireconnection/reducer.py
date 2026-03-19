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
    def ports_number(self) -> SteelPortsNum:
        return SteelPortsNum.ST_PORTS_2

    @override
    def ports_diameter(self) -> tuple[SteelDims, SteelDims]:
        return (self._large_diameter, self._small_diameter)
