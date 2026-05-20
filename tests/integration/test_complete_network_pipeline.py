from math import pi

from fireplanner.firecomponent import (
    Pipe,
    SteelConnection,
    SteelDims,
    SteelMaterial,
    SteelSchedule,
    SteelSpecs,
)
from fireplanner.geometry.primitives import Block, Line, Point
from fireplanner.networks import (
    CoreNetwork,
    CoreNetworkConfig,
    GeometryNetwork,
    ModelNetwork,
)
from fireplanner.networks.core_network import FlowRoute
from fireplanner.networks.junction import JunctionType

MM_SCALE = 1000.0


def mm(value: float) -> float:
    return value * MM_SCALE


def build_test_network() -> tuple[list[Line], list[Block]]:
    lines = [
        Line(
            id=0,
            start=Point(x=mm(27.094), y=mm(18.8190)),
            end=Point(x=mm(27.094), y=mm(25.0564)),
        ),
        Line(
            id=1,
            start=Point(x=mm(15.0486), y=mm(25.0564)),
            end=Point(x=mm(27.094), y=mm(25.0564)),
        ),
        Line(
            id=2,
            start=Point(x=mm(15.0486), y=mm(22.1564)),
            end=Point(x=mm(27.094), y=mm(22.1564)),
        ),
        Line(
            id=3,
            start=Point(x=mm(15.0486), y=mm(19.2562)),
            end=Point(x=mm(27.094), y=mm(19.2562)),
        ),
    ]

    blocks = [
        Block(id=1, name="SPR", center=Point(x=mm(15.0486), y=mm(25.0564))),
        Block(id=2, name="SPR", center=Point(x=mm(17.9786), y=mm(25.0564))),
        Block(id=3, name="SPR", center=Point(x=mm(20.9086), y=mm(25.0564))),
        Block(id=4, name="SPR", center=Point(x=mm(23.8386), y=mm(25.0564))),
        Block(id=5, name="SPR", center=Point(x=mm(26.7686), y=mm(25.0564))),
        Block(id=6, name="SPR", center=Point(x=mm(15.0486), y=mm(22.1564))),
        Block(id=7, name="SPR", center=Point(x=mm(17.9786), y=mm(22.1564))),
        Block(id=8, name="SPR", center=Point(x=mm(20.9086), y=mm(22.1564))),
        Block(id=9, name="SPR", center=Point(x=mm(23.8386), y=mm(22.1564))),
        Block(id=10, name="SPR", center=Point(x=mm(26.7686), y=mm(22.1564))),
        Block(id=11, name="SPR", center=Point(x=mm(15.0486), y=mm(19.2562))),
        Block(id=12, name="SPR", center=Point(x=mm(17.9786), y=mm(19.2562))),
        Block(id=13, name="SPR", center=Point(x=mm(20.9086), y=mm(19.2562))),
        Block(id=14, name="SPR", center=Point(x=mm(23.8386), y=mm(19.2562))),
        Block(id=15, name="SPR", center=Point(x=mm(26.7686), y=mm(19.2562))),
    ]
    return (lines, blocks)


