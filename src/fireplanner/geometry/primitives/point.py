from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from .base import Primitive2D
from math import sqrt


@dataclass(kw_only=True)
class Point(Primitive2D):
    x: float
    y: float
    z: float

    def distance(self, other: Point):
        return sqrt(
            (self.x - other.x) ** 2 + (self.y - other.y) ** 2 + (self.z - other.z) ** 2
        )
    
    def to_json(self) -> dict[str, str]:
        return {"Point" : f"{self.x}, {self.y}, {self.z}"} 

    @classmethod
    def from_json(cls, data: dict[str, str]) -> Point:
        point_data = [float(i) for i in data["Point"].split(",")]
        return Point(point_data[0], point_data[1], point_data[2])



