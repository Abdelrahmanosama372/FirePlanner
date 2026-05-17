from __future__ import annotations

from collections.abc import Iterable

from fireplanner.boq.models import (
    ConnectionBOQ,
    ConnectionKey,
    ElbowKey,
    HangerKey,
    ReducerKey,
    SteelSpec,
    TeeKey,
    Unit,
)
from fireplanner.firecomponent.fitting.fireconnection.elbow import Elbow
from fireplanner.firecomponent.fitting.fireconnection.reducer import Reducer
from fireplanner.firecomponent.fitting.fireconnection.tee import Tee
from fireplanner.firecomponent.fitting.hanger import Hanger


class ConnectionCalculator:
    @staticmethod
    def compute(fittings: Iterable[object]) -> ConnectionBOQ:
        fittings_counts: dict[ConnectionKey, int] = {}

        for fitting in fittings:
            key = ConnectionCalculator._to_connection_key(fitting)
            fittings_counts[key] = fittings_counts.get(key, 0) + 1

        return ConnectionBOQ(fittings_counts=fittings_counts, unit=Unit.Num)

    @staticmethod
    def _to_connection_key(fitting: object) -> ConnectionKey:
        if isinstance(fitting, Tee):
            return TeeKey(
                run_diameter=fitting.run_diameter,
                branch_diameter=fitting.branch_diameter,
                steel=SteelSpec(
                    material=fitting.material,
                    schedule=fitting.schedule,
                    specs=fitting.specs,
                ),
                connection=fitting.connection_type,
            )

        if isinstance(fitting, Elbow):
            return ElbowKey(
                diameter=fitting.diameter,
                steel=SteelSpec(
                    material=fitting.material,
                    schedule=fitting.schedule,
                    specs=fitting.specs,
                ),
                connection=fitting.connection_type,
            )

        if isinstance(fitting, Reducer):
            return ReducerKey(
                large_diameter=fitting.large_diameter,
                small_diameter=fitting.small_diameter,
                steel=SteelSpec(
                    material=fitting.material,
                    schedule=fitting.schedule,
                    specs=fitting.specs,
                ),
                connection=fitting.connection_type,
            )

        if isinstance(fitting, Hanger):
            return HangerKey(
                pipe_diameter=fitting.diameter,
                steel=SteelSpec(
                    material=fitting.material,
                    schedule=fitting.schedule,
                    specs=fitting.specs,
                ),
            )

        raise TypeError(
            f"Unsupported fitting type for BOQ calculation: {type(fitting)!r}"
        )
