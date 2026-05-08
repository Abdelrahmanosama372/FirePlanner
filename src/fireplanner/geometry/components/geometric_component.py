from abc import ABC, abstractmethod
from typing import Any, TypeVar

from ..primitives import Primitive2D, Primitive3D, Transform2D
from ..primitives.point import Point


T = TypeVar("T", bound="GeometricComponent")


class GeometricComponent(ABC):
    def __init__(self, start: Point | None = None, end: Point | None = None) -> None:
        self._start: Point | None = start
        self._end: Point | None = end
        self._primitives_2d: list[Primitive2D] = []
        self._primitives_3d: list[Primitive3D] = []
        self._transform: Transform2D | None = None

    @property
    def start(self):
        return self._start

    @start.setter
    def start(self, value: Point):
        self._start = value

    @property
    def end(self):
        return self._end

    @end.setter
    def end(self, value: Point):
        self._end = value

    @property
    def transform(self):
        return self._transform

    @transform.setter
    def transform(self, value: Transform2D):
        self._transform = value

    def has_transform(self) -> bool:
        return self._transform is not None

    @abstractmethod
    def _local_primitives_2d(self) -> list[Primitive2D]:
        """Geometry defined in local/origin space."""

    def _build_primitives_2d(self):
        if self.transform is None:
            raise ValueError("Couldn't build 2d Primitive, Tranform is None")

        self._primitives_2d = [
            prim.transform_2d(self._transform) for prim in self._local_primitives_2d()
        ]

    def _build_primitives_3d(self):
        raise NotImplementedError

    def get_primitives_2d(self) -> list[Primitive2D]:
        if len(self._primitives_2d) == 0:
            self._build_primitives_2d()
        return self._primitives_2d

    def get_primitives_3d(self) -> list[Primitive3D]:
        if len(self._primitives_3d) == 0:
            self._build_primitives_3d()
        return self._primitives_3d
