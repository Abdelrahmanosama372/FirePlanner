from fireplanner.units.enums import LengthUnit


class LengthUnitConverter:
    _TO_METER_FACTOR: dict[LengthUnit, float] = {
        LengthUnit.MILLIMETER: 0.001,
        LengthUnit.CENTIMETER: 0.01,
        LengthUnit.METER: 1.0,
        LengthUnit.KILOMETER: 1000.0,
    }

    @staticmethod
    def convert(value: float, from_unit: LengthUnit, to_unit: LengthUnit) -> float:
        if from_unit not in LengthUnitConverter._TO_METER_FACTOR:
            raise ValueError(f"Unsupported source unit: {from_unit}")
        if to_unit not in LengthUnitConverter._TO_METER_FACTOR:
            raise ValueError(f"Unsupported target unit: {to_unit}")

        value_in_meters = value * LengthUnitConverter._TO_METER_FACTOR[from_unit]
        return value_in_meters / LengthUnitConverter._TO_METER_FACTOR[to_unit]
