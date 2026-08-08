from dataclasses import dataclass, field

from fireplanner.geometry.primitives import Line, Point


@dataclass(frozen=True)
class EdgeInfo:
    edge_id: int
    line: Line
    length: float
    sprinkler_count: int
    elevation: float = 0.0


@dataclass(frozen=True)
class JunctionInfo:
    junction_id: int
    origin: Point


@dataclass(frozen=True)
class TwoWayJunctionInfo(JunctionInfo):
    edges: list[EdgeInfo] = field(default_factory=list)
    angle: float = 0.0


@dataclass(frozen=True)
class SprinklerInfo:
    k_factor: float
    temperature: float


@dataclass(frozen=True)
class SprinklerJunctionInfo(TwoWayJunctionInfo):
    sprinkler_info: SprinklerInfo | None = None


@dataclass(frozen=True)
class TerminalSprinklerInfo:
    origin: Point
    edge: EdgeInfo
    sprinkler_info: SprinklerInfo


@dataclass(frozen=True)
class ThreeWayJunctionInfo(JunctionInfo):
    run: list[EdgeInfo] = field(default_factory=list)
    branch: EdgeInfo | None = None


@dataclass(frozen=True)
class FourWayJunctionInfo(JunctionInfo):
    lower_run: list[EdgeInfo] = field(default_factory=list)
    upper_run: list[EdgeInfo] = field(default_factory=list)
