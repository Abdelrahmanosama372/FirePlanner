from __future__ import annotations

from math import pi

from fireplanner.boq.models import PaintBOQ, PaintConfig, PipeBOQ, Unit

INCH_TO_METER = 0.0254


class PaintCalculator:
    @staticmethod
    def compute(pipe_boq: PipeBOQ, paint_config: PaintConfig) -> PaintBOQ:
        total_area_m2 = 0.0
        for pipe_spec, length_m in pipe_boq.lengths_by_spec.items():
            diameter_m = float(pipe_spec.diameter.value) * INCH_TO_METER
            total_area_m2 += pi * diameter_m * length_m

        thickness_m: float = paint_config.thickness
        volume_solids: float = paint_config.volume_solids_precentage
        scrap: float = paint_config.scrap_precentage

        q_liters_per_m2: float = thickness_m / (volume_solids * 1000 * (1 - scrap))
        paint_liters: float = total_area_m2 * q_liters_per_m2

        return PaintBOQ(
            primer=paint_liters,
            lacque=paint_liters,
            thinner=paint_liters,
            unit=Unit.Liter,
        )
