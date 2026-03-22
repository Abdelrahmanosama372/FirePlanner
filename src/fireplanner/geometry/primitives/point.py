"""Point primitive definition and coordinate utility methods."""

from __future__ import annotations

from dataclasses import dataclass
from math import sqrt
from typing import override

import numpy as np

from .base import Primitive2D


@dataclass(init=False)
class Point(Primitive2D):
    """Cartesian point used by 2D/3D geometry primitives."""

    x: float
    y: float
    z: float = 0.0

    def __init__(self, x: float, y: float, z: float = 0.0, id: int = -1) -> None:
        self.x = x
        self.y = y
        self.z = z
        super().__init__(id=id)

    def distance(self, other: Point):
        """Return Euclidean distance to another point."""
        return sqrt(
            (self.x - other.x) ** 2 + (self.y - other.y) ** 2 + (self.z - other.z) ** 2
        )

    def __add__(self, other: Point) -> Point:
        """Return coordinate-wise addition of two points."""
        return Point(
            x=self.x + other.x,
            y=self.y + other.y,
            z=self.z + other.z,
        )

    def __sub__(self, other: Point) -> Point:
        """Return coordinate-wise subtraction of two points."""
        return Point(
            x=self.x - other.x,
            y=self.y - other.y,
            z=self.z - other.z,
        )

    def array(self) -> np.ndarray:
        """Return point coordinates as a NumPy array `[x, y, z]`."""
        return np.array([self.x, self.y, self.z])

    @override
    def to_json(self) -> dict[str, str]:
        """Serialize this point to the project JSON format."""
        return {"Point": f"{self.x}, {self.y}, {self.z}"}

    @override
    @classmethod
    def from_json(cls, data: dict[str, str]) -> Point:
        """Build a point instance from the project JSON format."""
        point_data = [float(i) for i in data["Point"].split(",")]
        return Point(x=point_data[0], y=point_data[1], z=point_data[2])
