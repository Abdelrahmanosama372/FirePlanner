"""Arc primitive definitions and JSON serialization helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, override

from .base import Primitive2D
from .point import Point


@dataclass(init=False)
class Arc(Primitive2D):
    """Circular arc represented by a start point, center point, and sweep angle."""

    start: Point
    center: Point
    angle: float

    def __init__(self, start: Point, center: Point, angle: float, id: int = -1) -> None:
        self.start = start
        self.center = center
        self.angle = angle
        super().__init__(id=id)

    @override
    def transform_2d(self, transform: "Transform2D") -> Primitive2D:
        start_trans = self.start.transform_2d(transform)
        center_trans = self.center.transform_2d(transform)
        return Arc(start=start_trans, center=center_trans, angle=self.angle)

    def __hash__(self) -> int:
        return hash(self.start) + hash(self.center)

    @override
    def to_json(self) -> dict[Any, Any]:
        """Serialize this arc to the project JSON format."""
        return {
            "Arc": {
                "start": self.start.to_json(),
                "center": self.center.to_json(),
                "angle": str(self.angle),
            }
        }

    @override
    @classmethod
    def from_json(cls, data: dict[Any, Any]) -> Arc:
        """Build an arc instance from the project JSON format."""
        arc_props = data["Arc"]
        start = Point.from_json(arc_props["start"])
        center = Point.from_json(arc_props["center"])
        angle = float(arc_props["angle"])
        return Arc(start=start, center=center, angle=angle)