def test_core_network_construction():
    lines, blocks = build_test_network()
    core_network = CoreNetwork(
        config=CoreNetworkConfig(
            lines=lines, sprinkler_blocks=blocks, root_flow_route=FlowRoute.BRANCH
        )
    )

    assert core_network.get_edges_ids() == [
        1,
        2,
        3,
        14,
        15,
        16,
        17,
        18,
        9,
        10,
        11,
        12,
        13,
        4,
        5,
        6,
        7,
        8,
    ]
    assert {
        edge_id: (
            line.start.x,
            line.start.y,
            line.end.x,
            line.end.y,
        )
        for edge_id, line in core_network.get_lines_with_edge_ids().items()
    } == {
        1: (mm(27.094), mm(18.819), mm(27.094), mm(19.2562)),
        2: (mm(27.094), mm(19.2562), mm(27.094), mm(22.1564)),
        3: (mm(27.094), mm(22.1564), mm(27.094), mm(25.0564)),
        14: (mm(27.094), mm(25.0564), mm(26.7686), mm(25.0564)),
        15: (mm(26.7686), mm(25.0564), mm(23.8386), mm(25.0564)),
        16: (mm(23.8386), mm(25.0564), mm(20.9086), mm(25.0564)),
        17: (mm(20.9086), mm(25.0564), mm(17.9786), mm(25.0564)),
        18: (mm(17.9786), mm(25.0564), mm(15.0486), mm(25.0564)),
        4: (mm(27.094), mm(19.2562), mm(26.7686), mm(19.2562)),
        5: (mm(26.7686), mm(19.2562), mm(23.8386), mm(19.2562)),
        6: (mm(23.8386), mm(19.2562), mm(20.9086), mm(19.2562)),
        7: (mm(20.9086), mm(19.2562), mm(17.9786), mm(19.2562)),
        8: (mm(17.9786), mm(19.2562), mm(15.0486), mm(19.2562)),
        9: (mm(27.094), mm(22.1564), mm(26.7686), mm(22.1564)),
        10: (mm(26.7686), mm(22.1564), mm(23.8386), mm(22.1564)),
        11: (mm(23.8386), mm(22.1564), mm(20.9086), mm(22.1564)),
        12: (mm(20.9086), mm(22.1564), mm(17.9786), mm(22.1564)),
        13: (mm(17.9786), mm(22.1564), mm(15.0486), mm(22.1564)),
    }
    assert {
        edge_id: core_network.find_edge_sprinkler_count(edge_id)
        for edge_id in core_network.get_edges_ids()
    } == {
        1: 15,
        2: 10,
        3: 5,
        14: 5,
        15: 4,
        16: 3,
        17: 2,
        18: 1,
        4: 5,
        5: 4,
        6: 3,
        7: 2,
        8: 1,
        9: 5,
        10: 4,
        11: 3,
        12: 2,
        13: 1,
    }
    assert {
        junction_id: (
            junction.origin.x,
            junction.origin.y,
            junction.junction_type,
            junction.connected_edges_ids,
            junction.angle,
            junction.has_sprinkler,
        )
        for junction_id, junction in core_network.get_junctions().items()
    } == {
        1: (mm(27.094), mm(19.2562), JunctionType.THREE_WAY, [1, 2, 4], None, False),
        2: (mm(27.094), mm(22.1564), JunctionType.THREE_WAY, [2, 3, 9], None, False),
        3: (mm(27.094), mm(25.0564), JunctionType.TWO_WAY, [3, 14], 90.0, False),
        4: (mm(26.7686), mm(25.0564), JunctionType.TWO_WAY, [14, 15], 0.0, True),
        5: (mm(23.8386), mm(25.0564), JunctionType.TWO_WAY, [15, 16], 0.0, True),
        6: (mm(20.9086), mm(25.0564), JunctionType.TWO_WAY, [16, 17], 0.0, True),
        7: (mm(17.9786), mm(25.0564), JunctionType.TWO_WAY, [17, 18], 0.0, True),
        8: (mm(26.7686), mm(22.1564), JunctionType.TWO_WAY, [9, 10], 0.0, True),
        9: (mm(23.8386), mm(22.1564), JunctionType.TWO_WAY, [10, 11], 0.0, True),
        10: (mm(20.9086), mm(22.1564), JunctionType.TWO_WAY, [11, 12], 0.0, True),
        11: (mm(17.9786), mm(22.1564), JunctionType.TWO_WAY, [12, 13], 0.0, True),
        12: (mm(26.7686), mm(19.2562), JunctionType.TWO_WAY, [4, 5], 0.0, True),
        13: (mm(23.8386), mm(19.2562), JunctionType.TWO_WAY, [5, 6], 0.0, True),
        14: (mm(20.9086), mm(19.2562), JunctionType.TWO_WAY, [6, 7], 0.0, True),
        15: (mm(17.9786), mm(19.2562), JunctionType.TWO_WAY, [7, 8], 0.0, True),
    }

    assert {
        edge_id: core_network.get_edge_flow_route(edge_id)
        for edge_id in core_network.get_edges_ids()
    } == {
        1: FlowRoute.BRANCH,
        2: FlowRoute.BRANCH,
        3: FlowRoute.BRANCH,
        14: FlowRoute.BRANCH,
        15: FlowRoute.BRANCH,
        16: FlowRoute.BRANCH,
        17: FlowRoute.BRANCH,
        18: FlowRoute.BRANCH,
        4: FlowRoute.BRANCH,
        5: FlowRoute.BRANCH,
        6: FlowRoute.BRANCH,
        7: FlowRoute.BRANCH,
        8: FlowRoute.BRANCH,
        9: FlowRoute.BRANCH,
        10: FlowRoute.BRANCH,
        11: FlowRoute.BRANCH,
        12: FlowRoute.BRANCH,
        13: FlowRoute.BRANCH,
    }


