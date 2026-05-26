from __future__ import annotations

from fireplanner.geometry.components.base import ViewType
from fireplanner.geometry.primitives.transform import Transform2D
from fireplanner.networks.placement.assembly import PlacementAssembly
from fireplanner.networks.placement.context import PlacementContext
from fireplanner.networks.placement.strategy.base import PlacementStrategy


class HangerPlacementStrategy(PlacementStrategy):
    def _build(
        self,
        placement_assembly: PlacementAssembly,
    ) -> dict[int, PlacementContext]:
        hangers = placement_assembly.components.hangers()
        if len(hangers) < 1:
            raise ValueError("HangerPlacementStrategy expects at least one hanger.")
        if len(placement_assembly.run_pipes) != 1:
            raise ValueError("HangerPlacementStrategy expects one pipe assembly.")

        pipe_line = placement_assembly.run_pipes[0].edge_info.line
        direction = pipe_line.direction()
        length = pipe_line.length()
        n = len(hangers)
        margin = length / (2.0 * n)

        contexts: dict[int, PlacementContext] = {}
        for idx, hanger in enumerate(hangers):
            offset_from_start = (2 * idx + 1) * margin
            hanger_origin = pipe_line.point_from_start(offset_from_start)
            contexts[id(hanger)] = PlacementContext(
                transform=Transform2D(origin=hanger_origin, rotation=direction),
                view_type=ViewType.ELEVATION,
            )
        return contexts
