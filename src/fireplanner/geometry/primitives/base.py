"""Abstract base types for geometry primitives and JSON contracts."""

from abc import ABC, abstractmethod
from typing import Any, Type, TypeVar

T = TypeVar("T", bound="Primitive")


class Primitive(ABC):
    """Abstract base contract for serializable geometry primitives."""

    @abstractmethod
    def to_json(self) -> dict[Any, Any]:
        """Serialize this primitive into a JSON-compatible dictionary."""
        pass

    @classmethod
    @abstractmethod
    def from_json(cls: Type[T], data: dict[Any, Any]) -> T:
        """Create a primitive instance from a JSON-compatible dictionary."""
        pass


class Primitive2D(Primitive, ABC):
    """Marker base class for geometric 2d primitives."""

    pass


class Primitive3D(Primitive, ABC):
    """Marker base class for geometric 3d primitives."""

    pass
