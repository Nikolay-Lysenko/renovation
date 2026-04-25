"""
Draw elements that do not represent any real objects, but provide info about them.

Author: Nikolay Lysenko
"""


import math
from typing import Optional

import matplotlib.axes
import numpy as np
from matplotlib.patches import Polygon

from renovation.utils import shift_in_direction
from .anchor_mixins import PivotAnchorMixin
from .element import Element


class DimensionArrow(Element):
    """Dimension arrow."""

    def __init__(
            self,
            pivot_point: tuple[float, float],
            another_pivot_point: Optional[tuple[float, float]] = None,
            length: Optional[float] = None,
            orientation_angle: float = 0,
            width: int = 0.01,
            tip_length: float = 0.1,
            font_size: int = 10,
            annotate_above: bool = False,
            color: str = 'black',
    ):
        """
        Initialize an instance.

        :param pivot_point:
            coordinates (in meters) of pivot point;
            the leftmost point is pivot point if `orientation_angle == 0`
        :param another_pivot_point:
            coordinates (in meters) of another pivot point;
            the rightmost point is pivot point if `orientation_angle == 0`
        :param length:
            length of the wall (in meters); this value is also placed to annotation;
            this argument is used only if `another_pivot_point` is not passed
        :param orientation_angle:
            angle (in degrees) that specifies orientation of the arrow;
            it is measured between X-axis and the arrow in positive direction (counterclockwise);
            initial arrow is rotated around pivot point to get the desired orientation;
            this argument is used only if `another_pivot_point` is not passed
        :param width:
            width of lines (in meters before scaling)
        :param tip_length:
            length of single arrow tip (in meters before scaling)
        :param font_size:
            font size
        :param annotate_above:
            if it is set to `True`, annotation is placed above the arrow (prior to its rotation)
        :param color:
            color to use for drawing the arrow and its annotation
        :return:
            freshly created instance of `DimensionArrow` class
        """
        if another_pivot_point is not None:
            x_shift = another_pivot_point[0] - pivot_point[0]
            y_shift = another_pivot_point[1] - pivot_point[1]
            length = round(math.sqrt(x_shift ** 2 + y_shift ** 2), 8)
            orientation_angle = math.degrees(math.atan2(y_shift, x_shift))
        self.pivot_point = pivot_point
        self.length = length
        self.orientation_angle = orientation_angle
        self.width = width
        self.tip_length = tip_length
        self.font_size = font_size
        self.annotate_above = annotate_above
        self.color = color

    def draw(self, ax: matplotlib.axes.Axes) -> None:
        """Draw dimension arrow."""
        tip_angle = math.radians(30)
        initial_vertices = np.array([
            [0, 0],
            [
                self.tip_length - math.sin(tip_angle) * self.width,
                math.tan(tip_angle) * (self.tip_length - math.sin(tip_angle) * self.width)
            ],
            [
                self.tip_length,
                math.tan(tip_angle) * (self.tip_length - math.sin(tip_angle) * self.width)
                - math.cos(tip_angle) * self.width
            ],
            [
                self.width / 2 / math.tan(tip_angle) + self.width / math.sin(tip_angle),
                self.width / 2
            ],
            [
                self.length
                - self.width / 2 / math.tan(tip_angle) - self.width / math.sin(tip_angle),
                self.width / 2
            ],
            [
                self.length - self.tip_length,
                math.tan(tip_angle) * (self.tip_length - math.sin(tip_angle) * self.width)
                - math.cos(tip_angle) * self.width
            ],
            [
                self.length - self.tip_length + math.sin(tip_angle) * self.width,
                math.tan(tip_angle) * (self.tip_length - math.sin(tip_angle) * self.width)
            ],
            [self.length, 0],
            [
                self.length - self.tip_length + math.sin(tip_angle) * self.width,
                -math.tan(tip_angle) * (self.tip_length - math.sin(tip_angle) * self.width)
            ],
            [
                self.length - self.tip_length,
                -math.tan(tip_angle) * (self.tip_length - math.sin(tip_angle) * self.width)
                + math.cos(tip_angle) * self.width
            ],
            [
                self.length
                - self.width / 2 / math.tan(tip_angle) - self.width / math.sin(tip_angle),
                -self.width / 2
            ],
            [
                self.width / 2 / math.tan(tip_angle) + self.width / math.sin(tip_angle),
                -self.width / 2
            ],
            [
                self.tip_length,
                -math.tan(tip_angle) * (self.tip_length - math.sin(tip_angle) * self.width)
                + math.cos(tip_angle) * self.width
            ],
            [
                self.tip_length - math.sin(tip_angle) * self.width,
                -math.tan(tip_angle) * (self.tip_length - math.sin(tip_angle) * self.width)
            ],
        ])
        rotation_angle = math.radians(self.orientation_angle)
        rotation_matrix = np.array([
            [math.cos(rotation_angle), -math.sin(rotation_angle)],
            [math.sin(rotation_angle), math.cos(rotation_angle)],
        ])
        rotated_vertices = np.dot(rotation_matrix, initial_vertices.T).T
        shift_vector = np.array([[self.pivot_point[0], self.pivot_point[1]]])
        vertices = rotated_vertices + shift_vector
        arrow = Polygon(vertices, facecolor=self.color)
        ax.add_patch(arrow)

        initial_text_center = [
            self.length / 2,
            (self.font_size * 0.0125 if self.annotate_above else -self.font_size * 0.0125)
        ]
        text_pivot_point = np.dot(rotation_matrix, np.array([initial_text_center]).T).T
        text_pivot_point += shift_vector
        text_pivot_x = text_pivot_point[0][0].item()
        text_pivot_y = text_pivot_point[0][1].item()
        text = str(self.length)
        ax.text(
            text_pivot_x, text_pivot_y, text,
            verticalalignment='center', horizontalalignment='center',
            rotation=self.orientation_angle, color=self.color, fontsize=self.font_size
        )

    def calculate_anchor_coordinates(self, anchor_type: str) -> tuple[float, float]:
        """
        Calculate coordinates of a point that can be used as anchor for other elements.

        :param anchor_type:
            one of:
            * 'end_one' (the pivot point),
            * 'end_two' (the other end of the arrow)
        :return:
            coordinates of the anchor point
        """
        if anchor_type == "end_one":
            return self.pivot_point
        elif anchor_type == "end_two":
            return shift_in_direction(self.pivot_point, self.length, self.orientation_angle)
        else:
            ValueError(
                f"Anchor type '{anchor_type}' is not supported by `DimensionArrow` class."
            )


class TextBox(PivotAnchorMixin, Element):
    """Text box."""

    def __init__(
            self,
            pivot_point: tuple[float, float],
            lines: list[str],
            font_size: int = 10,
            color: str = 'black',
            transparency: float = 0.75,
    ):
        """
        Initialize an instance.

        :param pivot_point:
            coordinates (in meters) of pivot point; the center of a text box is its pivot point
        :param lines:
            text lines to be printed
        :param font_size:
            font size
        :param color:
            color to use for drawing the text and the bounding box
        :param transparency:
            transparency of the bounding box
        """
        self.pivot_point = pivot_point
        self.lines = lines
        self.font_size = font_size
        self.color = color
        self.transparency = transparency

    def draw(self, ax: matplotlib.axes.Axes) -> None:
        """Draw text box."""
        ax.text(
            self.pivot_point[0],
            self.pivot_point[1],
            '\n'.join(self.lines),
            verticalalignment='center',
            horizontalalignment='center',
            color=self.color,
            fontsize=self.font_size,
            bbox={'boxstyle': 'round', 'facecolor': 'white', 'alpha': self.transparency}
        )
