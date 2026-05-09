from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from fireplanner.networks import (
    CoreNetwork,
    CoreNetworkConfig,
    GeometryNetwork,
    ModelNetwork,
    ModelNetworkConfig,
    PlacementResolver,
    PlacementResolverConfig,
)

from .reader import Reader
from .writer import Writer

if TYPE_CHECKING:
    from pyautocad import Autocad


@dataclass(frozen=True)
class NetworkPipelineResult:
    core_network_config: CoreNetworkConfig
    model_network_config: ModelNetworkConfig
    placement_resolver_config: PlacementResolverConfig
    core_network: CoreNetwork
    model_network: ModelNetwork
    geometry_network: GeometryNetwork


class Pipeline:
    def __init__(self, yaml_string: str, acad: Autocad | Any) -> None:
        self._reader = Reader(yaml_string)
        self._acad = acad

    def build(self) -> list[NetworkPipelineResult]:
        core_network_configs = self._reader.read_core_network_configs(self._acad)
        model_network_config = self._reader.read_model_network_config()
        placement_resolver_config = self._reader.read_placement_resolver_config()

        results: list[NetworkPipelineResult] = []
        for core_network_config in core_network_configs:
            core_network = CoreNetwork(
                sprinkles=core_network_config.sprinkler_blocks,
                lines=core_network_config.ordered_lines(),
            )
            model_network = ModelNetwork(
                core_network=core_network,
                config=model_network_config,
            )
            geometry_network = GeometryNetwork(
                core_network=core_network,
                model_network=model_network,
                placement_resolver=PlacementResolver(placement_resolver_config),
            )
            results.append(
                NetworkPipelineResult(
                    core_network_config=core_network_config,
                    model_network_config=model_network_config,
                    placement_resolver_config=placement_resolver_config,
                    core_network=core_network,
                    model_network=model_network,
                    geometry_network=geometry_network,
                )
            )

        return results

    def build_one(self) -> NetworkPipelineResult:
        results = self.build()
        if len(results) != 1:
            raise ValueError(
                f"Expected exactly one network pipeline result, got {len(results)}."
            )
        return results[0]

    def draw(self) -> list[list[Any]]:
        layer_config = self._reader.read_output_layer_config()
        writer = Writer(acad=self._acad, layer_config=layer_config)
        written_entities_per_network: list[list[Any]] = []
        for result in self.build():
            written_entities_per_network.append(
                writer.write_geometry_network(result.geometry_network)
            )
        return written_entities_per_network
