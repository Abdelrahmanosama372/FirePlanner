from __future__ import annotations

from dataclasses import dataclass
from math import atan2, cos, isclose, pi, sin, sqrt

from fireplanner.geometry.primitives import (
    Arc,
    Circle,
    Line,
    Point,
    Primitive2D,
    Rectangle,
)
from fireplanner.geometry.primitives.line import LineType

EPS = 1e-9


@dataclass
class PrimitivePartition:
    visible: list[Primitive2D]
    hidden: list[Primitive2D]


class PrimitiveVisibilityResolver:
    def resolve(
        self,
        occupancy_region: Rectangle,
        primitive: Arc | Line | Circle,
    ) -> PrimitivePartition:
        if isinstance(primitive, Line):
            return self._resolve_line(occupancy_region, primitive)
        if isinstance(primitive, Arc):
            return self._resolve_arc(occupancy_region, primitive)
        if isinstance(primitive, Circle):
            return self._resolve_circle(occupancy_region, primitive)
        raise TypeError(f"Unsupported primitive type: {type(primitive).__name__}")

    def _resolve_line(self, rect: Rectangle, line: Line) -> PrimitivePartition:
        clipped = self._clip_line_to_rect(line, rect)
        if clipped is None:
            return PrimitivePartition(visible=[line], hidden=[])

        hidden = [
            Line(
                start=clipped.start,
                end=clipped.end,
                line_type=LineType.Hidden,
            )
        ]
        visible: list[Primitive2D] = []
        if line.start != clipped.start:
            visible.append(
                Line(start=line.start, end=clipped.start, line_type=line.line_type)
            )
        if clipped.end != line.end:
            visible.append(
                Line(start=clipped.end, end=line.end, line_type=line.line_type)
            )
        return PrimitivePartition(visible=visible, hidden=hidden)

    def _resolve_circle(self, rect: Rectangle, circle: Circle) -> PrimitivePartition:
        intervals = self._build_circle_intervals(rect, circle)
        if len(intervals) == 1:
            if intervals[0][2]:
                return PrimitivePartition(
                    visible=[],
                    hidden=[
                        Circle(
                            center=circle.center,
                            radius=circle.radius,
                            line_type=LineType.Hidden,
                        )
                    ],
                )
            return PrimitivePartition(visible=[circle], hidden=[])

        visible: list[Primitive2D] = []
        hidden: list[Primitive2D] = []
        for start_theta, end_theta, is_hidden in intervals:
            sweep = end_theta - start_theta
            if sweep <= EPS:
                continue
            start = Point(
                x=circle.center.x + circle.radius * cos(start_theta),
                y=circle.center.y + circle.radius * sin(start_theta),
            )
            seg = Arc(
                start=start,
                center=circle.center,
                angle=sweep,
                line_type=LineType.Hidden if is_hidden else circle.line_type,
            )
            if is_hidden:
                hidden.append(seg)
            else:
                visible.append(seg)
        return PrimitivePartition(visible=visible, hidden=hidden)

    def _resolve_arc(self, rect: Rectangle, arc: Arc) -> PrimitivePartition:
        intervals = self._build_arc_intervals(rect, arc)
        visible: list[Primitive2D] = []
        hidden: list[Primitive2D] = []
        for t0, t1, is_hidden in intervals:
            dt = t1 - t0
            if dt <= EPS:
                continue
            start_theta = self._arc_start_theta(arc) + dt * 0 + t0 * arc.angle
            start = Point(
                x=arc.center.x + self._arc_radius(arc) * cos(start_theta),
                y=arc.center.y + self._arc_radius(arc) * sin(start_theta),
            )
            seg = Arc(
                start=start,
                center=arc.center,
                angle=arc.angle * dt,
                line_type=LineType.Hidden if is_hidden else arc.line_type,
            )
            if is_hidden:
                hidden.append(seg)
            else:
                visible.append(seg)
        return PrimitivePartition(visible=visible, hidden=hidden)

    def _clip_line_to_rect(self, line: Line, rect: Rectangle) -> Line | None:
        points: list[tuple[float, Point]] = []

        def _line_param(point: Point) -> float:
            dx = line.end.x - line.start.x
            dy = line.end.y - line.start.y
            if abs(dx) >= abs(dy):
                if abs(dx) <= EPS:
                    return 0.0
                return (point.x - line.start.x) / dx
            if abs(dy) <= EPS:
                return 0.0
            return (point.y - line.start.y) / dy

        if self._point_in_rect(line.start, rect):
            points.append((0.0, line.start))
        if self._point_in_rect(line.end, rect):
            points.append((1.0, line.end))

        for edge_start, edge_end in self._rect_edges(rect):
            hit, intersection = line.intersects_line_2D(
                Line(start=edge_start, end=edge_end)
            )
            if not hit or intersection is None:
                continue
            t = _line_param(intersection)
            if -EPS <= t <= 1.0 + EPS:
                points.append((max(0.0, min(1.0, t)), intersection))

        if len(points) < 2:
            return None

        points = sorted(points, key=lambda item: item[0])
        unique: list[tuple[float, Point]] = []
        for t, point in points:
            if unique and abs(unique[-1][0] - t) <= 1e-7:
                continue
            unique.append((t, point))

        if len(unique) < 2:
            return None

        return Line(
            start=unique[0][1],
            end=unique[-1][1],
            line_type=line.line_type,
        )

    def _build_circle_intervals(
        self,
        rect: Rectangle,
        circle: Circle,
    ) -> list[tuple[float, float, bool]]:
        cuts = [0.0, 2 * pi]
        for p in self._circle_rect_intersections(rect, circle.center, circle.radius):
            cuts.append(
                self._normalize_angle(
                    atan2(p.y - circle.center.y, p.x - circle.center.x)
                )
            )
        cuts = sorted(set(round(c, 9) for c in cuts))
        if cuts[-1] < 2 * pi:
            cuts.append(2 * pi)

        intervals: list[tuple[float, float, bool]] = []
        for a0, a1 in zip(cuts, cuts[1:]):
            mid = (a0 + a1) / 2
            p = Point(
                x=circle.center.x + circle.radius * cos(mid),
                y=circle.center.y + circle.radius * sin(mid),
            )
            intervals.append((a0, a1, self._point_in_rect(p, rect)))
        return self._merge_intervals(intervals)

    def _build_arc_intervals(
        self,
        rect: Rectangle,
        arc: Arc,
    ) -> list[tuple[float, float, bool]]:
        radius = self._arc_radius(arc)
        start_theta = self._arc_start_theta(arc)
        cuts = [0.0, 1.0]
        for p in self._circle_rect_intersections(rect, arc.center, radius):
            theta = atan2(p.y - arc.center.y, p.x - arc.center.x)
            t = self._arc_param_from_theta(start_theta, arc.angle, theta)
            if t is not None:
                cuts.append(t)
        cuts = sorted(set(round(c, 9) for c in cuts))

        intervals: list[tuple[float, float, bool]] = []
        for t0, t1 in zip(cuts, cuts[1:]):
            mid_t = (t0 + t1) / 2
            theta = start_theta + arc.angle * mid_t
            p = Point(
                x=arc.center.x + radius * cos(theta),
                y=arc.center.y + radius * sin(theta),
            )
            intervals.append((t0, t1, self._point_in_rect(p, rect)))
        return self._merge_intervals(intervals)

    def _circle_rect_intersections(
        self,
        rect: Rectangle,
        center: Point,
        radius: float,
    ) -> list[Point]:
        points: list[Point] = []

        def add(px: float, py: float):
            p = Point(x=px, y=py)
            if not any(existing == p for existing in points):
                points.append(p)

        for edge_start, edge_end in self._rect_edges(rect):
            dx = edge_end.x - edge_start.x
            dy = edge_end.y - edge_start.y
            fx = edge_start.x - center.x
            fy = edge_start.y - center.y

            a = dx * dx + dy * dy
            b = 2 * (fx * dx + fy * dy)
            c = fx * fx + fy * fy - radius * radius
            disc = b * b - 4 * a * c
            if disc < -EPS:
                continue
            disc = max(0.0, disc)
            sqrt_disc = sqrt(disc)
            for t in ((-b - sqrt_disc) / (2 * a), (-b + sqrt_disc) / (2 * a)):
                if -EPS <= t <= 1.0 + EPS:
                    add(edge_start.x + t * dx, edge_start.y + t * dy)

        return points

    def _arc_param_from_theta(
        self, start_theta: float, sweep: float, theta: float
    ) -> float | None:
        if isclose(sweep, 0.0, abs_tol=EPS):
            return None
        if sweep > 0:
            delta = self._normalize_angle(theta - start_theta)
            if delta < -EPS or delta > sweep + EPS:
                return None
            return min(max(delta / sweep, 0.0), 1.0)
        delta = -self._normalize_angle(start_theta - theta)
        if delta > EPS or delta < sweep - EPS:
            return None
        return min(max(delta / sweep, 0.0), 1.0)

    def _normalize_angle(self, theta: float) -> float:
        t = theta % (2 * pi)
        if t < 0:
            t += 2 * pi
        return t

    def _arc_start_theta(self, arc: Arc) -> float:
        return atan2(arc.start.y - arc.center.y, arc.start.x - arc.center.x)

    def _arc_radius(self, arc: Arc) -> float:
        return arc.center.distance(arc.start)

    def _rect_bounds(self, rect: Rectangle) -> tuple[float, float, float, float]:
        return rect.bounds()

    def _rect_edges(self, rect: Rectangle) -> list[tuple[Point, Point]]:
        points = [rect.point1, rect.point2, rect.point3, rect.point4]
        return list(zip(points, points[1:] + points[:1]))

    def _point_in_rect(self, point: Point, rect: Rectangle) -> bool:
        edges = self._rect_edges(rect)
        crosses = [
            (end.x - start.x) * (point.y - start.y)
            - (end.y - start.y) * (point.x - start.x)
            for start, end in edges
        ]
        non_negative = all(cross >= -EPS for cross in crosses)
        non_positive = all(cross <= EPS for cross in crosses)
        return non_negative or non_positive

    def _merge_intervals(
        self,
        intervals: list[tuple[float, float, bool]],
    ) -> list[tuple[float, float, bool]]:
        if not intervals:
            return []
        merged: list[tuple[float, float, bool]] = [intervals[0]]
        for start, end, hidden in intervals[1:]:
            last_start, last_end, last_hidden = merged[-1]
            if hidden == last_hidden and isclose(last_end, start, abs_tol=1e-7):
                merged[-1] = (last_start, end, hidden)
            else:
                merged.append((start, end, hidden))
        return merged
