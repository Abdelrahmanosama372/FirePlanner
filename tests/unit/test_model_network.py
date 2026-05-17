import pytest

from fireplanner.firecomponent import Elbow, Reducer, SteelDims, Tee
from fireplanner.networks import CoreNetwork, ModelNetwork


@pytest.fixture
def defaultModelNetwork():
    return ModelNetwork(CoreNetwork())


@pytest.mark.parametrize(
    "pipe1, pipe2, angle, expected_types",
    [
        # same diameter + straight
        (
            SteelDims.DIM_2_INCHES,
            SteelDims.DIM_2_INCHES,
            0.0,
            [],
        ),
        # different diameter + straight -> reducer
        (
            SteelDims.DIM_2_INCHES,
            SteelDims.DIM_1_INCHES,
            0.0,
            [Reducer],
        ),
        # angled -> elbow
        (
            SteelDims.DIM_2_INCHES,
            SteelDims.DIM_1_INCHES,
            90.0,
            [Elbow],
        ),
    ],
)
def test_create_fire_connection_for_two_way_junction(
    defaultModelNetwork,
    pipe1,
    pipe2,
    angle,
    expected_types,
):

    connections = defaultModelNetwork._create_fire_connection_for_two_way_junction(
        pipe1,
        pipe2,
        angle,
    )

    assert len(connections) == len(expected_types)

    for connection, expected_type in zip(connections, expected_types):
        assert isinstance(connection, expected_type)


@pytest.mark.parametrize(
    "run1, run2, branch, expected_types",
    [
        # equal runs + smaller branch
        (
            SteelDims.DIM_4_INCHES,
            SteelDims.DIM_4_INCHES,
            SteelDims.DIM_2_INCHES,
            [Tee],
        ),
        # unequal runs + smaller branch
        (
            SteelDims.DIM_4_INCHES,
            SteelDims.DIM_2_INCHES,
            SteelDims.DIM_1_INCHES,
            [Tee, Reducer],
        ),
        # branch is largest
        (
            SteelDims.DIM_2_INCHES,
            SteelDims.DIM_3_INCHES,
            SteelDims.DIM_6_INCHES,
            [Tee, Reducer, Reducer],
        ),
    ],
)
def test_create_fire_connection_for_three_way_junction(
    defaultModelNetwork,
    run1,
    run2,
    branch,
    expected_types,
):

    connections = defaultModelNetwork._create_fire_connection_for_three_way_junction(
        run1,
        run2,
        branch,
    )

    assert len(connections) == len(expected_types)

    for connection, expected_type in zip(connections, expected_types):
        assert isinstance(connection, expected_type)
