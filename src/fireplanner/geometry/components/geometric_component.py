from abc import ABC, abstractmethod
from typing import Any, TypeVar

from ..primitives import Line, Point, Primitive2D, Primitive3D, Transform2D

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

    @abstractmethod
    def _local_centerlines(self) -> list[Primitive2D]:
        """Center Line Model defined in local/origin space."""

    @abstractmethod
    def _local_layout_skeleton(self) -> list[Primitive2D]:
        """Analytical layout primitives defined in local/origin space."""

    def centerlines(self) -> list[Line]:
        if self.transform is None:
            raise ValueError("Couldn't build center lines, Tranform is None")

        return [
            line.transform_2d(self._transform) for line in self._local_centerlines()
        ]

    def layout_skeleton(self):
        if self.transform is None:
            raise ValueError("Couldn't build layout skeleton, Tranform is None")
        return [
            line.transform_2d(self._transform) for line in self._local_layout_skeleton()
        ]

    def _build_primitives_2d(self, include_centerlines):
        if self.transform is None:
            raise ValueError("Couldn't build 2d Primitive, Tranform is None")

        primitives = self._local_primitives_2d()
        if include_centerlines:
            primitives.extend(self._local_centerlines())
        self._primitives_2d = [
            prim.transform_2d(self._transform) for prim in primitives
        ]

    def _build_primitives_3d(self):
        raise NotImplementedError

    def get_primitives_2d(self, include_centerlines: bool = False) -> list[Primitive2D]:
        if len(self._primitives_2d) == 0:
            self._build_primitives_2d(include_centerlines)
        return self._primitives_2d

    def get_primitives_3d(self) -> list[Primitive3D]:
        if len(self._primitives_3d) == 0:
            self._build_primitives_3d()
        return self._primitives_3d
