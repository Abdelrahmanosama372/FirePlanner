from dataclasses import dataclass


@dataclass(frozen=True)
class PlacementRules:
    reducer_offset: float = 150.0
