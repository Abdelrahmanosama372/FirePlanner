from __future__ import annotations

from dataclasses import dataclass
from math import atan2, sqrt
from typing import Any

from fireplanner.geometry.primitives import Arc, Line, Point
from fireplanner.networks.geometry_network import GeometryNetwork


@dataclass(frozen=True)
class LayerConfig:
    name: str
    color: str | None = None
    line_weight: float | None = None


class Writer:
    def __init__(self, acad: Any, layer_config: LayerConfig) -> None:
        self._acad = acad
        self._layer_config = layer_config

    def write_geometry_network(self, geometry_network: GeometryNetwork) -> list[Any]:
        created_entities: list[Any] = []

        for pipe in geometry_network.get_geometric_pipes_with_edges_ids().values():
            for primitive in pipe.get_primitives_2d():
                created_entities.extend(self._write_primitive(primitive))

        for (
            component
        ) in (
            geometry_network.get_geometric_fire_connections_with_junctions_ids().values()
        ):
            for primitive in component.get_primitives_2d():
                created_entities.extend(self._write_primitive(primitive))

        return created_entities

    def _write_primitive(self, primitive: object) -> list[Any]:
        if isinstance(primitive, Line):
            entity = self._acad.model.AddLine(
                self._point3d(primitive.start),
                self._point3d(primitive.end),
            )
            self._apply_layer_properties(entity)
            return [entity]

        if isinstance(primitive, Arc):
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
                self._point3d(primitive.center),
                radius,
                start_angle,
                end_angle,
            )
            self._apply_layer_properties(entity)
            return [entity]

        return []

    def _apply_layer_properties(self, entity: Any) -> None:
        if self._layer_config.name:
            self._set_attr(entity, "Layer", self._layer_config.name)
        if self._layer_config.line_weight is not None:
            # AutoCAD COM expects hundredths of mm for lineweight.
            self._set_attr(
                entity, "Lineweight", int(round(self._layer_config.line_weight * 100))
            )
        if self._layer_config.color is not None:
            self._apply_color(entity, self._layer_config.color)

    def _apply_color(self, entity: Any, color: str) -> None:
        color_index = self._color_name_to_aci(color)
        if color_index is not None:
            self._set_attr(entity, "Color", color_index)

    def _color_name_to_aci(self, color: str) -> int | None:
        mapping = {
            "red": 1,
            "yellow": 2,
            "green": 3,
            "cyan": 4,
            "blue": 5,
            "magenta": 6,
            "white": 7,
        }
        return mapping.get(color.strip().lower())

    def _set_attr(self, obj: Any, attr_name: str, value: Any) -> None:
        for candidate in {
            attr_name,
            attr_name.lower(),
            attr_name.upper(),
            attr_name[:1].upper() + attr_name[1:],
        }:
            if hasattr(obj, candidate):
                setattr(obj, candidate, value)
                return

    def _point3d(self, point: Point) -> Any:
        point_factory = getattr(self._acad, "APoint")
        return point_factory(point.to_list3d())
