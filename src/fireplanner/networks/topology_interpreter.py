from fireplanner.geometry.primitives import Block, Line
from fireplanner.networks.junction import Junction, JunctionType
from fireplanner.networks.junction_info import (
    EdgeInfo,
    FourWayJunctionInfo,
    JunctionInfo,
    SprinklerInfo,
    SprinklerJunctionInfo,
    ThreeWayJunctionInfo,
    TwoWayJunctionInfo,
)


class TopologyInterpreter:
    def __init__(
        self,
        edge_id_line_map: dict[int, Line],
        edge_id_elevation_map: dict[int, int],
        edge_id_sprinkler_map: dict[int, int],
        sprinkler_blocks: list[Block] | None = None,
        sprinkler_block_data: dict[str, dict[str, float]] | None = None,
    ) -> None:
        self._edge_id_line_map = edge_id_line_map
        self._edge_id_sprinkler_map = edge_id_sprinkler_map
        self._edge_id_elevation_map = edge_id_elevation_map
        self._sprinkler_blocks = sprinkler_blocks or []
        self._sprinkler_block_data = sprinkler_block_data or {}

    def interpret_junction(self, junction: Junction) -> JunctionInfo:
        edge_infos = [
            self._edge_info(edge_id) for edge_id in junction.connected_edges_ids
        ]

        if junction.junction_type == JunctionType.TWO_WAY:
            sprinkler_info = self._sprinkler_info_for_junction(junction)
            if sprinkler_info is not None:
                return SprinklerJunctionInfo(
                    junction_id=junction.id,
                    origin=junction.origin,
                    edges=edge_infos,
                    angle=junction.angle,
                    sprinkler_info=sprinkler_info,
                )
            return TwoWayJunctionInfo(
                junction_id=junction.id,
                origin=junction.origin,
                edges=edge_infos,
                angle=junction.angle,
            )

        if junction.junction_type == JunctionType.THREE_WAY:
            run_edge_ids = self._find_collinear_edge_ids(junction.connected_edges_ids)
            run = [self._edge_info(edge_id) for edge_id in run_edge_ids]
            branch_id = next(
                edge_id
                for edge_id in junction.connected_edges_ids
                if edge_id not in run_edge_ids
            )
            return ThreeWayJunctionInfo(
                junction_id=junction.id,
                origin=junction.origin,
                run=run,
                branch=self._edge_info(branch_id),
            )

        if junction.junction_type == JunctionType.FOUR_WAY:
            first_run_ids = self._find_collinear_edge_ids(junction.connected_edges_ids)
            second_run_ids = [
                edge_id
                for edge_id in junction.connected_edges_ids
                if edge_id not in first_run_ids
            ]
            if len(second_run_ids) != 2:
                raise ValueError(
                    f"Junction {junction.id} does not contain two edge pairs."
                )

            first_run = [self._edge_info(edge_id) for edge_id in first_run_ids]
            second_run = [self._edge_info(edge_id) for edge_id in second_run_ids]
            self._validate_four_way_runs(junction.id, first_run, second_run)

            runs = sorted(
                (first_run, second_run),
                key=lambda run: run[0].elevation,
            )
            return FourWayJunctionInfo(
                junction_id=junction.id,
                origin=junction.origin,
                lower_run=runs[0],
                upper_run=runs[1],
            )

        return JunctionInfo(junction_id=junction.id, origin=junction.origin)

    def _validate_four_way_runs(
        self,
        junction_id: int,
        first_run: list[EdgeInfo],
        second_run: list[EdgeInfo],
    ) -> None:
        for run in (first_run, second_run):
            run_angle = min(
                run[0].line.angle_to(run[1].line),
                abs(180.0 - run[0].line.angle_to(run[1].line)),
            )
            if run_angle > 1.0:
                raise ValueError(
                    f"Four-way junction {junction_id} requires two collinear pairs."
                )

        if first_run[0].elevation != first_run[1].elevation or (
            second_run[0].elevation != second_run[1].elevation
        ):
            raise ValueError(
                f"Four-way junction {junction_id} requires one COP per collinear pair."
            )
        if first_run[0].elevation == second_run[0].elevation:
            raise ValueError(
                f"Four-way junction {junction_id} requires two different COP values."
            )

        first_line = first_run[0].line
        second_line = second_run[0].line
        angle = min(
            first_line.angle_to(second_line),
            abs(180.0 - first_line.angle_to(second_line)),
        )
        if abs(angle - 90.0) > 1.0:
            raise ValueError(
                f"Four-way junction {junction_id} requires perpendicular runs."
            )

    def _edge_info(self, edge_id: int) -> EdgeInfo:
        line = self._edge_id_line_map[edge_id]
        sprinkler_count = self._edge_id_sprinkler_map[edge_id]
        line_elevation = self._edge_id_elevation_map[edge_id]
        return EdgeInfo(
            edge_id=edge_id,
            line=line,
            length=line.length(),
            sprinkler_count=sprinkler_count,
            elevation=line_elevation,
        )

    def _find_collinear_edge_ids(self, edge_ids: list[int]) -> list[int]:
        best_pair: list[int] | None = None
        best_angle = float("inf")

        for first_index in range(len(edge_ids)):
            for second_index in range(first_index + 1, len(edge_ids)):
                first_line = self._edge_id_line_map[edge_ids[first_index]]
                second_line = self._edge_id_line_map[edge_ids[second_index]]
                angle = min(
                    first_line.angle_to(second_line),
                    abs(180.0 - first_line.angle_to(second_line)),
                )
                if angle < best_angle:
                    best_angle = angle
                    best_pair = [edge_ids[first_index], edge_ids[second_index]]

        if best_pair is None:
            raise ValueError(
                "Could not find a collinear pair of edges for three-way junction."
            )

        return best_pair

    def _sprinkler_info_for_junction(self, junction: Junction) -> SprinklerInfo | None:
        if not junction.has_sprinkler:
            return None

        block = next(
            (
                sprinkler_block
                for sprinkler_block in self._sprinkler_blocks
                if sprinkler_block.center == junction.origin
            ),
            None,
        )
        if block is None:
            return None

        metadata = self._sprinkler_block_data.get(block.name, {})
        if "k_factor" not in metadata or "temperature" not in metadata:
            return None

        return SprinklerInfo(
            k_factor=float(metadata["k_factor"]),
            temperature=float(metadata["temperature"]),
        )
