from __future__ import annotations

from copy import deepcopy
from math import pi

from fireplanner.geometry.components.base import ViewType
from fireplanner.geometry.primitives.transform import Transform2D
from fireplanner.networks.placement.assembly import PlacementAssembly
from fireplanner.networks.placement.context import PlacementContext
from fireplanner.networks.placement.rules import PlacementRules
from fireplanner.networks.placement.strategy.base import PlacementStrategy
from fireplanner.networks.placement.strategy.single_reducer import (
    SingleReducerPlacementStrategy,
)


class DoubleElbowPlacementStrategy(PlacementStrategy):
    def _build(
        self,
        placement_assembly: PlacementAssembly,
        placement_rules: PlacementRules,
    ) -> dict[int, PlacementContext]:
        elbows = placement_assembly.components.elbows()
        reducers = placement_assembly.components.reducers()
        if len(elbows) != 2:
            raise ValueError("DoubleElbowPlacementStrategy expects two elbows.")
        if len(placement_assembly.run_pipes) != 2:
            raise ValueError("DoubleElbowPlacementStrategy expects two run pipes.")
        if len(reducers) > 1:
            raise ValueError(
                "DoubleElbowPlacementStrategy supports at most one reducer."
            )

        contexts: dict[int, PlacementContext] = {}
        elevations = [pipe.edge_info.elevation for pipe in placement_assembly.run_pipes]

        for elbow, pipe, elevation in zip(
            elbows,
            placement_assembly.run_pipes,
            elevations,
        ):
            line = deepcopy(pipe.edge_info.line)
            if line.start != placement_assembly.origin:
                line.swap_end_points()

            contexts[id(elbow)] = PlacementContext(
                transform=Transform2D(
                    origin=placement_assembly.origin,
                    rotation=line.direction() - pi / 2,
                ),
                view_type=ViewType.PLAN,
                z_index=2 if elevation == max(elevations) else 1,
            )

        if reducers:
            contexts.update(
                SingleReducerPlacementStrategy(
                    placement_assembly,
                    placement_rules,
                )._build(placement_assembly, placement_rules)
            )

        return contexts
