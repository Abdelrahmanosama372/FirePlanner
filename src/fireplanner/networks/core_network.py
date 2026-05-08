from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ..geometry.primitives import Block, Line, Point
from .junction import Junction, JunctionType


@dataclass
class CoreNetworkConfig:
    sprinkler_block_data: dict[str, dict[str, Any]] = field(default_factory=dict)
    sprinkler_blocks: list[Block] = field(default_factory=list)
    lines: list[Line] = field(default_factory=list)
    root_line: Line | None = None

    def ordered_lines(self) -> list[Line]:
        if self.root_line is None:
            return list(self.lines)

        return [self.root_line] + [
            line for line in self.lines if line.id != self.root_line.id
        ]


class CoreNode:
    def __init__(self, line: Line):
        self._edge = line
        self._intersection_point: Point | None = None
        self._connected_nodes: list[CoreNode] = []

    @property
    def edge(self) -> Line:
        return self._edge

    @property
    def line(self) -> Line:
        return self._edge

    @property
    def edges(self) -> list[Line]:
        return [self._edge]

    @property
    def intersection_point(self) -> Point | None:
        return self._intersection_point

    def set_intersection_point(self, point: Point) -> None:
        self._intersection_point = point

    @property
    def connected_nodes(self) -> list[CoreNode]:
        return self._connected_nodes

    def add_node(self, node: CoreNode) -> None:
        self._connected_nodes.append(node)

    def get_connected_nodes_number(self) -> int:
        return len(self._connected_nodes)

    def get_connected_nodes(self) -> list[CoreNode]:
        return self._connected_nodes

    def to_json(self) -> dict[str, Any]:
        return {
            "CoreNode": {
                "id": self.edge.id,
                "edge": self.edge.to_json(),
                "intersection_point": (
                    self.intersection_point.to_json()
                    if self.intersection_point is not None
                    else None
                ),
                "connected_nodes": [
                    connected_node.to_json() for connected_node in self.connected_nodes
                ],
            }
        }


