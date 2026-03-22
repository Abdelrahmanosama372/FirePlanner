from enum import StrEnum
from typing import Dict

from fireplanner.firecomponent.base import SteelDims


class FireHazard(StrEnum):
    LIGHT = "light"
    ORDINARY = "ordinary"
    EXTRA = "extra"


hazard_sprinkler_capacity_table: Dict[FireHazard, Dict[SteelDims, int]] = {
    FireHazard.LIGHT: {
        SteelDims.DIM_1_INCHES: 2,
        SteelDims.DIM_1_25_INCHES: 3,
        SteelDims.DIM_1_5_INCHES: 5,
        SteelDims.DIM_2_INCHES: 10,
        SteelDims.DIM_2_5_INCHES: 30,
        SteelDims.DIM_3_INCHES: 60,
        SteelDims.DIM_4_INCHES: 100,
        SteelDims.DIM_6_INCHES: 275,
    },
    FireHazard.ORDINARY: {
        SteelDims.DIM_1_INCHES: 2,
        SteelDims.DIM_1_25_INCHES: 3,
        SteelDims.DIM_1_5_INCHES: 5,
        SteelDims.DIM_2_INCHES: 10,
        SteelDims.DIM_2_5_INCHES: 20,
        SteelDims.DIM_3_INCHES: 40,
        SteelDims.DIM_4_INCHES: 100,
        SteelDims.DIM_6_INCHES: 275,
    },
    FireHazard.EXTRA: {
        SteelDims.DIM_1_INCHES: 1,
        SteelDims.DIM_1_25_INCHES: 2,
        SteelDims.DIM_1_5_INCHES: 5,
        SteelDims.DIM_2_INCHES: 8,
        SteelDims.DIM_2_5_INCHES: 15,
        SteelDims.DIM_3_INCHES: 27,
        SteelDims.DIM_4_INCHES: 55,
        SteelDims.DIM_6_INCHES: 150,
    },
}


def find_min_steel_dim_for_sprinklers(
    hazard: FireHazard, sprinklers_count: int
) -> SteelDims:
    if sprinklers_count <= 0:
        raise ValueError("sprinklers_count must be a positive integer.")

    capacities = hazard_sprinkler_capacity_table[hazard]
    sorted_dims = sorted(capacities.items(), key=lambda item: item[0].value)

    for steel_dim, max_sprinklers in sorted_dims:
        if sprinklers_count <= max_sprinklers:
            return steel_dim

    raise ValueError(
        f"No steel dimension can handle {sprinklers_count} sprinklers "
        f"for hazard level '{hazard.value}'."
    )
