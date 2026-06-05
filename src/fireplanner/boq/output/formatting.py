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
    sections_by_name: dict[str, list[tuple[str, ...]]] = {}
    for key, count in connection_items:
        if isinstance(key, TeeKey):
            section_name = "Tees"
            row = (
                str(count),
                f"run={key.run_diameter.value}, branch={key.branch_diameter.value}",
                key.steel.material.value,
                key.steel.schedule.value,
                key.steel.specs.value,
                key.connection.value,
            )
        elif isinstance(key, ElbowKey):
            section_name = "Elbows"
            row = (
                str(count),
                str(key.diameter.value),
                key.steel.material.value,
                key.steel.schedule.value,
                key.steel.specs.value,
                key.connection.value,
            )
        elif isinstance(key, ReducerKey):
            section_name = "Reducers"
            row = (
                str(count),
                f"{key.large_diameter.value}->{key.small_diameter.value}",
                key.steel.material.value,
                key.steel.schedule.value,
                key.steel.specs.value,
                key.connection.value,
            )
        elif isinstance(key, HangerKey):
            section_name = "Hangers"
            row = (
                str(count),
                str(key.pipe_diameter.value),
                key.steel.material.value,
                key.steel.schedule.value,
                key.steel.specs.value,
                "-",
            )
        else:
            section_name = type(key).__name__
            row = (str(count), "-", "-", "-", "-", "-")

        sections_by_name.setdefault(section_name, []).append(row)

    ordered_section_names = [
        "Tees",
        "Elbows",
        "Reducers",
        "Hangers",
    ]
    ordered_sections = [
        (section_name, sections_by_name[section_name])
        for section_name in ordered_section_names
        if section_name in sections_by_name
    ]
    for section_name, rows in sections_by_name.items():
        if section_name not in ordered_section_names:
            ordered_sections.append((section_name, rows))
    return ordered_sections


def paint_headers() -> tuple[str, ...]:
    return ("Primer", "Lacque", "Thinner", "Unit")


def paint_rows(report: BOQReport) -> list[tuple[str, ...]]:
    return [
        (
            f"{report.paint.primer:.3f}",
            f"{report.paint.lacque:.3f}",
            f"{report.paint.thinner:.3f}",
            report.paint.unit.value,
        )
    ]


def hanger_headers() -> tuple[str, ...]:
    return ("Count", "Pipe Diameter")


def hanger_rows(report: BOQReport) -> list[tuple[str, ...]]:
    items = sorted(
        report.hangers.counts_by_spec.items(),
        key=lambda item: item[0].pipe_diameter.value,
    )
    return [(str(count), str(spec.pipe_diameter.value)) for spec, count in items]


def stud_headers() -> tuple[str, ...]:
    return ("Stud Diameter", "Count", "Total Length")


def stud_rows(report: BOQReport) -> list[tuple[str, ...]]:
    specs = sorted(report.studs.lengths_by_spec.keys(), key=lambda spec: spec.diameter)
    rows: list[tuple[str, ...]] = []
    for spec in specs:
        rows.append(
            (
                f"{spec.diameter:.3f}",
                str(report.studs.counts_by_spec.get(spec, 0)),
                f"{report.studs.lengths_by_spec[spec]:.3f}",
            )
        )
    return rows


def hanger_fitting_headers() -> tuple[str, ...]:
    return ("Item", "Diameter", "Count")


def hanger_fitting_rows(report: BOQReport) -> list[tuple[str, ...]]:
    items = sorted(
        report.hanger_fittings.counts_by_spec.items(),
        key=lambda item: (item[0].item, item[0].diameter),
    )
    return [(spec.item, f"{spec.diameter:.3f}", str(count)) for spec, count in items]


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
