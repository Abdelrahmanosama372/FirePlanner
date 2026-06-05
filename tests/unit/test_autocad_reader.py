from fireplanner.adaptors.autocad.reader import Reader
from fireplanner.firecomponent import (
    SteelConnection,
    SteelDims,
    SteelMaterial,
    SteelSchedule,
    SteelSpecs,
)
from fireplanner.networks import CoreNetworkConfig
from fireplanner.standards.hazard import FireHazard
from fireplanner.units import LengthUnit

CONFIG_YAML = """
firefighting:
  hazard_level: "light"
  steel:
    material: "seamless"
    schedule: "40"
    specs: "ASTM"
    connnection_type:
      "1": "Threaded"
      "2.5": "Welded"

processing:
  compute_pipe_dimensions: true
  layer_name_to_pipe_diameter:
    fire-cabinet: "1"
  hangers:
    multiplier: 1.5
  short_transition_edges:
    enabled: true
    max_length_mm: 400

autocad:
  input:
    drawing:
      units: "m"
    root_line_identifier::
      color: "red"
    line_network_layer:
      name: "line-network"
    sprinkler_blocks:
      SPR:
        temperature: 68
        k_factor: 5.6
  output:
    network:
      layers:
        line:
          name: "ff-sprinklers"
          properties:
            color: "green"
            line_weight: 0.13
        centerline:
          enabled: true
          name: "ff-sprinklers-thin"
          properties:
            color: "gray"
            line_weight: 0.05
    dimensions:
      enabled: true
      unit: "m"
      layer:
        name: "ff-dimensions"
      offset_mm: 500
      min_length_mm: 1000
      style:
        name: "FIRE_DIM"
    annotations:
      text_height: 125
      layer:
        name: "ff-annotations"
        properties:
          color: "white"
      pipe_labels:
        diameter_offset_mm: 200
        cop_offset_mm: 350
        cop:
          enabled: true
          unit: "m"
        pipe_dimension:
          enabled: true
    hangers:
      layer:
        name: "ff-hangers"
        properties:
          color: "yellow"

geometry:
  placement:
    reducer_offset: 175
  welded_connection:
    enabled: true
    min_main_pipe_diameter: "2"
"""


class FakeColor:
    def __init__(self, color_name: str) -> None:
        self.ColorName = color_name


class FakeLineEntity:
    def __init__(
        self,
        start: tuple[float, float, float],
        end: tuple[float, float, float],
        layer: str,
        color: int,
        handle: str,
    ) -> None:
        self.StartPoint = start
        self.EndPoint = end
        self.Layer = layer
        self.Color = color
        self.Handle = handle


class FakeBlockEntity:
    def __init__(
        self,
        name: str,
        insertion_point: tuple[float, float, float],
        handle: str,
    ) -> None:
        self.EffectiveName = name
        self.InsertionPoint = insertion_point
        self.Handle = handle


class FakeAcad:
    def __init__(
        self, lines: list[FakeLineEntity], blocks: list[FakeBlockEntity]
    ) -> None:
        self._lines = lines
        self._blocks = blocks

    def iter_objects(self, entity_name: str):
        if entity_name in {"Line", "AcDbLine"}:
            return iter(self._lines)
        if entity_name in {"AcDbBlockReference", "BlockReference", "INSERT"}:
            return iter(self._blocks)
        return iter([])


def test_reader_builds_model_network_config_from_yaml_string():
    reader = Reader(CONFIG_YAML)

    config = reader.read_model_network_config()

    assert config.compute_pipe_dimensions is True
    assert config.hazard == FireHazard.LIGHT
    assert config.material == SteelMaterial.Seamless
    assert config.schedule == SteelSchedule.SCD40
    assert config.specs == SteelSpecs.ASTM
    assert config.get_connection_type_for_diameter(SteelDims.DIM_1_INCHES) == (
        SteelConnection.Threaded
    )
    assert config.get_connection_type_for_diameter(SteelDims.DIM_2_5_INCHES) == (
        SteelConnection.Welded
    )
    assert config.get_connection_type_for_diameter(SteelDims.DIM_1_5_INCHES) == (
        SteelConnection.Grooved
    )
    assert config.layer_name_to_pipe_diameter == {"fire-cabinet": 1.0}
    assert config.hanger_multiplier == 1.5
    assert config.short_transition_edges_enabled is True
    assert config.short_transition_edges_max_length_mm == 400.0


