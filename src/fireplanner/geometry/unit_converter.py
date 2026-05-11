from fireplanner.geometry.primitives import Arc, Block, Line, Point
from fireplanner.units import LengthUnit, LengthUnitConverter


class GeometryUnitConverter:
    @staticmethod
    def point_to_unit(point: Point, from_unit: LengthUnit, to_unit: LengthUnit) -> Point:
        return Point(
            x=LengthUnitConverter.convert(point.x, from_unit, to_unit),
            y=LengthUnitConverter.convert(point.y, from_unit, to_unit),
            z=LengthUnitConverter.convert(point.z, from_unit, to_unit),
            id=point.id,
            style=point.style,
        )

    @staticmethod
    def line_to_unit(line: Line, from_unit: LengthUnit, to_unit: LengthUnit) -> Line:
        return Line(
            start=GeometryUnitConverter.point_to_unit(line.start, from_unit, to_unit),
            end=GeometryUnitConverter.point_to_unit(line.end, from_unit, to_unit),
            line_type=line.line_type,
            id=line.id,
            style=line.style,
        )

    @staticmethod
    def block_to_unit(
        block: Block, from_unit: LengthUnit, to_unit: LengthUnit
    ) -> Block:
        return Block(
            name=block.name,
            center=GeometryUnitConverter.point_to_unit(block.center, from_unit, to_unit),
            id=block.id,
            style=block.style,
        )

    @staticmethod
    def arc_to_unit(arc: Arc, from_unit: LengthUnit, to_unit: LengthUnit) -> Arc:
        return Arc(
            start=GeometryUnitConverter.point_to_unit(arc.start, from_unit, to_unit),
            center=GeometryUnitConverter.point_to_unit(arc.center, from_unit, to_unit),
            angle=arc.angle,
            id=arc.id,
        )
