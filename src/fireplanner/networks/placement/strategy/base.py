from __future__ import annotations

from abc import ABC, abstractmethod

from fireplanner.geometry.components import GeometricComponent
from fireplanner.networks.placement.assembly import PlacementAssembly
from fireplanner.networks.placement.context import PlacementContext


class PlacementStrategy(ABC):
    def __init__(self, placement_assembly: PlacementAssembly) -> None:
        self._contexts = self._build(placement_assembly)

    @abstractmethod
    def _build(
        self,
        placement_assembly: PlacementAssembly,
    ) -> dict[int, PlacementContext]:
        raise NotImplementedError

    def get_placement_context(self, component: GeometricComponent) -> PlacementContext:
        context = self._contexts.get(id(component))
        if context is None:
            raise ValueError(
                f"No placement context found for component id={id(component)}."
            )
        return context
