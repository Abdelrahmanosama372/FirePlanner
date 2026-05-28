from __future__ import annotations

import logging
from dataclasses import dataclass
from math import atan2, sqrt
from typing import Any

from fireplanner.geometry.primitives import Arc, Circle, Line, Point, Rectangle
from fireplanner.geometry.primitives.line import LineType
from fireplanner.geometry.unit_converter import GeometryUnitConverter
from fireplanner.networks.geometry_network import GeometryNetwork
from fireplanner.resolvers import DraftingScene
from fireplanner.units import LengthUnit

from .utils import color_name_to_aci

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class LayerConfig:
    line_layer_name: str
    centerline_layer_name: str = ""
    centerlines_enabled: bool = False
    line_color: str | None = None
    line_weight: float | None = None
    centerline_color: str | None = None
    centerline_weight: float | None = None


class Writer:
    def __init__(
        self, acad: Any, layer_config: LayerConfig, drawing_unit: LengthUnit
    ) -> None:
        self._acad = acad
        self._layer_config = layer_config
        self._drawing_unit = drawing_unit
        logger.info(
            "AutoCAD writer initialized (line_layer=%s, centerline_layer=%s, output_unit=%s).",
            self._layer_config.line_layer_name,
            self._layer_config.centerline_layer_name,
            self._drawing_unit.value,
        )

    def write_geometry_network(self, geometry_network: GeometryNetwork) -> list[Any]:
        logger.info("Writing geometry network primitives to AutoCAD.")
        created_entities: list[Any] = []

        for pipe in geometry_network.get_geometric_pipes():
            for primitive in pipe.get_primitives_2d():
                if (
                    self._is_auxiliary_line_type(primitive.line_type)
                    and not self._layer_config.centerlines_enabled
                ):
                    continue
                created_entities.extend(self._write_primitive(primitive))

        for (
            components
        ) in (
            geometry_network.get_geometric_fire_connections_with_junctions_ids().values()
        ):
            for component in components:
                for primitive in component.get_primitives_2d():
                    if (
                        self._is_auxiliary_line_type(primitive.line_type)
                        and not self._layer_config.centerlines_enabled
                    ):
                        continue
                    created_entities.extend(self._write_primitive(primitive))

        for hanger in geometry_network.get_geometric_hangers():
            for primitive in hanger.get_primitives_2d():
                if (
                    self._is_auxiliary_line_type(primitive.line_type)
                    and not self._layer_config.centerlines_enabled
                ):
                    continue
                created_entities.extend(self._write_primitive(primitive))

        logger.info("Wrote %d AutoCAD entity(ies).", len(created_entities))
        return created_entities

    def write_drafting_scene(self, drafting_scene: DraftingScene) -> list[Any]:
        created_entities: list[Any] = []
        for drawable in drafting_scene.drawables:
            for primitive in drawable.primitives:
                if (
                    self._is_auxiliary_line_type(primitive.line_type)
                    and not self._layer_config.centerlines_enabled
                ):
                    continue
                created_entities.extend(self._write_primitive(primitive))
        return created_entities

    def _write_primitive(self, primitive: object) -> list[Any]:
        try:
            from pyautocad import APoint
        except ImportError as exc:
            raise ImportError(
                "pyautocad must be installed to write primitive objects."
            ) from exc

        if isinstance(primitive, Line):
            primitive = GeometryUnitConverter.line_to_unit(
                primitive,
                from_unit=LengthUnit.MILLIMETER,
                to_unit=self._drawing_unit,
            )
            entity = self._acad.model.AddLine(
                APoint(primitive.start.to_list3d()),
                APoint(primitive.end.to_list3d()),
            )
            self._apply_layer(entity, primitive)
            return [entity]

        if isinstance(primitive, Circle):
            primitive = GeometryUnitConverter.circle_to_unit(
                primitive,
                from_unit=LengthUnit.MILLIMETER,
                to_unit=self._drawing_unit,
            )
            entity = self._acad.model.AddCircle(
                APoint(primitive.center.to_list3d()),
                primitive.radius,
            )
            self._apply_layer(entity, primitive)
            return [entity]

        if isinstance(primitive, Arc):
            primitive = GeometryUnitConverter.arc_to_unit(
                primitive,
                from_unit=LengthUnit.MILLIMETER,
                to_unit=self._drawing_unit,
            )
            radius = sqrt(
                (primitive.start.x - primitive.center.x) ** 2
                + (primitive.start.y - primitive.center.y) ** 2
            )
            start_angle = atan2(
                primitive.start.y - primitive.center.y,
                primitive.start.x - primitive.center.x,
            )
            end_angle = start_angle + primitive.angle
            entity = self._acad.model.AddArc(
                APoint(primitive.center.to_list3d()),
                radius,
                start_angle,
                end_angle,
            )
            self._apply_layer(entity, primitive)
            return [entity]

        if isinstance(primitive, Rectangle):
            p1 = primitive.point1
            p2 = primitive.point2
            x_min = min(p1.x, p2.x)
            x_max = max(p1.x, p2.x)
            y_min = min(p1.y, p2.y)
            y_max = max(p1.y, p2.y)
            corners = [
                Point(x=x_min, y=y_min),
                Point(x=x_max, y=y_min),
                Point(x=x_max, y=y_max),
                Point(x=x_min, y=y_max),
            ]
            entities: list[Any] = []
            for start, end in zip(corners, corners[1:] + corners[:1]):
                rect_line = GeometryUnitConverter.line_to_unit(
                    Line(start=start, end=end, line_type=primitive.line_type),
                    from_unit=LengthUnit.MILLIMETER,
                    to_unit=self._drawing_unit,
                )
                entity = self._acad.model.AddLine(
                    APoint(rect_line.start.to_list3d()),
                    APoint(rect_line.end.to_list3d()),
                )
                self._apply_layer(entity, rect_line)
                entities.append(entity)
            return entities

        return []

    def _apply_layer(self, entity: Any, primitive: object) -> None:
        is_centerline = isinstance(
            primitive, (Line, Arc, Circle)
        ) and self._is_auxiliary_line_type(primitive.line_type)

        if is_centerline:
            if self._layer_config.centerline_layer_name:
                self._set_attr(
                    entity, "Layer", self._layer_config.centerline_layer_name
                )
            return

        if self._layer_config.line_layer_name:
            self._set_attr(entity, "Layer", self._layer_config.line_layer_name)

    def _is_auxiliary_line_type(self, line_type: LineType) -> bool:
        return line_type in {LineType.CenterLine, LineType.Hidden}

    def _apply_color(self, entity: Any, color: str) -> None:
        color_index: int | None = color_name_to_aci(color)
        if color_index is not None:
            self._set_attr(entity, "Color", color_index)

    def _set_attr(self, obj: Any, attr_name: str, value: Any) -> None:
        for candidate in {
            attr_name,
            attr_name.lower(),
            attr_name.upper(),
        }:
            if hasattr(obj, candidate):
                setattr(obj, candidate, value)
                return
