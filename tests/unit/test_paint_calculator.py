from dataclasses import dataclass
from math import pi

from fireplanner.boq.calculators.paint_calculator import PaintCalculator
from fireplanner.boq.models import PaintConfig, PipeBOQ, PipeSpec, SteelSpec, Unit
from fireplanner.firecomponent.base import SteelMaterial, SteelSchedule, SteelSpecs


@dataclass(frozen=True)
class DiameterStub:
    value: float


def test_calculate_paint_boq_for_200mm_pipe_1000m() -> None:
    diameter_inch = 200.0 / 25.4
    pipe_spec = PipeSpec(
        diameter=DiameterStub(value=diameter_inch),  # type: ignore[arg-type]
        steel=SteelSpec(
            material=SteelMaterial.ERW,
            schedule=SteelSchedule.SCD40,
            specs=SteelSpecs.ASTM,
        ),
    )
    pipe_boq = PipeBOQ(lengths_by_spec={pipe_spec: 1000.0}, unit=Unit.M)
    paint_config = PaintConfig(
        thickness=140,
        scrap_precentage=0.4,
        volume_solids_precentage=0.75,
    )

    result = PaintCalculator.compute(pipe_boq=pipe_boq, paint_config=paint_config)

    area_m2 = pi * 0.2 * 1000.0
    print(area_m2)
    q_l_per_m2 = (140) / ((0.75 * 1000) * (1 - 0.4))
    print(q_l_per_m2)
    expected_liters = area_m2 * q_l_per_m2

    assert result.unit == Unit.Liter
    assert result.primer == expected_liters
    assert result.lacque == expected_liters
    assert result.thinner == expected_liters