def test_model_network_construction():
    lines, blocks = build_test_network()
    core_network = CoreNetwork(
        config=CoreNetworkConfig(lines=lines, sprinkler_blocks=blocks)
    )
    # using model network default config (light hazard + auto compute pipe dimensions)
    model_network = ModelNetwork(core_network)

    assert {
        edge_id: (
            pipe.diameter,
            pipe.material,
            pipe.schedule,
            pipe.specs,
            pipe.connection_type,
        )
        for edge_id, pipe in model_network.get_pipes_with_edges_ids().items()
    } == {
        1: (
            SteelDims.DIM_2_5_INCHES,
            SteelMaterial.ERW,
            SteelSchedule.SCD40,
            SteelSpecs.ASTM,
            SteelConnection.Grooved,
        ),
        2: (
            SteelDims.DIM_2_INCHES,
            SteelMaterial.ERW,
            SteelSchedule.SCD40,
            SteelSpecs.ASTM,
            SteelConnection.Grooved,
        ),
        3: (
            SteelDims.DIM_1_5_INCHES,
            SteelMaterial.ERW,
            SteelSchedule.SCD40,
            SteelSpecs.ASTM,
            SteelConnection.Grooved,
        ),
        14: (
            SteelDims.DIM_1_5_INCHES,
            SteelMaterial.ERW,
            SteelSchedule.SCD40,
            SteelSpecs.ASTM,
            SteelConnection.Grooved,
        ),
        15: (
            SteelDims.DIM_1_5_INCHES,
            SteelMaterial.ERW,
            SteelSchedule.SCD40,
            SteelSpecs.ASTM,
            SteelConnection.Grooved,
        ),
        16: (
            SteelDims.DIM_1_25_INCHES,
            SteelMaterial.ERW,
            SteelSchedule.SCD40,
            SteelSpecs.ASTM,
            SteelConnection.Grooved,
        ),
        17: (
            SteelDims.DIM_1_INCHES,
            SteelMaterial.ERW,
            SteelSchedule.SCD40,
            SteelSpecs.ASTM,
            SteelConnection.Grooved,
        ),
        18: (
            SteelDims.DIM_1_INCHES,
            SteelMaterial.ERW,
            SteelSchedule.SCD40,
            SteelSpecs.ASTM,
            SteelConnection.Grooved,
        ),
        9: (
            SteelDims.DIM_1_5_INCHES,
            SteelMaterial.ERW,
            SteelSchedule.SCD40,
            SteelSpecs.ASTM,
            SteelConnection.Grooved,
        ),
        10: (
            SteelDims.DIM_1_5_INCHES,
            SteelMaterial.ERW,
            SteelSchedule.SCD40,
            SteelSpecs.ASTM,
            SteelConnection.Grooved,
        ),
        11: (
            SteelDims.DIM_1_25_INCHES,
            SteelMaterial.ERW,
            SteelSchedule.SCD40,
            SteelSpecs.ASTM,
            SteelConnection.Grooved,
        ),
        12: (
            SteelDims.DIM_1_INCHES,
            SteelMaterial.ERW,
            SteelSchedule.SCD40,
            SteelSpecs.ASTM,
            SteelConnection.Grooved,
        ),
        13: (
            SteelDims.DIM_1_INCHES,
            SteelMaterial.ERW,
            SteelSchedule.SCD40,
            SteelSpecs.ASTM,
            SteelConnection.Grooved,
        ),
        4: (
            SteelDims.DIM_1_5_INCHES,
            SteelMaterial.ERW,
            SteelSchedule.SCD40,
            SteelSpecs.ASTM,
            SteelConnection.Grooved,
        ),
        5: (
            SteelDims.DIM_1_5_INCHES,
            SteelMaterial.ERW,
            SteelSchedule.SCD40,
            SteelSpecs.ASTM,
            SteelConnection.Grooved,
        ),
        6: (
            SteelDims.DIM_1_25_INCHES,
            SteelMaterial.ERW,
            SteelSchedule.SCD40,
            SteelSpecs.ASTM,
            SteelConnection.Grooved,
        ),
        7: (
            SteelDims.DIM_1_INCHES,
            SteelMaterial.ERW,
            SteelSchedule.SCD40,
            SteelSpecs.ASTM,
            SteelConnection.Grooved,
        ),
        8: (
            SteelDims.DIM_1_INCHES,
            SteelMaterial.ERW,
            SteelSchedule.SCD40,
            SteelSpecs.ASTM,
            SteelConnection.Grooved,
        ),
    }
    assert {
        junction_id: [
            (
                type(connection).__name__,
                getattr(connection, "run_diameter", None),
                getattr(connection, "branch_diameter", None),
                getattr(connection, "diameter", None),
                getattr(connection, "angle", None),
                getattr(connection, "large_diameter", None),
                getattr(connection, "small_diameter", None),
                connection.material,
                connection.schedule,
                connection.specs,
                connection.connection_type,
            )
            for connection in connections
        ]
        for junction_id, connections in (
            model_network.get_fire_connections_with_junctions_ids().items()
        )
    } == {
        1: [
            (
                "Tee",
                SteelDims.DIM_2_5_INCHES,
                SteelDims.DIM_1_5_INCHES,
                None,
                None,
                None,
                None,
                SteelMaterial.ERW,
                SteelSchedule.SCD40,
                SteelSpecs.ASTM,
                SteelConnection.Grooved,
            ),
            (
                "Reducer",
                None,
                None,
                None,
                None,
                SteelDims.DIM_2_5_INCHES,
                SteelDims.DIM_2_INCHES,
                SteelMaterial.ERW,
                SteelSchedule.SCD40,
                SteelSpecs.ASTM,
                SteelConnection.Grooved,
            ),
        ],
        2: [
            (
                "Tee",
                SteelDims.DIM_2_INCHES,
                SteelDims.DIM_1_5_INCHES,
                None,
                None,
                None,
                None,
                SteelMaterial.ERW,
                SteelSchedule.SCD40,
                SteelSpecs.ASTM,
                SteelConnection.Grooved,
            ),
            (
                "Reducer",
                None,
                None,
                None,
                None,
                SteelDims.DIM_2_INCHES,
                SteelDims.DIM_1_5_INCHES,
                SteelMaterial.ERW,
                SteelSchedule.SCD40,
                SteelSpecs.ASTM,
                SteelConnection.Grooved,
            ),
        ],
        3: [
            (
                "Elbow",
                None,
                None,
                SteelDims.DIM_1_5_INCHES,
                90.0,
                None,
                None,
                SteelMaterial.ERW,
                SteelSchedule.SCD40,
                SteelSpecs.ASTM,
                SteelConnection.Grooved,
            )
        ],
        5: [
            (
                "Reducer",
                None,
                None,
                None,
                None,
                SteelDims.DIM_1_5_INCHES,
                SteelDims.DIM_1_25_INCHES,
                SteelMaterial.ERW,
                SteelSchedule.SCD40,
                SteelSpecs.ASTM,
                SteelConnection.Grooved,
            )
        ],
        6: [
            (
                "Reducer",
                None,
                None,
                None,
                None,
                SteelDims.DIM_1_25_INCHES,
                SteelDims.DIM_1_INCHES,
                SteelMaterial.ERW,
                SteelSchedule.SCD40,
                SteelSpecs.ASTM,
                SteelConnection.Grooved,
            )
        ],
        9: [
            (
                "Reducer",
                None,
                None,
                None,
                None,
                SteelDims.DIM_1_5_INCHES,
                SteelDims.DIM_1_25_INCHES,
                SteelMaterial.ERW,
                SteelSchedule.SCD40,
                SteelSpecs.ASTM,
                SteelConnection.Grooved,
            )
        ],
        10: [
            (
                "Reducer",
                None,
                None,
                None,
                None,
                SteelDims.DIM_1_25_INCHES,
                SteelDims.DIM_1_INCHES,
                SteelMaterial.ERW,
                SteelSchedule.SCD40,
                SteelSpecs.ASTM,
                SteelConnection.Grooved,
            )
        ],
        13: [
            (
                "Reducer",
                None,
                None,
                None,
                None,
                SteelDims.DIM_1_5_INCHES,
                SteelDims.DIM_1_25_INCHES,
                SteelMaterial.ERW,
                SteelSchedule.SCD40,
                SteelSpecs.ASTM,
                SteelConnection.Grooved,
            )
        ],
        14: [
            (
                "Reducer",
                None,
                None,
                None,
                None,
                SteelDims.DIM_1_25_INCHES,
                SteelDims.DIM_1_INCHES,
                SteelMaterial.ERW,
                SteelSchedule.SCD40,
                SteelSpecs.ASTM,
                SteelConnection.Grooved,
            )
        ],
    }


