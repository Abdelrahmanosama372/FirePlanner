from dataclasses import dataclass
from math import isclose, radians

from fireplanner.firecomponent import (
    Elbow,
    SteelConnection,
    SteelDims,
    SteelMaterial,
    SteelSchedule,
    SteelSpecs,
    Tee,
)
from fireplanner.geometry.components import GeometricElbow, GeometricTee
from fireplanner.geometry.components.base import ViewType
from fireplanner.geometry.primitives import (
    Arc,
    Circle,
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
        _regions=[
            Rectangle.from_bounds(point1=Point(x=0, y=0), point2=Point(x=10, y=10))
        ],
    )
    lower = _FakeComponent(
        _primitives=[Line(start=Point(x=-5, y=5), end=Point(x=15, y=5))],
        _regions=[
            Rectangle.from_bounds(point1=Point(x=-5, y=0), point2=Point(x=15, y=10))
        ],
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
        _regions=[
            Rectangle.from_bounds(point1=Point(x=0, y=0), point2=Point(x=10, y=10))
        ],
    )
    low_a = _FakeComponent(
        _primitives=[Line(start=Point(x=-5, y=5), end=Point(x=15, y=5))],
        _regions=[
            Rectangle.from_bounds(point1=Point(x=-5, y=0), point2=Point(x=15, y=10))
        ],
    )
    top_b = _FakeComponent(
        _primitives=[Line(start=Point(x=100, y=0), end=Point(x=110, y=0))],
        _regions=[
            Rectangle.from_bounds(point1=Point(x=100, y=0), point2=Point(x=110, y=10))
        ],
    )
    low_b = _FakeComponent(
        _primitives=[Line(start=Point(x=95, y=5), end=Point(x=115, y=5))],
        _regions=[
            Rectangle.from_bounds(point1=Point(x=95, y=0), point2=Point(x=115, y=10))
        ],
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


def _build_rotated_tee_elbow_scene(tee_z_index: int, elbow_z_index: int):
    tee = GeometricTee(
        Tee(
            run_diameter=SteelDims.DIM_1_INCHES,
            branch_diameter=SteelDims.DIM_1_INCHES,
            material=SteelMaterial.ERW,
            schedule=SteelSchedule.SCD40,
            specs=SteelSpecs.ASTM,
            connection_type=SteelConnection.Grooved,
        )
    )
    elbow = GeometricElbow(
        Elbow(
            diameter=SteelDims.DIM_1_INCHES,
            angle=90.0,
            material=SteelMaterial.ERW,
            schedule=SteelSchedule.SCD40,
            specs=SteelSpecs.ASTM,
            connection_type=SteelConnection.Grooved,
        )
    )

    rotated_transform = Transform2D(origin=Point(x=0, y=0), rotation=radians(45))
    tee.placement_context = PlacementContext(
        transform=rotated_transform,
        view_type=ViewType.PLAN,
        z_index=tee_z_index,
    )
    elbow.placement_context = PlacementContext(
        transform=rotated_transform,
        view_type=ViewType.PLAN,
        z_index=elbow_z_index,
    )

    return DraftingOcclusionResolver().resolve(
        ResolvedAssemblies(
            assemblies=[
                ResolvedAssembly(
                    components=[
                        ResolvedComponent(
                            component=tee, placement_context=tee.placement_context
                        ),
                        ResolvedComponent(
                            component=elbow,
                            placement_context=elbow.placement_context,
                        ),
                    ]
                )
            ]
        )
    )


def test_drafting_occlusion_rotated_tee_above_elbow():
    scene = _build_rotated_tee_elbow_scene(tee_z_index=2, elbow_z_index=1)
    assert len(scene.drawables) == 2

    tee_drawable, elbow_drawable = scene.drawables
    tee_hidden = [p for p in tee_drawable.primitives if p.line_type == LineType.Hidden]
    assert len(tee_hidden) == 0

    elbow_hidden = [
        p for p in elbow_drawable.primitives if p.line_type == LineType.Hidden
    ]
    elbow_visible = [
        p for p in elbow_drawable.primitives if p.line_type != LineType.Hidden
    ]
    assert len(elbow_hidden) == 5
    assert len(elbow_visible) == 4
    assert len([p for p in elbow_hidden if isinstance(p, Circle)]) == 1
    assert len([p for p in elbow_hidden if isinstance(p, Line)]) == 4


def test_drafting_occlusion_rotated_elbow_above_tee():
    scene = _build_rotated_tee_elbow_scene(tee_z_index=1, elbow_z_index=2)
    assert len(scene.drawables) == 2

    tee_drawable, elbow_drawable = scene.drawables
    tee_hidden = [p for p in tee_drawable.primitives if p.line_type == LineType.Hidden]
    tee_visible = [p for p in tee_drawable.primitives if p.line_type != LineType.Hidden]
    assert len(tee_hidden) == 4
    assert len(tee_visible) == 8

    elbow_hidden = [
        p for p in elbow_drawable.primitives if p.line_type == LineType.Hidden
    ]
    elbow_visible = [
        p for p in elbow_drawable.primitives if p.line_type != LineType.Hidden
    ]
    assert len(elbow_hidden) == 0
    assert len(elbow_visible) == 6
