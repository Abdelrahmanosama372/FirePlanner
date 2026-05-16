"""Geometric mapper that maps FireComponents to their geometry."""

from __future__ import annotations
from dataclasses import dataclass
from fireplanner.firecomponent.base import FireComponent
from fireplanner.firecomponent.base import SteelDims
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
    GeometricWeldedBranch,
)


@dataclass(frozen=True)
class GeometryMapperConfig:
    welded_connection_enabled: bool = False
    welded_connection_min_main_pipe_diameter: SteelDims = SteelDims.DIM_2_INCHES


class GeometryMapper:
    """Simple factory maps FireComponents to their geometric components."""

    def __init__(self, config: GeometryMapperConfig | None = None) -> None:
        self._config = config or GeometryMapperConfig()

    def get_geometry(self, component: FireComponent) -> GeometricComponent:
        component_type = type(component)

        if component_type is Pipe:
            return GeometricPipe(component)
        if component_type is Elbow:
            return GeometricElbow(component)
        if component_type is Tee:
            if (
                self._config.welded_connection_enabled
                and component.run_diameter.value
                >= self._config.welded_connection_min_main_pipe_diameter.value
                and component.run_diameter.value >= 2 * component.branch_diameter.value
            ):
                return GeometricWeldedBranch(component)
            return GeometricTee(component)
        if component_type is Reducer:
            return GeometricReducer(component)

        raise KeyError(f"No geometry mapping for {component_type}")
