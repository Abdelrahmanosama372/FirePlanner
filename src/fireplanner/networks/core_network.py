from __future__ import annotations
from ..geometry.primitives import Block, Line


class CoreNode:
    def __init__(self, line: Line):
        self._line: Line = line
        self._blocks: list[Block] = []
        self._nodes: list[CoreNode] = []

    @property
    def line(self):
        return self._line

    @property
    def blocks(self):
        return self._blocks

    @property
    def connected_nodes(self):
        return self._nodes

    def add_block(self, block: Block):
        if isinstance(block, Block):
            self._blocks.append(block)
        else:
            # todo throw exception
            pass

    def add_node(self, node: CoreNode):
        if isinstance(node, CoreNode):
            self._nodes.append(node)
        else:
            # todo throw exception
            pass


class CoreNetwork:
    def __init__(self, lines: list[Line], blocks: list[Block]):
        self._root: CoreNode = self._create_network(lines, blocks)
        pass

    def _create_network(self, lines: list[Line], blocks: list[Block]):
        pass

    # def __iter__(self):
    #     self._curr_node = self._root
    #     return self
    #
    # def __next__(self):
    #     if self._curr_node is None:
    #         return StopIteration
    #     else:
    #         node = self._curr_node
    #         self._curr_node
    #         return node
