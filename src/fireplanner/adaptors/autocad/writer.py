from __future__ import annotations

from dataclasses import dataclass
from math import atan2, sqrt
from typing import Any, TYPE_CHECKING

from .utils import lineweight_to_aci, color_name_to_aci

from fireplanner.geometry.primitives import Arc, Line
from fireplanner.geometry.unit_converter import GeometryUnitConverter
from fireplanner.networks.geometry_network import GeometryNetwork
from fireplanner.units import LengthUnit


@dataclass(frozen=True)
class LayerConfig:
    name: str
    color: str | None = None
    line_weight: float | None = None


class Writer:
    def __init__(
        self, acad: Any, layer_config: LayerConfig, drawing_unit: LengthUnit
    ) -> None:
        self._acad = acad
        self._layer_config = layer_config
        self._drawing_unit = drawing_unit

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
            self._apply_layer(entity)
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
            self._apply_layer(entity)
            return [entity]

        return []

    def _apply_layer(self, entity: Any) -> None:
        if self._layer_config.name:
            self._set_attr(entity, "Layer", self._layer_config.name)

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
