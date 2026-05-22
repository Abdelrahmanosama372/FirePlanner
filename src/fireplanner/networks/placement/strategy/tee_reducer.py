from __future__ import annotations

from dataclasses import replace

from fireplanner.geometry.components import (
    GeometricComponent,
    GeometricReducer,
    GeometricTee,
    GeometricWeldedBranch,
)
from fireplanner.networks.placement.assembly import (
    AssemblyComponents,
    PlacementAssembly,
)
from fireplanner.networks.placement.context import PlacementContext
from fireplanner.networks.placement.strategy.base import PlacementStrategy
from fireplanner.networks.placement.strategy.single_reducer import (
    SingleReducerPlacementStrategy,
)
from fireplanner.networks.placement.strategy.single_tee import (
    SingleTeePlacementStrategy,
)


class TeeReducerPlacementStrategy(PlacementStrategy):
    def _build(
        self,
        placement_assembly: PlacementAssembly,
    ) -> dict[int, PlacementContext]:
        tee_like = [
            *placement_assembly.components.tees(),
            *placement_assembly.components.weldedbranch(),
        ]
        if len(tee_like) != 1:
            raise ValueError("Expected one tee component in tee+reducer strategy.")

        tee = tee_like[0]
        contexts = dict(
            SingleTeePlacementStrategy(placement_assembly)._build(placement_assembly)
        )

        if isinstance(tee, GeometricWeldedBranch):
            reducers_offset = 100
        else:
            reducers_offset = tee.run_center_to_end + 100

        reducers = placement_assembly.components.reducers()
        if not reducers:
            raise ValueError("Expected at least one reducer in tee+reducer strategy.")

        used_edge_ids: set[int] = set()
        edge_pipe_dim_map = {
            pipe.edge_info.edge_id: pipe.diameter
            for pipe in placement_assembly.run_pipes
        }
        if placement_assembly.branch_pipe is not None:
            edge_pipe_dim_map[placement_assembly.branch_pipe.edge_info.edge_id] = (
                placement_assembly.branch_pipe.diameter
            )

        all_pipes = list(placement_assembly.run_pipes)
        if placement_assembly.branch_pipe is not None:
            all_pipes.append(placement_assembly.branch_pipe)

        for reducer in reducers:
            reducer_edge_id = next(
                edge_id
                for edge_id, dim in edge_pipe_dim_map.items()
                if dim == reducer.small_diameter and edge_id not in used_edge_ids
            )
            used_edge_ids.add(reducer_edge_id)
            reducer_pipe = next(
                pipe for pipe in all_pipes if pipe.edge_info.edge_id == reducer_edge_id
            )
            reducer_assembly = replace(
                placement_assembly,
                run_pipes=[reducer_pipe],
                branch_pipe=None,
                components=AssemblyComponents(items=[reducer]),
            )
            contexts.update(
                SingleReducerPlacementStrategy(
                    reducer_assembly,
                    reducer_offset=reducers_offset,
                )._build(reducer_assembly)
            )

        return contexts
