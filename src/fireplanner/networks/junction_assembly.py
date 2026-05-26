from __future__ import annotations

from dataclasses import dataclass, field

from fireplanner.firecomponent import SteelDims
from fireplanner.firecomponent.fitting.fireconnection import FireConnection
from fireplanner.firecomponent.fitting.hanger import Hanger
from fireplanner.firecomponent.pipe import Pipe
from fireplanner.networks.junction_info import EdgeInfo, JunctionInfo


@dataclass(frozen=True)
class PipeAssembly:
    edge_info: EdgeInfo
    diameter: SteelDims
    pipe: Pipe | None = None


@dataclass(frozen=True)
class JunctionAssembly:
    junction_info: JunctionInfo
    connections: list[FireConnection] = field(default_factory=list)
    pipes: list[PipeAssembly] = field(default_factory=list)


@dataclass(frozen=True)
class HangerAssembly:
    hanger: Hanger
    pipe: PipeAssembly
    hangers_count: int = 1
