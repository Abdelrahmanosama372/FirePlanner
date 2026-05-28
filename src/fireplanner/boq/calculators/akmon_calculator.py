from __future__ import annotations

from fireplanner.boq.models import HangerFittingBOQ, HangerFittingSpec, StudBOQ, Unit


class AkmonCalculator:
    @staticmethod
    def compute(stud_boq: StudBOQ) -> HangerFittingBOQ:
        counts_by_spec: dict[HangerFittingSpec, int] = {}
        for spec, count in stud_boq.counts_by_spec.items():
            fitting_spec = HangerFittingSpec(item="akmon", diameter=spec.diameter)
            counts_by_spec[fitting_spec] = counts_by_spec.get(fitting_spec, 0) + count
        return HangerFittingBOQ(counts_by_spec=counts_by_spec, unit=Unit.Num)
