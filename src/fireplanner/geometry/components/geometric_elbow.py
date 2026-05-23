from __future__ import annotations

from math import radians
from typing import override

from fireplanner.firecomponent import Elbow
from fireplanner.standards import elbow_90_lr_center_to_end
from fireplanner.standards.steel_dim import steel_dim_table

from ..primitives import Arc, Line, LineType, Point, Primitive2D
from .base import ViewType
from .geometric_component import GeometricComponent


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

        primitives = []
        match self.placement_context.view_type:
            case ViewType.ELEVATION:
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
                primitives = [inner_arc, outer_arc, vertical_line, horizontal_line]

            case ViewType.PLAN:
                primitives = [
                    Circle(
                        center=Point(x=0, y=0),
                        radius=r,
                    ),
                    Line(
                        start=Point(x=r, y=0),
                        end=Point(x=r, y=self._center_to_end + r),
                    ),
                    Line(
                        start=Point(x=-r, y=0),
                        end=Point(x=-r, y=self._center_to_end + r),
                    ),
                    Line(
                        start=Point(x=-r, y=self._center_to_end + r),
                        end=Point(x=r, y=self._center_to_end + r),
                    ),
                ]

            case ViewType.SIDE:
                primitives = [
                    Circle(
                        center=Point(x=0, y=self._center_to_end),
                        radius=r,
                    ),
                    Line(
                        start=Point(x=r, y=0),
                        end=Point(x=r, y=self._center_to_end),
                    ),
                    Line(
                        start=Point(x=-r, y=0),
                        end=Point(x=-r, y=self._center_to_end),
                    ),
                    Line(
                        start=Point(x=-r, y=0),
                        end=Point(x=r, y=0),
                    ),
                ]

        return primitives

    @override
    def _local_centerlines(self) -> list[Primitive2D]:
        r = steel_dim_table[self._diameter] / 2.0
        center = Point(x=0.0, y=0.0)

        start = Point(x=self._center_to_end, y=0.0)

        primitives = []
        match self.placement_context.view_type:
            case ViewType.ELEVATION:
                primitives = [
                    Arc(
                        start=start,
                        center=center,
                        angle=radians(self._angle),
                        line_type=LineType.CenterLine,
                    )
                ]

            case ViewType.PLAN:
                primitives = [
                    Line(
                        start=Point(x=0, y=-r),
                        end=Point(x=0, y=self._center_to_end + r),
                        line_type=LineType.CenterLine,
                    ),
                    Line(
                        start=Point(x=-r, y=0),
                        end=Point(x=r, y=0),
                        line_type=LineType.CenterLine,
                    ),
                ]

            case ViewType.SIDE:
                primitives = [
                    Line(
                        start=Point(x=0, y=0),
                        end=Point(x=0, y=self._center_to_end + r),
                        line_type=LineType.CenterLine,
                    ),
                    Line(
                        start=Point(x=-r, y=self._center_to_end),
                        end=Point(x=r, y=self._center_to_end),
                        line_type=LineType.CenterLine,
                    ),
                ]

        return primitives

    @override
    def _local_layout_skeleton(self) -> list[Primitive2D]:
        primitives = []
        match self.placement_context.view_type:
            case ViewType.ELEVATION:
                primitives = [
                    Line(
                        start=Point(x=self.center_to_end, y=0),
                        end=Point(x=self.center_to_end, y=self.center_to_end),
                    ),
                    Line(
                        start=Point(x=self.center_to_end, y=self.center_to_end),
                        end=Point(x=0, y=self.center_to_end),
                    ),
                ]

            case ViewType.PLAN | ViewType.SIDE:
                primitives = self._local_centerlines(view_type)

        return primitives
