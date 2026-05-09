from __future__ import annotations
from fireplanner.geometry.primitives.line import Line
from .geometric_component import GeometricComponent
from fireplanner.geometry.primitives import Point, Primitive2D
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

    @property
    def length(self):
        if not (self._start and self._end):
            raise ValueError(
                "Cannot compute pipe length. pipe start or end points are None"
            )
        return self._start.distance(self._end)

    @override
    def _local_primitives_2d(self) -> list[Primitive2D]:
        r = self._diameter.value / 2.0
        top = Line(start=Point(x=self.start.x, y=r), end=Point(x=self.end.x, y=r))
        bottom = Line(start=Point(x=self.start.x, y=-r), end=Point(x=self.end.x, y=-r))
        return [top, bottom]
