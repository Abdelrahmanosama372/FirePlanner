from __future__ import annotations

import logging
from dataclasses import dataclass
from math import cos, sin
from pathlib import Path
from typing import TYPE_CHECKING, Any

from fireplanner.boq.calculators.akmon_calculator import AkmonCalculator
from fireplanner.boq.calculators.connection_calculator import ConnectionCalculator
from fireplanner.boq.calculators.hanger_calculator import HangerCalculator
from fireplanner.boq.calculators.nut_calculator import NutCalculator
from fireplanner.boq.calculators.paint_calculator import PaintCalculator
from fireplanner.boq.calculators.pipe_calculator import PipeCalculator
from fireplanner.boq.calculators.stud_calculator import StudCalculator
from fireplanner.boq.calculators.washer_calculator import WasherCalculator
from fireplanner.boq.models import BOQReport, HangerFittingBOQ
from fireplanner.boq.output.console import BOQConsolePrinter
from fireplanner.geometry.primitives import Point, PrimitiveStyle
from fireplanner.networks import (
    CoreNetwork,
    CoreNetworkConfig,
    GeometryNetwork,
    GeometryNetworkConfig,
    ModelNetwork,
    ModelNetworkConfig,
    PlacementResolver,
)
from fireplanner.resolvers import (
    DraftingOcclusionResolver,
    DraftingScene,
    DrawablePrimitive,
    PipePrimitiveOcclusionResolver,
)
from fireplanner.units import LengthUnit, LengthUnitConverter

from .reader import BOQConfig, Reader
from .writer import OutputAnnotationConfig, Writer

if TYPE_CHECKING:
    from pyautocad import Autocad

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class NetworkPipelineResult:
    core_network_config: CoreNetworkConfig
    model_network_config: ModelNetworkConfig
    geometry_network_config: GeometryNetworkConfig
    core_network: CoreNetwork
    model_network: ModelNetwork
    geometry_network: GeometryNetwork


