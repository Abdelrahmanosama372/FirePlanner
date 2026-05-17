from __future__ import annotations

from fireplanner.boq.models import BOQReport
from fireplanner.boq.output.formatting import (
    connection_headers,
    connection_sections,
    paint_headers,
    paint_rows,
    pipe_headers,
    pipe_rows,
)


class BOQConsolePrinter:
    @staticmethod
    def print_report(report: BOQReport) -> None:
        BOQConsolePrinter._print_pipes(report)
        print()
        BOQConsolePrinter._print_connections(report)
        print()
        BOQConsolePrinter._print_paint(report)

    @staticmethod
    def _print_pipes(report: BOQReport) -> None:
        print("PIPES")
        BOQConsolePrinter._print_table(pipe_headers(), pipe_rows(report))
        print(f"Unit: {report.pipes.unit.value}")

    @staticmethod
    def _print_connections(report: BOQReport) -> None:
        print("CONNECTIONS")
        for section_name, rows in connection_sections(report):
            print(section_name)
            BOQConsolePrinter._print_table(connection_headers(), rows)
            print()

        print(f"Unit: {report.connections.unit.value}")

    @staticmethod
    def _print_paint(report: BOQReport) -> None:
        print("PAINT")
        BOQConsolePrinter._print_table(paint_headers(), paint_rows(report))

    @staticmethod
    def _print_table(headers: tuple[str, ...], rows: list[tuple[str, ...]]) -> None:
        widths = [len(header) for header in headers]
        for row in rows:
            for idx, value in enumerate(row):
                widths[idx] = max(widths[idx], len(value))

        header_line = " | ".join(
            header.ljust(widths[idx]) for idx, header in enumerate(headers)
        )
        separator = "-+-".join("-" * widths[idx] for idx in range(len(headers)))
        print(header_line)
        print(separator)
        for row in rows:
            print(" | ".join(value.ljust(widths[idx]) for idx, value in enumerate(row)))
