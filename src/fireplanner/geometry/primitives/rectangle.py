from __future__ import annotations

from dataclasses import dataclass
from typing import Any, override

from .base import Primitive2D, PrimitiveStyle
from .line import Line, LineType
from .point import Point


@dataclass(init=False)
class Rectangle(Primitive2D):
    point1: Point
    point2: Point
    point3: Point
    point4: Point
    line_type: LineType = LineType.Normal

    def __init__(
        self,
        point1: Point,
        point2: Point,
        point3: Point,
        point4: Point,
        line_type: LineType = LineType.Normal,
        id: int = -1,
        style: PrimitiveStyle | None = None,
    ) -> None:
        self.point1 = point1
        self.point2 = point2
        self.point3 = point3
        self.point4 = point4
        self.line_type = line_type
        super().__init__(id=id, style=style)

    @classmethod
    def from_bounds(
        cls,
        point1: Point,
        point2: Point,
        line_type: LineType = LineType.Normal,
        id: int = -1,
        style: PrimitiveStyle | None = None,
    ) -> "Rectangle":
        x_min = min(point1.x, point2.x)
        x_max = max(point1.x, point2.x)
        y_min = min(point1.y, point2.y)
        y_max = max(point1.y, point2.y)
        return cls(
            point1=Point(x=x_min, y=y_min),
            point2=Point(x=x_max, y=y_min),
            point3=Point(x=x_max, y=y_max),
            point4=Point(x=x_min, y=y_max),
            line_type=line_type,
            id=id,
            style=style,
        )

    @override
    def transform_2d(self, transform: "Transform2D") -> Primitive2D:
        return Rectangle(
            point1=self.point1.transform_2d(transform),
            point2=self.point2.transform_2d(transform),
            point3=self.point3.transform_2d(transform),
            point4=self.point4.transform_2d(transform),
            line_type=self.line_type,
            id=self.id,
            style=self.style,
        )

    def edges(self) -> list[Line]:
        points = [self.point1, self.point2, self.point3, self.point4]
        return [
            Line(start=start, end=end, line_type=self.line_type)
            for start, end in zip(points, points[1:] + points[:1])
        ]

    def bounds(self) -> tuple[float, float, float, float]:
        points = [self.point1, self.point2, self.point3, self.point4]
        xs = [p.x for p in points]
        ys = [p.y for p in points]
        return min(xs), max(xs), min(ys), max(ys)

    def intersection(self, other: "Rectangle") -> "Rectangle | None":
        self_min_x, self_max_x, self_min_y, self_max_y = self.bounds()
        other_min_x, other_max_x, other_min_y, other_max_y = other.bounds()

        intersection_min_x = max(self_min_x, other_min_x)
        intersection_max_x = min(self_max_x, other_max_x)
        intersection_min_y = max(self_min_y, other_min_y)
        intersection_max_y = min(self_max_y, other_max_y)

        if intersection_min_x > intersection_max_x:
            return None
        if intersection_min_y > intersection_max_y:
            return None

        return Rectangle.from_bounds(
            point1=Point(x=intersection_min_x, y=intersection_min_y),
            point2=Point(x=intersection_max_x, y=intersection_max_y),
            line_type=self.line_type,
        )

    @override
    def to_json(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "Rectangle": {
                "point1": self.point1.to_json(),
                "point2": self.point2.to_json(),
                "point3": self.point3.to_json(),
                "point4": self.point4.to_json(),
                "line type": self.line_type.value,
            }
        }
        if self.style is not None:
            data["Rectangle"]["style"] = {
                "layer": self.style.layer,
                "color": self.style.color,
                "category": self.style.category,
            }
        return data

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> "Rectangle":
        props = data["Rectangle"]
        point1 = Point.from_json(props["point1"])
        point2 = Point.from_json(props["point2"])
        line_type = LineType(props["line type"])
        style_data = props.get("style")
        style = (
            PrimitiveStyle(
                layer=style_data.get("layer"),
                color=style_data.get("color"),
                category=style_data.get("category"),
            )
            if isinstance(style_data, dict)
            else None
        )
        if "point3" not in props or "point4" not in props:
            return Rectangle.from_bounds(
                point1=point1,
                point2=point2,
                line_type=line_type,
                style=style,
            )
        point3 = Point.from_json(props["point3"])
        point4 = Point.from_json(props["point4"])
        return Rectangle(
            point1=point1,
            point2=point2,
            point3=point3,
            point4=point4,
            line_type=line_type,
            style=style,
        )
