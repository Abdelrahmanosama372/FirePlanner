from fireplanner.geometry.unit_converter import GeometryUnitConverter
from fireplanner.units import LengthUnit
import pytest

from fireplanner.geometry.primitives import Block, Line, Point
from fireplanner.networks.core_network import CoreNetwork, CoreNetworkConfig


def build_loop_network_lines() -> list[Line]:
    lines = [
        Line(id=0, start=Point(x=0, y=0), end=Point(x=0, y=2)),
        Line(id=1, start=Point(x=0, y=2), end=Point(x=0, y=5)),
        Line(id=2, start=Point(x=0, y=4), end=Point(x=4, y=4)),
        Line(id=3, start=Point(x=4, y=4), end=Point(x=4, y=8)),
        Line(id=4, start=Point(x=4, y=8), end=Point(x=0, y=8)),
        Line(id=5, start=Point(x=0, y=9), end=Point(x=0, y=5)),
        Line(id=6, start=Point(x=0, y=9), end=Point(x=0, y=12)),
    ]
    lines = [
        GeometryUnitConverter.line_to_unit(line, from_unit=LengthUnit.METER, to_unit=LengthUnit.MILLIMETER)
        for line in lines
    ]
    return lines


def build_loop_network_blocks() -> list[Block]:
    blocks = [
        Block(id=0, name="SPR", center=Point(x=0, y=1)),
        Block(id=1, name="SPR", center=Point(x=0, y=3)),
        Block(id=2, name="SPR", center=Point(x=2, y=4)),
        Block(id=3, name="SPR", center=Point(x=4, y=6)),
        Block(id=4, name="SPR", center=Point(x=2, y=8)),
        Block(id=5, name="SPR", center=Point(x=0, y=6)),
        Block(id=6, name="SPR", center=Point(x=0, y=10)),
    ]
    blocks = [
        GeometryUnitConverter.block_to_unit(block, from_unit=LengthUnit.METER, to_unit=LengthUnit.MILLIMETER)
        for block in blocks
    ]
    return blocks


def build_loop_network_core_network() -> CoreNetwork:
    return CoreNetwork(
        config=CoreNetworkConfig(
            sprinkler_blocks=build_loop_network_blocks(),
            lines=build_loop_network_lines(),
        )
    )


@pytest.fixture
def loop_network() -> tuple[list[Line], list[Block]]:
    return build_loop_network_lines(), build_loop_network_blocks()


@pytest.fixture
def loop_core_network() -> CoreNetwork:
    return build_loop_network_core_network()
