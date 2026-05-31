from __future__ import annotations

from fireplanner.geometry.components import GeometricComponent, GeometricPipe
from fireplanner.geometry.primitives import Arc, Circle, Line, Primitive2D
from fireplanner.resolvers.drafting_occlusion_resolver import DrawablePrimitive
from fireplanner.resolvers.primitive_visibility_resolver import (
    PrimitiveVisibilityResolver,
)


class PipePrimitiveOcclusionResolver:
    def __init__(
        self,
        primitive_visibility_resolver: PrimitiveVisibilityResolver | None = None,
    ) -> None:
        self._primitive_visibility_resolver = (
            primitive_visibility_resolver or PrimitiveVisibilityResolver()
        )

    def resolve(
        self,
        pipe: GeometricPipe,
        occluding_components: list[GeometricComponent],
    ) -> DrawablePrimitive:
        primitives: list[Primitive2D] = pipe.get_primitives_2d()

        for component in occluding_components:
            for occupancy_region in component.occupied_regions():
                next_primitives: list[Primitive2D] = []
                for primitive in primitives:
                    if not isinstance(primitive, (Line, Arc, Circle)):
                        next_primitives.append(primitive)
                        continue
                    partition = self._primitive_visibility_resolver.resolve(
                        occupancy_region=occupancy_region,
                        primitive=primitive,
                    )
                    # Pipe trimming behavior: keep visible parts only.
                    next_primitives.extend(partition.visible)
                primitives = next_primitives

        return DrawablePrimitive(primitives=primitives)
