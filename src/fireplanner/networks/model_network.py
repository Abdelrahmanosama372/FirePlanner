from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from fireplanner.firecomponent import (
    Pipe,
    SteelConnection,
    SteelDims,
    SteelMaterial,
    SteelSchedule,
    SteelSpecs,
)
from fireplanner.firecomponent.fitting.fireconnection import FireConnection
from fireplanner.firecomponent.fitting.fireconnection.elbow import Elbow
from fireplanner.firecomponent.fitting.fireconnection.reducer import Reducer
from fireplanner.firecomponent.fitting.fireconnection.tee import Tee
from fireplanner.networks.core_network import CoreNetwork
from fireplanner.networks.junction import Junction, JunctionType
from fireplanner.standards.hazard import (
    FireHazard,
    find_min_steel_dim_for_sprinklers,
)


@dataclass
class ModelNetworkConfig:
    compute_pipe_dimensions: bool = True
    layer_name_to_pipe_dimension: dict[str, float] = field(default_factory=dict)
    hazard: FireHazard = FireHazard.LIGHT
    material: SteelMaterial = SteelMaterial.ERW
    schedule: SteelSchedule = SteelSchedule.SCD40
    specs: SteelSpecs = SteelSpecs.ASTM
    connection_type_by_diameter: dict[SteelDims, SteelConnection] = field(
        default_factory=dict
    )
    default_connection_type: SteelConnection = SteelConnection.Grooved

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ModelNetworkConfig:
        return cls(
            compute_pipe_dimensions=bool(data.get("compute_pipe_dimensions", True)),
            layer_name_to_pipe_dimension={
                str(layer_name): float(pipe_dimension)
                for layer_name, pipe_dimension in data.get(
                    "layer_name_to_pipe_dimension", {}
                ).items()
            },
            hazard=FireHazard(data.get("hazard", FireHazard.LIGHT)),
            material=SteelMaterial(data.get("material", SteelMaterial.ERW)),
            schedule=SteelSchedule(data.get("schedule", SteelSchedule.SCD40)),
            specs=SteelSpecs(data.get("specs", SteelSpecs.ASTM)),
            connection_type_by_diameter={
                SteelDims(float(diameter)): SteelConnection(connection_type)
                for diameter, connection_type in data.get(
                    "connection_type_by_diameter", {}
                ).items()
            },
            default_connection_type=SteelConnection(
                data.get("default_connection_type", SteelConnection.Grooved)
            ),
        )

    @classmethod
    def from_yaml_string(cls, yaml_string: str) -> ModelNetworkConfig:
        data = yaml.safe_load(yaml_string) or {}
        if not isinstance(data, dict):
            raise ValueError("ModelNetworkConfig YAML must deserialize to a mapping.")
        return cls.from_dict(data)

    @classmethod
    def from_yaml(cls, path: str | Path) -> ModelNetworkConfig:
        with Path(path).open("r", encoding="utf-8") as yaml_file:
            return cls.from_yaml_string(yaml_file.read())

    def get_connection_type_for_diameter(self, diameter: SteelDims) -> SteelConnection:
        return self.connection_type_by_diameter.get(
            diameter,
            self.default_connection_type,
        )


@dataclass
class ModelNode:
    junction_id: int
    fire_connection: FireConnection


@dataclass
class ModelEdge:
    edge_id: int
    pipe: Pipe


