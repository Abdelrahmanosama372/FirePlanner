from __future__ import annotations

from dataclasses import dataclass, field

from fireplanner.geometry.components import (
    GeometricComponent,
    GeometricElbow,
    GeometricReducer,
    GeometricTee,
    GeometricWeldedBranch,
)
from fireplanner.geometry.primitives.point import Point
from fireplanner.networks.junction_assembly import PipeAssembly
from fireplanner.networks.junction_info import JunctionInfo


@dataclass(frozen=True)
class AssemblyComponents:
    items: list[GeometricComponent] = field(default_factory=list)

    def reducers(self) -> list[GeometricReducer]:
        return [item for item in self.items if isinstance(item, GeometricReducer)]

    def elbow(self) -> list[GeometricElbow]:
        return [item for item in self.items if isinstance(item, GeometricElbow)]

    def tees(self) -> list[GeometricTee]:
        return [item for item in self.items if isinstance(item, GeometricTee)]

    def weldedbranch(self) -> list[GeometricWeldedBranch]:
        return [item for item in self.items if isinstance(item, GeometricWeldedBranch)]


@dataclass(frozen=True)
class PlacementAssembly:
    junction_info: JunctionInfo
    origin: Point
    run_pipes: list[PipeAssembly] = field(default_factory=list)
    branch_pipe: PipeAssembly | None = None
    components: AssemblyComponents = field(default_factory=AssemblyComponents)
