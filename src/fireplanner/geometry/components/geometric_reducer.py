from __future__ import annotations

from typing import override

from fireplanner.firecomponent import Reducer
from fireplanner.geometry.primitives.circle import Circle
from fireplanner.standards import reducer_end_to_end_table, steel_dim_table

from ..primitives import Line, LineType, Point, Primitive2D, Rectangle
from .base import ViewType
from .geometric_component import GeometricComponent


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

        primitives = []
        match self.placement_context.view_type:
            case ViewType.ELEVATION | ViewType.PLAN:
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

                primitives = [top, bottom, right, left]
            case ViewType.SIDE:
                primitives = [
                    Circle(center=Point(x=0, y=0), radius=r_large),
                    Circle(center=Point(x=0, y=0), radius=r_small),
                ]

        return primitives

    @override
    def _local_centerlines(self) -> list[Primitive2D]:
        r_large = steel_dim_table[self._large_diameter] / 2.0
        L = self._end_to_end

        x0 = -L / 2.0
        x1 = L / 2.0

        primitives = []
        match self.placement_context.view_type:
            case ViewType.ELEVATION | ViewType.PLAN:
                primitives = [
                    Line(
                        start=Point(x=x0, y=0),
                        end=Point(x=x1, y=0),
                        line_type=LineType.CenterLine,
                    ),
                ]
            case ViewType.SIDE:
                primitives = [
                    Line(
                        start=Point(x=-r_large, y=0),
                        end=Point(x=r_large, y=0),
                        line_type=LineType.CenterLine,
                    ),
                    Line(
                        start=Point(x=0, y=-r_large),
                        end=Point(x=0, y=r_large),
                        line_type=LineType.CenterLine,
                    ),
                ]

        return primitives

    @override
    def _local_layout_skeleton(self) -> list[Primitive2D]:
        return self._local_centerlines()

    @override
    def local_occupancy_regions(self) -> list[Rectangle]:
        L = self._end_to_end
        r_large = steel_dim_table[self._large_diameter] / 2.0

        regions = []
        match self.placement_context.view_type:
            case ViewType.ELEVATION | ViewType.PLAN:
                regions = [
                    Rectangle.from_bounds(
                        point1=Point(x=-L / 2.0, y=-r_large),
                        point2=Point(x=L / 2.0, y=r_large),
                    )
                ]
            case ViewType.SIDE:
                regions = [
                    Rectangle.from_bounds(
                        point1=Point(x=-r_large, y=-r_large),
                        point2=Point(x=r_large, y=r_large),
                    )
                ]

        return regions