class Pipeline:
    def __init__(self, yaml_string: str, acad: Autocad | Any) -> None:
        self._reader = Reader(yaml_string)
        self._acad = acad
        logger.info("AutoCAD pipeline initialized.")

    def build(self) -> list[NetworkPipelineResult]:
        logger.info("Pipeline build started.")
        core_network_configs = self._reader.read_core_network_configs(self._acad)
        model_network_config = self._reader.read_model_network_config()
        geometry_network_config = self._reader.read_geometry_network_config()

        results: list[NetworkPipelineResult] = []
        for core_network_config in core_network_configs:
            core_network = CoreNetwork(config=core_network_config)
            model_network = ModelNetwork(
                core_network=core_network,
                config=model_network_config,
            )
            geometry_network = GeometryNetwork(
                core_network=core_network,
                model_network=model_network,
                config=geometry_network_config,
                placement_resolver=PlacementResolver(),
            )
            results.append(
                NetworkPipelineResult(
                    core_network_config=core_network_config,
                    model_network_config=model_network_config,
                    geometry_network_config=geometry_network_config,
                    core_network=core_network,
                    model_network=model_network,
                    geometry_network=geometry_network,
                )
            )

        logger.info("Pipeline build completed with %d result set(s).", len(results))
        self._run_boq_pipeline(results)
        return results

    def build_one(self) -> NetworkPipelineResult:
        results = self.build()
        if len(results) != 1:
            raise ValueError(
                f"Expected exactly one network pipeline result, got {len(results)}."
            )
        return results[0]

    def draw(self) -> list[list[Any]]:
        logger.info("Pipeline draw started.")
        layer_config = self._reader.read_output_layer_config()
        output_annotation_config = self._reader.read_output_annotation_config()
        writer = Writer(
            acad=self._acad,
            layer_config=layer_config,
            drawing_unit=self._reader.read_drawing_length_unit(),
        )
        written_entities_per_network: list[list[Any]] = []
        drafting_occlusion_resolver = DraftingOcclusionResolver()
        pipe_primitive_occlusion_resolver = PipePrimitiveOcclusionResolver()
        for result in self.build():
            fire_connections_scene = drafting_occlusion_resolver.resolve(
                result.geometry_network.get_resolved_fire_connections_assemblies()
            )
            drawables = list(fire_connections_scene.drawables)
            for (
                edge_id,
                pipes,
            ) in result.geometry_network.get_geometric_pipes_with_edges_ids().items():
                edge_connections = (
                    result.geometry_network.get_geometric_fire_connections_on_edge(
                        edge_id
                    )
                )
                for pipe in pipes:
                    drawables.append(
                        pipe_primitive_occlusion_resolver.resolve(
                            pipe=pipe,
                            occluding_components=edge_connections,
                        )
                    )
            # Legacy direct pipe drawing kept for later removal:
            # for pipe in result.geometry_network.get_geometric_pipes():
            #     drawables.append(
            #         DrawablePrimitive(primitives=pipe.get_primitives_2d())
            #     )
            for hanger in result.geometry_network.get_geometric_hangers():
                hanger_primitives = hanger.get_primitives_2d()
                if layer_config.hanger_layer_name:
                    for primitive in hanger_primitives:
                        style = primitive.style or PrimitiveStyle()
                        style.layer = layer_config.hanger_layer_name
                        if layer_config.hanger_color and style.color is None:
                            style.color = layer_config.hanger_color
                        primitive.style = style
                drawables.append(DrawablePrimitive(primitives=hanger_primitives))
            scene = DraftingScene(drawables=drawables)
            created_entities = writer.write_drafting_scene(scene)
            created_entities.extend(
                self._write_output_annotations_and_dimensions(
                    writer=writer,
                    result=result,
                    config=output_annotation_config,
                )
            )
            written_entities_per_network.append(created_entities)
        logger.info(
            "Pipeline draw completed for %d network(s).",
            len(written_entities_per_network),
        )
        return written_entities_per_network

    def _write_output_annotations_and_dimensions(
        self,
        writer: Writer,
        result: NetworkPipelineResult,
        config: OutputAnnotationConfig,
    ) -> list[Any]:
        created: list[Any] = []

        if config.dimensions.enabled:
            if not config.dimensions.style.name:
                raise ValueError("autocad.output.dimensions.style.name is required.")
            writer.ensure_dimension_style_exists(config.dimensions.style.name)

        for pipe_assembly in result.model_network.get_pipes_assembly():
            line = pipe_assembly.edge_info.line
            pipe = pipe_assembly.pipe
            if pipe is None:
                continue
            direction = line.direction()
            nx, ny = self._downward_normal(direction)

            mid_x = (line.start.x + line.end.x) / 2.0
            mid_y = (line.start.y + line.end.y) / 2.0

            if config.annotations.pipe_labels.pipe_dimension.enabled:
                dia_mm = float(pipe.diameter.value) * 25.0
                dia_text = f"%%c{dia_mm:g}"
                dia_pos = Point(
                    x=mid_x - nx * config.annotations.pipe_labels.diameter_offset_mm,
                    y=mid_y - ny * config.annotations.pipe_labels.diameter_offset_mm,
                )
                created.append(
                    writer.write_text_annotation(
                        text=dia_text,
                        position_mm=dia_pos,
                        rotation_rad=direction,
                        layer_name=config.annotations.layer.name,
                        text_height_mm=config.annotations.text_height,
                    )
                )

            if config.annotations.pipe_labels.cop.enabled:
                elevation_val = LengthUnitConverter.convert(
                    pipe_assembly.edge_info.elevation,
                    from_unit=LengthUnit.MILLIMETER,
                    to_unit=config.annotations.pipe_labels.cop.unit,
                )
                cop_text = f"COP {elevation_val:g} {config.annotations.pipe_labels.cop.unit.value}"
                cop_pos = Point(
                    x=mid_x - nx * config.annotations.pipe_labels.cop_offset_mm,
                    y=mid_y - ny * config.annotations.pipe_labels.cop_offset_mm,
                )
                created.append(
                    writer.write_text_annotation(
                        text=cop_text,
                        position_mm=cop_pos,
                        rotation_rad=direction,
                        layer_name=config.annotations.layer.name,
                        text_height_mm=config.annotations.text_height,
                    )
                )

            if config.dimensions.enabled:
                if line.length() < config.dimensions.min_length_mm:
                    continue
                dim_offset = config.dimensions.offset_mm
                dim_point = Point(
                    x=mid_x + nx * dim_offset,
                    y=mid_y + ny * dim_offset,
                )
                created.append(
                    writer.write_aligned_dimension(
                        start_mm=line.start,
                        end_mm=line.end,
                        offset_point_mm=dim_point,
                        style_name=config.dimensions.style.name,
                        layer_name=config.dimensions.layer_name,
                    )
                )

        return created

    def _downward_normal(self, direction: float) -> tuple[float, float]:
        nx = sin(direction)
        ny = -cos(direction)
        # Force dimension side to always point downward in WCS.
        if ny > 0:
            nx = -nx
            ny = -ny
        return nx, ny

    def _run_boq_pipeline(self, results: list[NetworkPipelineResult]) -> None:
        boq_config = self._reader.read_boq_config()
        if not boq_config.console.enabled and not boq_config.excel.enabled:
            logger.info("BOQ pipeline skipped: all outputs disabled.")
            return

        logger.info("BOQ pipeline started.")
        for index, result in enumerate(results, start=1):
            report = self._build_boq_report(result, boq_config)
            self._emit_boq_report(
                report=report,
                config=boq_config,
                network_index=index,
                networks_count=len(results),
            )
        logger.info("BOQ pipeline completed for %d network(s).", len(results))

    def _build_boq_report(
        self, result: NetworkPipelineResult, boq_config: BOQConfig
    ) -> BOQReport:
        pipes_lengths = []
        for pipe_assembly in result.model_network.get_pipes_assembly():
            length_m = LengthUnitConverter.convert(
                pipe_assembly.edge_info.length,
                from_unit=LengthUnit.MILLIMETER,
                to_unit=LengthUnit.METER,
            )
            if pipe_assembly.pipe is not None:
                pipes_lengths.append((pipe_assembly.pipe, length_m))

        connections = []
        for (
            junction_connections
        ) in result.model_network.get_fire_connections_with_junctions_ids().values():
            connections.extend(junction_connections)
        connections.extend(result.model_network.get_boq_only_fire_connections())

        pipe_boq = PipeCalculator.compute(pipes_lengths)
        connection_boq = ConnectionCalculator.compute(connections)
        hanger_assemblies = result.model_network.get_hangers_assembly()
        hanger_boq = HangerCalculator.compute(hanger_assemblies)
        stud_boq = StudCalculator.compute(
            hanger_assemblies=hanger_assemblies,
            full_ceiling_elevation=boq_config.full_ceiling_elevation,
        )
        akmon_boq = AkmonCalculator.compute(stud_boq)
        nut_boq = NutCalculator.compute(stud_boq)
        washer_boq = WasherCalculator.compute(stud_boq)
        hanger_fittings_counts = dict(akmon_boq.counts_by_spec)
        for fitting_boq in (nut_boq, washer_boq):
            for spec, count in fitting_boq.counts_by_spec.items():
                hanger_fittings_counts[spec] = (
                    hanger_fittings_counts.get(spec, 0) + count
                )
        paint_boq = PaintCalculator.compute(
            pipe_boq=pipe_boq,
            paint_config=boq_config.paint,
        )
        return BOQReport(
            pipes=pipe_boq,
            connections=connection_boq,
            hangers=hanger_boq,
            studs=stud_boq,
            hanger_fittings=HangerFittingBOQ(
                counts_by_spec=hanger_fittings_counts,
                unit=akmon_boq.unit,
            ),
            paint=paint_boq,
        )

    def _emit_boq_report(
        self,
        report: BOQReport,
        config: BOQConfig,
        network_index: int = 1,
        networks_count: int = 1,
    ) -> None:
        if config.console.enabled:
            BOQConsolePrinter.print_report(report)
        if config.excel.enabled:
            try:
                from fireplanner.boq.output.excel import BOQExcelExporter
            except ModuleNotFoundError:
                logger.warning(
                    "Excel BOQ export skipped because required dependency is missing."
                )
                return
            BOQExcelExporter.export(
                report=report,
                output_path=self._resolve_boq_output_path(
                    config.excel.path,
                    network_index=network_index,
                    networks_count=networks_count,
                ),
            )

    def _resolve_boq_output_path(
        self,
        output_path: str,
        network_index: int,
        networks_count: int,
    ) -> str:
        if networks_count <= 1:
            return output_path

        path = Path(output_path)
        return str(path.with_name(f"{path.stem}{network_index}{path.suffix}"))
