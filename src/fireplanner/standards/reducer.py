from typing import Dict
from fireplanner.firecomponent.base import SteelDims

reducer_end_to_end_table: Dict[SteelDims, float] = {
    SteelDims.DIM_0_5_INCHES: 38.1,
    SteelDims.DIM_0_75_INCHES: 38.1,
    SteelDims.DIM_1_INCHES: 50.8,
    SteelDims.DIM_1_25_INCHES: 50.8,
    SteelDims.DIM_1_5_INCHES: 63.5,
    SteelDims.DIM_2_INCHES: 76.2,
    SteelDims.DIM_2_5_INCHES: 88.9,
    SteelDims.DIM_3_INCHES: 88.9,
    SteelDims.DIM_4_INCHES: 101.6,
    SteelDims.DIM_6_INCHES: 139.7,
    SteelDims.DIM_8_INCHES: 152.4,
    SteelDims.DIM_10_INCHES: 177.8,
    SteelDims.DIM_12_INCHES: 203.2,
}
