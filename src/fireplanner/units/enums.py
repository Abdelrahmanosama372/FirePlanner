from enum import Enum


class LengthUnit(str, Enum):
    MILLIMETER = "mm"
    CENTIMETER = "cm"
    METER = "m"
    KILOMETER = "km"
