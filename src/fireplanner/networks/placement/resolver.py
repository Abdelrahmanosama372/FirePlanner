from __future__ import annotations

from fireplanner.geometry.components import (
    GeometricComponent,
    GeometricElbow,
    GeometricReducer,
    GeometricTee,
    GeometricWeldedBranch,
)
from fireplanner.networks.junction_assembly import JunctionAssembly
from fireplanner.networks.placement.assembly_builder import PlacementAssemblyBuilder
from fireplanner.networks.placement.strategy import (
    SingleElbowPlacementStrategy,
    SingleReducerPlacementStrategy,
    SingleTeePlacementStrategy,
    TeeElbowRisePlacementStrategy,
    TeeReducerPlacementStrategy,
)
from fireplanner.networks.placement.strategy.base import PlacementStrategy


class PlacementResolver:
    def __init__(
        self, placement_assembly_builder: PlacementAssemblyBuilder | None = None
    ):
        self._placement_assembly_builder = (
            placement_assembly_builder or PlacementAssemblyBuilder()
        )

    def resolve(
        self,
        junction_assembly: JunctionAssembly,
        geometric_components: list[GeometricComponent],
    ) -> PlacementStrategy:
        placement_assembly = self._placement_assembly_builder.build(
            junction_assembly, geometric_components
        )

        if len(placement_assembly.components.items) == 1:
            component = placement_assembly.components.items[0]
            if isinstance(component, (GeometricTee, GeometricWeldedBranch)):
                return SingleTeePlacementStrategy(placement_assembly)
            if isinstance(component, GeometricReducer):
                return SingleReducerPlacementStrategy(
                    placement_assembly, reducer_offset=250
                )
            if isinstance(component, GeometricElbow):
                return SingleElbowPlacementStrategy(placement_assembly)

        if len(placement_assembly.components.reducers()) >= 1 and any(
            isinstance(component, (GeometricTee, GeometricWeldedBranch))
            for component in placement_assembly.components.items
        ):
            return TeeReducerPlacementStrategy(placement_assembly)

        if len(placement_assembly.components.elbow()) == 1 and any(
            isinstance(component, (GeometricTee, GeometricWeldedBranch))
            for component in placement_assembly.components.items
        ):
            return TeeElbowRisePlacementStrategy(placement_assembly)

        raise ValueError(
            "No placement strategy found for provided geometric components"
        )
