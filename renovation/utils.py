"""
Utities for renovation project.

Author: Krzysztof Bartczak
"""

import math

def rotate_point(anchor_point: tuple[float, float],
                 offset_x: float, offset_y: float, angle_rad: float) -> tuple[float, float]:
    """
    Rotate a point around an anchor point.
    Classic 2D rotation formula:
        x' = a + offset_x * cos(theta) - offset_y * sin(theta)
        y' = b + offset_x * sin(theta) + offset_y * cos(theta)

    Parameters:
        anchor_point : tuple (a, b)
            The anchor point coordinates.
        offset_x : float
            X offset of point relative to anchor.
        offset_y : float
            Y offset of point relative to anchor.
        angle_rad : float
            Rotation angle in radians (counter-clockwise).

    Returns:
        (x_rot, y_rot) : tuple
            Coordinates of rotated point.
    """
    a = anchor_point[0]
    b = anchor_point[1]

    cos_theta = math.cos(angle_rad)
    sin_theta = math.sin(angle_rad)

    x_rot = a + offset_x * cos_theta - offset_y * sin_theta
    y_rot = b + offset_x * sin_theta + offset_y * cos_theta

    return x_rot, y_rot
