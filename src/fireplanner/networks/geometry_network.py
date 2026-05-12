from __future__ import annotations

from fireplanner.geometry.components import GeometricComponent, GeometricPipe
from fireplanner.networks.core_network import CoreNetwork
from fireplanner.networks.geometry_mapper import GeometryMapper
from fireplanner.networks.model_network import ModelNetwork
from fireplanner.networks.placement_resolver import PlacementResolver


class GeometryNetwork:
    def __init__(
        self,
        core_network: CoreNetwork,
        model_network: ModelNetwork,
        geometry_mapper: GeometryMapper | None = None,
        placement_resolver: PlacementResolver | None = None,
    ) -> None:
        self._core_network = core_network
        self._model_network = model_network
        self._geometry_mapper = geometry_mapper or GeometryMapper()
        self._placement_resolver = placement_resolver or PlacementResolver()
        self._junction_id_to_component: dict[int, GeometricComponent] = {}
        self._edge_id_to_pipe: dict[int, GeometricPipe] = {}
        self._create_network()

    @property
    def junction_id_to_component(self) -> dict[int, GeometricComponent]:
        return self._junction_id_to_component

    @property
    def edge_id_to_pipe(self) -> dict[int, GeometricPipe]:
        return self._edge_id_to_pipe

    def get_geometric_fire_connections_with_junctions_ids(
        self,
    ) -> dict[int, GeometricComponent]:
        return dict(self._junction_id_to_component)

    def get_geometric_pipes_with_edges_ids(self) -> dict[int, GeometricPipe]:
        return dict(self._edge_id_to_pipe)

    def _create_network(self) -> None:
        self._junction_id_to_component = self.construct_nodes()
        self._edge_id_to_pipe = self.construct_edges()

    def construct_nodes(self) -> dict[int, GeometricComponent]:
        junctions = self._core_network.get_junctions()
        edge_id_line_map = self._core_network.get_lines_with_edge_ids()
        edge_pipe_dim_map = self._model_network.get_edge_id_to_pipe_diameter_map()

        geometric_components: dict[int, GeometricComponent] = {}
        for (
            junction_id,
            fire_connection,
        ) in self._model_network.get_fire_connections_with_junctions_ids().items():
            junction = junctions[junction_id]
            geometric_component = self._geometry_mapper.get_geometry(fire_connection)
            geometric_component.transform = self._placement_resolver.resolve_transform(
                junction=junction,
                edge_id_line_map=edge_id_line_map,
                edge_pipe_dim_map=edge_pipe_dim_map,
                geometric_component=geometric_component,
            )
            geometric_components[junction_id] = geometric_component

        return geometric_components

    def construct_edges(self) -> dict[int, GeometricPipe]:
        edge_junction_ids = self._core_network.get_edge_junction_ids()
        junctions = self._core_network.get_junctions()
        edge_id_line_map = self._core_network.get_lines_with_edge_ids()
        geometric_pipes: dict[int, GeometricPipe] = {}

        for edge_id, pipe in self._model_network.get_pipes_with_edges_ids().items():
            geometric_pipe = self._geometry_mapper.get_geometry(pipe)
            if not isinstance(geometric_pipe, GeometricPipe):
                raise TypeError(
                    f"Pipe geometry mapping must return GeometricPipe, got {type(geometric_pipe).__name__}."
                )

            line = edge_id_line_map[edge_id]
            start_junction_id, end_junction_id = edge_junction_ids[edge_id]
            geometric_pipe.start = (
                junctions[start_junction_id].origin
                if start_junction_id is not None
                else line.start
            )
            geometric_pipe.end = (
                junctions[end_junction_id].origin
                if end_junction_id is not None
                else line.end
            )
            geometric_pipe.transform = self._placement_resolver.resolve_transform(
                junction=None,
                edge_id_line_map={},
                edge_pipe_dim_map={},
                geometric_component=geometric_pipe,
            )
            geometric_pipes[edge_id] = geometric_pipe

        return geometric_pipes
