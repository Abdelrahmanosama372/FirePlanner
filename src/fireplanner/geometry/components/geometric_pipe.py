from __future__ import annotations

from math import isclose

from fireplanner.geometry.primitives.line import Line
from fireplanner.standards.steel_dim import steel_dim_table
from .geometric_component import GeometricComponent
from fireplanner.geometry.primitives import Point, Primitive2D
from fireplanner.firecomponent import Pipe
from typing import override


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

    @property
    def diameter(self):
        return self._diameter

    @property
    def length(self):
        if not (self._start and self._end):
            raise ValueError(
                "Cannot compute pipe length. pipe start or end points are None"
            )
        return self._start.distance(self._end)

    @override
    def _local_primitives_2d(self) -> list[Primitive2D]:
        if not (self._start and self._end):
            raise ValueError("Cannot build local pipe geometry without start and end.")
        r = steel_dim_table[self._diameter] / 2.0
        length = self.length
        if isclose(length, 0.0, abs_tol=1e-9):
            raise ValueError("Cannot build local pipe geometry for zero-length pipe.")
        top = Line(start=Point(x=0.0, y=r), end=Point(x=length, y=r))
        bottom = Line(start=Point(x=0.0, y=-r), end=Point(x=length, y=-r))
        return [top, bottom]
