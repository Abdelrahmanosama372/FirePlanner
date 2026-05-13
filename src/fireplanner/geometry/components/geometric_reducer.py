from __future__ import annotations
from typing import override

from fireplanner.standards import steel_dim_table
from .geometric_component import GeometricComponent
from ..primitives import Primitive2D, Point, Line
from fireplanner.firecomponent import Reducer
from fireplanner.standards import reducer_end_to_end_table


class GeometricReducer(GeometricComponent):
    def __init__(
        self, reducer: Reducer, start: Point | None = None, end: Point | None = None
    ) -> None:
        self._large_diameter = reducer.large_diameter
        self._small_diameter = reducer.small_diameter
        self._end_to_end: float = reducer_end_to_end_table[reducer.large_diameter]
        super().__init__(start, end)

    @property
    def large_diameter(self):
        return self._large_diameter

    @property
    def small_diameter(self):
        return self._small_diameter

    @property
    def end_to_end(self):
        return self._end_to_end

    @override
    def _local_primitives_2d(self) -> list[Primitive2D]:
        L = self._end_to_end

        r_large = steel_dim_table[self._large_diameter] / 2.0
        r_small = steel_dim_table[self._small_diameter] / 2.0

        x0 = -L / 2.0
        x1 = L / 2.0

        top = Line(
            start=Point(x=x0, y=r_small),
            end=Point(x=x1, y=r_large),
        )

        bottom = Line(
            start=Point(x=x1, y=-r_large),
            end=Point(x=x0, y=-r_small),
        )

        left = Line(
            start=Point(x=x0, y=-r_small),
            end=Point(x=x0, y=r_small),
        )

        right = Line(
            start=Point(x=x1, y=r_large),
            end=Point(x=x1, y=-r_large),
        )

        return [top, bottom, right, left]

    @override
    def _local_center_line_model(self) -> list[Line]:
        L = self._end_to_end

        x0 = -L / 2.0
        x1 = L / 2.0
        return [
            Line(start=Point(x=x0, y=0), end=Point(x=x1, y=0)),
        ]
