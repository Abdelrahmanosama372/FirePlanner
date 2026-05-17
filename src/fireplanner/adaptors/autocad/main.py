from __future__ import annotations

import argparse
import logging
from pathlib import Path

from pyautocad import Autocad

from .pipeline import Pipeline

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")


def main() -> None:
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
