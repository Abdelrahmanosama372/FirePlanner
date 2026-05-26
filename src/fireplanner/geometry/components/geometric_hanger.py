from __future__ import annotations

from typing import override

from fireplanner.firecomponent import Hanger
from fireplanner.geometry.primitives import Line, LineType, Point, Primitive2D

from .base import ViewType
from .geometric_component import GeometricComponent


class GeometricHanger(GeometricComponent):
    def __init__(self, hanger: Hanger) -> None:
        self._diameter = hanger.diameter
        super().__init__()

    @override
    def _local_primitives_2d(self) -> list[Primitive2D]:
        # simple hanger symbol around local origin
        # will be updated later
        width = 60.0
        stem = 80.0
        match self.placement_context.view_type:
            case ViewType.ELEVATION | ViewType.PLAN:
                return [
                    Line(start=Point(x=-width / 2, y=0), end=Point(x=width / 2, y=0)),
                    Line(start=Point(x=0, y=0), end=Point(x=0, y=stem)),
                ]
            case ViewType.SIDE:
                raise NotImplementedError

    @override
    def _local_centerlines(self) -> list[Primitive2D]:
        return [
            Line(
                start=Point(x=-20, y=0),
                end=Point(x=20, y=0),
                line_type=LineType.CenterLine,
            )
        ]

    @override
    def _local_layout_skeleton(self) -> list[Primitive2D]:
        return []
