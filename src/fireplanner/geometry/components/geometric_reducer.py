from __future__ import annotations
from typing import Any, List, override
from .geometric_component import GeometricComponent
from ..primitives import Point
from fireplanner.firecomponent import Reducer
from fireplanner.standards import reducer_end_to_end_table


class GeometricReducer(GeometricComponent):
    def __init__(self, reducer: Reducer, start: Point | None = None, end:Point | None = None) -> None:
        self._large_diameter = reducer.large_diameter 
        self._small_diameter = reducer.small_diameter 
        self._end_to_end: float = reducer_end_to_end_table[self._large_diameter]
        super().__init__(start, end)

    def get_primitives_2d(self) -> List[Any]:
        ...

    def get_primitives_3d(self) -> List[Any]:
        ...
    
    @override
    def to_json(self) -> str:
        ... 
 
    @classmethod  
    def from_json(cls, data: str) -> GeometricReducer:
        ...
    
