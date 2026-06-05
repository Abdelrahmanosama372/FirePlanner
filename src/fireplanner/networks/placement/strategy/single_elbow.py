from __future__ import annotations

from copy import deepcopy
from math import isclose, radians

from fireplanner.geometry.components.base import ViewType
from fireplanner.geometry.primitives.transform import Transform2D
from fireplanner.networks.placement.assembly import PlacementAssembly
from fireplanner.networks.placement.constants import ANGLE_TOLERANCE_RAD
from fireplanner.networks.placement.context import PlacementContext
from fireplanner.networks.placement.rules import PlacementRules
from fireplanner.networks.placement.strategy.base import PlacementStrategy
from fireplanner.networks.utils import wrap_to_pi


class SingleElbowPlacementStrategy(PlacementStrategy):
    def _build(
        self,
        placement_assembly: PlacementAssembly,
        placement_rules: PlacementRules,
    ) -> dict[int, PlacementContext]:

        # currently, it handles only 90 degrees elbows
        pipe1_line, pipe2_line = deepcopy(
            [pipe_info.edge_info.line for pipe_info in placement_assembly.run_pipes]
        )
        if not pipe1_line.end == placement_assembly.origin:
            pipe1_line.swap_end_points()

        if pipe2_line.end == placement_assembly.origin:
            pipe2_line.swap_end_points()

        elbow = placement_assembly.components.elbows()[0]

        transform = Transform2D(origin=placement_assembly.origin, rotation=0.0)
        pipe1_dir = pipe1_line.direction()
        pipe2_dir = pipe2_line.direction()
        if (
            isclose((pipe1_dir + radians(90)), pipe2_dir, abs_tol=ANGLE_TOLERANCE_RAD)
            or isclose(
                wrap_to_pi(pipe1_dir + radians(90)),
                pipe2_dir,
                abs_tol=ANGLE_TOLERANCE_RAD,
            )
            or isclose(
                (-pipe1_dir - radians(90)),
                pipe2_dir,
                abs_tol=ANGLE_TOLERANCE_RAD,
            )
        ):
            rotation = pipe2_dir + radians(180)
            transform.angle = rotation
        else:
            rotation = pipe1_dir
            transform.angle = rotation

        transform_offset = -elbow.center_to_end
        transform.translate_local(dx=transform_offset, dy=transform_offset)

        return {
            id(elbow): PlacementContext(
                transform=transform, view_type=ViewType.ELEVATION
            )
        }


#
