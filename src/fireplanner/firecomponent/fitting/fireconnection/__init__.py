from abc import ABC, abstractmethod
from enum import Enum

from ...base import SteelDims


class SteelPortsNum(Enum):
    ST_PORTS_2 = 2
    ST_PORTS_3 = 3


class FireConnection(ABC):
    @abstractmethod
    def ports_number(self) -> SteelPortsNum:
        pass

    @abstractmethod
    def ports_diameter(
        self,
    ) -> tuple[SteelDims, SteelDims] | tuple[SteelDims, SteelDims, SteelDims]:
        pass
