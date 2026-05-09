import pytest

from fireplanner.firecomponent.base import SteelDims
from fireplanner.standards.hazard import FireHazard, find_min_steel_dim_for_sprinklers


@pytest.mark.parametrize(
    "hazard,sprinklers_count,expected_dim",
    [
        (FireHazard.LIGHT, 1, SteelDims.DIM_1_INCHES),
        (FireHazard.LIGHT, 3, SteelDims.DIM_1_25_INCHES),
        (FireHazard.LIGHT, 10, SteelDims.DIM_2_INCHES),
        (FireHazard.ORDINARY, 1, SteelDims.DIM_1_INCHES),
        (FireHazard.ORDINARY, 6, SteelDims.DIM_2_INCHES),
        (FireHazard.ORDINARY, 21, SteelDims.DIM_3_INCHES),
        (FireHazard.EXTRA, 1, SteelDims.DIM_1_INCHES),
        (FireHazard.EXTRA, 2, SteelDims.DIM_1_25_INCHES),
        (FireHazard.EXTRA, 56, SteelDims.DIM_6_INCHES),
    ],
)
def test_find_min_steel_dim_for_sprinklers(hazard, sprinklers_count, expected_dim):
    assert find_min_steel_dim_for_sprinklers(hazard, sprinklers_count) == expected_dim


@pytest.mark.parametrize("invalid_count", [0, -1, -10])
def test_find_min_steel_dim_for_sprinklers_invalid_count(invalid_count):
    with pytest.raises(ValueError, match="positive integer"):
        find_min_steel_dim_for_sprinklers(FireHazard.LIGHT, invalid_count)


@pytest.mark.parametrize(
    "hazard,sprinklers_count",
    [
        (FireHazard.LIGHT, 276),
        (FireHazard.ORDINARY, 276),
        (FireHazard.EXTRA, 151),
    ],
)
def test_find_min_steel_dim_for_sprinklers_when_over_capacity_raises(
    hazard, sprinklers_count
):
    with pytest.raises(ValueError, match="No steel dimension can handle"):
        find_min_steel_dim_for_sprinklers(hazard, sprinklers_count)
