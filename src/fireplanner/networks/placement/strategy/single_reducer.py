from __future__ import annotations

from copy import deepcopy

from fireplanner.firecomponent import SteelDims
from fireplanner.geometry.components import GeometricReducer
from fireplanner.geometry.components.base import ViewType
from fireplanner.geometry.primitives.transform import Transform2D
from fireplanner.networks.placement.assembly import PlacementAssembly
from fireplanner.networks.placement.context import PlacementContext
from fireplanner.networks.placement.strategy.base import PlacementStrategy


class SingleReducerPlacementStrategy(PlacementStrategy):
    def __init__(
        self,
        placement_assembly: PlacementAssembly,
        reducer_offset: float = 250,
    ) -> None:
        self._reducer_offset = reducer_offset
        super().__init__(placement_assembly)

    def _build(
        self,
        placement_assembly: PlacementAssembly,
    ) -> dict[int, PlacementContext]:
        junction_info = placement_assembly.junction_info
        edge_id_line_map = {
            pipe.edge_info.edge_id: pipe.edge_info.line
            for pipe in placement_assembly.run_pipes
        }
        if placement_assembly.branch_pipe is not None:
            edge_id_line_map[placement_assembly.branch_pipe.edge_info.edge_id] = (
                placement_assembly.branch_pipe.edge_info.line
            )
        edge_pipe_dim_map: dict[int, SteelDims] = {
            pipe.edge_info.edge_id: pipe.diameter
            for pipe in placement_assembly.run_pipes
        }
        if placement_assembly.branch_pipe is not None:
            edge_pipe_dim_map[placement_assembly.branch_pipe.edge_info.edge_id] = (
                placement_assembly.branch_pipe.diameter
            )

        reducers = placement_assembly.components.reducers()
        if len(reducers) != 1:
            raise ValueError("SingleReducerPlacementStrategy expects one reducer.")
        component = reducers[0]
        if not isinstance(component, GeometricReducer):
            raise ValueError(
                "SingleReducerPlacementStrategy supports reducer components only."
            )

        small_edge_id = next(
            edge_id
            for edge_id, dim in edge_pipe_dim_map.items()
            if dim == component.small_diameter
        )
        small_edge_line = deepcopy(edge_id_line_map[small_edge_id])

        if small_edge_line.end != junction_info.origin:
            small_edge_line.swap_end_points()

        transform = Transform2D(
            origin=small_edge_line.point_from_end(self._reducer_offset),
            rotation=small_edge_line.direction(),
        )
        return {
            id(component): PlacementContext(
                transform=transform, view_type=ViewType.ELEVATION
            )
        }
