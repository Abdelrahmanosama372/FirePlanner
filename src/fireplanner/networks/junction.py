from dataclasses import dataclass, field
from enum import StrEnum

from fireplanner.geometry.primitives import Point


class JunctionType(StrEnum):
    TWO_WAY = "two_way"
    THREE_WAY = "three_way"
    FOUR_WAY = "four_way"


@dataclass
class Junction:
    id: int
    origin: Point
    junction_type: JunctionType | None
    connected_edges_ids: list[int] = field(default_factory=list)
    angle: float | None = None
    has_sprinkler: bool = False
