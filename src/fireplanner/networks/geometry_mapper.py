"""Geometric mapper that maps FireComponents to their geometry."""

from __future__ import annotations
from fireplanner.firecomponent.base import FireComponent
from fireplanner.firecomponent.pipe import Pipe
from fireplanner.firecomponent.fitting.fireconnection.elbow import Elbow
from fireplanner.firecomponent.fitting.fireconnection.tee import Tee
from fireplanner.firecomponent.fitting.fireconnection.reducer import Reducer
from fireplanner.geometry.components import GeometricComponent
from fireplanner.geometry.components import (
    GeometricElbow,
    GeometricReducer,
    GeometricPipe,
    GeometricTee,
)


class GeometryMapper:
    """Simple factory maps FireComponents to their geometric components."""

    def get_geometry(self, component: FireComponent) -> GeometricComponent:
        component_type = type(component)

        if component_type is Pipe:
            return GeometricPipe(component)
        if component_type is Elbow:
            return GeometricElbow(component)
        if component_type is Tee:
            return GeometricTee(component)
        if component_type is Reducer:
            return GeometricReducer(component)

        raise KeyError(f"No geometry mapping for {component_type}")
