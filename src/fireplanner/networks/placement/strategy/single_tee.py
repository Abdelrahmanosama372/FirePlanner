from __future__ import annotations

from copy import deepcopy
from math import isclose, pi, radians

from fireplanner.geometry.components import (
    GeometricTee,
    GeometricWeldedBranch,
)
from fireplanner.geometry.components.base import ViewType
from fireplanner.geometry.primitives import Line
from fireplanner.geometry.primitives.transform import Transform2D
from fireplanner.networks.junction_info import JunctionInfo, ThreeWayJunctionInfo
from fireplanner.networks.placement.assembly import PlacementAssembly
from fireplanner.networks.placement.constants import ANGLE_TOLERANCE_RAD
from fireplanner.networks.placement.context import PlacementContext
from fireplanner.networks.placement.rules import PlacementRules
from fireplanner.networks.placement.strategy.base import PlacementStrategy
from fireplanner.networks.utils import find_collinear_edge_ids, wrap_to_pi


class SingleTeePlacementStrategy(PlacementStrategy):
    def _build(
        self,
        placement_assembly: PlacementAssembly,
        placement_rules: PlacementRules,
    ) -> dict[int, PlacementContext]:
        junction_info: JunctionInfo = placement_assembly.junction_info
        edge_id_line_map: dict[int, Line] = {
            pipe.edge_info.edge_id: pipe.edge_info.line
            for pipe in placement_assembly.run_pipes
        }
        for branch_pipe in placement_assembly.branch_pipes:
            edge_id_line_map[branch_pipe.edge_info.edge_id] = branch_pipe.edge_info.line

        tees = placement_assembly.components.tees()
        welded = placement_assembly.components.weldedbranches()
        tee_like_components = [*tees, *welded]
        if len(tee_like_components) != 1:
            raise ValueError(
                "SingleTeePlacementStrategy expects one tee-like component."
            )

        component = tee_like_components[0]
        if not isinstance(component, (GeometricTee, GeometricWeldedBranch)):
            raise ValueError("SingleTeePlacementStrategy supports tee components only.")

        if not isinstance(junction_info, ThreeWayJunctionInfo):
            raise ValueError(
                f"Junction {junction_info.junction_id} is not a three-way junction."
            )

        main_edge_ids = find_collinear_edge_ids(edge_id_line_map)
        connected_edge_ids = [edge_info.edge_id for edge_info in junction_info.run]
        if junction_info.branch is not None:
            connected_edge_ids.append(junction_info.branch.edge_id)
        branch_edge_id = next(
            edge_id for edge_id in connected_edge_ids if edge_id not in main_edge_ids
        )

        branch = deepcopy(edge_id_line_map[branch_edge_id])
        if branch.end == junction_info.origin:
            branch.swap_end_points()

        branch_dir = branch.direction()
        main_dir = edge_id_line_map[main_edge_ids[0]].direction()

        if (
            isclose((main_dir + radians(90)), branch_dir, abs_tol=ANGLE_TOLERANCE_RAD)
            or isclose(
                wrap_to_pi(main_dir + radians(90)),
                branch_dir,
                abs_tol=ANGLE_TOLERANCE_RAD,
            )
            or isclose(
                (-main_dir - radians(90)),
                branch_dir,
                abs_tol=ANGLE_TOLERANCE_RAD,
            )
        ):
            rotation = main_dir
        elif isclose(
            wrap_to_pi(main_dir + radians(270)),
            branch_dir,
            abs_tol=ANGLE_TOLERANCE_RAD,
        ):
            rotation = wrap_to_pi(main_dir + pi)
        else:
            raise ValueError(
                "Could not find tee transform rotation for geometric tee component"
            )

        return {
            id(component): PlacementContext(
                transform=Transform2D(
                    origin=junction_info.origin,
                    rotation=rotation,
                ),
                view_type=ViewType.ELEVATION,
            )
        }
