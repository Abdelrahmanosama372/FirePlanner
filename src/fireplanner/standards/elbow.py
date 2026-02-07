from fireplanner.firecomponent.base import SteelDims


def elbow_90_lr_center_to_end(dim: SteelDims) -> float:
    return round(dim.value * 1.5 * 25.4)

def elbow_90_sr_center_to_end(dim: SteelDims) -> float:
    return round(dim.value * 25.4)
