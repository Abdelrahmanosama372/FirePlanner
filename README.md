# FirePlanner

FirePlanner is a library-first engine for firefighting network planning. It takes drawing-like inputs, builds core/model/geometry networks, and produces engineering outputs such as BOQ reports and drawable primitives.

AutoCAD is one adaptor implementation, not the only intended source/target. The architecture is designed for additional import/export adaptors.

## Core Capabilities

- Build one or more network graphs from source geometry (including multiple root matches).
- Compute model-layer components (pipes/fittings with steel specs and connection types).
- Resolve geometric components and primitives.
- Export geometry through adaptors (AutoCAD writer is implemented).
- Generate BOQ:
- Pipe BOQ grouped by diameter and steel spec.
- Connection BOQ grouped by fitting key type.
- Paint BOQ (liters) from area and paint config.
- Output BOQ to console and Excel.

## Installation

```bash
pip install -e .
```

Dependencies:

- `numpy`
- `openpyxl`
- `pyautocad` (needed for AutoCAD adaptor runtime)

## AutoCAD Adaptor CLI

```bash
autocad-fire-planner --config examples/config.yaml
```

Script entrypoint:

- `fireplanner.adaptors.autocad.main:main`

## AutoCAD Config

See `examples/config.yaml` for the reference schema. Main groups:

- `firefighting`: hazard and steel defaults.
- `processing`: BOQ/processing options.
- `autocad.input`: units, root line identifier, network lines, sprinkler blocks.
- `autocad.output`: output layer and properties.

## Pipeline Overview

1. Reader stage: adaptor reads config + source entities.
2. Build stage: `CoreNetwork` -> `ModelNetwork` -> `GeometryNetwork`.
3. Writer stage: adaptor converts primitives to target-native entities.

## Extensibility

- Extend BOQ calculators and output renderers independently from adaptors.
- Add new import adaptors to map external drawing/data systems into core inputs.
- Add new export adaptors to render primitives to different CAD/BIM or serialization targets.
