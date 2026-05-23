from __future__ import annotations

from math import pi

from fireplanner.geometry.components.base import ViewType
from fireplanner.geometry.components.geometric_component import GeometricComponent
from fireplanner.geometry.primitives.transform import Transform2D
from fireplanner.networks.placement.assembly import PlacementAssembly
from fireplanner.networks.placement.context import PlacementContext
from fireplanner.networks.placement.strategy.base import PlacementStrategy
from fireplanner.networks.placement.strategy.tee_reducer import (
    TeeReducerPlacementStrategy,
)


class TeeReducerElbowPlacementStrategy(PlacementStrategy):
    def _build(
        self,
        placement_assembly: PlacementAssembly,
    ) -> dict[int, PlacementContext]:
        junction_info = placement_assembly.junction_info
        junction_origin = junction_info.origin
        elbow = placement_assembly.components.elbow()[0]

        tee_reducers: list[GeometricComponent] = []
        tee_reducers.extend(placement_assembly.components.reducers())
        tee_reducers.extend(placement_assembly.components.tees())

        contexts: dict[int, PlacementContext] = TeeReducerPlacementStrategy._build(
            placement_assembly
        )

        branch_dirction = placement_assembly.branch_pipe.edge_info.line.direction()
        elbow_transform = Transform2D(
            origin=junction_origin, rotation=branch_dirction - pi / 2
        )
        elbow_view = ViewType.PLAN

        contexts[id(elbow)] = PlacementContext(
            transform=elbow_transform, view_type=elbow_view
        )

        return contexts
