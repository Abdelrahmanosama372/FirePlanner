from __future__ import annotations

from fireplanner.geometry.components import (
    GeometricComponent,
    GeometricElbow,
    GeometricHanger,
    GeometricReducer,
    GeometricTee,
    GeometricWeldedBranch,
)
from fireplanner.networks.placement.assembly import PlacementAssembly
from fireplanner.networks.placement.strategy import (
    HangerPlacementStrategy,
    SingleElbowPlacementStrategy,
    SingleReducerPlacementStrategy,
    SingleTeePlacementStrategy,
    TeeElbowRisePlacementStrategy,
    TeeReducerElbowPlacementStrategy,
    TeeReducerPlacementStrategy,
)
from fireplanner.networks.placement.strategy.base import PlacementStrategy


class PlacementResolver:
    def resolve(
        self,
        placement_assembly: PlacementAssembly,
    ) -> PlacementStrategy:
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
            if isinstance(component, GeometricHanger):
                return HangerPlacementStrategy(placement_assembly)

        if len(placement_assembly.components.items) >= 1 and len(
            placement_assembly.components.hangers()
        ) == len(placement_assembly.components.items):
            return HangerPlacementStrategy(placement_assembly)

        if len(placement_assembly.components.reducers()) >= 1 and any(
            isinstance(component, (GeometricTee, GeometricWeldedBranch))
            for component in placement_assembly.components.items
        ):
            if len(placement_assembly.components.elbows()) == 1:
                return TeeReducerElbowPlacementStrategy(placement_assembly)
            else:
                return TeeReducerPlacementStrategy(placement_assembly)

        if len(placement_assembly.components.elbows()) == 1 and any(
            isinstance(component, (GeometricTee, GeometricWeldedBranch))
            for component in placement_assembly.components.items
        ):
            return TeeElbowRisePlacementStrategy(placement_assembly)

        raise ValueError(
            "No placement strategy found for provided geometric components"
        )
