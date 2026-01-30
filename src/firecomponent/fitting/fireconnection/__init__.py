
from abc import ABC
from enum import Enum
from typing import override

from firecomponent import SteelDims


class SteelPortsNum(Enum):
    ST_PORTS_2 = 2
    ST_PORTS_3 = 3

class FireConnection(ABC):
    @override
    def ports_number(self) -> SteelPortsNum:
        pass

    @override
    def ports_diameter(self) -> tuple[SteelDims, SteelDims] | tuple[SteelDims, SteelDims, SteelDims]:
        pass
