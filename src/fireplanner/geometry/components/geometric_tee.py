from __future__ import annotations
from typing import Any, List, override
from .geometric_component import GeometricComponent
from ..primitives import Point
from fireplanner.firecomponent import Tee
from fireplanner.standards import tee_center_dims


class GeometricTee(GeometricComponent):
    def __init__(self, tee: Tee, start: Point | None = None, end:Point | None = None) -> None:
        self._run_diameter = tee.run_diameter 
        self._branch_diameter = tee.branch_diameter 
        self._run_center_to_end, self._branch_center_to_end = tee_center_dims[(self._run_diameter, self._branch_diameter)]
        super().__init__(start, end)

    def get_primitives_2d(self) -> List[Any]:
        ...

    def get_primitives_3d(self) -> List[Any]:
        ...
    
    @override
    def to_json(self) -> str:
        ... 
 
    @classmethod  
    def from_json(cls, data: str) -> GeometricTee:
        ...
    
