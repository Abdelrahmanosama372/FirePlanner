from __future__ import annotations

from dataclasses import dataclass, field
from multiprocessing.sharedctypes import Value
from pathlib import Path
from typing import Any

import yaml

from fireplanner.firecomponent import (
    Hanger,
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
from fireplanner.geometry.primitives.line import Line
from fireplanner.networks.core_network import CoreNetwork
from fireplanner.networks.junction_assembly import (
    HangerAssembly,
    JunctionAssembly,
    PipeAssembly,
)
from fireplanner.networks.junction_info import (
    EdgeInfo,
    JunctionInfo,
    ThreeWayJunctionInfo,
    TwoWayJunctionInfo,
)
from fireplanner.standards.hanger import find_min_number_of_hangers_for_pipe
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
    fire_connection: list[FireConnection]


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

    def get_fire_connections_with_junctions_ids(
        self,
    ) -> dict[int, list[FireConnection]]:
        return {
            model_node.junction_id: model_node.fire_connection
            for model_node in self.model_nodes
        }

    def get_edge_id_to_pipe_diameter_map(self) -> dict[int, SteelDims]:
        return dict(self._edge_id_to_pipe_dimension)

    def get_junctions_assembly(self) -> list[JunctionAssembly]:
        junction_info_by_id: dict[int, JunctionInfo] = {
            info.junction_id: info for info in self._core_network.get_junctions_info()
        }
        edge_info_by_id: dict[int, EdgeInfo] = {
            info.edge_id: info for info in self._core_network.get_edges_info()
        }
        edge_id_to_pipe = self.get_pipes_with_edges_ids()

        assemblies: list[JunctionAssembly] = []
        for node in self.model_nodes:
            junction_info = junction_info_by_id.get(node.junction_id)
            if junction_info is None:
                continue

            if isinstance(junction_info, TwoWayJunctionInfo):
                edge_infos = junction_info.edges
            elif isinstance(junction_info, ThreeWayJunctionInfo):
                edge_infos = list(junction_info.run)
                if junction_info.branch is not None:
                    edge_infos.append(junction_info.branch)
            else:
                edge_infos = []

            pipes: list[PipeAssembly] = []
            for edge_info in edge_infos:
                pipe = edge_id_to_pipe.get(edge_info.edge_id)
                if pipe is None:
                    continue
                canonical_edge_info = edge_info_by_id.get(edge_info.edge_id, edge_info)
                pipes.append(
                    PipeAssembly(
                        edge_info=canonical_edge_info,
                        diameter=pipe.diameter,
                        pipe=pipe,
                    )
                )

            assemblies.append(
                JunctionAssembly(
                    junction_info=junction_info,
                    connections=node.fire_connection,
                    pipes=pipes,
                )
            )
        return assemblies

    def construct_edges(self) -> list[ModelEdge]:
        edges_info = self._core_network.get_edges_info()
        model_edges: list[ModelEdge] = []
        self._edge_id_to_pipe_dimension = {}

        for info in edges_info:
            pipe = self._create_pipe_for_edge_id(info)
            self._edge_id_to_pipe_dimension[info.edge_id] = pipe.diameter
            model_edges.append(ModelEdge(edge_id=info.edge_id, pipe=pipe))

        return model_edges

    def _create_pipe_for_edge_id(self, edge_info: EdgeInfo) -> Pipe:

        pipe_dimension = find_min_steel_dim_for_sprinklers(
            self.config.hazard,
            edge_info.sprinkler_count,
        )

        return Pipe(
            diameter=pipe_dimension,
            material=self.config.material,
            schedule=self.config.schedule,
            specs=self.config.specs,
            connection_type=self.config.get_connection_type_for_diameter(
                pipe_dimension
            ),
        )

    def construct_nodes(self) -> list[ModelNode]:
        nodes: list[ModelNode] = []

        fire_connections: FireConnection = []

        for junction_info in self._core_network.get_junctions_info():

            if isinstance(junction_info, TwoWayJunctionInfo):
                pipe1_dim, pipe2_dim = [
                    self._edge_id_to_pipe_dimension[edge_info.edge_id]
                    for edge_info in junction_info.edges
                ]

                fire_connections = self._create_fire_connection_for_two_way_junction(
                    pipe1_dim=pipe1_dim,
                    pipe2_dim=pipe2_dim,
                    angle=junction_info.angle,
                )

            elif isinstance(junction_info, ThreeWayJunctionInfo):
                pipe1_dim, pipe2_dim = [
                    self._edge_id_to_pipe_dimension[edge_info.edge_id]
                    for edge_info in junction_info.run
                ]

                branch_dim = self._edge_id_to_pipe_dimension[
                    junction_info.branch.edge_id
                ]

                fire_connections = self._create_fire_connection_for_three_way_junction(
                    run1_dim=pipe1_dim,
                    run2_dim=pipe2_dim,
                    branch_dim=branch_dim,
                )

                if junction_info.run[0].elevation != junction_info.branch.elevation:
                    connection_type = self.config.get_connection_type_for_diameter(
                        branch_dim
                    )
                    fire_connections.append(
                        Elbow(
                            diameter=branch_dim,
                            angle=90,
                            material=self.config.material,
                            schedule=self.config.schedule,
                            specs=self.config.specs,
                            connection_type=connection_type,
                        )
                    )

            else:
                raise ValueError(
                    "Unsupported junction type for model node construction: "
                    f"{junction.junction_type}"
                )

            if len(fire_connections) == 0:
                continue

            nodes.append(
                ModelNode(
                    junction_id=junction_info.junction_id,
                    fire_connection=fire_connections,
                )
            )

        return nodes

    def _create_fire_connection_for_two_way_junction(
        self,
        pipe1_dim: SteelDims,
        pipe2_dim: SteelDims,
        angle: float,
    ) -> list[FireConnection]:
        largest_diameter = max(
            pipe1_dim,
            pipe2_dim,
            key=lambda diameter: diameter.value,
        )

        connection_type = self.config.get_connection_type_for_diameter(largest_diameter)

        if abs(angle) <= 1.0:
            if pipe1_dim == pipe2_dim:
                return []

            return [
                Reducer(
                    diameter1=pipe1_dim,
                    diameter2=pipe2_dim,
                    material=self.config.material,
                    schedule=self.config.schedule,
                    specs=self.config.specs,
                    connection_type=connection_type,
                )
            ]

        return [
            Elbow(
                diameter=largest_diameter,
                angle=angle,
                material=self.config.material,
                schedule=self.config.schedule,
                specs=self.config.specs,
                connection_type=connection_type,
            )
        ]

    def _create_fire_connection_for_three_way_junction(
        self,
        run1_dim: SteelDims,
        run2_dim: SteelDims,
        branch_dim: SteelDims,
    ) -> list[FireConnection]:
        largest_diameter = max(
            run1_dim,
            run2_dim,
            branch_dim,
            key=lambda diameter: diameter.value,
        )

        connection_type = self.config.get_connection_type_for_diameter(largest_diameter)
        fire_connections: list[FireConnection] = []

        if branch_dim <= run1_dim or branch_dim <= run2_dim:
            fire_connections.append(
                Tee(
                    run_diameter=largest_diameter,
                    branch_diameter=branch_dim,
                    material=self.config.material,
                    schedule=self.config.schedule,
                    specs=self.config.specs,
                    connection_type=connection_type,
                )
            )

            if run1_dim != run2_dim:
                fire_connections.append(
                    Reducer(
                        diameter1=run1_dim,
                        diameter2=run2_dim,
                        material=self.config.material,
                        schedule=self.config.schedule,
                        specs=self.config.specs,
                        connection_type=connection_type,
                    )
                )
        else:
            # branch diameter is largest diameter
            fire_connections.extend(
                [
                    Tee(
                        run_diameter=largest_diameter,
                        branch_diameter=largest_diameter,
                        material=self.config.material,
                        schedule=self.config.schedule,
                        specs=self.config.specs,
                        connection_type=connection_type,
                    ),
                    Reducer(
                        diameter1=largest_diameter,
                        diameter2=run1_dim,
                        material=self.config.material,
                        schedule=self.config.schedule,
                        specs=self.config.specs,
                        connection_type=connection_type,
                    ),
                    Reducer(
                        diameter1=largest_diameter,
                        diameter2=run2_dim,
                        material=self.config.material,
                        schedule=self.config.schedule,
                        specs=self.config.specs,
                        connection_type=connection_type,
                    ),
                ]
            )
        return fire_connections

    def get_pipes_assembly(self) -> list[PipeAssembly]:
        edge_id_info_map = {
            info.edge_id: info for info in self._core_network.get_edges_info()
        }

        return [
            PipeAssembly(
                edge_info=edge_id_info_map[edge.edge_id],
                diameter=edge.pipe.diameter,
                pipe=edge.pipe,
            )
            for edge in self._model_edges
        ]

    def get_hangers_assembly(self) -> list[HangerAssembly]:
        hangers: list[HangerAssembly] = []
        for pipe_assembly in self.get_pipes_assembly():
            pipe = pipe_assembly.pipe
            if pipe is None:
                continue
            hanger = Hanger(
                diameter=pipe.diameter,
                material=pipe.material,
                schedule=pipe.schedule,
                specs=pipe.specs,
                connection_type=pipe.connection_type,
            )
            hangers_count = max(
                1,
                find_min_number_of_hangers_for_pipe(
                    pipe_diameter=pipe.diameter,
                    pipe_length=pipe_assembly.edge_info.length,
                ),
            )
            hangers.append(
                HangerAssembly(
                    hanger=hanger,
                    pipe=pipe_assembly,
                    hangers_count=hangers_count,
                )
            )
        return hangers
