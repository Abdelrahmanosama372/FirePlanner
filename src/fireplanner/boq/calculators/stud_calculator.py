from __future__ import annotations

from collections.abc import Iterable

from fireplanner.boq.models import StudBOQ, StudSpec, Unit
from fireplanner.networks.junction_assembly import HangerAssembly
from fireplanner.standards.hanger import hanger_dimensions
from fireplanner.units import LengthUnit, LengthUnitConverter


class StudCalculator:
    @staticmethod
    def compute(
        hanger_assemblies: Iterable[HangerAssembly],
        full_ceiling_elevation: float,
    ) -> StudBOQ:
        lengths_by_spec: dict[StudSpec, float] = {}
        counts_by_spec: dict[StudSpec, int] = {}

        for assembly in hanger_assemblies:
            hanger_props = hanger_dimensions[assembly.hanger.diameter]
            stud_spec = StudSpec(diameter=hanger_props.rod_size)
            drop_mm = max(
                0.0,
                full_ceiling_elevation - float(assembly.pipe.edge_info.elevation),
            )
            stud_length_m = LengthUnitConverter.convert(
                drop_mm,
                from_unit=LengthUnit.MILLIMETER,
                to_unit=LengthUnit.METER,
            )
            lengths_by_spec[stud_spec] = (
                lengths_by_spec.get(stud_spec, 0.0)
                + stud_length_m * assembly.hangers_count
            )
            counts_by_spec[stud_spec] = (
                counts_by_spec.get(stud_spec, 0) + assembly.hangers_count
            )

        return StudBOQ(
            lengths_by_spec=lengths_by_spec,
            counts_by_spec=counts_by_spec,
            unit=Unit.M,
        )
