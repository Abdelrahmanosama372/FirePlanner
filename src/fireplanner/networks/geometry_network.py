from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from itertools import chain
from math import pi

from fireplanner.firecomponent import SteelDims
from fireplanner.geometry.components import (
    GeometricComponent,
    GeometricPipe,
    GeometricReducer,
)
from fireplanner.geometry.primitives import Line
from fireplanner.networks.core_network import CoreNetwork
from fireplanner.networks.geometry_mapper import GeometryMapper, GeometryMapperConfig
from fireplanner.networks.model_network import ModelNetwork
from fireplanner.networks.placement_resolver import PlacementResolver


@dataclass(frozen=True)
class GeometryNetworkConfig:
    welded_connection_enabled: bool = False
    welded_connection_min_main_pipe_diameter: SteelDims = SteelDims.DIM_2_INCHES


class GeometryNetwork:
    def __init__(
        self,
        core_network: CoreNetwork,
        model_network: ModelNetwork,
        config: GeometryNetworkConfig | None = None,
        geometry_mapper: GeometryMapper | None = None,
        placement_resolver: PlacementResolver | None = None,
    ) -> None:
        self._core_network = core_network
        self._model_network = model_network
        self._config = config or GeometryNetworkConfig()
        self._geometry_mapper = geometry_mapper or GeometryMapper(
            config=GeometryMapperConfig(
                welded_connection_enabled=self._config.welded_connection_enabled,
                welded_connection_min_main_pipe_diameter=self._config.welded_connection_min_main_pipe_diameter,
            )
        )
        self._placement_resolver = placement_resolver or PlacementResolver()
        self._junction_id_to_component: dict[int, list[GeometricComponent]] = {}
        self._edge_id_to_pipe: dict[int, list[GeometricPipe]] = {}
        self._create_network()

    @property
    def junction_id_to_component(self) -> dict[int, list[GeometricComponent]]:
        return self._junction_id_to_component

    @property
    def edge_id_to_pipe(self) -> dict[int, list[GeometricPipe]]:
        return self._edge_id_to_pipe

    def get_geometric_fire_connections_with_junctions_ids(
        self,
    ) -> dict[int, list[GeometricComponent]]:
        return dict(self._junction_id_to_component)

    def get_geometric_fire_connection_at_junction(
        self, junction_id: int
    ) -> list[GeometricComponent]:
        return self._junction_id_to_component.get(junction_id, [])

    def get_geometric_pipes_with_edges_ids(self) -> dict[int, list[GeometricPipe]]:
        return dict(self._edge_id_to_pipe)

    def get_geometric_pipes(self) -> dict[int, list[GeometricPipe]]:
        return list(chain.from_iterable(self.edge_id_to_pipe.values()))

    def _create_network(self) -> None:
        self._junction_id_to_component = self.construct_nodes()
        self._edge_id_to_pipe = self.construct_edges()

    def construct_nodes(self) -> dict[int, list[GeometricComponent]]:
        geometric_components_map: dict[int, list[GeometricComponent]] = {}
        for assembly in self._model_network.get_junctions_assembly():
            junction_id = assembly.junction_info.junction_id
            fire_connections = assembly.connections
            geometric_components = [
                self._geometry_mapper.get_geometry(connection)
                for connection in fire_connections
            ]

            transformed_geometric_components: list[GeometricComponent] = []

            if len(geometric_components) <= 1:
                transform = self._placement_resolver.resolve_transform(
                    junction_assembly=assembly,
                    geometric_component=geometric_components[0],
                )
                geometric_components[0].transform = transform
                transformed_geometric_components.append(geometric_components[0])
            else:
                geometric_components_with_transform = (
                    self._placement_resolver.group_resolve_transform(
                        junction_assembly=assembly,
                        geometric_components=geometric_components,
                    )
                )
                for component, transform in geometric_components_with_transform:
                    component.transform = transform
                    transformed_geometric_components.append(component)

            geometric_components_map[junction_id] = transformed_geometric_components

        return geometric_components_map

    def construct_edges(self) -> dict[int, list[GeometricPipe]]:
        edge_junction_ids = self._core_network.get_edge_junction_ids()
        edge_id_line_map = self._core_network.get_lines_with_edge_ids()
        geometric_pipes: dict[int, list[GeometricPipe]] = {}

        for edge_id, pipe in self._model_network.get_pipes_with_edges_ids().items():
            geometric_pipe = self._geometry_mapper.get_geometry(pipe)
            if not isinstance(geometric_pipe, GeometricPipe):
                raise TypeError(
                    f"Pipe geometry mapping must return GeometricPipe, got {type(geometric_pipe).__name__}."
                )

            pipe_line: Line = edge_id_line_map[edge_id]
            start_junction_id, end_junction_id = edge_junction_ids[edge_id]

            connections: list[GeometricComponent] = []
            if start_junction_id is not None:
                connections.extend(
                    self.get_geometric_fire_connection_at_junction(start_junction_id)
                )

            if end_junction_id is not None:
                connections.extend(
                    self.get_geometric_fire_connection_at_junction(end_junction_id)
                )

            free_pipe_lines = self.find_free_pipes_lines(pipe_line, connections)

            if len(free_pipe_lines) == 1:
                # no reducer on network edge
                geometric_pipe.start = free_pipe_lines[0].start
                geometric_pipe.end = free_pipe_lines[0].end
                geometric_pipe.transform = (
                    self._placement_resolver.resolve_pipe_transform(geometric_pipe)
                )
                geometric_pipes.setdefault(edge_id, []).append(geometric_pipe)

            elif len(free_pipe_lines) == 2:
                first_line, second_line = free_pipe_lines
                geometric_reducer_on_pipe = next(
                    con
                    for con in connections
                    if isinstance(con, GeometricReducer)
                    and pipe_line.pass_through_point(con.transform.origin)
                )
                reducer_center_line = geometric_reducer_on_pipe.layout_skeleton()[0]
                if reducer_center_line.start in [first_line.start, first_line.end]:
                    first_line_pipe_dim = geometric_reducer_on_pipe.small_diameter
                    second_line_pipe_dim = geometric_reducer_on_pipe.large_diameter
                else:
                    first_line_pipe_dim = geometric_reducer_on_pipe.large_diameter
                    second_line_pipe_dim = geometric_reducer_on_pipe.small_diameter

                geometric_pipe1 = GeometricPipe(
                    pipe, start=first_line.start, end=first_line.end
                )
                geometric_pipe1.diameter = first_line_pipe_dim

                geometric_pipe2 = GeometricPipe(
                    pipe, start=second_line.start, end=second_line.end
                )
                geometric_pipe2.diameter = second_line_pipe_dim

                geometric_pipe1.transform = (
                    self._placement_resolver.resolve_pipe_transform(geometric_pipe1)
                )
                geometric_pipe2.transform = (
                    self._placement_resolver.resolve_pipe_transform(geometric_pipe2)
                )
                geometric_pipes.setdefault(edge_id, []).append(geometric_pipe1)
                geometric_pipes[edge_id].append(geometric_pipe2)
            else:
                raise ValueError(
                    f"Undefined segmentation of pipe line, number of free pipe lines: {len(free_pipe_lines)}"
                )

        return geometric_pipes

    def find_free_pipes_lines(
        self, pipe_line: Line, connections: GeometricComponent
    ) -> list[Line]:
        connections_center_lines: list[Line] = []
        for con in connections:
            connections_center_lines.extend(con.layout_skeleton())

        free_pipe_lines = pipe_line.subtract_lines(connections_center_lines)
        return free_pipe_lines
