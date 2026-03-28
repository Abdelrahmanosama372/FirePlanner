import pytest

from fireplanner.geometry.primitives import Block, Line, Point
from fireplanner.networks import CoreNetwork, CoreNode


def get_child(node: CoreNode, line_id: int) -> CoreNode | None:
    return next(
        (child for child in node.connected_nodes if child.line.id == line_id), None
    )


@pytest.fixture
def simple_network():
    """
                 (0,9)------(6,9)
                  |
                  |
                (0,5)
    (-6,4)--------|
                  |-------(4,3)
                  |
                  |
                (0,0)
    """
    lines = [
        Line(id=0, start=Point(x=0, y=0), end=Point(x=0, y=4)),
        Line(id=1, start=Point(x=0, y=3), end=Point(x=4, y=3)),
        Line(id=2, start=Point(x=0, y=4), end=Point(x=-6, y=4)),
        Line(id=3, start=Point(x=0, y=5), end=Point(x=0, y=9)),
        Line(id=4, start=Point(x=0, y=9), end=Point(x=6, y=9)),
    ]

    blocks = [
        Block(id=0, name="SPR", center=Point(x=0, y=2)),
        Block(id=1, name="SPR", center=Point(x=2, y=3)),
        Block(id=2, name="SPR", center=Point(x=-4, y=4)),
        Block(id=3, name="SPR", center=Point(x=0, y=8)),
        Block(id=4, name="SPR", center=Point(x=1, y=9)),
    ]

    return lines, blocks