class CoreNetwork:
    def __init__(
        self,
        sprinkles: list[object] | None = None,
        lines: list[Line] | None = None,
        blocks: list[object] | None = None,
    ):
        if sprinkles is None:
            sprinkles = []

        if lines is None:
            lines = []

        self._sprinkles = list(sprinkles)
        self._lines = list(lines)
        self._root: CoreNode | None = None
        self._edge_sprinkler_map: dict[int, int] = {}
        self._junctions: dict[int, Junction] = {}
        self._next_created_line_id = 1
        self._next_junction_id = 1

        if not self._lines:
            return

        root_line = self._lines[0]
        remaining_lines = self._lines[1:]
        self._preprocessing(root_line, remaining_lines)
        self._root = self._create_network(root_line, remaining_lines)
        self.create_sprinkler_map()

    @property
    def sprinkles(self) -> list[object]:
        return self._sprinkles

    @property
    def root(self) -> CoreNode | None:
        return self._root

    def find_edge_sprinkler_count(self, edge_id: int) -> int | None:
        return self._edge_sprinkler_map.get(edge_id)

    def get_edge_junction_ids(self) -> dict[int, tuple[int | None, int | None]]:
        junction_origin_id_map = {
            junction.origin: junction.id for junction in self.get_junctions().values()
        }
        return {
            edge_id: (
                junction_origin_id_map.get(line.start),
                junction_origin_id_map.get(line.end),
            )
            for edge_id, line in self.get_lines_with_edge_ids().items()
        }

    def _preprocessing(
        self,
        root_line: Line,
        lines: list[Line],
        visited_line_ids: set[int] | None = None,
    ) -> list[Line]:
        if visited_line_ids is None:
            visited_line_ids = {root_line.id}

        intersected_lines: list[Line] = []
        for line in lines:
            if line.id in visited_line_ids:
                continue

            intersects, _ = root_line.intersects_line_2D(line)
            if not intersects:
                continue

            if root_line.pass_through_point(line.end):
                line.swap_end_points()

            intersected_lines.append(line)

        processed_lines: list[Line] = []
        for line in intersected_lines:
            visited_line_ids.add(line.id)
            processed_lines.append(line)
            processed_lines.extend(self._preprocessing(line, lines, visited_line_ids))

        return processed_lines

    def _create_network(self, root_line: Line, lines: list[Line]) -> CoreNode:
        self._next_created_line_id = 1
        return self._create_network_recursive(root_line, list(lines), {root_line.id})

    def _create_network_recursive(
        self,
        root_line: Line,
        lines: list[Line],
        visited_line_ids: set[int],
    ) -> CoreNode:
        intersected_lines: list[tuple[Line, Point]] = []
        split_points: list[Point] = []

        for sprinkle in self._sprinkles:
            if root_line.pass_through_point(sprinkle.center):
                split_points.append(sprinkle.center)

        for line in lines:
            if line.id in visited_line_ids:
                continue

            intersects, intersection_point = root_line.intersects_line_2D(line)
            if not intersects or intersection_point is None:
                continue

            intersected_lines.append((line, intersection_point))
            split_points.append(intersection_point)

        sorted_split_points = sorted(
            split_points,
            key=lambda point: root_line.start.distance(point),
        )

        sorted_intersected_lines = sorted(
            intersected_lines,
            key=lambda item: root_line.start.distance(item[1]),
        )

        split_lines = root_line.split_at_unchecked(sorted_split_points)
        if not split_lines:
            split_lines = [root_line]

        for split_line in split_lines:
            split_line.id = self._next_created_line_id
            self._next_created_line_id += 1

        root_node = CoreNode(split_lines[0])
        segment_nodes = [root_node]
        previous_node = root_node

        for split_line in split_lines[1:]:
            node = CoreNode(split_line)
            node.set_intersection_point(split_line.start)
            previous_node.add_node(node)
            segment_nodes.append(node)
            previous_node = node

        for line, intersection_point in sorted_intersected_lines:
            visited_line_ids.add(line.id)
            child_node = self._create_network_recursive(line, lines, visited_line_ids)
            child_node.set_intersection_point(intersection_point)

            parent_node = next(
                (node for node in segment_nodes if node.edge.end == intersection_point),
                segment_nodes[-1],
            )
            parent_node.add_node(child_node)

        return root_node

    def create_sprinkler_map(self) -> dict[int, int]:
        self._edge_sprinkler_map = {}
        if self.root is None:
            return self._edge_sprinkler_map

        self._create_sprinkler_map_recursive(self.root)
        return self._edge_sprinkler_map

    def _create_sprinkler_map_recursive(self, core_node: CoreNode) -> int:
        connected_nodes_sprinklers = sum(
            self._create_sprinkler_map_recursive(connected_node)
            for connected_node in core_node.connected_nodes
        )

        current_edge_sprinklers = int(
            any(sprinkle.center == core_node.edge.end for sprinkle in self.sprinkles)
        )

        total_sprinklers = current_edge_sprinklers + connected_nodes_sprinklers
        self._edge_sprinkler_map[core_node.edge.id] = total_sprinklers
        return total_sprinklers

    def get_junctions(self) -> dict[int, Junction]:
        if self._junctions:
            return self._junctions
        if self.root is None:
            return self._junctions

        self._junctions = {}
        self._next_junction_id = 1
        self._get_junctions_recursive(self.root)
        return self._junctions

    def _get_junctions_recursive(self, core_node: CoreNode) -> None:
        if core_node.connected_nodes:
            # nodes are connected from start point
            # root node has no intersection_point since nothing connects to it from top
            intersection_point = (
                core_node.connected_nodes[0].intersection_point or core_node.edge.end
            )
            connected_edges_ids = [core_node.edge.id] + [
                connected_node.edge.id for connected_node in core_node.connected_nodes
            ]

            if len(connected_edges_ids) == 2:
                junction_type: JunctionType | None = JunctionType.TWO_WAY
            elif len(connected_edges_ids) == 3:
                junction_type = JunctionType.THREE_WAY
            else:
                junction_type = None

            junction = Junction(
                id=self._next_junction_id,
                origin=intersection_point,
                junction_type=junction_type,
                connected_edges_ids=connected_edges_ids,
                angle=(
                    core_node.edge.angle_to(core_node.connected_nodes[0].edge)
                    if junction_type == JunctionType.TWO_WAY
                    else None
                ),
                has_sprinkler=any(
                    sprinkle.center == intersection_point for sprinkle in self.sprinkles
                ),
            )
            self._junctions[junction.id] = junction
            self._next_junction_id += 1

        for connected_node in core_node.connected_nodes:
            self._get_junctions_recursive(connected_node)

    def get_edges_ids(self) -> list[int]:
        if self.root is None:
            return []

        edges_ids: list[int] = []
        self._get_edges_ids_recursive(self.root, edges_ids)
        return edges_ids

    def _get_edges_ids_recursive(
        self,
        core_node: CoreNode,
        edges_ids: list[int],
    ) -> None:
        edges_ids.append(core_node.edge.id)
        for connected_node in core_node.connected_nodes:
            self._get_edges_ids_recursive(connected_node, edges_ids)

    def get_lines_with_edge_ids(self) -> dict[int, Line]:
        if self.root is None:
            return {}

        edge_id_line_map: dict[int, Line] = {}
        self._get_lines_with_edge_ids_recursive(self.root, edge_id_line_map)
        return edge_id_line_map

    def _get_lines_with_edge_ids_recursive(
        self,
        core_node: CoreNode,
        edge_id_line_map: dict[int, Line],
    ) -> None:
        edge_id_line_map[core_node.edge.id] = core_node.edge
        for connected_node in core_node.connected_nodes:
            self._get_lines_with_edge_ids_recursive(
                connected_node,
                edge_id_line_map,
            )

    def to_json(self) -> dict[str, Any]:
        return {
            "CoreNetwork": {
                "sprinkles": [sprinkle.to_json() for sprinkle in self.sprinkles],
                "lines": [line.to_json() for line in self._lines],
                "root": self.root.to_json() if self.root is not None else None,
            }
        }
