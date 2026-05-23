from __future__ import annotations

from math import asin
from typing import override

from fireplanner.firecomponent import Tee
from fireplanner.standards import (
    calculate_welded_branch_penetration_depth,
    steel_dim_table,
)

from ..primitives import Arc, Circle, Line, LineType, Point, Primitive2D
from .base import ViewType
from .geometric_component import GeometricComponent


class GeometricWeldedBranch(GeometricComponent):
    def __init__(
        self, tee: Tee, start: Point | None = None, end: Point | None = None
    ) -> None:
        self._run_diameter = tee.run_diameter
        self._branch_diameter = tee.branch_diameter
        self._penetration_depth: float = calculate_welded_branch_penetration_depth(
            run_diameter=self._run_diameter, branch_diameter=self._branch_diameter
        )
        super().__init__(start, end)

    @property
    def run_diameter(self):
        return self._run_diameter

    @property
    def branch_diameter(self):
        return self._branch_diameter

    @override
    def _local_primitives_2d(self) -> list[Primitive2D]:
        run_raduis = steel_dim_table[self._run_diameter] / 2
        branch_raduis = steel_dim_table[self._branch_diameter] / 2
        arc_raduis = (
            branch_raduis * branch_raduis / self._penetration_depth
            + self._penetration_depth
        ) / 2
        arc_center = Point(x=0, y=arc_raduis - self._penetration_depth + run_raduis)
        arc_start = Point(x=-branch_raduis, y=run_raduis)
        arc_angle = 2 * asin(branch_raduis / arc_raduis)

        match self.placement_context.view_type:
            case ViewType.ELEVATION | ViewType.SIDE:
                primitives = [Arc(start=arc_start, center=arc_center, angle=arc_angle)]

            case ViewType.PLAN:
                primitives = [
                    Circle(
                        center=Point(x=0, y=0),
                        radius=branch_raduis,
                    ),
                ]

        return primitives

    @override
    def _local_centerlines(self) -> list[Primitive2D]:
        R = steel_dim_table[self._run_diameter] / 2

        primitives = []
        match self.placement_context.view_type:
            case ViewType.ELEVATION | ViewType.SIDE:
                primitives = [
                    Line(
                        start=Point(x=0, y=0),
                        end=Point(x=0, y=R),
                        line_type=LineType.CenterLine,
                    ),  # branch center line
                ]

            case ViewType.PLAN:
                primitives = [
                    Circle(
                        center=Point(x=0, y=0),
                        radius=R,
                        line_type=LineType.CenterLine,
                    ),
                ]

        return primitives

    @override
    def _local_layout_skeleton(self) -> list[Primitive2D]:
        return self._local_centerlines(view_type)
