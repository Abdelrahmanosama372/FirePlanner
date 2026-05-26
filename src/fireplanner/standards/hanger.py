from math import ceil

from fireplanner.firecomponent.base import SteelDims

steel_pipe_to_max_distance_between_hangers: dict[SteelDims, float] = {
    SteelDims.DIM_0_5_INCHES: 3700.0,
    SteelDims.DIM_0_75_INCHES: 3700.0,
    SteelDims.DIM_1_INCHES: 3700.0,
    SteelDims.DIM_1_25_INCHES: 3700.0,
    SteelDims.DIM_1_5_INCHES: 4600.0,
    SteelDims.DIM_2_INCHES: 4600.0,
    SteelDims.DIM_2_5_INCHES: 4600.0,
    SteelDims.DIM_3_INCHES: 4600.0,
    SteelDims.DIM_4_INCHES: 4600.0,
    SteelDims.DIM_6_INCHES: 4600.0,
    SteelDims.DIM_8_INCHES: 4600.0,
    SteelDims.DIM_10_INCHES: 4600.0,
    SteelDims.DIM_12_INCHES: 4600.0,
}


def find_min_number_of_hangers_for_pipe(
    pipe_diameter: SteelDims, pipe_length: float
) -> int:
    max_distance_between_hangers = steel_pipe_to_max_distance_between_hangers[
        pipe_diameter
    ]
    hangers_number = ceil(pipe_length / max_distance_between_hangers)
    return hangers_number
