from __future__ import annotations

from copy import deepcopy
from math import isclose, radians

from fireplanner.geometry.components import GeometricComponent, GeometricElbow
from fireplanner.geometry.components.base import ViewType
from fireplanner.geometry.primitives.transform import Transform2D
from fireplanner.networks.junction_info import TwoWayJunctionInfo
from fireplanner.networks.placement.assembly import PlacementAssembly
from fireplanner.networks.placement.context import PlacementContext
from fireplanner.networks.placement.strategy.base import PlacementStrategy


def _wrap_to_pi(angle: float) -> float:
    return (angle + 3.141592653589793) % (2 * 3.141592653589793) - 3.141592653589793


class TeeElbowRisePlacementStrategy(PlacementStrategy):
    def _build(
        self,
        placement_assembly: PlacementAssembly,
    ) -> dict[int, PlacementContext]:
        junction_info = placement_assembly.junction_info
        if not isinstance(junction_info, TwoWayJunctionInfo):
            raise ValueError(
                "resolving elbow connection: "
                f"Junction {junction_info.junction_id} is not a two-way junction."
            )

        elbows = placement_assembly.components.elbow()
        if len(elbows) != 1:
            raise ValueError(
                "TeeElbowRisePlacementStrategy expects one elbow component."
            )
        component: GeometricComponent = elbows[0]
        if not isinstance(component, GeometricElbow):
            raise ValueError(
                "TeeElbowRisePlacementStrategy supports elbow components only."
            )

        edge_id_line_map = {
            pipe.edge_info.edge_id: pipe.edge_info.line
            for pipe in placement_assembly.run_pipes
        }
        if placement_assembly.branch_pipe is not None:
            edge_id_line_map[placement_assembly.branch_pipe.edge_info.edge_id] = (
                placement_assembly.branch_pipe.edge_info.line
            )

        first_line_id = junction_info.edges[0].edge_id
        second_line_id = junction_info.edges[1].edge_id

        first_line = deepcopy(edge_id_line_map[first_line_id])
        second_line = deepcopy(edge_id_line_map[second_line_id])

        if first_line.end != junction_info.origin:
            first_line.swap_end_points()

        if second_line.end == junction_info.origin:
            second_line.swap_end_points()

        transform = Transform2D(origin=junction_info.origin, rotation=0.0)
        first_line_dir = first_line.direction()
        second_line_dir = second_line.direction()
        if (
            isclose((first_line_dir + radians(90)), second_line_dir, rel_tol=1e-3)
            or isclose(
                _wrap_to_pi(first_line_dir + radians(90)),
                second_line_dir,
                rel_tol=1e-3,
            )
            or isclose((-first_line_dir - radians(90)), second_line_dir, rel_tol=1e-3)
        ):
            transform.angle = second_line.direction() + radians(180)
        else:
            transform.angle = first_line.direction()

        transform_offset = -component.center_to_end
        transform.translate_local(dx=transform_offset, dy=transform_offset)
        return {
            id(component): PlacementContext(
                transform=transform, view_type=ViewType.ELEVATION
            )
        }
