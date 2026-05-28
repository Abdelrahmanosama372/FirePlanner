from __future__ import annotations

import logging
from dataclasses import dataclass
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
)
from fireplanner.units import LengthUnit, LengthUnitConverter

from .reader import BOQConfig, Reader
from .writer import Writer

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
        writer = Writer(
            acad=self._acad,
            layer_config=layer_config,
            drawing_unit=self._reader.read_drawing_length_unit(),
        )
        written_entities_per_network: list[list[Any]] = []
        drafting_occlusion_resolver = DraftingOcclusionResolver()
        for result in self.build():
            fire_connections_scene = drafting_occlusion_resolver.resolve(
                result.geometry_network.get_resolved_fire_connections_assemblies()
            )
            drawables = list(fire_connections_scene.drawables)
            for pipe in result.geometry_network.get_geometric_pipes():
                drawables.append(DrawablePrimitive(primitives=pipe.get_primitives_2d()))
            for hanger in result.geometry_network.get_geometric_hangers():
                drawables.append(
                    DrawablePrimitive(primitives=hanger.get_primitives_2d())
                )
            scene = DraftingScene(drawables=drawables)
            written_entities_per_network.append(writer.write_drafting_scene(scene))
        logger.info(
            "Pipeline draw completed for %d network(s).",
            len(written_entities_per_network),
        )
        return written_entities_per_network

    def _run_boq_pipeline(self, results: list[NetworkPipelineResult]) -> None:
        boq_config = self._reader.read_boq_config()
        if not boq_config.console.enabled and not boq_config.excel.enabled:
            logger.info("BOQ pipeline skipped: all outputs disabled.")
            return

        logger.info("BOQ pipeline started.")
        for result in results:
            report = self._build_boq_report(result, boq_config)
            self._emit_boq_report(report, boq_config)
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

    def _emit_boq_report(self, report: BOQReport, config: BOQConfig) -> None:
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
            BOQExcelExporter.export(report=report, output_path=config.excel.path)
