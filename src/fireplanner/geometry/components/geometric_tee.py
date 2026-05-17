from __future__ import annotations

from typing import Any, List, override

from fireplanner.firecomponent import Tee
from fireplanner.geometry.primitives.transform import Transform2D
from fireplanner.standards import steel_dim_table, tee_center_dims

from ..primitives import Line, LineType, Point
from .geometric_component import GeometricComponent


class GeometricTee(GeometricComponent):
    def __init__(
        self, tee: Tee, start: Point | None = None, end: Point | None = None
    ) -> None:
        self._run_diameter = tee.run_diameter
        self._branch_diameter = tee.branch_diameter
        self._run_center_to_end, self._branch_center_to_end = tee_center_dims[
            (self._run_diameter, self._branch_diameter)
        ]
        super().__init__(start, end)

    @property
    def run_diameter(self):
        return self._run_diameter

    @property
    def branch_diameter(self):
        return self._branch_diameter

    @property
    def run_center_to_end(self):
        return self._run_center_to_end

    @property
    def branch_center_to_end(self):
        return self._branch_center_to_end

    @override
    def _local_primitives_2d(self) -> list[Primitive2D]:
        R = self.run_center_to_end
        B = self.branch_center_to_end

        rw = steel_dim_table[self.run_diameter] / 2.0
        bw = steel_dim_table[self.branch_diameter] / 2.0

        run_lines = [
            Line(start=Point(x=-R, y=-rw), end=Point(x=R, y=-rw)),  # bottom
            Line(start=Point(x=R, y=-rw), end=Point(x=R, y=rw)),  # right
            Line(start=Point(x=-R, y=rw), end=Point(x=-bw, y=rw)),  # top left
            Line(start=Point(x=bw, y=rw), end=Point(x=R, y=rw)),  # top right
            Line(start=Point(x=-R, y=rw), end=Point(x=-R, y=-rw)),  # left
        ]

        branch_lines = [
            Line(start=Point(x=-bw, y=B), end=Point(x=bw, y=B)),  # bottom
            Line(start=Point(x=bw, y=B), end=Point(x=bw, y=rw)),  # right
            Line(start=Point(x=-bw, y=B), end=Point(x=-bw, y=rw)),  # left
            Line(start=Point(x=0, y=0), end=Point(x=bw, y=rw)),  # center right
            Line(start=Point(x=0, y=0), end=Point(x=-bw, y=rw)),  # center left
        ]

        return run_lines + branch_lines

    @override
    def _local_centerlines(self) -> list[Primitive2D]:
        R = self.run_center_to_end
        B = self.branch_center_to_end
        return [
            Line(
                start=Point(x=-R, y=0),
                end=Point(x=R, y=0),
                line_type=LineType.CenterLine,
            ),  # run center line
            Line(
                start=Point(x=0, y=0),
                end=Point(x=0, y=B),
                line_type=LineType.CenterLine,
            ),  # branch center line
        ]

    @override
    def _local_layout_skeleton(self) -> list[Primitive2D]:
        return self._local_centerlines()
