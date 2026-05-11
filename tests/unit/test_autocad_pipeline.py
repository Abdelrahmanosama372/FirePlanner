from fireplanner.adaptors.autocad.pipeline import Pipeline
from fireplanner.geometry.components import GeometricPipe
from fireplanner.geometry.primitives import Point
from fireplanner.networks import CoreNetwork, GeometryNetwork, ModelNetwork
from fireplanner.networks.placement_resolver import PlacementUnit

from tests.unit.test_autocad_reader import (
    CONFIG_YAML,
    FakeAcad,
    FakeBlockEntity,
    FakeLineEntity,
)


def test_pipeline_builds_single_network_result():
    acad = FakeAcad(
        lines=[
            FakeLineEntity(
                start=(0.0, 0.0, 0.0),
                end=(10.0, 0.0, 0.0),
                layer="line-network",
                color=1,
                handle="A",
            ),
        ],
        blocks=[
            FakeBlockEntity(
                name="SPR",
                insertion_point=(10.0, 0.0, 0.0),
                handle="10",
            ),
        ],
    )

    results = Pipeline(CONFIG_YAML, acad).build()

    assert len(results) == 1
    result = results[0]
    assert isinstance(result.core_network, CoreNetwork)
    assert isinstance(result.model_network, ModelNetwork)
    assert isinstance(result.geometry_network, GeometryNetwork)
    assert result.placement_resolver_config.unit == PlacementUnit.M
    assert result.core_network.get_edges_ids() == [1]
    assert result.model_network.get_pipes_with_edges_ids().keys() == {1}
    assert result.geometry_network.get_geometric_fire_connections_with_junctions_ids() == {}
    geometric_pipe = result.geometry_network.get_geometric_pipes_with_edges_ids()[1]
    assert isinstance(geometric_pipe, GeometricPipe)
    assert geometric_pipe.start == Point(x=0.0, y=0.0)
    assert geometric_pipe.end == Point(x=10000.0, y=0.0)


def test_pipeline_builds_multiple_results_when_multiple_roots_exist():
    acad = FakeAcad(
        lines=[
            FakeLineEntity(
                start=(0.0, 0.0, 0.0),
                end=(10.0, 0.0, 0.0),
                layer="line-network",
                color=1,
                handle="A",
            ),
            FakeLineEntity(
                start=(20.0, 0.0, 0.0),
                end=(30.0, 0.0, 0.0),
                layer="line-network",
                color=1,
                handle="B",
            ),
        ],
        blocks=[
            FakeBlockEntity(
                name="SPR",
                insertion_point=(10.0, 0.0, 0.0),
                handle="10",
            ),
            FakeBlockEntity(
                name="SPR",
                insertion_point=(30.0, 0.0, 0.0),
                handle="11",
            ),
        ],
    )

    results = Pipeline(CONFIG_YAML, acad).build()

    assert len(results) == 2
    assert [result.core_network.get_edges_ids() for result in results] == [[1], [1]]
    assert [
        (
            result.core_network_config.root_line.start.x,
            result.core_network_config.root_line.start.y,
            result.core_network_config.root_line.end.x,
            result.core_network_config.root_line.end.y,
        )
        for result in results
        if result.core_network_config.root_line is not None
    ] == [
        (0.0, 0.0, 10000.0, 0.0),
        (20000.0, 0.0, 30000.0, 0.0),
    ]
    assert [result.geometry_network.get_geometric_fire_connections_with_junctions_ids() for result in results] == [
        {},
        {},
    ]
