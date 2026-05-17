from typing import Dict

from fireplanner.firecomponent.base import SteelDims

steel_dim_table: Dict[SteelDims, float] = {
    SteelDims.DIM_0_5_INCHES: 21.34,  # NPS 1/2" OD
    SteelDims.DIM_0_75_INCHES: 26.67,  # NPS 3/4" OD
    SteelDims.DIM_1_INCHES: 33.40,  # NPS 1" OD
    SteelDims.DIM_1_25_INCHES: 42.16,  # NPS 1-1/4" OD
    SteelDims.DIM_1_5_INCHES: 48.26,  # NPS 1-1/2" OD
    SteelDims.DIM_2_INCHES: 60.33,  # NPS 2" OD
    SteelDims.DIM_2_5_INCHES: 73.03,  # NPS 2-1/2" OD
    SteelDims.DIM_3_INCHES: 88.90,  # NPS 3" OD
    SteelDims.DIM_4_INCHES: 114.30,  # NPS 4" OD
    SteelDims.DIM_6_INCHES: 168.28,  # NPS 6" OD
    SteelDims.DIM_8_INCHES: 219.08,  # NPS 8" OD
    SteelDims.DIM_10_INCHES: 273.05,  # NPS 10" OD
    SteelDims.DIM_12_INCHES: 323.85,  # NPS 12" OD
}
