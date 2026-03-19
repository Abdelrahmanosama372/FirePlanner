from .base import (
    FireComponent,
    SteelConnection,
    SteelDims,
    SteelMaterial,
    SteelSchedule,
    SteelSpecs,
)
from typing_extensions import final


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