class ModelNetwork:
    def __init__(
        self,
        core_network: CoreNetwork,
        config: ModelNetworkConfig | None = None,
    ) -> None:
        self._core_network = core_network
        self._config = config or ModelNetworkConfig()
        self._model_nodes: list[ModelNode] = []
        self._model_edges: list[ModelEdge] = []
        self._edge_id_to_pipe_dimension: dict[int, SteelDims] = {}
        self._create_network(core_network)

    def _create_network(self, core_network: CoreNetwork) -> None:
        self._model_edges = self.construct_edges()
        self._model_nodes = self.construct_nodes()

    @property
    def config(self) -> ModelNetworkConfig:
        return self._config

    @property
    def model_nodes(self) -> list[ModelNode]:
        return self._model_nodes

    @property
    def model_edges(self) -> list[ModelEdge]:
        return self._model_edges

    def get_pipes_with_edges_ids(self) -> dict[int, Pipe]:
        return {model_edge.edge_id: model_edge.pipe for model_edge in self.model_edges}

    def get_fire_connections_with_junctions_ids(self) -> dict[int, FireConnection]:
        return {
            model_node.junction_id: model_node.fire_connection
            for model_node in self.model_nodes
        }

    def get_edge_id_to_pipe_diameter_map(self) -> dict[int, SteelDims]:
        return dict(self._edge_id_to_pipe_dimension)

    def construct_edges(self) -> list[ModelEdge]:
        edges_ids = self._core_network.get_edges_ids()
        model_edges: list[ModelEdge] = []
        self._edge_id_to_pipe_dimension = {}

        for edge_id in edges_ids:
            pipe = self._create_pipe_for_edge_id(edge_id)
            self._edge_id_to_pipe_dimension[edge_id] = pipe.diameter
            model_edges.append(ModelEdge(edge_id=edge_id, pipe=pipe))

        return model_edges

    def _create_pipe_for_edge_id(self, edge_id: int) -> Pipe:
        sprinklers_count = self._core_network.find_edge_sprinkler_count(edge_id)
        if sprinklers_count is None:
            raise ValueError(f"Could not find sprinkler count for edge id {edge_id}.")

        pipe_dimension = find_min_steel_dim_for_sprinklers(
            self.config.hazard,
            sprinklers_count,
        )

        return Pipe(
            diameter=pipe_dimension,
            material=self.config.material,
            schedule=self.config.schedule,
            specs=self.config.specs,
            connection_type=self.config.get_connection_type_for_diameter(pipe_dimension),
        )

    def construct_nodes(self) -> list[ModelNode]:
        return [
            ModelNode(
                junction_id=junction.id,
                fire_connection=fire_connection,
            )
            for junction in self._core_network.get_junctions().values()
            if (fire_connection := self._create_fire_connection_for_junction(junction))
            is not None
        ]

    def _create_fire_connection_for_junction(
        self,
        junction: Junction,
    ) -> FireConnection | None:
        connected_edge_diameters = [
            self._edge_id_to_pipe_dimension[edge_id]
            for edge_id in junction.connected_edges_ids
        ]
        main_connection_type = self.config.get_connection_type_for_diameter(
            max(
                connected_edge_diameters,
                key=lambda diameter: diameter.value,
            )
        )

        if junction.junction_type == JunctionType.TWO_WAY:
            first_diameter, second_diameter = connected_edge_diameters
            if junction.angle is None:
                raise ValueError(
                    f"junction angle is None for junction id: {junction.id}"
                )

            if abs(junction.angle) <= 1.0:
                if first_diameter != second_diameter:
                    return Reducer(
                        diameter1=first_diameter,
                        diameter2=second_diameter,
                        material=self.config.material,
                        schedule=self.config.schedule,
                        specs=self.config.specs,
                        connection_type=main_connection_type,
                    )
                else:
                    return None

            return Elbow(
                diameter=max(
                    connected_edge_diameters,
                    key=lambda diameter: diameter.value,
                ),
                angle=junction.angle,
                material=self.config.material,
                schedule=self.config.schedule,
                specs=self.config.specs,
                connection_type=main_connection_type,
            )

        if junction.junction_type == JunctionType.THREE_WAY:
            run_diameter = max(
                connected_edge_diameters, key=lambda diameter: diameter.value
            )
            branch_diameter = min(
                connected_edge_diameters,
                key=lambda diameter: diameter.value,
            )
            return Tee(
                run_diameter=run_diameter,
                branch_diameter=branch_diameter,
                material=self.config.material,
                schedule=self.config.schedule,
                specs=self.config.specs,
                connection_type=main_connection_type,
            )

        raise ValueError(
            f"Unsupported junction type for model node construction: {junction.junction_type}"
        )
