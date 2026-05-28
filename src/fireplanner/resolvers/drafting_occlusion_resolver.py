from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from fireplanner.geometry.components import GeometricComponent
from fireplanner.geometry.primitives import Arc, Circle, Line, Primitive2D
from fireplanner.resolvers.primitive_visibility_resolver import (
    PrimitiveVisibilityResolver,
)


class _PlacementWithZIndex(Protocol):
    z_index: int


@dataclass(frozen=True)
class ResolvedComponent:
    component: GeometricComponent
    placement_context: _PlacementWithZIndex


@dataclass(frozen=True)
class ResolvedAssembly:
    components: list[ResolvedComponent]


@dataclass(frozen=True)
class ResolvedAssemblies:
    assemblies: list[ResolvedAssembly]


@dataclass(frozen=True)
class DrawablePrimitive:
    primitives: list[Primitive2D]


@dataclass(frozen=True)
class DraftingScene:
    drawables: list[DrawablePrimitive]


class DraftingOcclusionResolver:
    def __init__(
        self,
        primitive_visibility_resolver: PrimitiveVisibilityResolver | None = None,
    ) -> None:
        self._primitive_visibility_resolver = (
            primitive_visibility_resolver or PrimitiveVisibilityResolver()
        )

    def resolve(self, resolved_assemblies: ResolvedAssemblies) -> DraftingScene:
        drawables: list[DrawablePrimitive] = []
        for assembly in resolved_assemblies.assemblies:
            drawables.extend(self._resolve_assembly(assembly))
        return DraftingScene(drawables=drawables)

    def _resolve_assembly(
        self,
        resolved_assembly: ResolvedAssembly,
    ) -> list[DrawablePrimitive]:
        if not resolved_assembly.components:
            return []

        highest = max(
            resolved_assembly.components,
            key=lambda rc: rc.placement_context.z_index,
        )
        highest_regions = highest.component.occupied_regions()

        drawables: list[DrawablePrimitive] = []
        for resolved_component in resolved_assembly.components:
            component = resolved_component.component
            primitives: list[Primitive2D] = component.get_primitives_2d()

            if (
                resolved_component.placement_context.z_index
                < highest.placement_context.z_index
            ):
                lower_regions = component.occupied_regions()
                intersection_regions = []
                for high_region in highest_regions:
                    for low_region in lower_regions:
                        intersection = high_region.intersection(low_region)
                        if intersection is not None:
                            intersection_regions.append(intersection)

                for intersection_region in intersection_regions:
                    next_primitives: list[Primitive2D] = []
                    for primitive in primitives:
                        if not isinstance(primitive, (Line, Arc, Circle)):
                            next_primitives.append(primitive)
                            continue
                        partition = self._primitive_visibility_resolver.resolve(
                            occupancy_region=intersection_region,
                            primitive=primitive,
                        )
                        next_primitives.extend(partition.visible)
                        next_primitives.extend(partition.hidden)
                    primitives = next_primitives

            drawables.append(DrawablePrimitive(primitives=primitives))

        return drawables
