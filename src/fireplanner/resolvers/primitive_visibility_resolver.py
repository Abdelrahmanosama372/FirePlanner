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
        xmin, xmax, ymin, ymax = self._rect_bounds(rect)
        x0, y0 = line.start.x, line.start.y
        x1, y1 = line.end.x, line.end.y
        dx, dy = x1 - x0, y1 - y0
        p = [-dx, dx, -dy, dy]
        q = [x0 - xmin, xmax - x0, y0 - ymin, ymax - y0]
        u1, u2 = 0.0, 1.0
        for pi_, qi_ in zip(p, q):
            if isclose(pi_, 0.0, abs_tol=EPS):
                if qi_ < 0:
                    return None
                continue
            t = qi_ / pi_
            if pi_ < 0:
                u1 = max(u1, t)
            else:
                u2 = min(u2, t)
            if u1 > u2:
                return None
        return Line(
            start=Point(x=x0 + u1 * dx, y=y0 + u1 * dy),
            end=Point(x=x0 + u2 * dx, y=y0 + u2 * dy),
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
        xmin, xmax, ymin, ymax = self._rect_bounds(rect)
        points: list[Point] = []

        def add(px: float, py: float):
            p = Point(x=px, y=py)
            if not any(existing == p for existing in points):
                points.append(p)

        for x in (xmin, xmax):
            d = radius * radius - (x - center.x) ** 2
            if d < -EPS:
                continue
            d = max(0.0, d)
            y_a = center.y + sqrt(d)
            y_b = center.y - sqrt(d)
            if ymin - EPS <= y_a <= ymax + EPS:
                add(x, y_a)
            if ymin - EPS <= y_b <= ymax + EPS:
                add(x, y_b)

        for y in (ymin, ymax):
            d = radius * radius - (y - center.y) ** 2
            if d < -EPS:
                continue
            d = max(0.0, d)
            x_a = center.x + sqrt(d)
            x_b = center.x - sqrt(d)
            if xmin - EPS <= x_a <= xmax + EPS:
                add(x_a, y)
            if xmin - EPS <= x_b <= xmax + EPS:
                add(x_b, y)

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
        xmin = min(rect.point1.x, rect.point2.x)
        xmax = max(rect.point1.x, rect.point2.x)
        ymin = min(rect.point1.y, rect.point2.y)
        ymax = max(rect.point1.y, rect.point2.y)
        return xmin, xmax, ymin, ymax

    def _point_in_rect(self, point: Point, rect: Rectangle) -> bool:
        xmin, xmax, ymin, ymax = self._rect_bounds(rect)
        return (
            xmin - EPS <= point.x <= xmax + EPS and ymin - EPS <= point.y <= ymax + EPS
        )

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
