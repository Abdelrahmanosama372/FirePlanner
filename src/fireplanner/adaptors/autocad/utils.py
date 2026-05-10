LINEWEIGHT_MAP = {
    0.00: 0,
    0.05: 5,
    0.09: 9,
    0.13: 13,
    0.15: 15,
    0.18: 18,
    0.20: 20,
    0.25: 25,
    0.30: 30,
    0.35: 35,
    0.40: 40,
    0.50: 50,
    0.53: 53,
    0.60: 60,
    0.70: 70,
    0.80: 80,
    0.90: 90,
    1.00: 100,
    1.06: 106,
    1.20: 120,
    1.40: 140,
    1.58: 158,
    2.00: 200,
    2.11: 211,
}

color_mapping = {
    "red": 1,
    "yellow": 2,
    "green": 3,
    "cyan": 4,
    "blue": 5,
    "magenta": 6,
    "white": 7,
    "Dark Gray": 8,
    "Light Gray": 9,
}


def color_name_to_aci(color: str) -> int | None:
    return color_mapping.get(color.strip().lower())


def lineweight_to_aci(weight: float) -> int:
    valid_weights = sorted(LINEWEIGHT_MAP.keys())

    nearest = valid_weights[0]

    for w in valid_weights:
        if w <= weight:
            nearest = w
        else:
            break

    return LINEWEIGHT_MAP[nearest]
