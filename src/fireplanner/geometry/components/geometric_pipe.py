from __future__ import annotations
from typing import override, Any
from fireplanner.firecomponent import SteelDims
from .geometric_component import GeometricComponent 
from fireplanner.standards import steel_dim_table
from fireplanner.geometry.primitives import Point, Primitive2D, Primitive3D
from .base import UndefinedGeometry


class GeometricPipe(GeometricComponent):
    def __init__(
        self,
        diameter: SteelDims,
        length: float = 0.0,
        start: Point | None = None,
        end: Point | None = None,
    ) -> None:
        self._diameter = steel_dim_table[diameter]
        self._length = length
        super().__init__(start, end)

    @override
    def is_defined_geometry(self) -> bool:
        if self.start is None or self.end is None:
            return False
        else:
            return True


    @override
    def _build_primitives_2d(self):


    @override
    def _build_primitives_3d(self):
        ...

    @override
    def to_json(self) -> dict[str, Any]:
        if not self.is_defined_geometry():
            raise UndefinedGeometry("failed serialization due to undefined geometry")

        primitives = [prim.to_json() for prim in self.get_primitives_2d()]

        return {
            "Pipe": {
                "diameter": self._diameter,
                "length": self._length,
                "start": self.start.to_json(),
                "end": self.end.to_json(),
                "primitives": primitives
            }
        }

    @classmethod
    @override
    def from_json(cls, data: dict[str, Any]) -> GeometricPipe: 
        """ Saftey: no exception happens as value always exsits since it is serialized using same table """
        diameter = next( key for key, value in steel_dim_table.items() if value == float(data["Pipe"]["diameter"]))
        length = float(data["Pipe"]["length"])
        start = Point.from_json(data["Pipe"]["start"]) 
        end = Point.from_json(data["Pipe"]["end"]) 
        return GeometricPipe(diameter, length, start, end)
