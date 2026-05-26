from __future__ import annotations

from copy import deepcopy
from math import isclose, pi, radians

from fireplanner.geometry.components.base import ViewType
from fireplanner.geometry.primitives.transform import Transform2D
from fireplanner.networks.placement.assembly import PlacementAssembly
from fireplanner.networks.placement.context import PlacementContext
from fireplanner.networks.placement.strategy.base import PlacementStrategy


class TeeElbowRisePlacementStrategy(PlacementStrategy):
    def _build(
        self,
        placement_assembly: PlacementAssembly,
    ) -> dict[int, PlacementContext]:
        junction_info = placement_assembly.junction_info
        elbow = placement_assembly.components.elbows()[0]
        if len(placement_assembly.components.tees()) == 1:
            tee = placement_assembly.components.tees()[0]
        else:
            tee = placement_assembly.components.weldedbranches()[0]

        contexts: dict[int, PlacementContext] = {}

        junction_origin = junction_info.origin
        run_dirction = placement_assembly.run_pipes[0].edge_info.line.direction()
        tee_transform = Transform2D(origin=junction_origin, rotation=run_dirction)
        tee_view = ViewType.PLAN

        branch_dirction = placement_assembly.branch_pipe.edge_info.line.direction()
        elbow_transform = Transform2D(
            origin=junction_origin, rotation=branch_dirction - pi / 2
        )
        elbow_view = ViewType.PLAN

        contexts[id(tee)] = PlacementContext(
            transform=tee_transform, view_type=tee_view
        )
        contexts[id(elbow)] = PlacementContext(
            transform=elbow_transform, view_type=elbow_view
        )

        return contexts
