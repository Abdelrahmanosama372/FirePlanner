from __future__ import annotations

from copy import deepcopy

from fireplanner.geometry.components import (
    GeometricComponent,
    GeometricPipe,
    GeometricReducer,
)
from fireplanner.geometry.components.base import ViewType
from fireplanner.geometry.primitives import Line
from fireplanner.geometry.primitives.transform import Transform2D
from fireplanner.networks.placement.context import PlacementContext


class PipeTrimmerResolver:
    def resolve(
        self,
        geometric_pipe: GeometricPipe,
        start_connections: list[GeometricComponent],
        end_connections: list[GeometricComponent],
    ) -> list[GeometricPipe]:
        if geometric_pipe.start is None or geometric_pipe.end is None:
            raise ValueError("PipeTrimmerResolver expects pipe start/end to be set.")

        pipe_line = Line(start=geometric_pipe.start, end=geometric_pipe.end)
        all_connections = [*start_connections, *end_connections]

        connections_center_lines: list[Line] = []
        for connection in all_connections:
            connections_center_lines.extend(connection.layout_skeleton())

        free_pipe_lines = pipe_line.subtract_lines(connections_center_lines)
        if len(free_pipe_lines) == 0:
            return []

        # Keep deterministic order along the original edge direction.
        free_pipe_lines = sorted(
            free_pipe_lines, key=lambda line: pipe_line.start.distance(line.start)
        )

        # Preserve current reducer-driven diameter split logic.
        reducer_on_pipe = next(
            (
                connection
                for connection in all_connections
                if isinstance(connection, GeometricReducer)
                and connection.placement_context is not None
                and pipe_line.pass_through_point(
                    connection.placement_context.transform.origin
                )
            ),
            None,
        )

        if reducer_on_pipe is None or len(free_pipe_lines) == 1:
            return (
                [
                    self._build_segment_pipe(
                        geometric_pipe, free_pipe_lines[0], geometric_pipe.diameter
                    )
                ]
                if len(free_pipe_lines) == 1
                else [
                    self._build_segment_pipe(
                        geometric_pipe, line, geometric_pipe.diameter
                    )
                    for line in free_pipe_lines
                ]
            )

        if len(free_pipe_lines) != 2:
            raise ValueError("there is more than one reducer on the pipe !!!")

        first_line, second_line = free_pipe_lines
        reducer_center_line = reducer_on_pipe.layout_skeleton()[0]
        if reducer_center_line.start in [first_line.start, first_line.end]:
            first_dim = reducer_on_pipe.small_diameter
            second_dim = reducer_on_pipe.large_diameter
        else:
            first_dim = reducer_on_pipe.large_diameter
            second_dim = reducer_on_pipe.small_diameter

        return [
            self._build_segment_pipe(geometric_pipe, first_line, first_dim),
            self._build_segment_pipe(geometric_pipe, second_line, second_dim),
        ]

    def _build_segment_pipe(
        self,
        source_pipe: GeometricPipe,
        line: Line,
        diameter,
    ) -> GeometricPipe:
        segment_pipe = deepcopy(source_pipe)
        segment_pipe.start = line.start
        segment_pipe.end = line.end
        segment_pipe.diameter = diameter
        segment_pipe.placement_context = PlacementContext(
            transform=Transform2D(
                origin=segment_pipe.start,
                rotation=Line(
                    start=segment_pipe.start, end=segment_pipe.end
                ).direction(),
            ),
            view_type=ViewType.ELEVATION,
        )
        return segment_pipe
