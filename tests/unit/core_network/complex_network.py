import pytest

from fireplanner.geometry.primitives import Block, Line, Point
from fireplanner.networks.core_network import CoreNetwork, CoreNetworkConfig


def build_complex_network_lines() -> list[Line]:
    return [
        Line(id=0, start=Point(x=0, y=0), end=Point(x=0, y=6)),
        Line(id=1, start=Point(x=0, y=6), end=Point(x=0, y=12)),
        Line(id=2, start=Point(x=0, y=12), end=Point(x=0, y=15)),
        Line(id=3, start=Point(x=0, y=4), end=Point(x=6, y=4)),
        Line(id=4, start=Point(x=0, y=5), end=Point(x=-6, y=5)),
        Line(id=5, start=Point(x=0, y=10), end=Point(x=8, y=10)),
        Line(id=6, start=Point(x=0, y=9), end=Point(x=-8, y=9)),
        Line(id=7, start=Point(x=0, y=15), end=Point(x=5, y=15)),
        Line(id=8, start=Point(x=6, y=4), end=Point(x=10, y=4)),
        Line(id=9, start=Point(x=-6, y=5), end=Point(x=-10, y=5)),
        Line(id=10, start=Point(x=8, y=10), end=Point(x=12, y=10)),
        Line(id=11, start=Point(x=-8, y=9), end=Point(x=-12, y=9)),
        Line(id=12, start=Point(x=5, y=15), end=Point(x=9, y=18)),
        Line(id=13, start=Point(x=12, y=10), end=Point(x=12, y=14)),
        Line(id=14, start=Point(x=12, y=14), end=Point(x=16, y=14)),
    ]


def build_complex_network_blocks() -> list[Block]:
    return [
        Block(id=0, name="SRC", center=Point(x=0, y=0)),
        Block(id=1, name="SPR", center=Point(x=0, y=3)),
        Block(id=2, name="SPR", center=Point(x=4, y=5)),
        Block(id=3, name="SPR", center=Point(x=-3, y=5)),
        Block(id=4, name="SPR", center=Point(x=0, y=8)),
        Block(id=5, name="SPR", center=Point(x=6, y=10)),
        Block(id=6, name="SPR", center=Point(x=-5, y=10)),
        Block(id=7, name="SPR", center=Point(x=0, y=13)),
        Block(id=8, name="SPR", center=Point(x=9, y=10)),
        Block(id=9, name="SPR", center=Point(x=-10, y=10)),
        Block(id=10, name="SPR", center=Point(x=6, y=16)),
        Block(id=11, name="SPR", center=Point(x=12, y=12)),
        Block(id=12, name="SPR", center=Point(x=15, y=14)),
    ]


def build_complex_network_core_network() -> CoreNetwork:
    return CoreNetwork(
        config=CoreNetworkConfig(
            sprinkler_blocks=build_complex_network_blocks(),
            lines=build_complex_network_lines(),
        )
    )


@pytest.fixture
def complex_network() -> tuple[list[Line], list[Block]]:
    return build_complex_network_lines(), build_complex_network_blocks()


@pytest.fixture
def complex_core_network() -> CoreNetwork:
    return build_complex_network_core_network()
