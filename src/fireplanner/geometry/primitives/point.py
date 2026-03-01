from __future__ import annotations
from dataclasses import dataclass
from .base import Primitive2D
from math import sqrt
import numpy as np


@dataclass(kw_only=True)
class Point(Primitive2D):
    x: float
    y: float
    z: float = 0.0

    def distance(self, other: Point):
        return sqrt(
            (self.x - other.x) ** 2 + (self.y - other.y) ** 2 + (self.z - other.z) ** 2
        )

    def __add__(self, other: Point) -> Point:
        return Point(
            x=self.x + other.x,
            y=self.y + other.y,
            z=self.z + other.z,
        )

    def __sub__(self, other: Point) -> Point:
        return Point(
            x=self.x - other.x,
            y=self.y - other.y,
            z=self.z - other.z,
        )

    def array(self) -> np.ndarray:
        return np.array([self.x, self.y, self.z])

    def to_json(self) -> dict[str, str]:
        return {"Point": f"{self.x}, {self.y}, {self.z}"}

    @classmethod
    def from_json(cls, data: dict[str, str]) -> Point:
        point_data = [float(i) for i in data["Point"].split(",")]
        return Point(x=point_data[0], y=point_data[1], z=point_data[2])
