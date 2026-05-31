from __future__ import annotations

import logging
from dataclasses import dataclass
from math import atan2, sqrt
from typing import Any

from fireplanner.geometry.primitives import Arc, Circle, Line, Rectangle
from fireplanner.geometry.primitives.line import LineType
from fireplanner.geometry.unit_converter import GeometryUnitConverter
from fireplanner.networks.geometry_network import GeometryNetwork
from fireplanner.resolvers import DraftingScene
from fireplanner.units import LengthUnit, LengthUnitConverter

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


@dataclass(frozen=True)
class DimensionStyleConfig:
    name: str


@dataclass(frozen=True)
class DimensionsConfig:
    enabled: bool = False
    unit: LengthUnit = LengthUnit.METER
    style: DimensionStyleConfig = DimensionStyleConfig(name="STANDARD")
    offset_mm: float = 500.0


@dataclass(frozen=True)
class AnnotationLayerConfig:
    name: str = ""
    color: str | None = None


@dataclass(frozen=True)
class CopLabelConfig:
    enabled: bool = False
    unit: LengthUnit = LengthUnit.METER


@dataclass(frozen=True)
class PipeDimensionLabelConfig:
    enabled: bool = False


@dataclass(frozen=True)
class PipeLabelsConfig:
    cop: CopLabelConfig = CopLabelConfig()
    pipe_dimension: PipeDimensionLabelConfig = PipeDimensionLabelConfig()
    diameter_offset_mm: float = 200.0
    cop_offset_mm: float = 350.0


@dataclass(frozen=True)
class AnnotationsConfig:
    layer: AnnotationLayerConfig = AnnotationLayerConfig()
    pipe_labels: PipeLabelsConfig = PipeLabelsConfig()
    text_height: float = 125.0


@dataclass(frozen=True)
class OutputAnnotationConfig:
    dimensions: DimensionsConfig = DimensionsConfig()
    annotations: AnnotationsConfig = AnnotationsConfig()


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
            entities: list[Any] = []
            for edge in primitive.edges():
                rect_line = GeometryUnitConverter.line_to_unit(
                    edge,
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

    def ensure_dimension_style_exists(self, style_name: str) -> None:
        doc = getattr(self._acad, "doc", None)
        if doc is None or not hasattr(doc, "DimStyles"):
            raise ValueError("Unable to access AutoCAD dimension styles collection.")
        dim_styles = doc.DimStyles
        for style in dim_styles:
            if getattr(style, "Name", "") == style_name:
                return
        raise ValueError(
            f"AutoCAD dimension style '{style_name}' does not exist. Please create it first."
        )

    def write_text_annotation(
        self,
        text: str,
        position_mm: Any,
        rotation_rad: float,
        layer_name: str,
        text_height_mm: float,
    ) -> Any:
        try:
            from pyautocad import APoint
        except ImportError as exc:
            raise ImportError(
                "pyautocad must be installed to write text annotations."
            ) from exc

        position = GeometryUnitConverter.point_to_unit(
            point=position_mm,
            from_unit=LengthUnit.MILLIMETER,
            to_unit=self._drawing_unit,
        )
        text_height = LengthUnitConverter.convert(
            text_height_mm,
            from_unit=LengthUnit.MILLIMETER,
            to_unit=self._drawing_unit,
        )
        entity = self._acad.model.AddText(
            text, APoint(position.to_list3d()), text_height
        )
        self._set_attr(entity, "Rotation", rotation_rad)
        if layer_name:
            self._set_attr(entity, "Layer", layer_name)
        return entity

    def write_aligned_dimension(
        self,
        start_mm: Any,
        end_mm: Any,
        offset_point_mm: Any,
        style_name: str,
    ) -> Any:
        try:
            from pyautocad import APoint
        except ImportError as exc:
            raise ImportError(
                "pyautocad must be installed to write dimensions."
            ) from exc

        start = GeometryUnitConverter.point_to_unit(
            point=start_mm,
            from_unit=LengthUnit.MILLIMETER,
            to_unit=self._drawing_unit,
        )
        end = GeometryUnitConverter.point_to_unit(
            point=end_mm,
            from_unit=LengthUnit.MILLIMETER,
            to_unit=self._drawing_unit,
        )
        offset = GeometryUnitConverter.point_to_unit(
            point=offset_point_mm,
            from_unit=LengthUnit.MILLIMETER,
            to_unit=self._drawing_unit,
        )
        entity = self._acad.model.AddDimAligned(
            APoint(start.to_list3d()),
            APoint(end.to_list3d()),
            APoint(offset.to_list3d()),
        )
        self._set_attr(entity, "StyleName", style_name)
        return entity
