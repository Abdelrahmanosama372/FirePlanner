from __future__ import annotations
from math import atan2
from .point import Point
import numpy as np
from numpy.typing import NDArray


class Transform2D:
    def __init__(self, origin: Point, rotation: float):
        self._origin: Point = origin
        self._rotation: float = rotation


    @property
    def origin(self) -> Point:
        return self._origin

    @property
    def angle(self) -> float:
        return self._rotation

    @property
    def transform(self) -> NDArray[np.float64]:
        transform: NDArray[np.float64] = np.array(
            [
                [np.cos(self._rotation), -np.sin(self._rotation), self._origin.x],
                [np.sin(self._rotation), np.cos(self._rotation), self._origin.y],
                [0, 0, 1],
            ]
        )
        return transform

    def translated_local(self, dx: float, dy: float) -> Transform2D:
        translation = np.array([[dx, dy, 1]]).T
        new_transform: NDArray[np.float64] = np.dot(self.transform, translation)
        new_origin = Point(x=new_transform[0, 0], y=new_transform[1, 0], z=0)
        return Transform2D(origin=new_origin, rotation=self._rotation)

    def translate_local(self, dx: float, dy: float):
        new_transform = self.translated_local(dx, dy)
        self._origin = new_transform.origin

    def rotated_local(self, angle: float) -> Transform2D:
        return Transform2D(origin=self.origin, rotation=self._rotation + angle)

    def rotate_local(self, angle: float):
        self._rotation += angle
 
    @staticmethod
    def from_array(transform: NDArray[np.float64]) -> Transform2D:
        c = transform[0,0]
        s = transform[1,0]
        rotation = atan2(s, c)
        origin = Point(x=transform[0,2], y=transform[1,2], z=0)
        return Transform2D(origin, rotation)

    def __matmul__(self, other: Transform2D) -> Transform2D:
        composed = self.transform @ other.transform
        return Transform2D.from_array(composed)