def test_reader_builds_geometry_network_config_from_yaml_string():
    reader = Reader(CONFIG_YAML)

    config = reader.read_geometry_network_config()

    assert config.welded_connection_enabled is True
    assert config.welded_connection_min_main_pipe_diameter == SteelDims.DIM_2_INCHES
    assert config.reducer_offset == 175


def test_reader_builds_output_layer_config_from_yaml_string():
    reader = Reader(CONFIG_YAML)

    config = reader.read_output_layer_config()

    assert config.line_layer_name == "ff-sprinklers"
    assert config.line_color == "green"
    assert config.line_weight == 0.13
    assert config.centerline_layer_name == "ff-sprinklers-thin"
    assert config.centerline_color == "gray"
    assert config.centerline_weight == 0.05
    assert config.hanger_layer_name == "ff-hangers"
    assert config.hanger_color == "yellow"
    assert config.centerlines_enabled is True


def test_reader_builds_boq_config_from_yaml_string():
    boq_yaml = (
        CONFIG_YAML
        + """
boq:
  full_ceiling_elevation: 5200
  output:
    excel:
      enabled: true
      path: "test_boq.xlsx"
    console:
      enabled: false
  paint:
    thickness: 180
    scrap_precentage: 0.2
    volume_solids_precentage: 0.8
"""
    )
    reader = Reader(boq_yaml)

    config = reader.read_boq_config()

    assert config.excel.enabled is True
    assert config.excel.path == "test_boq.xlsx"
    assert config.console.enabled is False
    assert config.full_ceiling_elevation == 5200
    assert config.paint.thickness == 180
    assert config.paint.scrap_precentage == 0.2
    assert config.paint.volume_solids_precentage == 0.8


def test_reader_builds_output_annotation_config_from_yaml_string():
    reader = Reader(CONFIG_YAML)

    config = reader.read_output_annotation_config()

    assert config.dimensions.enabled is True
    assert config.dimensions.unit == LengthUnit.METER
    assert config.dimensions.layer_name == "ff-dimensions"
    assert config.dimensions.offset_mm == 500.0
    assert config.dimensions.min_length_mm == 1000.0
    assert config.dimensions.style.name == "FIRE_DIM"
    assert config.annotations.layer.name == "ff-annotations"
    assert config.annotations.layer.color == "white"
    assert config.annotations.text_height == 125.0
    assert config.annotations.pipe_labels.diameter_offset_mm == 200.0
    assert config.annotations.pipe_labels.cop_offset_mm == 350.0
    assert config.annotations.pipe_labels.cop.enabled is True
    assert config.annotations.pipe_labels.cop.unit == LengthUnit.METER
    assert config.annotations.pipe_labels.pipe_dimension.enabled is True


