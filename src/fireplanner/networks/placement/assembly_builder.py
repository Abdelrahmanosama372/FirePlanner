from __future__ import annotations

from fireplanner.geometry.components import GeometricComponent
from fireplanner.networks.junction_assembly import HangerAssembly, JunctionAssembly
from fireplanner.networks.junction_info import ThreeWayJunctionInfo
from fireplanner.networks.placement.assembly import (
    AssemblyComponents,
    PlacementAssembly,
)


class PlacementAssemblyBuilder:
    def build(
        self,
        junction_assembly: JunctionAssembly,
        geometric_components: list[GeometricComponent],
    ) -> PlacementAssembly:
        junction_info = junction_assembly.junction_info
        pipe_by_edge_id = {
            pipe_assembly.edge_info.edge_id: pipe_assembly
            for pipe_assembly in junction_assembly.pipes
        }

        run_pipes = []
        branch_pipe = None

        if isinstance(junction_info, ThreeWayJunctionInfo):
            run_pipes = [
                pipe_by_edge_id[edge_info.edge_id]
                for edge_info in junction_info.run
                if edge_info.edge_id in pipe_by_edge_id
            ]
            if (
                junction_info.branch is not None
                and junction_info.branch.edge_id in pipe_by_edge_id
            ):
                branch_pipe = pipe_by_edge_id[junction_info.branch.edge_id]
        else:
            run_pipes = list(junction_assembly.pipes)

        return PlacementAssembly(
            junction_info=junction_info,
            origin=junction_info.origin,
            run_pipes=run_pipes,
            branch_pipe=branch_pipe,
            components=AssemblyComponents(items=geometric_components),
        )

    def build_from_hanger_assembly(
        self,
        hanger_assembly: HangerAssembly,
        geometric_components: list[GeometricComponent],
    ) -> PlacementAssembly:
        pipe_assembly = hanger_assembly.pipe
        line = pipe_assembly.edge_info.line
        return PlacementAssembly(
            junction_info=None,
            origin=line.middle_point(),
            run_pipes=[pipe_assembly],
            branch_pipe=None,
            components=AssemblyComponents(items=geometric_components),
        )
