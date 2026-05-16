from math import sqrt
from fireplanner.firecomponent.base import SteelDims
from fireplanner.standards.steel_dim import steel_dim_table


def calculate_welded_branch_penetration_depth(
    run_diameter: SteelDims, branch_diameter: SteelDims
) -> float:
    R = steel_dim_table[run_diameter] / 2
    r = steel_dim_table[branch_diameter] / 2
    penetration_depth = R - sqrt(R * R - r * r)
    return penetration_depth
