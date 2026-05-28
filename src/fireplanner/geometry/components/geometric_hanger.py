from __future__ import annotations

from typing import override

from fireplanner.firecomponent import Hanger
from fireplanner.geometry.primitives import (
    Circle,
    Line,
    LineType,
    Point,
    Primitive2D,
    Rectangle,
)
from fireplanner.standards.hanger import hanger_dimensions

from .base import ViewType
from .geometric_component import GeometricComponent


class GeometricHanger(GeometricComponent):
    def __init__(self, hanger: Hanger) -> None:
        self._diameter = hanger.diameter
        super().__init__()

    @override
    def _local_primitives_2d(self) -> list[Primitive2D]:
        hanger_props = hanger_dimensions[self._diameter]
        rod_size = hanger_props.rod_size
        width = hanger_props.width
        length = hanger_props.length
        cb_length = hanger_props.cross_bolt_length
        cb_raduis = hanger_props.cross_bolt_diameter / 2
        match self.placement_context.view_type:
            case ViewType.PLAN:
                return [
                    Circle(center=Point(x=0, y=0), radius=rod_size),
                    Rectangle.from_bounds(
                        Point(x=-width / 2, y=-length / 2),
                        Point(x=width / 2, y=length / 2),
                    ),
                    Rectangle.from_bounds(
                        Point(x=-cb_raduis, y=length / 2),
                        Point(x=cb_raduis, y=cb_length / 2),
                    ),
                    Rectangle.from_bounds(
                        Point(x=-cb_raduis, y=-length / 2),
                        Point(x=cb_raduis, y=-cb_length / 2),
                    ),
                ]
            case ViewType.ELEVATION | ViewType.SIDE:
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

    @override
    def local_occupancy_regions(self) -> list[Rectangle]:
        hanger_props = hanger_dimensions[self._diameter]
        width = hanger_props.width
        cb_length = hanger_props.cross_bolt_length

        regions = []
        match self.placement_context.view_type:
            case ViewType.PLAN:
                regions = [
                    Rectangle.from_bounds(
                        Point(x=-width / 2, y=-cb_length / 2),
                        Point(x=width / 2, y=cb_length / 2),
                    ),
                ]
            case ViewType.ELEVATION | ViewType.SIDE:
                raise NotImplementedError

        return regions
