from __future__ import annotations

from dataclasses import dataclass

from fireplanner.geometry.primitives.transform import Transform2D


@dataclass(frozen=True)
class PlacementContext:
    transform: Transform2D