def test_geometry_network_construction():
    lines, blocks = build_test_network()
    core_network = CoreNetwork(
        config=CoreNetworkConfig(lines=lines, sprinkler_blocks=blocks)
    )
    model_network = ModelNetwork(core_network)
    geometry_network = GeometryNetwork(core_network, model_network)

    assert {
        junction_id: [
            (
                type(component).__name__,
                component.transform.origin.x,
                component.transform.origin.y,
                component.transform.angle,
            )
            for component in components
        ]
        for junction_id, components in (
            geometry_network.get_geometric_fire_connections_with_junctions_ids().items()
        )
    } == {
        1: [
            ("GeometricTee", mm(27.094), mm(19.2562), pi / 2.0),
            ("GeometricReducer", mm(27.094), mm(19.4322), -pi / 2.0),
        ],
        2: [
            ("GeometricTee", mm(27.094), mm(22.1564), pi / 2.0),
            ("GeometricReducer", mm(27.094), 22320.4, -pi / 2.0),
        ],
        3: [("GeometricElbow", 27037.0, 24999.4, 2 * pi)],
        5: [("GeometricReducer", 23588.6, mm(25.0564), 0.0)],
        6: [("GeometricReducer", 20658.6, mm(25.0564), 0.0)],
        9: [("GeometricReducer", 23588.6, mm(22.1564), 0.0)],
        10: [("GeometricReducer", 20658.6, mm(22.1564), 0.0)],
        13: [("GeometricReducer", 23588.6, mm(19.2562), 0.0)],
        14: [("GeometricReducer", 20658.6, mm(19.2562), 0.0)],
    }
    assert {
        edge_id: [
            (
                type(pipe).__name__,
                pipe.start.x,
                pipe.start.y,
                pipe.end.x,
                pipe.end.y,
            )
            for pipe in pipes
        ]
        for edge_id, pipes in geometry_network.get_geometric_pipes_with_edges_ids().items()
    } == {
        1: [
            ("GeometricPipe", mm(27.094), mm(18.819), mm(27.094), mm(19.1802)),
        ],
        2: [
            ("GeometricPipe", mm(27.094), mm(19.3322), mm(27.094), mm(19.38775)),
            ("GeometricPipe", mm(27.094), 19476.65, mm(27.094), mm(22.0924)),
        ],
        3: [
            ("GeometricPipe", mm(27.094), 22220.4, 27094.0, 22282.300000000003),
            ("GeometricPipe", mm(27.094), mm(22.3585), mm(27.094), mm(24.9994)),
        ],
        4: [
            ("GeometricPipe", mm(27.027), mm(19.2562), mm(26.7686), mm(19.2562)),
        ],
        5: [
            ("GeometricPipe", mm(26.7686), mm(19.2562), mm(23.8386), mm(19.2562)),
        ],
        6: [
            ("GeometricPipe", mm(23.8386), mm(19.2562), mm(23.62035), mm(19.2562)),
            ("GeometricPipe", 23556.85, mm(19.2562), mm(20.9086), mm(19.2562)),
        ],
        7: [
            ("GeometricPipe", mm(20.9086), mm(19.2562), mm(20.684), mm(19.2562)),
            ("GeometricPipe", mm(20.6332), mm(19.2562), mm(17.9786), mm(19.2562)),
        ],
        8: [
            ("GeometricPipe", mm(17.9786), mm(19.2562), mm(15.0486), mm(19.2562)),
        ],
        9: [
            ("GeometricPipe", mm(27.034), mm(22.1564), mm(26.7686), mm(22.1564)),
        ],
        10: [
            ("GeometricPipe", mm(26.7686), mm(22.1564), mm(23.8386), mm(22.1564)),
        ],
        11: [
            ("GeometricPipe", mm(23.8386), mm(22.1564), mm(23.62035), mm(22.1564)),
            ("GeometricPipe", 23556.85, mm(22.1564), mm(20.9086), mm(22.1564)),
        ],
        12: [
            ("GeometricPipe", mm(20.9086), mm(22.1564), mm(20.684), mm(22.1564)),
            ("GeometricPipe", mm(20.6332), mm(22.1564), mm(17.9786), mm(22.1564)),
        ],
        13: [
            ("GeometricPipe", mm(17.9786), mm(22.1564), mm(15.0486), mm(22.1564)),
        ],
        14: [
            ("GeometricPipe", mm(27.037), mm(25.0564), mm(26.7686), mm(25.0564)),
        ],
        15: [
            ("GeometricPipe", mm(26.7686), mm(25.0564), mm(23.8386), mm(25.0564)),
        ],
        16: [
            ("GeometricPipe", mm(23.8386), mm(25.0564), mm(23.62035), mm(25.0564)),
            ("GeometricPipe", 23556.85, mm(25.0564), mm(20.9086), mm(25.0564)),
        ],
        17: [
            ("GeometricPipe", mm(20.9086), mm(25.0564), mm(20.684), mm(25.0564)),
            ("GeometricPipe", mm(20.6332), mm(25.0564), mm(17.9786), mm(25.0564)),
        ],
        18: [
            ("GeometricPipe", mm(17.9786), mm(25.0564), mm(15.0486), mm(25.0564)),
        ],
    }
