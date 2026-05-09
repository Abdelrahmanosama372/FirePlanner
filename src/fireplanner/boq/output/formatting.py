from __future__ import annotations

from fireplanner.boq.models import (
    BOQReport,
    ConnectionKey,
    ElbowKey,
    HangerKey,
    ReducerKey,
    TeeKey,
)


def pipe_headers() -> tuple[str, ...]:
    return ("Diameter", "Material", "Schedule", "Specs", "Length")


def pipe_rows(report: BOQReport) -> list[tuple[str, ...]]:
    rows: list[tuple[str, ...]] = []
    pipe_items = sorted(
        report.pipes.lengths_by_spec.items(),
        key=lambda item: (
            item[0].diameter.value,
            item[0].steel.material.value,
            item[0].steel.schedule.value,
            item[0].steel.specs.value,
        ),
    )
    for pipe_spec, length in pipe_items:
        rows.append(
            (
                str(pipe_spec.diameter.value),
                pipe_spec.steel.material.value,
                pipe_spec.steel.schedule.value,
                pipe_spec.steel.specs.value,
                f"{length:.3f}",
            )
        )
    return rows


def connection_headers() -> tuple[str, ...]:
    return ("Count", "Diameter(s)", "Material", "Schedule", "Specs", "Connection")


def connection_sections(report: BOQReport) -> list[tuple[str, list[tuple[str, ...]]]]:
    connection_items = sorted(
        report.connections.fittings_counts.items(),
        key=lambda item: (type(item[0]).__name__, connection_sort_key(item[0])),
    )
    sections: list[tuple[str, list[tuple[str, ...]]]] = []
    for key, count in connection_items:
        if isinstance(key, TeeKey):
            rows = [(
                str(count),
                f"run={key.run_diameter.value}, branch={key.branch_diameter.value}",
                key.steel.material.value,
                key.steel.schedule.value,
                key.steel.specs.value,
                key.connection.value,
            )]
        elif isinstance(key, ElbowKey):
            rows = [(
                str(count),
                str(key.diameter.value),
                key.steel.material.value,
                key.steel.schedule.value,
                key.steel.specs.value,
                key.connection.value,
            )]
        elif isinstance(key, ReducerKey):
            rows = [(
                str(count),
                f"{key.large_diameter.value}->{key.small_diameter.value}",
                key.steel.material.value,
                key.steel.schedule.value,
                key.steel.specs.value,
                key.connection.value,
            )]
        elif isinstance(key, HangerKey):
            rows = [(
                str(count),
                str(key.pipe_diameter.value),
                key.steel.material.value,
                key.steel.schedule.value,
                key.steel.specs.value,
                "-",
            )]
        else:
            rows = [(str(count), "-", "-", "-", "-", "-")]

        sections.append((type(key).__name__, rows))
    return sections


def paint_headers() -> tuple[str, ...]:
    return ("Primer", "Lacque", "Thinner", "Unit")


def paint_rows(report: BOQReport) -> list[tuple[str, ...]]:
    return [(
        f"{report.paint.primer:.3f}",
        f"{report.paint.lacque:.3f}",
        f"{report.paint.thinner:.3f}",
        report.paint.unit.value,
    )]


def connection_sort_key(key: ConnectionKey) -> tuple[float, float, str, str, str, str]:
    if isinstance(key, TeeKey):
        return (
            key.run_diameter.value,
            key.branch_diameter.value,
            key.steel.material.value,
            key.steel.schedule.value,
            key.steel.specs.value,
            key.connection.value,
        )
    if isinstance(key, ElbowKey):
        return (
            key.diameter.value,
            0.0,
            key.steel.material.value,
            key.steel.schedule.value,
            key.steel.specs.value,
            key.connection.value,
        )
    if isinstance(key, ReducerKey):
        return (
            key.large_diameter.value,
            key.small_diameter.value,
            key.steel.material.value,
            key.steel.schedule.value,
            key.steel.specs.value,
            key.connection.value,
        )
    if isinstance(key, HangerKey):
        return (
            key.pipe_diameter.value,
            0.0,
            key.steel.material.value,
            key.steel.schedule.value,
            key.steel.specs.value,
            "",
        )
    return (0.0, 0.0, "", "", "", "")
