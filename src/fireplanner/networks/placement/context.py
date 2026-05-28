from __future__ import annotations

from dataclasses import dataclass

from fireplanner.geometry.components.base import ViewType
from fireplanner.geometry.primitives.transform import Transform2D


@dataclass
class PlacementContext:
    transform: Transform2D
    view_type: ViewType
    z_index: int = 1
