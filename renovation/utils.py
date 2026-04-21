"""
Do auxiliary tasks.

Author: Nikolay Lysenko
"""


import math


def shift_in_direction(
        start: tuple[float, float], shift: float, angle: float
) -> tuple[float, float]:
    """
    Shift starting point to the given distance in the given direction.

    :param start:
        starting point
    :param shift:
        shift value
    :param angle:
        angle (in degrees)
    :return:
        coordinates of the shifted point
    """
    angle_in_rad = math.radians(angle)
    return start[0] + math.cos(angle_in_rad) * shift, start[1] + math.sin(angle_in_rad) * shift
