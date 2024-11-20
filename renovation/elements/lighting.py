"""
Draw elements representing lighting-related objects.

Author: Nikolay Lysenko
"""


import math

import matplotlib.axes
from matplotlib.patches import Arc, Circle, Rectangle

from renovation.constants import STRAIGHT_ANGLE_IN_DEGREES
from .element import Element


class CeilingLamp(Element):
    """Ceiling lamp represented by a circle and a cross inside."""

    def __init__(
            self,
            anchor_point: tuple[float, float],
            symbol_diameter: float,
            line_width: float = 0.5,
            color: str = 'black'
    ):
        """
        Initialize an instance.

        :param anchor_point:
            coordinates (in meters) of anchor point; here, it is the center of the symbol
        :param symbol_diameter:
            diameter of the symbol (in meters)
        :param line_width:
            width of lines for `matplotlib`
        :param color:
            color to use for drawing the lamp
        :return:
            freshly created instance of `CeilingLamp` class
        """
        self.anchor_point = anchor_point
        self.symbol_diameter = symbol_diameter
        self.line_width = line_width
        self.color = color

    def draw(self, ax: matplotlib.axes.Axes) -> None:
        """Draw ceiling lamp."""
        radius = 0.5 * self.symbol_diameter
        circle = Circle(
            self.anchor_point,
            radius,
            fill=False,
            lw=self.line_width,
            edgecolor=self.color
        )
        ax.add_patch(circle)

        ax.plot(
            [
                self.anchor_point[0] - 0.5 * math.sqrt(2) * radius,
                self.anchor_point[0] + 0.5 * math.sqrt(2) * radius
            ],
            [
                self.anchor_point[1] - 0.5 * math.sqrt(2) * radius,
                self.anchor_point[1] + 0.5 * math.sqrt(2) * radius
            ],
            lw=self.line_width,
            color=self.color
        )
        ax.plot(
            [
                self.anchor_point[0] - 0.5 * math.sqrt(2) * radius,
                self.anchor_point[0] + 0.5 * math.sqrt(2) * radius
            ],
            [
                self.anchor_point[1] + 0.5 * math.sqrt(2) * radius,
                self.anchor_point[1] - 0.5 * math.sqrt(2) * radius
            ],
            lw=self.line_width,
            color=self.color
        )


class WallLamp(Element):
    """Wall lamp (e.g., sconce)."""

    def __init__(
            self,
            anchor_point: tuple[float, float],
            symbol_diameter: float,
            orientation_angle: float = 0.0,
            stub_relative_depth: float = 0.3,
            line_width: float = 0.5,
            color: str = 'black'
    ):
        """
        Initialize an instance.

        :param anchor_point:
            coordinates (in meters) of anchor point;
            here, it is the center of wall connection segment
        :param symbol_diameter:
            diameter of the symbol (in meters)
        :param orientation_angle:
            angle (in degrees) that specifies orientation of the lamp;
            it is measured between X-axis and the lamp in positive direction (counterclockwise);
            initial lamp is rotated around anchor point to get the desired orientation
        :param stub_relative_depth:
            ratio of stub depth to its width
        :param line_width:
            width of lines for `matplotlib`
        :param color:
            color to use for drawing the lamp
        :return:
            freshly created instance of `WallLamp` class
        """
        self.anchor_point = anchor_point
        self.symbol_diameter = symbol_diameter
        self.orientation_angle = orientation_angle
        self.stub_relative_depth = stub_relative_depth
        self.line_width = line_width
        self.color = color

    def draw(self, ax: matplotlib.axes.Axes) -> None:
        """Draw wall lamp."""
        orientation_angle_in_radians = math.radians(self.orientation_angle)
        stub_width = 0.5 * math.sqrt(2) * self.symbol_diameter
        stub_depth = self.stub_relative_depth * stub_width
        stub_anchor_point = (
            self.anchor_point[0] - 0.5 * math.cos(orientation_angle_in_radians) * stub_width,
            self.anchor_point[1] - 0.5 * math.sin(orientation_angle_in_radians) * stub_width
        )
        stub = Rectangle(
            stub_anchor_point,
            stub_width,
            stub_depth,
            angle=self.orientation_angle,
            fill=False,
            lw=self.line_width,
            edgecolor=self.color
        )
        ax.add_patch(stub)

        orthogonal_angle_in_radians = orientation_angle_in_radians + math.pi / 2
        shift = stub_depth + 0.5 * stub_width
        arc_center = (
            self.anchor_point[0] + math.cos(orthogonal_angle_in_radians) * shift,
            self.anchor_point[1] + math.sin(orthogonal_angle_in_radians) * shift
        )
        arc = Arc(
            arc_center,
            self.symbol_diameter,
            self.symbol_diameter,
            theta1=self.orientation_angle - 0.5 * STRAIGHT_ANGLE_IN_DEGREES,
            theta2=self.orientation_angle + 2.5 * STRAIGHT_ANGLE_IN_DEGREES,
            lw=self.line_width,
            color=self.color
        )
        ax.add_patch(arc)

        cross_angles = [
            orientation_angle_in_radians - 0.75 * math.pi,
            orientation_angle_in_radians + 0.25 * math.pi,
            orientation_angle_in_radians + 0.75 * math.pi,
            orientation_angle_in_radians - 0.25 * math.pi
        ]
        ax.plot(
            [
                arc_center[0] + 0.5 * math.cos(cross_angles[0]) * self.symbol_diameter,
                arc_center[0] + 0.5 * math.cos(cross_angles[1]) * self.symbol_diameter
            ],
            [
                arc_center[1] + 0.5 * math.sin(cross_angles[0]) * self.symbol_diameter,
                arc_center[1] + 0.5 * math.sin(cross_angles[1]) * self.symbol_diameter
            ],
            lw=self.line_width,
            color=self.color
        )
        ax.plot(
            [
                arc_center[0] + 0.5 * math.cos(cross_angles[2]) * self.symbol_diameter,
                arc_center[0] + 0.5 * math.cos(cross_angles[3]) * self.symbol_diameter
            ],
            [
                arc_center[1] + 0.5 * math.sin(cross_angles[2]) * self.symbol_diameter,
                arc_center[1] + 0.5 * math.sin(cross_angles[3]) * self.symbol_diameter
            ],
            lw=self.line_width,
            color=self.color
        )
