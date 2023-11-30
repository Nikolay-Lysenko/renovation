"""
Draw basic elements.

Author: Nikolay Lysenko
"""


from abc import ABC, abstractmethod

import matplotlib.axes
from matplotlib.patches import Arc, Rectangle


class Element(ABC):
    """Abstract element."""

    @abstractmethod
    def draw(self, ax: matplotlib.axes.Axes):
        """Draw the element."""
        pass


class Wall(Element):
    """Rectangular wall."""

    def __init__(
            self,
            anchor_point: tuple[float, float],
            length: float,
            width: float,
            orientation_angle: float,
            color: str = 'black'
    ):
        """
        Initialize an instance.

        :param anchor_point:
            coordinates (in meters) of anchor point;
            bottom left point is anchor point if `orientation_angle == 0`
        :param length:
            length of the wall (in meters)
        :param width:
            width of the wall (in meters)
        :param orientation_angle:
            angle (in degrees) that specifies orientation of the wall;
            initial wall is rotated around anchor point to get the desired orientation
        :param color:
            color to use for drawing the wall
        """
        self.anchor_point = anchor_point
        self.length = length
        self.width = width
        self.orientation_angle = orientation_angle
        self.color = color

    def draw(self, ax: matplotlib.axes.Axes):
        """Draw rectangular wall."""
        patch = Rectangle(
            self.anchor_point,
            self.length,
            self.width,
            angle=self.orientation_angle,
            facecolor=self.color
        )
        ax.add_patch(patch)