@pytest.fixture
def complex_network():
    """
                                        (9,18)
                                          /
                                         /
                         (0,15)------(5,15)
                            |
                            |
                         (0,12)            (12,14)---------(16,14)
                            |                 |
                            |----(8,10)----(12,10)
    (-12,9)---(-8,9)--------|
                            |
                         (0,6)
                            |
     (-10,5)---(-6,5)-------|
                            |-----(6,4)-----(10,4)
                            |
                          (0,0)

    """
    lines = [
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

    blocks = [
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

    return lines, blocks


@pytest.fixture
def loop_network():
    """
    (0,12)
      |
    (0,9)
      |--------(4,8)
      |          |
    (0|5)        |
      |--------(4,4)
      |
      |
    (0,2)
      |
      |
    (0,0)
    """
    lines = [
        Line(id=0, start=Point(x=0, y=0), end=Point(x=0, y=2)),
        Line(id=1, start=Point(x=0, y=2), end=Point(x=0, y=5)),
        Line(id=2, start=Point(x=0, y=4), end=Point(x=4, y=4)),
        Line(id=3, start=Point(x=4, y=4), end=Point(x=4, y=8)),
        Line(id=4, start=Point(x=4, y=8), end=Point(x=0, y=8)),
        Line(id=5, start=Point(x=0, y=9), end=Point(x=0, y=5)),
        Line(id=6, start=Point(x=0, y=9), end=Point(x=0, y=12)),
    ]

    blocks = [
        Block(id=0, name="SPR", center=Point(x=0, y=1)),
        Block(id=1, name="SPR", center=Point(x=0, y=3)),
        Block(id=2, name="SPR", center=Point(x=2, y=4)),
        Block(id=3, name="SPR", center=Point(x=4, y=6)),
        Block(id=4, name="SPR", center=Point(x=2, y=8)),
        Block(id=5, name="SPR", center=Point(x=0, y=6)),
        Block(id=6, name="SPR", center=Point(x=0, y=10)),
    ]

    return lines, blocks


@pytest.fixture
def simple_core_network(simple_network):
    lines, blocks = simple_network
    return CoreNetwork(lines=lines, blocks=blocks)


@pytest.fixture
def complex_core_network(complex_network):
    lines, blocks = complex_network
    return CoreNetwork(lines=lines, blocks=blocks)


@pytest.fixture
def loop_core_network(loop_network):
    lines, blocks = loop_network
    return CoreNetwork(lines=lines, blocks=blocks)


def test_construct_simple_network(simple_core_network):
    assert simple_core_network.root is not None


def test_construct_complex_network(complex_core_network):
    assert complex_core_network.root is not None


def test_simple_network_keeps_deep_branch_structure(simple_core_network):
    root_node = simple_core_network.root

    assert root_node is not None
    assert root_node.line.id == 0
    assert len(root_node.connected_nodes) == 2

    l1_node = get_child(root_node, 1)
    l2_node = get_child(root_node, 2)
    l3_node = get_child(root_node, 3)
    l4_node = get_child(root_node, 4)

    assert l1_node is not None
    assert l2_node is not None
    assert l3_node is None
    assert l4_node is None
    assert len(l1_node.connected_nodes) == 0
    assert len(l2_node.connected_nodes) == 0


def test_simple_network_block_placement(simple_core_network):
    root_node = simple_core_network.root

    assert root_node is not None

    l1_node = get_child(root_node, 1)
    l2_node = get_child(root_node, 2)
    l3_node = get_child(root_node, 3)
    l4_node = get_child(root_node, 4)

    assert l1_node is not None
    assert l2_node is not None
    assert l3_node is None
    assert l4_node is None

    assert [block.id for block in root_node.blocks] == [0]
    assert [block.id for block in l1_node.blocks] == [1]
    assert [block.id for block in l2_node.blocks] == [2]
    assert sorted(
        [block.id for node in [root_node, l1_node, l2_node] for block in node.blocks]
    ) == [0, 1, 2]


def test_complex_network_keeps_deep_branch_structure(complex_core_network):
    root_node = complex_core_network.root

    assert root_node is not None

    l1_node = get_child(root_node, 1)
    l3_node = get_child(root_node, 3)
    l4_node = get_child(root_node, 4)

    assert l1_node is not None
    assert l3_node is not None
    assert l4_node is not None

    l2_node = get_child(l1_node, 2)
    l5_node = get_child(l1_node, 5)
    l6_node = get_child(l1_node, 6)

    assert l2_node is not None
    assert l5_node is not None
    assert l6_node is not None

    l7_node = get_child(l2_node, 7)
    assert l7_node is not None

    l8_node = get_child(l3_node, 8)
    l9_node = get_child(l4_node, 9)
    l10_node = get_child(l5_node, 10)
    l11_node = get_child(l6_node, 11)

    assert l8_node is not None
    assert l9_node is not None
    assert l10_node is not None
    assert l11_node is not None

    l12_node = get_child(l7_node, 12)
    assert l12_node is not None

    l13_node = get_child(l10_node, 13)
    assert l13_node is not None

    l14_node = get_child(l13_node, 14)
    assert l14_node is not None

    assert len(root_node.connected_nodes) == 3
    assert len(l1_node.connected_nodes) == 3
    assert len(l2_node.connected_nodes) == 1
    assert len(l3_node.connected_nodes) == 1
    assert len(l4_node.connected_nodes) == 1
    assert len(l5_node.connected_nodes) == 1
    assert len(l6_node.connected_nodes) == 1
    assert len(l7_node.connected_nodes) == 1
    assert len(l8_node.connected_nodes) == 0
    assert len(l9_node.connected_nodes) == 0
    assert len(l10_node.connected_nodes) == 1
    assert len(l11_node.connected_nodes) == 0
    assert len(l12_node.connected_nodes) == 0
    assert len(l13_node.connected_nodes) == 1
    assert len(l14_node.connected_nodes) == 0

    assert get_child(root_node, 7) is None
    assert get_child(root_node, 8) is None
    assert get_child(l1_node, 8) is None
    assert get_child(l1_node, 9) is None
    assert get_child(l2_node, 12) is None
    assert get_child(l3_node, 10) is None
    assert get_child(l4_node, 11) is None
    assert get_child(l5_node, 13) is None
    assert get_child(l6_node, 12) is None
    assert get_child(l7_node, 14) is None


def test_complex_network_block_placement(complex_core_network):
    root_node = complex_core_network.root

    assert root_node is not None

    l1_node = get_child(root_node, 1)
    l3_node = get_child(root_node, 3)
    l4_node = get_child(root_node, 4)

    assert l1_node is not None
    assert l3_node is not None
    assert l4_node is not None

    l2_node = get_child(l1_node, 2)
    l5_node = get_child(l1_node, 5)
    l6_node = get_child(l1_node, 6)

    assert l2_node is not None
    assert l5_node is not None
    assert l6_node is not None

    l7_node = get_child(l2_node, 7)
    assert l7_node is not None

    l8_node = get_child(l3_node, 8)
    l9_node = get_child(l4_node, 9)
    l10_node = get_child(l5_node, 10)
    l11_node = get_child(l6_node, 11)

    assert l8_node is not None
    assert l9_node is not None
    assert l10_node is not None
    assert l11_node is not None

    l12_node = get_child(l7_node, 12)
    assert l12_node is not None

    l13_node = get_child(l10_node, 13)
    assert l13_node is not None

    l14_node = get_child(l13_node, 14)
    assert l14_node is not None

    assert [block.id for block in root_node.blocks] == [0, 1]
    assert [block.id for block in l1_node.blocks] == [4]
    assert [block.id for block in l2_node.blocks] == [7]
    assert l3_node.blocks == []
    assert [block.id for block in l4_node.blocks] == [3]
    assert [block.id for block in l5_node.blocks] == [5]
    assert l6_node.blocks == []
    assert l7_node.blocks == []
    assert l8_node.blocks == []
    assert l9_node.blocks == []
    assert [block.id for block in l10_node.blocks] == [8]
    assert l11_node.blocks == []
    assert l12_node.blocks == []
    assert [block.id for block in l13_node.blocks] == [11]
    assert [block.id for block in l14_node.blocks] == [12]


def test_loop_network_keeps_mid_loop_structure(loop_core_network):
    root_node = loop_core_network.root

    assert root_node is not None
    assert root_node.line.id == 0
    assert len(root_node.connected_nodes) == 1

    l1_node = get_child(root_node, 1)
    assert l1_node is not None
    assert len(l1_node.connected_nodes) == 2

    l2_node = get_child(l1_node, 2)
    l5_node = get_child(l1_node, 5)

    assert l2_node is not None
    assert l5_node is not None

    l3_from_bottom = get_child(l2_node, 3)
    assert l3_from_bottom is not None

    l4_from_right = get_child(l3_from_bottom, 4)
    assert l4_from_right is not None

    l6_from_right = get_child(l5_node, 6)
    assert l6_from_right is not None

    # Shared loop segments should be consumed only once and not reconstructed
    # from sibling branches.
    assert l4_from_right.connected_nodes == []


def test_loop_network_block_placement(loop_core_network):
    root_node = loop_core_network.root

    assert root_node is not None

    l1_node = get_child(root_node, 1)
    assert l1_node is not None

    l2_node = get_child(l1_node, 2)
    l5_node = get_child(l1_node, 5)

    assert l2_node is not None
    assert l5_node is not None

    l3_node = get_child(l2_node, 3)
    assert l3_node is not None

    l4_node = get_child(l3_node, 4)
    assert l4_node is not None

    l6_node = get_child(l5_node, 6)
    assert l6_node is not None

    assert [block.id for block in root_node.blocks] == [0]
    assert [block.id for block in l1_node.blocks] == [1]
    assert [block.id for block in l2_node.blocks] == [2]
    assert [block.id for block in l3_node.blocks] == [3]
    assert [block.id for block in l4_node.blocks] == [4]
    assert [block.id for block in l5_node.blocks] == [5]
    assert [block.id for block in l6_node.blocks] == [6]
    assert sorted(
        [
            block.id
            for node in [
                root_node,
                l1_node,
                l2_node,
                l3_node,
                l4_node,
                l5_node,
                l6_node,
            ]
            for block in node.blocks
        ]
    ) == list(range(7))
