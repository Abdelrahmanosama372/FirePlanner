from fireplanner.adaptors.autocad.reader import Reader
from fireplanner.firecomponent import (
    SteelConnection,
    SteelDims,
    SteelMaterial,
    SteelSchedule,
    SteelSpecs,
)
from fireplanner.networks import CoreNetworkConfig
from fireplanner.networks.placement_resolver import PlacementUnit
from fireplanner.standards.hazard import FireHazard


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


def test_reader_builds_placement_resolver_config_from_yaml_string():
    reader = Reader(CONFIG_YAML)

    config = reader.read_placement_resolver_config()

    assert config.unit == PlacementUnit.M


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
