from math import isclose
from types import SimpleNamespace

from fireplanner.adaptors.autocad.pipeline import Pipeline
from fireplanner.adaptors.autocad.writer import (
    AnnotationLayerConfig,
    AnnotationsConfig,
    CopLabelConfig,
    DimensionsConfig,
    DimensionStyleConfig,
    OutputAnnotationConfig,
    PipeDimensionLabelConfig,
    PipeLabelsConfig,
)
from fireplanner.geometry.components import GeometricPipe
from fireplanner.geometry.primitives import Point
from fireplanner.networks import CoreNetwork, GeometryNetwork, ModelNetwork
from fireplanner.units import LengthUnit
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
    assert result.core_network.get_edges_ids() == [1]
    assert result.model_network.get_pipes_with_edges_ids().keys() == {1}
    assert (
        result.geometry_network.get_geometric_fire_connections_with_junctions_ids()
        == {}
    )
    geometric_pipe = result.geometry_network.get_geometric_pipes()[0]
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
    assert [
        result.geometry_network.get_geometric_fire_connections_with_junctions_ids()
        for result in results
    ] == [
        {},
        {},
    ]


def test_pipeline_runs_boq_outputs_from_config(monkeypatch):
    yaml_with_boq = (
        CONFIG_YAML
        + """
boq:
  output:
    excel:
      enabled: false
      path: "boq_test.xlsx"
    console:
      enabled: true
"""
    )

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

    calls = {"console": 0}

    def _fake_console(_report):
        calls["console"] += 1

    monkeypatch.setattr(
        "fireplanner.adaptors.autocad.pipeline.BOQConsolePrinter.print_report",
        _fake_console,
    )

    results = Pipeline(yaml_with_boq, acad).build()
    assert len(results) == 1
    assert calls["console"] == 1


def test_pipeline_suffixes_boq_excel_paths_for_multiple_networks(monkeypatch):
    yaml_with_boq = (
        CONFIG_YAML
        + """
boq:
  output:
    excel:
      enabled: true
      path: "boq_test.xlsx"
    console:
      enabled: false
"""
    )

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

    exported_paths: list[str] = []

    def _fake_export(*, report, output_path):
        exported_paths.append(output_path)
        return output_path

    monkeypatch.setitem(
        __import__("sys").modules,
        "fireplanner.boq.output.excel",
        SimpleNamespace(
            BOQExcelExporter=SimpleNamespace(export=_fake_export),
        ),
    )

    results = Pipeline(yaml_with_boq, acad).build()

    assert len(results) == 2
    assert exported_paths == ["boq_test1.xlsx", "boq_test2.xlsx"]


def test_pipeline_applies_hanger_multiplier_from_config():
    yaml_with_multiplier = CONFIG_YAML.replace("multiplier: 1.5", "multiplier: 2.0")
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
    result = Pipeline(yaml_with_multiplier, acad).build()[0]
    assemblies = result.model_network.get_hangers_assembly()
    assert len(assemblies) == 1
    assert assemblies[0].hangers_count == 6


class _CaptureWriter:
    def __init__(self) -> None:
        self.text_calls: list[dict] = []
        self.dim_calls: list[dict] = []
        self.style_checked: str | None = None

    def ensure_dimension_style_exists(self, style_name: str) -> None:
        self.style_checked = style_name

    def write_text_annotation(
        self,
        text: str,
        position_mm: Point,
        rotation_rad: float,
        layer_name: str,
        text_height_mm: float,
    ):
        self.text_calls.append(
            {
                "text": text,
                "position": position_mm,
                "rotation": rotation_rad,
                "layer": layer_name,
                "height": text_height_mm,
            }
        )
        return object()

    def write_aligned_dimension(
        self,
        start_mm: Point,
        end_mm: Point,
        offset_point_mm: Point,
        style_name: str,
        layer_name: str = "",
    ):
        self.dim_calls.append(
            {
                "start": start_mm,
                "end": end_mm,
                "offset": offset_point_mm,
                "style": style_name,
                "layer": layer_name,
            }
        )
        return object()


