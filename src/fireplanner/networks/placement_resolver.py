"""Placement resolver to calculate geometric transforms from junction nodes."""

from __future__ import annotations

from copy import deepcopy
from math import isclose, pi, radians

from fireplanner.firecomponent import SteelDims
from fireplanner.geometry.components import (
    GeometricComponent,
    GeometricElbow,
    GeometricPipe,
    GeometricReducer,
    GeometricTee,
    GeometricWeldedBranch,
)
from fireplanner.geometry.primitives import Line
from fireplanner.geometry.primitives.transform import Transform2D
from fireplanner.networks.junction import Junction, JunctionType
from fireplanner.networks.utils import find_collinear_edge_ids


def wrap_to_pi(angle: float) -> float:
    return (angle + pi) % (2 * pi) - pi


class PlacementResolver:

    def group_resolve_transform(
        self,
        junction: Junction,
        edge_id_line_map: dict[int, Line],
        edge_pipe_dim_map: dict[int, SteelDims],
        geometric_components: list[GeometricComponent],
    ) -> list[tuple[GeometricComponent, Transform2D]]:

        components_with_transforms: list[tuple[GeometricComponent, Transform2D]] = []

        ########### Temporary implementation to be refactored later #############
        # Possible geometric component groups:
        # - tee + reducer
        # - tee + two reducers

        # Resolve tee first
        tee = next(
            (
                component
                for component in geometric_components
                if isinstance(component, GeometricTee)
            ),
            None,
        )

        if tee is None:
            raise ValueError(
                "Expected a GeometricTee in grouped placement resolving "
                "of geometric components"
            )

        tee_transform = self._resolve_tee_connection(
            junction,
            edge_id_line_map,
            edge_pipe_dim_map,
            tee,
        )

        components_with_transforms.append((tee, tee_transform))
        reducers_offset: float = tee.run_center_to_end

        reducer = next(
            (
                component
                for component in geometric_components
                if isinstance(component, GeometricReducer)
            ),
            None,
        )

        if reducer is None:
            raise ValueError(
                "Expected at least one GeometricReducer in grouped placement resolving "
                "of geometric components"
            )

        first_reducer_line_id, first_reducer_pipe_dim = next(
            (edge_id, dim)
            for edge_id, dim in edge_pipe_dim_map.items()
            if dim == reducer.small_diameter
        )
        temp_edge_pipe_dim_map = {first_reducer_line_id: first_reducer_pipe_dim}

        transform = self.resolve_transform(
            junction,
            edge_id_line_map,
            temp_edge_pipe_dim_map,
            reducer,
            reducers_offset,
        )

        components_with_transforms.append((reducer, transform))

        if len(geometric_components) == 3:
            reducer2 = next(
                (
                    component
                    for component in geometric_components
                    if isinstance(component, GeometricReducer) and component != reducer
                ),
                None,
            )

            second_reducer_line_id, second_reducer_pipe_dim = next(
                (edge_id, dim)
                for edge_id, dim in edge_pipe_dim_map.items()
                if dim == reducer2.small_diameter and edge_id != first_reducer_line_id
            )
            temp_edge_pipe_dim_map = {second_reducer_line_id: second_reducer_pipe_dim}

            transform = self.resolve_transform(
                junction,
                edge_id_line_map,
                temp_edge_pipe_dim_map,
                reducer2,
                reducers_offset,
            )

            components_with_transforms.append((reducer, transform))

        # # Resolve remaining components
        # for component in geometric_components:
        #
        #     # Skip tee since already resolved
        #     if component is tee:
        #         continue
        #
        #     transform = self.resolve_transform(
        #         junction,
        #         edge_id_line_map,
        #         edge_pipe_dim_map,
        #         component,
        #         reducers_offset,
        #     )
        #
        #     components_with_transforms.append((component, transform))

        return components_with_transforms

    def resolve_transform(
        self,
        junction: Junction,
        edge_id_line_map: dict[int, Line],
        edge_pipe_dim_map: dict[int, SteelDims],
        geometric_component: GeometricComponent,
        junction_origin_offset: float | None = None,
    ) -> Transform2D:
        if isinstance(geometric_component, (GeometricTee, GeometricWeldedBranch)):
            return self._resolve_tee_connection(
                junction,
                edge_id_line_map,
                edge_pipe_dim_map,
                geometric_component,
            )

        if isinstance(geometric_component, GeometricReducer):
            reducer_offset = junction_origin_offset or 250

            return self._resolve_reducer_connection(
                junction,
                edge_id_line_map,
                edge_pipe_dim_map,
                geometric_component,
                reducer_offset,
            )

        if isinstance(geometric_component, GeometricElbow):
            return self._resolve_elbow_connection(
                junction,
                edge_id_line_map,
                edge_pipe_dim_map,
                geometric_component,
            )
        if isinstance(geometric_component, GeometricPipe):
            return self._resolve_pipe_transform(geometric_component)

        raise ValueError(
            f"Unsupported geometric component type: {type(geometric_component).__name__}"
        )

    def _resolve_pipe_transform(self, geometric_pipe: GeometricPipe) -> Transform2D:
        if geometric_pipe.start is None or geometric_pipe.end is None:
            raise ValueError("Cannot resolve pipe transform without start/end points.")
        line = Line(start=geometric_pipe.start, end=geometric_pipe.end)
        return Transform2D(origin=geometric_pipe.start, rotation=line.direction())

    def _resolve_tee_connection(
        self,
        junction: Junction,
        edge_id_line_map: dict[int, Line],
        edge_pipe_dim_map: dict[int, SteelDims],
        geometric_tee: GeometricTee | GeometricWeldedBranch,
    ) -> Transform2D:
        if junction.junction_type != JunctionType.THREE_WAY:
            raise ValueError(f"Junction {junction.id} is not a three-way junction.")

        main_edge_ids = find_collinear_edge_ids(edge_id_line_map)
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

        if (
            isclose((main_dir + radians(90)), branch_dir, rel_tol=1e-3)
            or isclose(wrap_to_pi(main_dir + radians(90)), branch_dir, rel_tol=1e-3)
            or isclose((-main_dir - radians(90)), branch_dir, rel_tol=1e-3)
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
        reducers_offset: float,
    ) -> Transform2D:
        # reducer tranform is choosen so that at angle 0.
        # the tranform is at reducer center, smaller diameter end is
        # on left side and large diameter end is on right side

        small_edge_id = next(
            edge_id
            for edge_id, dim in edge_pipe_dim_map.items()
            if dim == geometric_reducer.small_diameter
        )
        small_edge_line = deepcopy(edge_id_line_map[small_edge_id])

        if not small_edge_line.end == junction.origin:
            small_edge_line.swap_end_points()

        return Transform2D(
            origin=small_edge_line.point_from_end(reducers_offset),
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
