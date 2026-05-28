from __future__ import annotations

from collections.abc import Iterable

from fireplanner.boq.models import HangerBOQ, HangerSpec, Unit
from fireplanner.networks.junction_assembly import HangerAssembly


class HangerCalculator:
    @staticmethod
    def compute(hanger_assemblies: Iterable[HangerAssembly]) -> HangerBOQ:
        counts_by_spec: dict[HangerSpec, int] = {}

        for assembly in hanger_assemblies:
            spec = HangerSpec(pipe_diameter=assembly.hanger.diameter)
            counts_by_spec[spec] = counts_by_spec.get(spec, 0) + assembly.hangers_count

        return HangerBOQ(counts_by_spec=counts_by_spec, unit=Unit.Num)