def test_pipeline_output_annotations_follow_edge_center_and_direction():
    acad = FakeAcad(
        lines=[
            FakeLineEntity(
                start=(0.0, 0.0, 3000.0),
                end=(10.0, 10.0, 3000.0),
                layer="line-network",
                color=1,
                handle="A",
            ),
        ],
        blocks=[
            FakeBlockEntity(
                name="SPR",
                insertion_point=(10.0, 10.0, 3000.0),
                handle="10",
            ),
        ],
    )
    pipeline = Pipeline(CONFIG_YAML, acad)
    result = pipeline.build()[0]
    writer = _CaptureWriter()
    config = OutputAnnotationConfig(
        dimensions=DimensionsConfig(
            enabled=True,
            unit=LengthUnit.METER,
            style=DimensionStyleConfig(name="FIRE_DIM"),
            layer_name="ff-dimensions",
            offset_mm=500.0,
        ),
        annotations=AnnotationsConfig(
            layer=AnnotationLayerConfig(name="ff-annotations"),
            pipe_labels=PipeLabelsConfig(
                cop=CopLabelConfig(enabled=True, unit=LengthUnit.METER),
                pipe_dimension=PipeDimensionLabelConfig(enabled=True),
                diameter_offset_mm=200.0,
                cop_offset_mm=350.0,
            ),
            text_height=125.0,
        ),
    )

    created = pipeline._write_output_annotations_and_dimensions(
        writer=writer, result=result, config=config
    )
    assert len(created) == 3
    assert writer.style_checked == "FIRE_DIM"
    assert len(writer.text_calls) == 2
    assert len(writer.dim_calls) == 1

    edge_line = result.core_network.get_lines_with_edge_ids()[1]
    direction = edge_line.direction()
    nx = __import__("math").sin(direction)
    ny = -__import__("math").cos(direction)
    mid_x = (edge_line.start.x + edge_line.end.x) / 2.0
    mid_y = (edge_line.start.y + edge_line.end.y) / 2.0

    dia = writer.text_calls[0]
    cop = writer.text_calls[1]
    expected_cop = f"COP {result.model_network.get_pipes_assembly()[0].edge_info.elevation / 1000:g} m"
    assert cop["text"] == expected_cop
    assert isclose(dia["rotation"], direction, rel_tol=1e-9)
    assert isclose(cop["rotation"], direction, rel_tol=1e-9)
    assert isclose(dia["position"].x, mid_x - nx * 200.0, rel_tol=1e-9)
    assert isclose(dia["position"].y, mid_y - ny * 200.0, rel_tol=1e-9)
    assert isclose(cop["position"].x, mid_x - nx * 350.0, rel_tol=1e-9)
    assert isclose(cop["position"].y, mid_y - ny * 350.0, rel_tol=1e-9)

    dim = writer.dim_calls[0]
    assert dim["style"] == "FIRE_DIM"
    assert dim["layer"] == "ff-dimensions"
    assert isclose(dim["offset"].x, mid_x + nx * 500.0, rel_tol=1e-9)
    assert isclose(dim["offset"].y, mid_y + ny * 500.0, rel_tol=1e-9)


def test_pipeline_dimensions_stay_below_for_reversed_edge_direction():
    acad = FakeAcad(
        lines=[
            FakeLineEntity(
                start=(10.0, 10.0, 3000.0),
                end=(0.0, 0.0, 3000.0),
                layer="line-network",
                color=1,
                handle="A",
            ),
        ],
        blocks=[
            FakeBlockEntity(
                name="SPR",
                insertion_point=(0.0, 0.0, 3000.0),
                handle="10",
            ),
        ],
    )
    pipeline = Pipeline(CONFIG_YAML, acad)
    result = pipeline.build()[0]
    writer = _CaptureWriter()
    config = OutputAnnotationConfig(
        dimensions=DimensionsConfig(
            enabled=True,
            unit=LengthUnit.METER,
            style=DimensionStyleConfig(name="FIRE_DIM"),
            layer_name="ff-dimensions",
            offset_mm=500.0,
        ),
        annotations=AnnotationsConfig(
            layer=AnnotationLayerConfig(name="ff-annotations"),
            pipe_labels=PipeLabelsConfig(
                cop=CopLabelConfig(enabled=True, unit=LengthUnit.METER),
                pipe_dimension=PipeDimensionLabelConfig(enabled=True),
                diameter_offset_mm=200.0,
                cop_offset_mm=350.0,
            ),
            text_height=125.0,
        ),
    )

    pipeline._write_output_annotations_and_dimensions(
        writer=writer, result=result, config=config
    )
    line = result.core_network.get_lines_with_edge_ids()[1]
    mid_y = (line.start.y + line.end.y) / 2.0

    assert len(writer.dim_calls) == 1
    assert writer.dim_calls[0]["offset"].y < mid_y
    assert len(writer.text_calls) == 2
    for text_call in writer.text_calls:
        assert text_call["position"].y > mid_y


def test_pipeline_skips_dimensions_for_short_edges_by_threshold():
    acad = FakeAcad(
        lines=[
            FakeLineEntity(
                start=(0.0, 0.0, 3000.0),
                end=(10.0, 0.0, 3000.0),
                layer="line-network",
                color=1,
                handle="A",
            ),
        ],
        blocks=[
            FakeBlockEntity(
                name="SPR",
                insertion_point=(10.0, 0.0, 3000.0),
                handle="10",
            ),
        ],
    )
    pipeline = Pipeline(CONFIG_YAML, acad)
    result = pipeline.build()[0]
    writer = _CaptureWriter()
    config = OutputAnnotationConfig(
        dimensions=DimensionsConfig(
            enabled=True,
            unit=LengthUnit.METER,
            style=DimensionStyleConfig(name="FIRE_DIM"),
            layer_name="ff-dimensions",
            offset_mm=500.0,
            min_length_mm=20000.0,
        ),
        annotations=AnnotationsConfig(
            layer=AnnotationLayerConfig(name="ff-annotations"),
            pipe_labels=PipeLabelsConfig(
                cop=CopLabelConfig(enabled=True, unit=LengthUnit.METER),
                pipe_dimension=PipeDimensionLabelConfig(enabled=True),
                diameter_offset_mm=200.0,
                cop_offset_mm=350.0,
            ),
            text_height=125.0,
        ),
    )

    created = pipeline._write_output_annotations_and_dimensions(
        writer=writer, result=result, config=config
    )
    assert len(writer.dim_calls) == 0
    assert len(writer.text_calls) == 2
    assert len(created) == 2
