from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import yaml

from fireplanner.adaptors.autocad.utils import color_name_to_aci
from fireplanner.firecomponent import (
    SteelConnection,
    SteelDims,
    SteelMaterial,
    SteelSchedule,
    SteelSpecs,
)
from fireplanner.geometry.primitives import Block, Line, Point
from fireplanner.geometry.unit_converter import GeometryUnitConverter
from fireplanner.networks import CoreNetworkConfig, FlowRoute, ModelNetworkConfig
from fireplanner.standards.hazard import FireHazard
from fireplanner.units import LengthUnit
from .writer import LayerConfig

if TYPE_CHECKING:
    from pyautocad import Autocad


@dataclass(frozen=True)
class _LineRecord:
    entity: Any
    line: Line


class Reader:
    def __init__(self, yaml_string: str) -> None:
        self._raw_data = self._load_yaml_string(yaml_string)

    def read_model_network_config(self) -> ModelNetworkConfig:
        firefighting_data = self._mapping(self._raw_data.get("firefighting"))
        steel_data = self._mapping(firefighting_data.get("steel"))
        processing_data = self._mapping(self._raw_data.get("processing"))
        connection_type_data = self._mapping(
            steel_data.get("connnection_type") or steel_data.get("connection_type")
        )

        return ModelNetworkConfig.from_dict(
            {
                "compute_pipe_dimensions": processing_data.get(
                    "compute_pipe_dimensions",
                    True,
                ),
                "hazard": self._parse_hazard(
                    firefighting_data.get("hazard_level", FireHazard.LIGHT)
                ).value,
                "material": self._parse_material(
                    steel_data.get("material", SteelMaterial.ERW)
                ).value,
                "schedule": self._parse_schedule(
                    steel_data.get("schedule", SteelSchedule.SCD40)
                ).value,
                "specs": self._parse_specs(
                    steel_data.get("specs", SteelSpecs.ASTM)
                ).value,
                "connection_type_by_diameter": {
                    str(float(diameter)): self._parse_connection_type(
                        connection_type
                    ).value
                    for diameter, connection_type in connection_type_data.items()
                },
                "default_connection_type": SteelConnection.Grooved.value,
            }
        )

    def read_drawing_length_unit(self) -> LengthUnit:
        drawing_data = self._mapping(
            self._mapping(
                self._mapping(self._raw_data.get("autocad")).get("input")
            ).get("drawing")
        )
        return self._parse_length_unit(drawing_data.get("units", LengthUnit.MILLIMETER))

    def read_core_network_configs(self, acad: Autocad | Any) -> list[CoreNetworkConfig]:
        root_flow_route = self._read_root_flow_route()
        input_data = self._mapping(
            self._mapping(self._raw_data.get("autocad")).get("input")
        )
        drawing_unit = self.read_drawing_length_unit()
        line_network_data = self._mapping(input_data.get("line_network_layer"))
        sprinkler_block_data = self._mapping(input_data.get("sprinkler_blocks"))
        root_identifier = self._mapping(input_data.get("root_line_identifier"))

        line_records = self._read_line_records(
            acad=acad,
            layer_name=str(line_network_data.get("name", "")),
            drawing_unit=drawing_unit,
        )
        root_lines = self._find_root_lines(line_records, root_identifier)
        sprinkler_blocks = self._read_sprinkler_blocks(
            acad=acad,
            sprinkler_block_names=set(sprinkler_block_data.keys()),
            drawing_unit=drawing_unit,
        )
        sprinkler_block_metadata = {
            str(name): self._mapping(data)
            for name, data in sprinkler_block_data.items()
        }

        configs: list[CoreNetworkConfig] = []
        for root_line in root_lines:
            configs.append(
                CoreNetworkConfig(
                    sprinkler_block_data=sprinkler_block_metadata,
                    sprinkler_blocks=list(sprinkler_blocks),
                    lines=[record.line for record in line_records],
                    root_line=root_line,
                    root_flow_route=root_flow_route,
                )
            )

        return configs

    def _read_root_flow_route(self) -> FlowRoute:
        preprocessing_data = self._mapping(self._raw_data.get("processing"))
        value = preprocessing_data.get("root_flow_route", FlowRoute.CONTINUATION)
        normalized = str(getattr(value, "value", value)).strip().lower()
        return FlowRoute(normalized)

    def read_core_network_config(self, acad: Autocad | Any) -> CoreNetworkConfig:
        configs = self.read_core_network_configs(acad)
        if len(configs) != 1:
            raise ValueError(
                f"Expected exactly one root line, got {len(configs)} matching root lines."
            )
        return configs[0]

    def read_output_layer_config(self) -> LayerConfig:
        output_data = self._mapping(
            self._mapping(
                self._mapping(self._raw_data.get("autocad")).get("output")
            ).get("network")
        )
        layer_data = self._mapping(output_data.get("layer"))
        properties = self._mapping(layer_data.get("properties"))
        return LayerConfig(
            name=str(layer_data.get("name", "")),
            color=str(properties.get("color")) if "color" in properties else None,
            line_weight=(
                float(properties["line_weight"])
                if "line_weight" in properties
                else None
            ),
        )

    def _load_yaml_string(self, yaml_string: str) -> dict[str, Any]:
        data = yaml.safe_load(yaml_string) or {}
        if not isinstance(data, dict):
            raise ValueError("Reader input YAML must deserialize to a mapping.")
        return self._normalize_mapping_keys(data)

    def _normalize_mapping_keys(self, value: Any) -> Any:
        if isinstance(value, dict):
            return {
                str(key).strip().rstrip(":"): self._normalize_mapping_keys(item)
                for key, item in value.items()
            }
        if isinstance(value, list):
            return [self._normalize_mapping_keys(item) for item in value]
        return value

    def _mapping(self, value: Any) -> dict[str, Any]:
        return value if isinstance(value, dict) else {}

    def _parse_hazard(self, value: Any) -> FireHazard:
        normalized = str(getattr(value, "value", value)).strip().lower()
        return FireHazard(normalized)

    def _parse_material(self, value: Any) -> SteelMaterial:
        normalized = str(getattr(value, "value", value)).strip().lower()
        if normalized == "erw":
            return SteelMaterial.ERW
        if normalized == "seamless":
            return SteelMaterial.Seamless
        raise ValueError(f"Unsupported steel material: {value}")

    def _parse_schedule(self, value: Any) -> SteelSchedule:
        normalized = str(getattr(value, "value", value)).strip().lower()
        if normalized in {"40", "scd40"}:
            return SteelSchedule.SCD40
        if normalized in {"80", "scd80"}:
            return SteelSchedule.SCD80
        raise ValueError(f"Unsupported steel schedule: {value}")

    def _parse_specs(self, value: Any) -> SteelSpecs:
        normalized = str(getattr(value, "value", value)).strip().lower()
        if normalized == "astm":
            return SteelSpecs.ASTM
        if normalized == "iso":
            return SteelSpecs.ISO
        raise ValueError(f"Unsupported steel specs: {value}")

    def _parse_connection_type(self, value: Any) -> SteelConnection:
        normalized = str(getattr(value, "value", value)).strip().lower()
        if normalized == "grooved":
            return SteelConnection.Grooved
        if normalized == "welded":
            return SteelConnection.Welded
        if normalized == "threaded":
            return SteelConnection.Threaded
        raise ValueError(f"Unsupported connection type: {value}")

    def _read_line_records(
        self, acad: Autocad | Any, layer_name: str, drawing_unit: LengthUnit
    ) -> list[_LineRecord]:
        line_records: list[_LineRecord] = []
        for index, entity in enumerate(self._iter_objects(acad, "AcDbLine"), start=1):
            entity_layer = str(self._get_entity_attr(entity, "Layer", "")).strip()
            if layer_name and entity_layer != layer_name:
                continue
            line = Line(
                id=self._entity_id(entity, index),
                start=self._point_from_entity_value(
                    self._get_entity_attr(entity, "StartPoint")
                ),
                end=self._point_from_entity_value(
                    self._get_entity_attr(entity, "EndPoint")
                ),
            )
            line_records.append(
                _LineRecord(
                    entity=entity,
                    line=GeometryUnitConverter.line_to_unit(
                        line, from_unit=drawing_unit, to_unit=LengthUnit.MILLIMETER
                    ),
                )
            )
        return line_records

    def _read_sprinkler_blocks(
        self,
        acad: Autocad | Any,
        sprinkler_block_names: set[str],
        drawing_unit: LengthUnit,
    ) -> list[Block]:
        blocks: list[Block] = []
        for index, entity in enumerate(
            self._iter_objects(acad, "AcDbBlockReference"),
            start=1,
        ):
            block_name = str(
                self._get_entity_attr(
                    entity,
                    "EffectiveName",
                    self._get_entity_attr(entity, "Name", ""),
                )
            )
            if sprinkler_block_names and block_name not in sprinkler_block_names:
                continue
            block = Block(
                id=self._entity_id(entity, index),
                name=block_name,
                center=self._point_from_entity_value(
                    self._get_entity_attr(entity, "InsertionPoint")
                ),
            )
            blocks.append(
                GeometryUnitConverter.block_to_unit(
                    block, from_unit=drawing_unit, to_unit=LengthUnit.MILLIMETER
                )
            )
        return blocks

    def _parse_length_unit(self, value: Any) -> LengthUnit:
        normalized = str(getattr(value, "value", value)).strip().lower()
        return LengthUnit(normalized)

    def _find_root_lines(
        self,
        line_records: list[_LineRecord],
        identifier: dict[str, Any],
    ) -> list[Line]:
        if not line_records:
            raise ValueError("No line-network entities were found in AutoCAD.")

        matches = [
            record.line
            for record in line_records
            if self._entity_matches_identifier(record.entity, identifier)
        ]
        if not matches:
            raise ValueError("Root line identifier did not match any line.")
        return matches

    def _entity_matches_identifier(
        self, entity: Any, identifier: dict[str, Any]
    ) -> bool:
        if not identifier:
            return False

        for key, expected in identifier.items():
            if key.strip().lower() == "color":
                # convert expected color from string to autocad color index
                expected = color_name_to_aci(expected)
            actual = self._get_entity_attr(entity, key, None)
            if self._normalize_scalar(actual) != self._normalize_scalar(expected):
                return False
        return True

    def _normalize_scalar(self, value: Any) -> Any:
        if isinstance(value, str):
            return value.strip().lower()
        return value

    def _get_entity_attr(self, entity: Any, attr_name: str, default: Any = None) -> Any:
        if entity is None:
            return default

        for candidate in {
            attr_name,
            attr_name.lower(),
            attr_name.upper(),
            attr_name[:1].upper() + attr_name[1:],
        }:
            if hasattr(entity, candidate):
                return getattr(entity, candidate)
        return default

    def _entity_id(self, entity: Any, fallback: int) -> int:
        handle = self._get_entity_attr(entity, "Handle", None)
        if handle is not None:
            try:
                return int(str(handle), 16)
            except ValueError:
                pass

        object_id = self._get_entity_attr(entity, "ObjectID", None)
        if object_id is not None:
            try:
                return int(object_id)
            except (TypeError, ValueError):
                pass

        return fallback

    def _point_from_entity_value(self, point: Any) -> Point:
        if point is None:
            raise ValueError("Could not read point data from AutoCAD entity.")

        if hasattr(point, "x") and hasattr(point, "y"):
            return Point(
                x=float(point.x),
                y=float(point.y),
                z=float(getattr(point, "z", 0.0)),
            )

        if isinstance(point, (list, tuple)) and len(point) >= 2:
            return Point(
                x=float(point[0]),
                y=float(point[1]),
                z=float(point[2]) if len(point) >= 3 else 0.0,
            )

        raise ValueError(f"Unsupported AutoCAD point value: {point!r}")

    def _iter_objects(self, acad: Autocad | Any, entity_name: str) -> list[Any]:
        iter_objects = getattr(acad, "iter_objects", None)
        if not callable(iter_objects):
            raise ValueError("AutoCAD reader expects an object with iter_objects().")

        objects = list(iter_objects(entity_name))
        if objects:
            return objects
        return []
