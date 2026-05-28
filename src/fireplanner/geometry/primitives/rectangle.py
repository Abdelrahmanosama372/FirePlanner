from __future__ import annotations

from dataclasses import dataclass
from typing import Any, override

from .base import Primitive2D, PrimitiveStyle
from .line import LineType
from .point import Point


@dataclass(init=False)
class Rectangle(Primitive2D):
    point1: Point
    point2: Point
    line_type: LineType = LineType.Normal

    def __init__(
        self,
        point1: Point,
        point2: Point,
        line_type: LineType = LineType.Normal,
        id: int = -1,
        style: PrimitiveStyle | None = None,
    ) -> None:
        self.point1 = point1
        self.point2 = point2
        self.line_type = line_type
        super().__init__(id=id, style=style)

    @override
    def transform_2d(self, transform: "Transform2D") -> Primitive2D:
        return Rectangle(
            point1=self.point1.transform_2d(transform),
            point2=self.point2.transform_2d(transform),
            line_type=self.line_type,
            id=self.id,
            style=self.style,
        )

    def intersection(self, other: "Rectangle") -> "Rectangle | None":
        self_min_x = min(self.point1.x, self.point2.x)
        self_max_x = max(self.point1.x, self.point2.x)
        self_min_y = min(self.point1.y, self.point2.y)
        self_max_y = max(self.point1.y, self.point2.y)

        other_min_x = min(other.point1.x, other.point2.x)
        other_max_x = max(other.point1.x, other.point2.x)
        other_min_y = min(other.point1.y, other.point2.y)
        other_max_y = max(other.point1.y, other.point2.y)

        intersection_min_x = max(self_min_x, other_min_x)
        intersection_max_x = min(self_max_x, other_max_x)
        intersection_min_y = max(self_min_y, other_min_y)
        intersection_max_y = min(self_max_y, other_max_y)

        if intersection_min_x > intersection_max_x:
            return None
        if intersection_min_y > intersection_max_y:
            return None

        return Rectangle(
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
        return Rectangle(
            point1=point1,
            point2=point2,
            line_type=line_type,
            style=style,
        )
