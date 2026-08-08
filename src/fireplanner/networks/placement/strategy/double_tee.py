from __future__ import annotations

from dataclasses import replace

from fireplanner.geometry.components import GeometricTee, GeometricWeldedBranch
from fireplanner.geometry.components.base import ViewType
from fireplanner.geometry.primitives.transform import Transform2D
from fireplanner.networks.placement.assembly import (
    AssemblyComponents,
    PlacementAssembly,
)
from fireplanner.networks.placement.context import PlacementContext
from fireplanner.networks.placement.rules import PlacementRules
from fireplanner.networks.placement.strategy.base import PlacementStrategy
from fireplanner.networks.placement.strategy.single_reducer import (
    SingleReducerPlacementStrategy,
)


class DoubleTeePlacementStrategy(PlacementStrategy):
    def _build(
        self,
        placement_assembly: PlacementAssembly,
        placement_rules: PlacementRules,
    ) -> dict[int, PlacementContext]:
        tee_like_components = [
            component
            for component in placement_assembly.components.items
            if isinstance(component, (GeometricTee, GeometricWeldedBranch))
        ]
        reducers = placement_assembly.components.reducers()
        if len(tee_like_components) != 2:
            raise ValueError("DoubleTeePlacementStrategy expects two tees.")
        if len(placement_assembly.run_pipes) != 2:
            raise ValueError("DoubleTeePlacementStrategy expects two lower run pipes.")
        if len(placement_assembly.branch_pipes) != 2:
            raise ValueError("DoubleTeePlacementStrategy expects two upper run pipes.")

        lower_tee, upper_tee = tee_like_components
        lower_direction = placement_assembly.run_pipes[0].edge_info.line.direction()
        upper_direction = placement_assembly.branch_pipes[0].edge_info.line.direction()
        contexts = {
            id(lower_tee): PlacementContext(
                transform=Transform2D(
                    origin=placement_assembly.origin,
                    rotation=lower_direction,
                ),
                view_type=ViewType.PLAN,
                z_index=1,
            ),
            id(upper_tee): PlacementContext(
                transform=Transform2D(
                    origin=placement_assembly.origin,
                    rotation=upper_direction,
                ),
                view_type=ViewType.PLAN,
                z_index=2,
            ),
        }

        reducer_pipes = [
            pipe
            for pipe in placement_assembly.run_pipes
            if pipe.diameter != lower_tee.run_diameter
        ]
        reducer_pipes.extend(
            pipe
            for pipe in placement_assembly.branch_pipes
            if pipe.diameter != upper_tee.run_diameter
        )
        if len(reducers) != len(reducer_pipes):
            raise ValueError(
                "Double-tee reducer count does not match the connected pipe diameters."
            )

        for reducer, pipe in zip(reducers, reducer_pipes):
            tee = lower_tee if pipe in placement_assembly.run_pipes else upper_tee
            reducer_assembly = replace(
                placement_assembly,
                run_pipes=[pipe],
                branch_pipes=[],
                components=AssemblyComponents(items=[reducer]),
            )
            tee_offset = (
                0.0 if isinstance(tee, GeometricWeldedBranch) else tee.run_center_to_end
            )
            reducer_rules = replace(
                placement_rules,
                reducer_offset=tee_offset + placement_rules.reducer_offset,
            )
            contexts.update(
                SingleReducerPlacementStrategy(
                    reducer_assembly,
                    reducer_rules,
                )._build(reducer_assembly, reducer_rules)
            )

        return contexts
