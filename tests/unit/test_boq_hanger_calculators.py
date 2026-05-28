from fireplanner.boq.calculators.akmon_calculator import AkmonCalculator
from fireplanner.boq.calculators.hanger_calculator import HangerCalculator
from fireplanner.boq.calculators.nut_calculator import NutCalculator
from fireplanner.boq.calculators.stud_calculator import StudCalculator
from fireplanner.boq.calculators.washer_calculator import WasherCalculator
from fireplanner.firecomponent import (
    Hanger,
    Pipe,
    SteelConnection,
    SteelDims,
    SteelMaterial,
    SteelSchedule,
    SteelSpecs,
)
from fireplanner.geometry.primitives import Line, Point
from fireplanner.networks.junction_assembly import HangerAssembly, PipeAssembly
from fireplanner.networks.junction_info import EdgeInfo


def _pipe(diameter: SteelDims) -> Pipe:
    return Pipe(
        diameter=diameter,
        material=SteelMaterial.ERW,
        schedule=SteelSchedule.SCD40,
        specs=SteelSpecs.ASTM,
        connection_type=SteelConnection.Grooved,
    )


def _hanger(diameter: SteelDims) -> Hanger:
    return Hanger(
        diameter=diameter,
        material=SteelMaterial.ERW,
        schedule=SteelSchedule.SCD40,
        specs=SteelSpecs.ASTM,
        connection_type=SteelConnection.Grooved,
    )


def _hanger_assembly(
    diameter: SteelDims, elevation: float, count: int
) -> HangerAssembly:
    edge_info = EdgeInfo(
        edge_id=1,
        line=Line(start=Point(x=0, y=0), end=Point(x=1000, y=0)),
        length=1000.0,
        sprinkler_count=0,
        elevation=elevation,
    )
    pipe_assembly = PipeAssembly(
        edge_info=edge_info, diameter=diameter, pipe=_pipe(diameter)
    )
    return HangerAssembly(
        hanger=_hanger(diameter), pipe=pipe_assembly, hangers_count=count
    )


def test_hanger_stud_and_fittings_calculators():
    assemblies = [
        _hanger_assembly(SteelDims.DIM_1_INCHES, elevation=3000, count=2),
        _hanger_assembly(SteelDims.DIM_3_INCHES, elevation=4200, count=1),
    ]

    hanger_boq = HangerCalculator.compute(assemblies)
    assert sum(hanger_boq.counts_by_spec.values()) == 3

    stud_boq = StudCalculator.compute(
        hanger_assemblies=assemblies,
        full_ceiling_elevation=4500,
    )
    assert sum(stud_boq.counts_by_spec.values()) == 3
    assert round(sum(stud_boq.lengths_by_spec.values()), 3) == 3.3

    akmon_boq = AkmonCalculator.compute(stud_boq)
    nut_boq = NutCalculator.compute(stud_boq)
    washer_boq = WasherCalculator.compute(stud_boq)

    assert sum(akmon_boq.counts_by_spec.values()) == 3
    assert sum(nut_boq.counts_by_spec.values()) == 12
    assert sum(washer_boq.counts_by_spec.values()) == 12
