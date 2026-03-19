import pytest
from fireplanner.geometry.primitives import Block, Line, Point
from fireplanner.networks import CoreNetwork


@pytest.fixture
def simple_network():
    """
                 (0,9)------(6,9)
                  |
                  |
                  |
    (-6,3)------(0,3)------(4,3)
                  |
                  |
                  |
                (0,0)
    """
    l0 = Line(start=Point(x=0, y=0), end=Point(x=0, y=3))
    l1 = Line(start=Point(x=0, y=3), end=Point(x=4, y=3))
    l2 = Line(start=Point(x=0, y=3), end=Point(x=-6, y=3))
    l3 = Line(start=Point(x=0, y=3), end=Point(x=0, y=9))
    l4 = Line(start=Point(x=0, y=9), end=Point(x=6, y=9))

    lines = [l0, l1, l2, l3, l4]

    b0 = Block(name="SPR", position=Point(x=0, y=2))
    b1 = Block(name="SPR", position=Point(x=2, y=3))
    b2 = Block(name="SPR", position=Point(x=-4, y=3))
    b3 = Block(name="SPR", position=Point(x=0, y=8))
    b4 = Block(name="SPR", position=Point(x=1, y=9))

    blocks = [b0, b1, b2, b3, b4]
    return lines, blocks


@pytest.fixture
def complex_network():
    """
                (16,14)
                  |
                  |
    ( -12,10)--(-8,10)--(0,10)--(8,10)--(12,10)--(12,14)--(16,14)
                  |         |
                  |         |
            (-6,5)--(0,5)--(6,5)--(10,5)
                  |
                  |
                (0,0)
    """
    # Main vertical spine
    l0 = Line(start=Point(x=0, y=0), end=Point(x=0, y=5))
    l1 = Line(start=Point(x=0, y=5), end=Point(x=0, y=10))
    l2 = Line(start=Point(x=0, y=10), end=Point(x=0, y=15))

    # First level branches
    l3 = Line(start=Point(x=0, y=5), end=Point(x=6, y=5))
    l4 = Line(start=Point(x=0, y=5), end=Point(x=-6, y=5))

    l5 = Line(start=Point(x=0, y=10), end=Point(x=8, y=10))
    l6 = Line(start=Point(x=0, y=10), end=Point(x=-8, y=10))

    l7 = Line(start=Point(x=0, y=15), end=Point(x=5, y=15))

    # Second level branches
    l8 = Line(start=Point(x=6, y=5), end=Point(x=10, y=5))
    l9 = Line(start=Point(x=-6, y=5), end=Point(x=-10, y=5))

    l10 = Line(start=Point(x=8, y=10), end=Point(x=12, y=10))
    l11 = Line(start=Point(x=-8, y=10), end=Point(x=-12, y=10))

    l12 = Line(start=Point(x=5, y=15), end=Point(x=9, y=18))

    # Third level branch (adds asymmetry and depth)
    l13 = Line(start=Point(x=12, y=10), end=Point(x=12, y=14))
    l14 = Line(start=Point(x=12, y=14), end=Point(x=16, y=14))

    lines = [l0, l1, l2, l3, l4, l5, l6, l7, l8, l9, l10, l11, l12, l13, l14]

    # Blocks distributed across different hierarchy levels
    b0 = Block(name="SRC", position=Point(x=0, y=0))

    b1 = Block(name="SPR", position=Point(x=0, y=3))
    b2 = Block(name="SPR", position=Point(x=4, y=5))
    b3 = Block(name="SPR", position=Point(x=-3, y=5))

    b4 = Block(name="SPR", position=Point(x=0, y=8))
    b5 = Block(name="SPR", position=Point(x=6, y=10))
    b6 = Block(name="SPR", position=Point(x=-5, y=10))

    b7 = Block(name="SPR", position=Point(x=0, y=13))
    b8 = Block(name="SPR", position=Point(x=9, y=10))
    b9 = Block(name="SPR", position=Point(x=-10, y=10))

    b10 = Block(name="SPR", position=Point(x=6, y=16))
    b11 = Block(name="SPR", position=Point(x=12, y=12))
    b12 = Block(name="SPR", position=Point(x=15, y=14))

    blocks = [b0, b1, b2, b3, b4, b5, b6, b7, b8, b9, b10, b11, b12]

    return lines, blocks


@pytest.fixture
def simple_core_network(simple_network):
    lines, blocks = simple_network
    return CoreNetwork(lines=lines, blocks=blocks)


@pytest.fixture
def complex_core_network(complex_network):
    lines, blocks = complex_network
    return CoreNetwork(lines=lines, blocks=blocks)


def test_construct_simple_network(simple_core_network):
    net = simple_core_network

    assert net is not None


def test_construct_complex_network(complex_core_network):
    net = complex_core_network

    assert net is not None


## topology correctness
# def test_simple_network_node_count(simple_core_network):
#     net = simple_core_network
#
#     assert len(net.nodes) == 6
#
#
# def test_simple_network_edge_count(simple_core_network):
#     net = simple_core_network
#
#     assert len(net.edges) == 5
#
#
# def test_junction_degree(simple_core_network):
#     net = simple_core_network
#
#     node = net.get_node_at(Point(0, 3))
#
#     assert net.degree(node) == 4


## connectivity tests
# def test_network_is_connected(simple_core_network):
#     net = simple_core_network
#
#     assert net.is_connected()
#
#
# def test_path_exists(simple_core_network):
#     net = simple_core_network
#
#     start = Point(0,0)
#     end   = Point(6,9)
#
#     path = net.find_path(start, end)
#
#     assert path is not None
#     assert len(path) > 0

## block assotiation tests
# def test_blocks_attached(simple_core_network):
#     net = simple_core_network
#
#     assert len(net.blocks) == 5
#
#
# def test_block_has_parent_edge(simple_core_network):
#     net = simple_core_network
#
#     block = net.blocks[0]
#
#     assert block.edge is not None

## query tests
# def test_find_nearest_node(simple_core_network):
#     net = simple_core_network
#
#     node = net.find_nearest_node(Point(0.1, 3.1))
#
#     assert node.position == Point(0,3)
#
#
# def test_find_edge_at(simple_core_network):
#     net = simple_core_network
#
#     edge = net.find_edge_at(Point(0,2))
#
#     assert edge is not None

## graph integrity tests
# def test_all_edges_have_valid_nodes(simple_core_network):
#     net = simple_core_network
#
#     for edge in net.edges:
#         assert edge.start in net.nodes
#         assert edge.end in net.nodes
#
#
# def test_no_duplicate_nodes(simple_core_network):
#     net = simple_core_network
#
#     positions = [node.position for node in net.nodes]
#
#     assert len(set(positions)) == len(positions)

## traversal tests
# def test_traverse_from_root(simple_core_network):
#     net = simple_core_network
#
#     root = net.get_node_at(Point(0,0))
#
#     visited = list(net.traverse(root))
#
#     assert len(visited) == len(net.nodes)

## edge cases
## validation tests
