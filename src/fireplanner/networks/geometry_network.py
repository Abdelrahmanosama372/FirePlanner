from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from itertools import chain
from math import pi

from fireplanner.firecomponent import SteelDims
from fireplanner.geometry.components import (
    GeometricComponent,
    GeometricHanger,
    GeometricPipe,
    GeometricReducer,
)
from fireplanner.geometry.components.base import ViewType
from fireplanner.geometry.primitives import Line, Transform2D
from fireplanner.networks.core_network import CoreNetwork
from fireplanner.networks.geometry_mapper import GeometryMapper, GeometryMapperConfig
from fireplanner.networks.model_network import ModelNetwork
from fireplanner.networks.placement.assembly_builder import PlacementAssemblyBuilder
from fireplanner.networks.placement.context import PlacementContext
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
        self._placement_assembly_builder = PlacementAssemblyBuilder()
        self._junction_id_to_component: dict[int, list[GeometricComponent]] = {}
        self._edge_id_to_pipe: dict[int, list[GeometricPipe]] = {}
        self._geometric_hangers: list[GeometricHanger] = []
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

    def get_geometric_hangers(self) -> list[GeometricHanger]:
        return list(self._geometric_hangers)

    def _create_network(self) -> None:
        self._junction_id_to_component = self.construct_nodes()
        self._edge_id_to_pipe = self.construct_edges()
        self._geometric_hangers = self.construct_hangers()

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
            if geometric_components:
                placement_assembly = self._placement_assembly_builder.build(
                    assembly, geometric_components
                )
                strategy = self._placement_resolver.resolve(
                    placement_assembly=placement_assembly,
                )
                for component in geometric_components:
                    context = strategy.get_placement_context(component)
                    component.placement_context = context
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
                geometric_pipe.placement_context = PlacementContext(
                    Transform2D(
                        origin=geometric_pipe.start,
                        rotation=Line(
                            start=geometric_pipe.start,
                            end=geometric_pipe.end,
                        ).direction(),
                    ),
                    view_type=ViewType.ELEVATION,
                )
                geometric_pipes.setdefault(edge_id, []).append(geometric_pipe)

            elif len(free_pipe_lines) == 2:
                first_line, second_line = free_pipe_lines
                geometric_reducer_on_pipe = next(
                    con
                    for con in connections
                    if isinstance(con, GeometricReducer)
                    and pipe_line.pass_through_point(
                        con.placement_context.transform.origin
                    )
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

                geometric_pipe1.placement_context = PlacementContext(
                    Transform2D(
                        origin=geometric_pipe1.start,
                        rotation=Line(
                            start=geometric_pipe1.start,
                            end=geometric_pipe1.end,
                        ).direction(),
                    ),
                    view_type=ViewType.ELEVATION,
                )
                geometric_pipe2.placement_context = PlacementContext(
                    Transform2D(
                        origin=geometric_pipe2.start,
                        rotation=Line(
                            start=geometric_pipe2.start,
                            end=geometric_pipe2.end,
                        ).direction(),
                    ),
                    view_type=ViewType.ELEVATION,
                )
                geometric_pipes.setdefault(edge_id, []).append(geometric_pipe1)
                geometric_pipes[edge_id].append(geometric_pipe2)
            else:
                raise ValueError(
                    f"Undefined segmentation of pipe line, number of free pipe lines: {len(free_pipe_lines)}"
                )

        return geometric_pipes

    def construct_hangers(self) -> list[GeometricHanger]:
        geometric_hangers: list[GeometricHanger] = []
        for hanger_assembly in self._model_network.get_hangers_assembly():
            hangers_for_pipe: list[GeometricHanger] = []
            for _ in range(hanger_assembly.hangers_count):
                geometric_hanger = self._geometry_mapper.get_geometry(
                    hanger_assembly.hanger
                )
                if not isinstance(geometric_hanger, GeometricHanger):
                    raise TypeError(
                        "Hanger geometry mapping must return GeometricHanger, "
                        f"got {type(geometric_hanger).__name__}."
                    )
                hangers_for_pipe.append(geometric_hanger)
            placement_assembly = (
                self._placement_assembly_builder.build_from_hanger_assembly(
                    hanger_assembly,
                    hangers_for_pipe,
                )
            )
            strategy = self._placement_resolver.resolve(placement_assembly)
            for geometric_hanger in hangers_for_pipe:
                geometric_hanger.placement_context = strategy.get_placement_context(
                    geometric_hanger
                )
                geometric_hangers.append(geometric_hanger)
        return geometric_hangers

    def find_free_pipes_lines(
        self, pipe_line: Line, connections: GeometricComponent
    ) -> list[Line]:
        connections_center_lines: list[Line] = []
        for con in connections:
            connections_center_lines.extend(con.layout_skeleton())

        free_pipe_lines = pipe_line.subtract_lines(connections_center_lines)
        return free_pipe_lines
