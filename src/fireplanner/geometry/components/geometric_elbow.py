from __future__ import annotations
from typing import override
from .geometric_component import GeometricComponent
from ..primitives import Point, Primitive2D, Primitive3D
from fireplanner.firecomponent import Elbow
from fireplanner.standards import elbow_90_lr_center_to_end


class GeometricElbow(GeometricComponent):
    def __init__(
        self, elbow: Elbow, start: Point | None = None, end: Point | None = None
    ) -> None:
        self._diameter = elbow.diameter
        self._center_to_end: float = elbow_90_lr_center_to_end(self._diameter)
        super().__init__(start, end)

    @override
    def get_primitives_2d(self) -> list[Primitive2D]: ...

    @override
    def get_primitives_3d(self) -> list[Primitive3D]: ...

    @override
    def to_json(self) -> str: ...

    @classmethod
    @override
    def from_json(cls, data: str) -> GeometricElbow: ...
