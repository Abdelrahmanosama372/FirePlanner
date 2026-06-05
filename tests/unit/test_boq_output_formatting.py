from fireplanner.boq.models import (
    BOQReport,
    ConnectionBOQ,
    ElbowKey,
    HangerBOQ,
    HangerFittingBOQ,
    PaintBOQ,
    PipeBOQ,
    ReducerKey,
    SteelSpec,
    StudBOQ,
    TeeKey,
    Unit,
)
from fireplanner.boq.output.formatting import connection_sections
from fireplanner.firecomponent import (
    SteelConnection,
    SteelDims,
    SteelMaterial,
    SteelSchedule,
    SteelSpecs,
)


def test_connection_sections_group_rows_under_connection_category():
    steel = SteelSpec(
        material=SteelMaterial.ERW,
        schedule=SteelSchedule.SCD40,
        specs=SteelSpecs.ASTM,
    )
    report = BOQReport(
        pipes=PipeBOQ(lengths_by_spec={}, unit=Unit.M),
        connections=ConnectionBOQ(
            fittings_counts={
                ElbowKey(
                    diameter=SteelDims.DIM_1_INCHES,
                    steel=steel,
                    connection=SteelConnection.Threaded,
                ): 2,
                ElbowKey(
                    diameter=SteelDims.DIM_1_5_INCHES,
                    steel=steel,
                    connection=SteelConnection.Threaded,
                ): 3,
                TeeKey(
                    run_diameter=SteelDims.DIM_1_5_INCHES,
                    branch_diameter=SteelDims.DIM_1_INCHES,
                    steel=steel,
                    connection=SteelConnection.Threaded,
                ): 4,
                ReducerKey(
                    large_diameter=SteelDims.DIM_1_5_INCHES,
                    small_diameter=SteelDims.DIM_1_INCHES,
                    steel=steel,
                    connection=SteelConnection.Threaded,
                ): 5,
            },
            unit=Unit.Num,
        ),
        hangers=HangerBOQ(counts_by_spec={}, unit=Unit.Num),
        studs=StudBOQ(lengths_by_spec={}, counts_by_spec={}, unit=Unit.M),
        hanger_fittings=HangerFittingBOQ(counts_by_spec={}, unit=Unit.Num),
        paint=PaintBOQ(primer=0.0, lacque=0.0, thinner=0.0, unit=Unit.Liter),
    )

    sections = connection_sections(report)

    assert [section_name for section_name, _ in sections] == [
        "Tees",
        "Elbows",
        "Reducers",
    ]
    assert sections[0][1] == [
        ("4", "run=1.5, branch=1.0", "erw", "scd40", "astm", "threaded")
    ]
    assert sections[1][1] == [
        ("2", "1.0", "erw", "scd40", "astm", "threaded"),
        ("3", "1.5", "erw", "scd40", "astm", "threaded"),
    ]
    assert sections[2][1] == [("5", "1.5->1.0", "erw", "scd40", "astm", "threaded")]
