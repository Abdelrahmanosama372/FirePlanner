from __future__ import annotations
from abc import abstractmethod
from tracemalloc import start
from typing import override, Any
from fireplanner.firecomponent import SteelDims
from fireplanner.geometry.primitives.line import Line
from .geometric_component import GeometricComponent
from fireplanner.standards import steel_dim_table
from fireplanner.geometry.primitives import Point, Primitive2D, Primitive3D
from fireplanner.geometry.primitives.transform import Transform2D
from .base import UndefinedGeometry
from fireplanner.firecomponent import Pipe


class GeometricPipe(GeometricComponent):
    def __init__(
        self,
        pipe: Pipe,
        start: Point | None = None,
        end: Point | None = None,
    ) -> None:
        self._diameter = pipe.diameter
        self._length = None
        super().__init__(start, end)

    @override
    def _local_primitives_2d(self) -> list[Primitive2D]:
        r = self._diameter.value / 2.0
        top = Line(start=Point(x=self.start.x, y=r), end=Point(x=self.end.x, y=r))
        bottom = Line(start=Point(x=self.start.x, y=-r), end=Point(x=self.end.x, y=-r))
        return [top, bottom]
