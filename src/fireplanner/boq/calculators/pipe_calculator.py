from __future__ import annotations

from collections.abc import Iterable

from fireplanner.boq.models import PipeBOQ, PipeSpec, SteelSpec, Unit
from fireplanner.firecomponent.pipe import Pipe


class PipeCalculator:
    @staticmethod
    def compute(pipes_lengths: Iterable[tuple[Pipe, float]]) -> PipeBOQ:
        lengths_by_spec: dict[PipeSpec, float] = {}

        for pipe, length in pipes_lengths:
            key = PipeSpec(
                diameter=pipe.diameter,
                steel=SteelSpec(
                    material=pipe.material,
                    schedule=pipe.schedule,
                    specs=pipe.specs,
                ),
            )
            lengths_by_spec[key] = lengths_by_spec.get(key, 0.0) + length

        return PipeBOQ(lengths_by_spec=lengths_by_spec, unit=Unit.M)
