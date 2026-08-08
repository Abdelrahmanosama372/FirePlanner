from __future__ import annotations

from copy import deepcopy
from math import pi

from fireplanner.geometry.components.base import ViewType
from fireplanner.geometry.primitives.transform import Transform2D
from fireplanner.networks.placement.assembly import PlacementAssembly
from fireplanner.networks.placement.context import PlacementContext
from fireplanner.networks.placement.rules import PlacementRules
from fireplanner.networks.placement.strategy.base import PlacementStrategy


class TeeElbowPlacementStrategy(PlacementStrategy):
    def _build(
        self,
        placement_assembly: PlacementAssembly,
        placement_rules: PlacementRules,
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

        branch_line = deepcopy(placement_assembly.branch_pipes[0].edge_info.line)
        if branch_line.start != junction_origin:
            branch_line.swap_end_points()

        branch_dirction = branch_line.direction()
        elbow_transform = Transform2D(
            origin=junction_origin, rotation=branch_dirction - pi / 2
        )
        elbow_view = ViewType.PLAN

        run_elevation = placement_assembly.run_pipes[0].edge_info.elevation
        branch_elevation = placement_assembly.branch_pipes[0].edge_info.elevation

        tee_z_index = 1
        elbow_z_index = 1
        if run_elevation > branch_elevation:
            tee_z_index = 2
        elif branch_elevation > run_elevation:
            elbow_z_index = 2

        contexts[id(tee)] = PlacementContext(
            transform=tee_transform, view_type=tee_view, z_index=tee_z_index
        )
        contexts[id(elbow)] = PlacementContext(
            transform=elbow_transform, view_type=elbow_view, z_index=elbow_z_index
        )

        return contexts
