from abc import ABC, abstractmethod
from typing import Any, TypeVar
from ..primitives import Primitive2D, Primitive3D
from ..primitives.point import Point


T = TypeVar("T", bound="GeometricComponent")


class GeometricComponent(ABC):
    def __init__(self, start: Point | None = None, end: Point | None = None) -> None:
        self._start: Point | None = start
        self._end: Point | None = end
        self._primitives_2d: list[Primitive2D] | None = None
        self._primitives_3d: list[Primitive3D] | None = None

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

    @abstractmethod
    def is_defined_geometry(self) -> bool: ...

    @abstractmethod
    def _build_primitives_2d(self): ...

    @abstractmethod
    def _build_primitives_3d(self): ...

    def get_primitives_2d(self) -> list[Primitive2D]:
        if self._primitives_2d is None:
            self._build_primitives_2d()
        return self._primitives_2d

    def get_primitives_3d(self) -> list[Primitive3D]:
        if self._primitives_3d is None:
            self._build_primitives_3d()
        return self._primitives_3d

    @abstractmethod
    def to_json(self) -> dict[str, Any]: ...

    @classmethod
    @abstractmethod
    def from_json(cls: type[T], data: dict[str, Any]) -> T: ...
