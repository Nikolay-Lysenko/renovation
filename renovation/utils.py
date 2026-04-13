"""
Utities for renovation project.

Author: Krzysztof Bartczak
"""

import math
import matplotlib.axes
from renovation.elements.options import get_label_color, get_id_color



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




def _get_text_alignment(rotation: float) -> tuple[str, str]:
    """
    Calculate text alignment based on rotation angle.

    :param rotation:
        rotation angle in degrees (0-360)
    :return:
        tuple of (horizontal_alignment, vertical_alignment)
    """
    textrotation = rotation % 360
    verticalalignment = 'bottom' if textrotation < 180 else 'top'
    horizontalalignment = 'left' if textrotation < 90 or textrotation >= 270 else 'right'
    return horizontalalignment, verticalalignment


def _render_text(
        ax: matplotlib.axes.Axes,
        position: tuple[float, float],
        text: str,
        rotation: float,
        color: str,
        fontsize: int = 9
) -> None:
    """
    Render text with automatic alignment based on rotation.

    :param ax:
        matplotlib axes to draw on
    :param position:
        (x, y) position for the text
    :param text:
        text to render
    :param rotation:
        rotation angle in degrees
    :param color:
        text color
    :param fontsize:
        font size for the text
    """
    horizontalalignment, verticalalignment = _get_text_alignment(rotation)
    ax.text(
        position[0],
        position[1],
        text,
        fontsize=fontsize,
        color=color,
        rotation=rotation,
        horizontalalignment=horizontalalignment,
        verticalalignment=verticalalignment
    )


def _render_label_and_id(
        ax: matplotlib.axes.Axes,
        element,
        element_type: str,
        position: tuple[float, float],
        rotation: float,
        label_prefix: str = "",
        id_prefix: str = ""
) -> None:
    """
    Render both label and ID for an element if colors are configured.

    :param ax:
        matplotlib axes to draw on
    :param element:
        element instance with .label and .id attributes
    :param element_type:
        type name for color lookup
    :param position:
        (x, y) position for the text
    :param rotation:
        rotation angle in degrees
    :param label_prefix:
        prefix to add before label text
    :param id_prefix:
        prefix to add before id text
    """

    # Render label if present and color is configured
    if element.label is not None:
        label_color = get_label_color(element_type)
        if label_color is not None:
            _render_text(ax, position, label_prefix + element.label, rotation, label_color)

    # Render ID if color is configured
    id_color = get_id_color(element_type)
    if id_color is not None:
        _render_text(ax, position, id_prefix + element.id, rotation, id_color)


