"""Line primitive types and 2D segment intersection helpers."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Optional, Tuple

import numpy as np

from .base import Primitive2D
from .point import Point

EPS = 1e-9


def cross_2d(ax: float, ay: float, bx: float, by: float) -> float:
    """Return the result of the 2D cross product."""
    return ax * by - ay * bx


class LineType(StrEnum):
    """Supported semantic types for a line segment."""

    Normal = "Normal"
    CenterLine = "CenterLine"


@dataclass(init=False)
class Line(Primitive2D):
    """Finite 2D line segment with optional semantic type metadata."""

    start: Point
    end: Point
    line_type: LineType = LineType.Normal

    def __init__(
        self,
        start: Point,
        end: Point,
        line_type: LineType = LineType.Normal,
        id: int = -1,
    ) -> None:
        self.start = start
        self.end = end
        self.line_type = line_type
        super().__init__(id=id)

    def __eq__(self, other):
        if not isinstance(other, Line):
            return NotImplemented
        return (
            self.start == other.start
            and self.end == other.end
            and self.line_type == other.line_type
        )

    def pass_through_point(self, point: Point, tol: float = EPS) -> bool:
        """Return whether a point lies on this segment within tolerance."""
        P = point.array()
        A = self.start.array()
        B = self.end.array()

        AB = B - A
        AP = P - A

        cross = np.cross(AB, AP)
        if not np.allclose(cross, 0, atol=tol):
            return False

        dot = np.dot(AP, AB)
        if dot < 0:
            return False
        if dot > np.dot(AB, AB):
            return False

        return True

    def intersects_line_2D(self, line: Line) -> Tuple[bool, Optional[Point]]:
        """Compute segment-segment intersection and return hit flag and point."""
        A = self.start
        B = self.end
        C = line.start
        D = line.end

        # r = B - A
        rx = B.x - A.x
        ry = B.y - A.y

        # s = D - C
        sx = D.x - C.x
        sy = D.y - C.y

        # w = C - A
        wx = C.x - A.x
        wy = C.y - A.y

        denom = cross_2d(rx, ry, sx, sy)

        # -------------------------------------------------
        # Case 1: Not parallel
        # -------------------------------------------------
        if abs(denom) > EPS:

            t = cross_2d(wx, wy, sx, sy) / denom
            u = cross_2d(wx, wy, rx, ry) / denom

            if 0.0 <= t <= 1.0 and 0.0 <= u <= 1.0:
                intersection_x = A.x + t * rx
                intersection_y = A.y + t * ry
                return True, Point(x=intersection_x, y=intersection_y)

            return False, None

        # -------------------------------------------------
        # Case 2: Parallel
        # -------------------------------------------------
        # Check collinearity
        if abs(cross_2d(wx, wy, rx, ry)) > EPS:
            return False, None  # Parallel but not collinear

        # -------------------------------------------------
        # Case 3: Collinear - check overlap
        # -------------------------------------------------
        def within(a: float, b: float, c: float) -> bool:
            """Return whether c lies within inclusive range [a, b] with epsilon."""
            return min(a, b) - EPS <= c <= max(a, b) + EPS

        if within(A.x, B.x, C.x) and within(A.y, B.y, C.y):
            return True, C

        if within(A.x, B.x, D.x) and within(A.y, B.y, D.y):
            return True, D

        if within(C.x, D.x, A.x) and within(C.y, D.y, A.y):
            return True, A

        if within(C.x, D.x, B.x) and within(C.y, D.y, B.y):
            return True, B

        return False, None

    def to_json(self) -> dict[str, Any]:
        """Serialize this line to the project JSON format."""
        return {
            "Line": {
                "start": self.start.to_json(),
                "end": self.end.to_json(),
                "line type": self.line_type.value,
            }
        }

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> Line:
        """Build a line instance from the project JSON format."""
        line_props = data["Line"]
        start = Point.from_json(line_props["start"])
        end = Point.from_json(line_props["end"])
        line_type = LineType(line_props["line type"])
        return Line(start=start, end=end, line_type=line_type)
