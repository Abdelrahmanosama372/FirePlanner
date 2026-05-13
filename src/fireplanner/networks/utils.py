from fireplanner.geometry.primitives.line import Line


def find_collinear_edge_ids(edge_id_line_map: dict[int, Line]) -> list[int]:
    best_pair: list[int] | None = None
    best_angle = float("inf")

    edges_ids = list(edge_id_line_map.keys())
    for first_index in range(len(edges_ids)):
        for second_index in range(first_index + 1, len(edges_ids)):
            first_line = edge_id_line_map[edges_ids[first_index]]
            second_line = edge_id_line_map[edges_ids[second_index]]
            angle = min(
                first_line.angle_to(second_line),
                abs(180.0 - first_line.angle_to(second_line)),
            )
            if angle < best_angle:
                best_angle = angle
                best_pair = [edges_ids[first_index], edges_ids[second_index]]

    if best_pair is None:
        raise ValueError("Could not find collinear pair of edges for tee placement.")

    return best_pair
