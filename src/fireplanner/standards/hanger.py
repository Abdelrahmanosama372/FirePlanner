from dataclasses import dataclass
from math import ceil

from fireplanner.firecomponent.base import SteelDims


@dataclass
class HangerProps:
    width: float
    length: float
    rod_size: float
    cross_bolt_length: float
    cross_bolt_diameter: float


hanger_dimensions: dict[SteelDims, HangerProps] = {
    SteelDims.DIM_0_5_INCHES: HangerProps(
        width=19,
        length=31.5 + 2 * 2.5,
        rod_size=10.0,
        cross_bolt_length=49,
        cross_bolt_diameter=6.35,
    ),
    SteelDims.DIM_0_75_INCHES: HangerProps(
        width=19,
        length=37 + 2 * 2.5,
        rod_size=10.0,
        cross_bolt_length=55,
        cross_bolt_diameter=6.35,
    ),
    SteelDims.DIM_1_INCHES: HangerProps(
        width=19,
        length=43.5 + 2 * 2.5,
        rod_size=10.0,
        cross_bolt_length=61.2,
        cross_bolt_diameter=6.35,
    ),
    SteelDims.DIM_1_25_INCHES: HangerProps(
        width=25,
        length=52 + 2 * 2.5,
        rod_size=10.0,
        cross_bolt_length=74,
        cross_bolt_diameter=6.35,
    ),
    SteelDims.DIM_1_5_INCHES: HangerProps(
        width=25,
        length=58 + 2 * 2.5,
        rod_size=10.0,
        cross_bolt_length=80.2,
        cross_bolt_diameter=6.35,
    ),
    SteelDims.DIM_2_INCHES: HangerProps(
        width=25,
        length=70 + 2 * 3,
        rod_size=10.0,
        cross_bolt_length=93,
        cross_bolt_diameter=6.35,
    ),
    SteelDims.DIM_2_5_INCHES: HangerProps(
        width=30,
        length=83.5 + 2 * 3,
        rod_size=10.0,
        cross_bolt_length=107,
        cross_bolt_diameter=9.525,
    ),
    SteelDims.DIM_3_INCHES: HangerProps(
        width=30,
        length=100 + 2 * 3.5,
        rod_size=10.0,
        cross_bolt_length=126.1,
        cross_bolt_diameter=9.525,
    ),
    SteelDims.DIM_4_INCHES: HangerProps(
        width=30,
        length=124 + 2 * 5,
        rod_size=10.0,
        cross_bolt_length=158,
        cross_bolt_diameter=9.525,
    ),
    SteelDims.DIM_6_INCHES: HangerProps(
        width=38,
        length=183 + 2 * 8,
        rod_size=12,
        cross_bolt_length=247.5,
        cross_bolt_diameter=12.7,
    ),
    SteelDims.DIM_8_INCHES: HangerProps(
        width=45,
        length=235 + 2 * 10,
        rod_size=12,
        cross_bolt_length=320,
        cross_bolt_diameter=15.875,
    ),
    SteelDims.DIM_10_INCHES: HangerProps(
        width=50,
        length=290 + 2 * 12,
        rod_size=16,
        cross_bolt_length=400,
        cross_bolt_diameter=19.05,
    ),
    SteelDims.DIM_12_INCHES: HangerProps(
        width=55,
        length=345 + 2 * 14,
        rod_size=16,
        cross_bolt_length=480,
        cross_bolt_diameter=19.05,
    ),
}

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
