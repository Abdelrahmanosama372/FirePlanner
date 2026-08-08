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
from fireplanner.networks.placement.rules import PlacementRules
from fireplanner.networks.placement.strategy import (
    DoubleElbowPlacementStrategy,
    DoubleTeePlacementStrategy,
    HangerPlacementStrategy,
    SingleElbowPlacementStrategy,
    SingleReducerPlacementStrategy,
    SingleTeePlacementStrategy,
    TeeElbowPlacementStrategy,
    TeeReducerElbowPlacementStrategy,
    TeeReducerPlacementStrategy,
)
from fireplanner.networks.placement.strategy.base import PlacementStrategy


class PlacementResolver:
    def resolve(
        self,
        placement_assembly: PlacementAssembly,
        placement_rules: PlacementRules | None = None,
    ) -> PlacementStrategy:
        placement_rules = placement_rules or PlacementRules()
        if len(placement_assembly.components.items) == 1:
            component = placement_assembly.components.items[0]
            if isinstance(component, (GeometricTee, GeometricWeldedBranch)):
                return SingleTeePlacementStrategy(placement_assembly, placement_rules)
            if isinstance(component, GeometricReducer):
                return SingleReducerPlacementStrategy(
                    placement_assembly,
                    placement_rules,
                )
            if isinstance(component, GeometricElbow):
                return SingleElbowPlacementStrategy(
                    placement_assembly,
                    placement_rules,
                )
            if isinstance(component, GeometricHanger):
                return HangerPlacementStrategy(placement_assembly, placement_rules)

        if len(placement_assembly.components.items) >= 1 and len(
            placement_assembly.components.hangers()
        ) == len(placement_assembly.components.items):
            return HangerPlacementStrategy(placement_assembly, placement_rules)

        tee_like_count = sum(
            isinstance(component, (GeometricTee, GeometricWeldedBranch))
            for component in placement_assembly.components.items
        )
        if tee_like_count == 2 and tee_like_count + len(
            placement_assembly.components.reducers()
        ) == len(placement_assembly.components.items):
            return DoubleTeePlacementStrategy(
                placement_assembly,
                placement_rules,
            )

        if len(placement_assembly.components.elbows()) == 2 and len(
            placement_assembly.components.reducers()
        ) in (0, 1):
            return DoubleElbowPlacementStrategy(
                placement_assembly,
                placement_rules,
            )

        if len(placement_assembly.components.reducers()) >= 1 and any(
            isinstance(component, (GeometricTee, GeometricWeldedBranch))
            for component in placement_assembly.components.items
        ):
            if len(placement_assembly.components.elbows()) == 1:
                return TeeReducerElbowPlacementStrategy(
                    placement_assembly,
                    placement_rules,
                )
            else:
                return TeeReducerPlacementStrategy(placement_assembly, placement_rules)

        if len(placement_assembly.components.elbows()) == 1 and any(
            isinstance(component, (GeometricTee, GeometricWeldedBranch))
            for component in placement_assembly.components.items
        ):
            return TeeElbowPlacementStrategy(placement_assembly, placement_rules)

        raise ValueError(
            "No placement strategy found for provided geometric components"
        )