def test_reader_builds_core_network_config_from_autocad_entities():
    reader = Reader(CONFIG_YAML)
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
                start=(10.0, 0.0, 0.0),
                end=(15.0, 5.0, 0.0),
                layer="line-network",
                color=3,
                handle="B",
            ),
            FakeLineEntity(
                start=(0.0, 5.0, 0.0),
                end=(10.0, 5.0, 0.0),
                layer="other-layer",
                color=1,
                handle="C",
            ),
        ],
        blocks=[
            FakeBlockEntity(
                name="SPR",
                insertion_point=(2.0, 0.0, 0.0),
                handle="10",
            ),
            FakeBlockEntity(
                name="IGNORE",
                insertion_point=(8.0, 0.0, 0.0),
                handle="11",
            ),
        ],
    )

    configs = reader.read_core_network_configs(acad)
    assert len(configs) == 1
    config = configs[0]

    assert isinstance(config, CoreNetworkConfig)
    assert config.sprinkler_block_data == {"SPR": {"temperature": 68, "k_factor": 5.6}}
    assert [
        (line.start.x, line.start.y, line.end.x, line.end.y) for line in config.lines
    ] == [
        (0.0, 0.0, 10000.0, 0.0),
        (10000.0, 0.0, 15000.0, 5000.0),
    ]
    assert [line.style.layer for line in config.lines] == [
        "line-network",
        "line-network",
    ]
    assert config.root_line is not None
    assert (
        config.root_line.start.x,
        config.root_line.start.y,
        config.root_line.end.x,
        config.root_line.end.y,
    ) == (0.0, 0.0, 10000.0, 0.0)
    assert [
        (block.name, block.center.x, block.center.y)
        for block in config.sprinkler_blocks
    ] == [
        ("SPR", 2000.0, 0.0),
    ]
    assert [
        (line.start.x, line.start.y, line.end.x, line.end.y)
        for line in config.ordered_lines()
    ] == [
        (0.0, 0.0, 10000.0, 0.0),
        (10000.0, 0.0, 15000.0, 5000.0),
    ]
    assert reader.read_core_network_config(acad).root_line == config.root_line


def test_reader_builds_core_network_config_with_multiple_sprinkler_block_names():
    yaml_with_multiple_sprinklers = CONFIG_YAML.replace(
        "    sprinkler_blocks:\n      SPR:\n        temperature: 68\n        k_factor: 5.6\n",
        "    sprinkler_blocks:\n"
        "      SPR56:\n"
        "        temperature: 68\n"
        "        k_factor: 5.6\n"
        "      SPR8:\n"
        "        temperature: 74\n"
        "        k_factor: 8\n",
    )
    reader = Reader(yaml_with_multiple_sprinklers)
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
                name="SPR56",
                insertion_point=(2.0, 0.0, 0.0),
                handle="10",
            ),
            FakeBlockEntity(
                name="SPR8",
                insertion_point=(8.0, 0.0, 0.0),
                handle="11",
            ),
            FakeBlockEntity(
                name="IGNORE",
                insertion_point=(5.0, 0.0, 0.0),
                handle="12",
            ),
        ],
    )

    config = reader.read_core_network_config(acad)

    assert config.sprinkler_block_data == {
        "SPR56": {"temperature": 68, "k_factor": 5.6},
        "SPR8": {"temperature": 74, "k_factor": 8},
    }
    assert [
        (block.name, block.center.x, block.center.y)
        for block in config.sprinkler_blocks
    ] == [
        ("SPR56", 2000.0, 0.0),
        ("SPR8", 8000.0, 0.0),
    ]


def test_reader_builds_multiple_core_network_configs_when_multiple_roots_match():
    reader = Reader(CONFIG_YAML)
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
            FakeLineEntity(
                start=(10.0, 0.0, 0.0),
                end=(15.0, 5.0, 0.0),
                layer="line-network",
                color=3,
                handle="C",
            ),
        ],
        blocks=[
            FakeBlockEntity(
                name="SPR",
                insertion_point=(2.0, 0.0, 0.0),
                handle="10",
            ),
        ],
    )

    configs = reader.read_core_network_configs(acad)

    assert len(configs) == 2
    assert [
        (
            config.root_line.start.x,
            config.root_line.start.y,
            config.root_line.end.x,
            config.root_line.end.y,
        )
        for config in configs
        if config.root_line is not None
    ] == [
        (0.0, 0.0, 10000.0, 0.0),
        (20000.0, 0.0, 30000.0, 0.0),
    ]
    assert [
        [
            (line.start.x, line.start.y, line.end.x, line.end.y)
            for line in config.ordered_lines()
        ]
        for config in configs
    ] == [
        [
            (0.0, 0.0, 10000.0, 0.0),
            (20000.0, 0.0, 30000.0, 0.0),
            (10000.0, 0.0, 15000.0, 5000.0),
        ],
        [
            (20000.0, 0.0, 30000.0, 0.0),
            (0.0, 0.0, 10000.0, 0.0),
            (10000.0, 0.0, 15000.0, 5000.0),
        ],
    ]
