import pytest

from fireplanner.geometry.primitives import Block, Line, Point
from fireplanner.networks.core_network import CoreNetwork


def build_simple_network_lines() -> list[Line]:
    return [
        Line(id=0, start=Point(x=0, y=0), end=Point(x=0, y=5)),
        Line(id=1, start=Point(x=0, y=3), end=Point(x=4, y=3)),
        Line(id=2, start=Point(x=0, y=4), end=Point(x=-6, y=4)),
        Line(id=3, start=Point(x=0, y=5), end=Point(x=0, y=9)),
        Line(id=4, start=Point(x=0, y=9), end=Point(x=6, y=9)),
    ]


def build_simple_network_inverted_lines() -> list[Line]:
    return [
        Line(id=0, start=Point(x=0, y=0), end=Point(x=0, y=5)),
        Line(id=1, start=Point(x=4, y=3), end=Point(x=0, y=3)),
        Line(id=2, start=Point(x=-6, y=4), end=Point(x=0, y=4)),
        Line(id=3, start=Point(x=0, y=9), end=Point(x=0, y=5)),
        Line(id=4, start=Point(x=6, y=9), end=Point(x=0, y=9)),
    ]


def build_simple_network_blocks() -> list[Block]:
    return [
        Block(id=0, name="SPR", center=Point(x=0, y=2)),
        Block(id=1, name="SPR", center=Point(x=2, y=3)),
        Block(id=2, name="SPR", center=Point(x=-4, y=4)),
        Block(id=3, name="SPR", center=Point(x=0, y=8)),
        Block(id=4, name="SPR", center=Point(x=1, y=9)),
    ]


def build_simple_network_core_network() -> CoreNetwork:
    return CoreNetwork(
        sprinkles=build_simple_network_blocks(),
        lines=build_simple_network_lines(),
    )


def build_simple_network_inverted_core_network() -> CoreNetwork:
    return CoreNetwork(
        sprinkles=build_simple_network_blocks(),
        lines=build_simple_network_inverted_lines(),
    )


@pytest.fixture
def simple_network() -> tuple[list[Line], list[Block]]:
    return build_simple_network_lines(), build_simple_network_blocks()


@pytest.fixture
def simple_network_inverted() -> tuple[list[Line], list[Block]]:
    return build_simple_network_inverted_lines(), build_simple_network_blocks()


@pytest.fixture
def simple_core_network() -> CoreNetwork:
    return build_simple_network_core_network()


@pytest.fixture
def simple_inverted_core_network() -> CoreNetwork:
    return build_simple_network_inverted_core_network()
