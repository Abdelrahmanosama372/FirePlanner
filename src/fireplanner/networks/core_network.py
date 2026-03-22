from __future__ import annotations

from ..geometry.primitives import Block, Line


class CoreNode:
    def __init__(self, line: Line):
        self._line: Line = line
        self._blocks: list[Block] = []
        self._nodes: list[CoreNode] = []

    @property
    def line(self) -> Line:
        return self._line

    @property
    def blocks(self) -> list[Block]:
        return self._blocks

    @property
    def connected_nodes(self) -> list[CoreNode]:
        return self._nodes

    def add_block(self, block: Block) -> None:
        if isinstance(block, Block):
            self._blocks.append(block)
            return
        raise TypeError("block must be an instance of Block")

    def add_node(self, node: CoreNode) -> None:
        if isinstance(node, CoreNode):
            self._nodes.append(node)
            return
        raise TypeError("node must be an instance of CoreNode")


class CoreNetwork:
    def __init__(self, lines: list[Line], blocks: list[Block]):
        self._root: CoreNode | None = self._create_network(lines, blocks)

    @property
    def root(self) -> CoreNode | None:
        return self._root

    def _create_network(
        self, lines: list[Line], blocks: list[Block]
    ) -> CoreNode | None:
        if not lines:
            return None

        root_line = lines[0]
        remaining_lines = lines[1:]
        return self._create_network_recursive(root_line, remaining_lines, blocks)

    def _create_network_recursive(
        self, root_line: Line, lines: list[Line], blocks: list[Block]
    ) -> CoreNode:
        """
        Build a network node for `root_line`.

        - Create a `CoreNode` for the current line.
        - Attach every block that lies on the current line.
        - Find child lines by checking intersections with the current line.
        - Recursively build child nodes using a shared mutable pool of
          remaining unvisited lines so descendants are not reconstructed by
          sibling branches.
        """

        node = CoreNode(root_line)

        remaining_blocks: list[Block] = []
        for block in blocks:
            if root_line.pass_through_point(block.center):
                node.add_block(block)
            else:
                remaining_blocks.append(block)

        child_lines: list[Line] = []
        next_remaining_lines: list[Line] = []
        for line in lines:
            intersects, _ = root_line.intersects_line_2D(line)
            if intersects:
                child_lines.append(line)
            else:
                next_remaining_lines.append(line)

        # Remove direct children from the shared remaining-lines pool before
        # recursing so each branch consumes from the same unvisited set.
        lines[:] = next_remaining_lines

        for child_line in child_lines:
            child_node = self._create_network_recursive(
                child_line,
                lines,
                remaining_blocks,
            )
            used_block_ids = {block.id for block in child_node.blocks}
            remaining_blocks = [
                block for block in remaining_blocks if block.id not in used_block_ids
            ]
            node.add_node(child_node)

        return node
