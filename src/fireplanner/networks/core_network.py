from __future__ import annotations

from ..geometry.primitives import Block, Line, Point


class CoreNode:
    def __init__(self, line: Line):
        self._line: Line = line
        self._blocks: list[Block] = []
        self._nodes: list[CoreNode] = []
        self._intersection_points: dict[Point, CoreNode] = {}
        self._edges: list[Line] | None = None

    @property
    def line(self) -> Line:
        return self._line

    @property
    def blocks(self) -> list[Block]:
        return self._blocks

    @property
    def connected_nodes(self) -> list[CoreNode]:
        return self._nodes

    @property
    def intersection_points(self) -> dict[Point, CoreNode]:
        return self._intersection_points

    def find_intersection_points(self) -> list[Point]:
        return list(self._intersection_points.keys())

    def find_intersection_points_with_nodes(self) -> dict[Point, CoreNode]:
        return self._intersection_points

    @property
    def edges(self) -> list[Line]:
        if self._edges is None:
            self._edges = self._construct_edges()
        return self._edges

    def add_block(self, block: Block) -> None:
        if isinstance(block, Block):
            self._blocks.append(block)
            return
        raise TypeError("block must be an instance of Block")

    def add_node(self, node: CoreNode, intersection_point: Point) -> None:
        if not isinstance(node, CoreNode):
            raise TypeError("node must be an instance of CoreNode")
        if not isinstance(intersection_point, Point):
            raise TypeError("intersection_point must be an instance of Point")

        self._nodes.append(node)
        self._intersection_points[intersection_point] = node
        self._edges = None

    def _construct_edges(self) -> list[Line]:
        sorted_points = sorted(
            self.find_intersection_points(),
            key=lambda point: self.line.start.distance(point),
        )

        edge_points = [self.line.start]
        for point in sorted_points:
            if point == edge_points[-1]:
                continue
            edge_points.append(point)
        if edge_points[-1] != self.line.end:
            edge_points.append(self.line.end)

        edges: list[Line] = []
        for edge_id, (start, end) in enumerate(
            zip(edge_points, edge_points[1:]),
            start=1,
        ):
            if start == end:
                continue
            edges.append(
                Line(
                    id=edge_id,
                    start=start,
                    end=end,
                    line_type=self.line.line_type,
                )
            )

        if not edges:
            return [
                Line(
                    id=1,
                    start=self.line.start,
                    end=self.line.end,
                    line_type=self.line.line_type,
                )
            ]

        return edges


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

        child_lines: list[tuple[Line, Point]] = []
        next_remaining_lines: list[Line] = []
        for line in lines:
            intersects, intersection_point = root_line.intersects_line_2D(line)
            if intersects:
                if intersection_point is None:
                    continue
                child_lines.append((line, intersection_point))
            else:
                next_remaining_lines.append(line)

        # Remove direct children from the shared remaining-lines pool before
        # recursing so each branch consumes from the same unvisited set.
        lines[:] = next_remaining_lines

        for child_line, intersection_point in child_lines:
            child_node = self._create_network_recursive(
                child_line,
                lines,
                remaining_blocks,
            )
            used_block_ids = {block.id for block in child_node.blocks}
            remaining_blocks = [
                block for block in remaining_blocks if block.id not in used_block_ids
            ]
            node.add_node(child_node, intersection_point)

        return node
