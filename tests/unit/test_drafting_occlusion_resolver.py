from dataclasses import dataclass
from math import radians

from fireplanner.geometry.components.base import ViewType
from fireplanner.geometry.primitives import (
    Line,
    LineType,
    Point,
    Rectangle,
    Transform2D,
)
from fireplanner.networks.placement.context import PlacementContext
from fireplanner.resolvers import (
    DraftingOcclusionResolver,
    ResolvedAssemblies,
    ResolvedAssembly,
    ResolvedComponent,
)


@dataclass
class _FakeComponent:
    _primitives: list
    _regions: list[Rectangle]

    def get_primitives_2d(self):
        return list(self._primitives)

    def occupied_regions(self):
        return list(self._regions)


def test_drafting_occlusion_resolver_hides_lower_component_segments():
    top = _FakeComponent(
        _primitives=[Line(start=Point(x=0, y=5), end=Point(x=10, y=5))],
        _regions=[Rectangle(point1=Point(x=0, y=0), point2=Point(x=10, y=10))],
    )
    lower = _FakeComponent(
        _primitives=[Line(start=Point(x=-5, y=5), end=Point(x=15, y=5))],
        _regions=[Rectangle(point1=Point(x=-5, y=0), point2=Point(x=15, y=10))],
    )

    assemblies = ResolvedAssemblies(
        assemblies=[
            ResolvedAssembly(
                components=[
                    ResolvedComponent(
                        component=top,
                        placement_context=PlacementContext(
                            transform=Transform2D(
                                origin=Point(x=0, y=0), rotation=radians(0)
                            ),
                            view_type=ViewType.ELEVATION,
                            z_index=2,
                        ),
                    ),
                    ResolvedComponent(
                        component=lower,
                        placement_context=PlacementContext(
                            transform=Transform2D(
                                origin=Point(x=0, y=0), rotation=radians(0)
                            ),
                            view_type=ViewType.ELEVATION,
                            z_index=1,
                        ),
                    ),
                ]
            )
        ]
    )

    scene = DraftingOcclusionResolver().resolve(assemblies)

    lower_drawable = scene.drawables[1]
    hidden = [p for p in lower_drawable.primitives if p.line_type == LineType.Hidden]
    visible = [p for p in lower_drawable.primitives if p.line_type != LineType.Hidden]
    assert len(hidden) == 1
    assert len(visible) == 2


def test_drafting_occlusion_resolver_resolves_each_assembly_independently():
    top_a = _FakeComponent(
        _primitives=[Line(start=Point(x=0, y=0), end=Point(x=10, y=0))],
        _regions=[Rectangle(point1=Point(x=0, y=0), point2=Point(x=10, y=10))],
    )
    low_a = _FakeComponent(
        _primitives=[Line(start=Point(x=-5, y=5), end=Point(x=15, y=5))],
        _regions=[Rectangle(point1=Point(x=-5, y=0), point2=Point(x=15, y=10))],
    )
    top_b = _FakeComponent(
        _primitives=[Line(start=Point(x=100, y=0), end=Point(x=110, y=0))],
        _regions=[Rectangle(point1=Point(x=100, y=0), point2=Point(x=110, y=10))],
    )
    low_b = _FakeComponent(
        _primitives=[Line(start=Point(x=95, y=5), end=Point(x=115, y=5))],
        _regions=[Rectangle(point1=Point(x=95, y=0), point2=Point(x=115, y=10))],
    )

    assemblies = ResolvedAssemblies(
        assemblies=[
            ResolvedAssembly(
                components=[
                    ResolvedComponent(
                        component=top_a,
                        placement_context=PlacementContext(
                            transform=Transform2D(
                                origin=Point(x=0, y=0), rotation=radians(0)
                            ),
                            view_type=ViewType.ELEVATION,
                            z_index=2,
                        ),
                    ),
                    ResolvedComponent(
                        component=low_a,
                        placement_context=PlacementContext(
                            transform=Transform2D(
                                origin=Point(x=0, y=0), rotation=radians(0)
                            ),
                            view_type=ViewType.ELEVATION,
                            z_index=1,
                        ),
                    ),
                ]
            ),
            ResolvedAssembly(
                components=[
                    ResolvedComponent(
                        component=top_b,
                        placement_context=PlacementContext(
                            transform=Transform2D(
                                origin=Point(x=0, y=0), rotation=radians(0)
                            ),
                            view_type=ViewType.ELEVATION,
                            z_index=2,
                        ),
                    ),
                    ResolvedComponent(
                        component=low_b,
                        placement_context=PlacementContext(
                            transform=Transform2D(
                                origin=Point(x=0, y=0), rotation=radians(0)
                            ),
                            view_type=ViewType.ELEVATION,
                            z_index=1,
                        ),
                    ),
                ]
            ),
        ]
    )

    scene = DraftingOcclusionResolver().resolve(assemblies)

    assert len(scene.drawables) == 4
    hidden_counts = [
        len([p for p in drawable.primitives if p.line_type == LineType.Hidden])
        for drawable in scene.drawables
    ]
    assert hidden_counts.count(1) == 2
