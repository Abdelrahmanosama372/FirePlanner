"""Placement resolver to calculate geometric transforms from junction nodes."""

from __future__ import annotations

from copy import deepcopy
from math import pi, isclose, radians

from fireplanner.firecomponent import SteelDims
from fireplanner.geometry.components import (
    GeometricComponent,
    GeometricElbow,
    GeometricReducer,
    GeometricTee,
)
from fireplanner.geometry.primitives import Line, Point
from fireplanner.geometry.primitives.transform import Transform2D
from fireplanner.networks.junction import Junction, JunctionType


def wrap_to_pi(angle: float) -> float:
    return (angle + pi) % (2 * pi) - pi


class PlacementResolver:

    def resolve_transform(
        self,
        junction: Junction,
        edge_id_line_map: dict[int, Line],
        edge_pipe_dim_map: dict[int, SteelDims],
        geometric_component: GeometricComponent,
    ) -> Transform2D:
        if isinstance(geometric_component, GeometricTee):
            return self._resolve_tee_connection(
                junction,
                edge_id_line_map,
                edge_pipe_dim_map,
                geometric_component,
            )

        if isinstance(geometric_component, GeometricReducer):
            return self._resolve_reducer_connection(
                junction,
                edge_id_line_map,
                edge_pipe_dim_map,
                geometric_component,
            )

        if isinstance(geometric_component, GeometricElbow):
            return self._resolve_elbow_connection(
                junction,
                edge_id_line_map,
                edge_pipe_dim_map,
                geometric_component,
            )

        raise ValueError(
            f"Unsupported geometric component type: {type(geometric_component).__name__}"
        )

    def _resolve_tee_connection(
        self,
        junction: Junction,
        edge_id_line_map: dict[int, Line],
        edge_pipe_dim_map: dict[int, SteelDims],
        geometric_tee: GeometricTee,
    ) -> Transform2D:
        if junction.junction_type != JunctionType.THREE_WAY:
            raise ValueError(f"Junction {junction.id} is not a three-way junction.")

        main_edge_ids = self._find_collinear_edge_ids(
            junction.connected_edges_ids, edge_id_line_map
        )
        branch_edge_id = next(
            edge_id
            for edge_id in junction.connected_edges_ids
            if edge_id not in main_edge_ids
        )

        branch = deepcopy(edge_id_line_map[branch_edge_id])
        # make sure that branch line point away from junction point
        if branch.end == junction.origin:
            branch.swap_end_points()

        branch_dir = branch.direction()
        main_dir = edge_id_line_map[main_edge_ids[0]].direction()

        if isclose((main_dir + radians(90)), branch_dir, rel_tol=1e-3) or isclose(
            wrap_to_pi(main_dir + radians(90)),
            branch_dir,
            rel_tol=1e-3
            or isclose((-main_dir - radians(90)), branch_dir, rel_tol=1e-3),
        ):
            rotation = main_dir
        elif isclose(wrap_to_pi(main_dir + radians(270)), branch_dir, rel_tol=1e-3):
            # reverse main line vector angle
            rotation = wrap_to_pi(main_dir + pi)

        else:
            raise ValueError(
                f"Could not find tee transform rotation for geometric tee component main direction: {main_dir}, branch direction: {branch_dir}",
            )

        return Transform2D(
            origin=junction.origin,
            rotation=rotation,
        )

    def _resolve_reducer_connection(
        self,
        junction: Junction,
        edge_id_line_map: dict[int, Line],
        edge_pipe_dim_map: dict[int, SteelDims],
        geometric_reducer: GeometricReducer,
    ) -> Transform2D:
        # reducer tranform is choosen so that at angle 0.
        # the tranform is at reducer center, smaller diameter end is
        # on left side and large diameter end is on right side

        # current implementation places reducer at 25cm
        # from end of the smaller pipe

        collinear_edge_ids = self._find_collinear_edge_ids(
            junction.connected_edges_ids, edge_id_line_map
        )
        first_edge_id, second_edge_id = collinear_edge_ids
        first_diameter = edge_pipe_dim_map[first_edge_id]
        second_diameter = edge_pipe_dim_map[second_edge_id]

        if first_diameter.value >= second_diameter.value:
            large_edge_id, small_edge_id = first_edge_id, second_edge_id
        else:
            large_edge_id, small_edge_id = second_edge_id, first_edge_id

        small_edge_line = deepcopy(edge_id_line_map[small_edge_id])
        large_edge_line = deepcopy(edge_id_line_map[large_edge_id])

        if not small_edge_line.end == junction.origin:
            small_edge_line.swap_end_points()

        if large_edge_line.end == junction.origin:
            large_edge_line.swap_end_points()

        return Transform2D(
            origin=small_edge_line.point_from_end(250.0),
            rotation=small_edge_line.direction(),
        )

    def _resolve_elbow_connection(
        self,
        junction: Junction,
        edge_id_line_map: dict[int, Line],
        _edge_pipe_dim_map: dict[int, SteelDims],
        geometric_elbow: GeometricElbow,
    ) -> Transform2D:
        # elbows here are assumed to have first and second edges of same SteelDims
        # no need now for reducing elbows but can be supported later
        if junction.junction_type != JunctionType.TWO_WAY:
            raise ValueError(
                f"resolving elbow connection: Junction {junction.id} is not a two-way junction."
            )
        first_line_id = junction.connected_edges_ids[0]
        second_line_id = junction.connected_edges_ids[1]

        first_line = deepcopy(edge_id_line_map[first_line_id])
        second_line = deepcopy(edge_id_line_map[second_line_id])

        if not first_line.end == junction.origin:
            first_line.swap_end_points()

        if second_line.end == junction.origin:
            second_line.swap_end_points()

        transform = Transform2D(origin=junction.origin, rotation=0.0)
        first_line_dir = first_line.direction()
        second_line_dir = second_line.direction()
        if (
            isclose((first_line_dir + radians(90)), second_line_dir, rel_tol=1e-3)
            or isclose(
                wrap_to_pi(first_line_dir + radians(90)),
                second_line_dir,
                rel_tol=1e-3,
            )
            or isclose((-first_line_dir - radians(90)), second_line_dir, rel_tol=1e-3)
        ):
            rotation = second_line.direction() + radians(180)
            transform.angle = rotation
        else:
            rotation = first_line.direction()
            transform.angle = rotation

        transform_offset = -geometric_elbow.center_to_end
        transform.translate_local(dx=transform_offset, dy=transform_offset)

        return transform

    def _find_collinear_edge_ids(
        self, edge_ids: list[int], edge_id_line_map: dict[int, Line]
    ) -> list[int]:
        best_pair: list[int] | None = None
        best_angle = float("inf")

        for first_index in range(len(edge_ids)):
            for second_index in range(first_index + 1, len(edge_ids)):
                first_line = edge_id_line_map[edge_ids[first_index]]
                second_line = edge_id_line_map[edge_ids[second_index]]
                angle = min(
                    first_line.angle_to(second_line),
                    abs(180.0 - first_line.angle_to(second_line)),
                )
                if angle < best_angle:
                    best_angle = angle
                    best_pair = [edge_ids[first_index], edge_ids[second_index]]

        if best_pair is None:
            raise ValueError(
                "Could not find collinear pair of edges for tee placement."
            )

        return best_pair
