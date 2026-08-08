from __future__ import annotations

import argparse
import logging
from pathlib import Path

from pyautocad import Autocad

from .pipeline import Pipeline


class ColorFormatter(logging.Formatter):
    COLORS = {
        logging.INFO: "\033[36m",
        logging.WARNING: "\033[33m",
        logging.ERROR: "\033[31m",
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        message = super().format(record)
        color = self.COLORS.get(record.levelno)
        if color is None:
            return message
        return f"{color}{message}{self.RESET}"


def configure_logging() -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(ColorFormatter("%(levelname)s - %(message)s"))
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.handlers.clear()
    root_logger.addHandler(handler)


def main() -> None:
    configure_logging()

    parser = argparse.ArgumentParser(description="AutoCAD Fire Planner")
    parser.add_argument(
        "-c",
        "--config",
        default="examples/config.yaml",
        help="Path to YAML config file.",
    )
    args = parser.parse_args()

    config_path = Path(args.config)
    yaml_string = config_path.read_text(encoding="utf-8")

    acad = Autocad(create_if_not_exists=True)
    pipeline = Pipeline(yaml_string=yaml_string, acad=acad)
    pipeline.draw()


if __name__ == "__main__":
    main()
