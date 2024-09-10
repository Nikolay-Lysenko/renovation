"""
Draw elements that do not represent any real objects, but provide info about them.

Author: Nikolay Lysenko
"""


import math

import matplotlib.axes
import numpy as np
from matplotlib.patches import Polygon

from .element import Element


class DimensionArrow(Element):
    """Dimension arrow."""

    def __init__(
            self,
            anchor_point: tuple[float, float],
            length: float,
            orientation_angle: float = 0,
            width: int = 0.01,
            tip_length: float = 0.1,
            font_size: int = 10,
            annotate_above: bool = False,
            color: str = 'black',
    ):
        """
        Initialize an instance.

        :param anchor_point:
            coordinates (in meters) of anchor point;
            the leftmost point is anchor point if `orientation_angle == 0`
        :param length:
            length of the wall (in meters); this value is also placed to annotation
        :param orientation_angle:
            angle (in degrees) that specifies orientation of the arrow;
            it is measured between X-axis and the arrow in positive direction (counterclockwise);
            initial arrow is rotated around anchor point to get the desired orientation
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
        self.anchor_point = anchor_point
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
        shift_vector = np.array([[self.anchor_point[0], self.anchor_point[1]]])
        vertices = rotated_vertices + shift_vector
        arrow = Polygon(vertices, facecolor=self.color)
        ax.add_patch(arrow)

        initial_text_center = [
            self.length / 2,
            (self.font_size * 0.0125 if self.annotate_above else -self.font_size * 0.0125)
        ]
        text_anchor_point = np.dot(rotation_matrix, np.array([initial_text_center]).T).T
        text_anchor_point += shift_vector
        text_anchor_x = text_anchor_point[0][0].item()
        text_anchor_y = text_anchor_point[0][1].item()
        text = str(self.length)
        ax.text(
            text_anchor_x, text_anchor_y, text,
            verticalalignment='center', horizontalalignment='center',
            rotation=self.orientation_angle, color=self.color, fontsize=self.font_size
        )
