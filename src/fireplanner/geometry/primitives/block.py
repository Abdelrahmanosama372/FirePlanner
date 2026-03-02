"""Block primitive definition and JSON conversion utilities."""

from __future__ import annotations

from typing import Any, override

from . import Point, Primitive2D


class Block(Primitive2D):
    """Named block entity positioned at a single point in 2D space."""

    def __init__(self, name: str, center: Point) -> None:
        """Initialize a block with a display name and insertion position."""
        self._name: str = name
        self._center: Point = center
        super().__init__()

    @property
    def name(self) -> str:
        """Return the block name."""
        return self._name

    @property
    def center(self) -> Point:
        """Return the block insertion point."""
        return self._center

    @override
    def to_json(self) -> dict[Any, Any]:
        """Serialize this block to the project JSON shape."""
        return {"Block": {"name": self.name, "center": self.center.to_json()}}

    @override
    @classmethod
    def from_json(cls, data: dict[Any, Any]) -> Block:
        """Build a block instance from the project JSON shape."""
        block_props = data["Block"]
        name = str(block_props["name"])
        center = Point.from_json(block_props["center"])
        return Block(name=name, center=center)
