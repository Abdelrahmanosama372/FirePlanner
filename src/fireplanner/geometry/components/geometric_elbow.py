from __future__ import annotations
from math import radians
from typing import override

from fireplanner.standards.steel_dim import steel_dim_table
from .geometric_component import GeometricComponent
from ..primitives import Point, Primitive2D, Arc, Line, LineType
from fireplanner.firecomponent import Elbow
from fireplanner.standards import elbow_90_lr_center_to_end


class GeometricElbow(GeometricComponent):
    def __init__(
        self, elbow: Elbow, start: Point | None = None, end: Point | None = None
    ) -> None:
        self._diameter = elbow.diameter
        self._center_to_end: float = elbow_90_lr_center_to_end(self._diameter)
        self._angle = elbow.angle
        super().__init__(start, end)

    @property
    def center_to_end(self):
        return self._center_to_end

    @property
    def diameter(self):
        return self._diameter

    @property
    def angle(self):
        return self._angle

    @override
    def _local_primitives_2d(self) -> list[Primitive2D]:
        r = steel_dim_table[self._diameter] / 2.0

        center = Point(x=0.0, y=0.0)

        # Start points of the two arc segments
        # (assuming a 90° elbow from horizontal to vertical)
        start_out = Point(x=self._center_to_end + r, y=0.0)
        start_in = Point(x=self._center_to_end - r, y=0.0)

        inner_arc = Arc(
            start=start_in,
            center=center,
            angle=radians(self._angle),
        )

        outer_arc = Arc(
            start=start_out,
            center=center,
            angle=radians(self._angle),
        )

        vertical_line = Line(
            start=Point(x=0, y=self._center_to_end - r),
            end=Point(x=0, y=self._center_to_end + r),
        )
        horizontal_line = Line(
            start=Point(x=self._center_to_end - r, y=0),
            end=Point(x=self._center_to_end + r, y=0),
        )

        return [inner_arc, outer_arc, vertical_line, horizontal_line]

    @override
    def _local_centerlines(self) -> list[Primitive2D]:
        center = Point(x=0.0, y=0.0)

        start = Point(x=self._center_to_end, y=0.0)
        return [
            Arc(
                start=start,
                center=center,
                angle=radians(self._angle),
                line_type=LineType.CenterLine,
            )
        ]

    @override
    def _local_layout_skeleton(self) -> list[Primitive2D]:
        return [
            Line(
                start=Point(x=self.center_to_end, y=0),
                end=Point(x=self.center_to_end, y=self.center_to_end),
            ),
            Line(
                start=Point(x=self.center_to_end, y=self.center_to_end),
                end=Point(x=0, y=self.center_to_end),
            ),
        ]
