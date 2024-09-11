"""
Draw elements representing electricity-related objects.

Author: Nikolay Lysenko
"""


import math

import matplotlib.axes
from matplotlib.patches import Arc

from renovation.constants import STRAIGHT_ANGLE_IN_DEGREES
from .element import Element


class PowerOutlet(Element):
    """Power outlet."""

    def __init__(
            self,
            anchor_point: tuple[float, float],
            length: float,
            orientation_angle: float = 0,
            waterproof: bool = False,
            high_voltage: bool = False,
            low_current: bool = False,
            line_width: float = 0.5,
            color: str = 'black',
    ):
        """
        Initialize an instance.

        :param anchor_point:
            coordinates (in meters) of anchor point;
            the center of the segment shared with a wall is anchor point
        :param length:
            length of the power outlet (in meters)
        :param orientation_angle:
            angle (in degrees) that specifies orientation of the power outlet;
            it is measured between X-axis and the outlet in positive direction (counterclockwise);
            initial outlet is rotated around anchor point to get the desired orientation
        :param waterproof:
            indicator whether the power outlet is waterproof
        :param high_voltage:
            indicator whether the power outlet has 380-400V instead of regular 220-230V
        :param low_current:
            indicator whether the power outlet is designed for low-current appliances
            (e.g., Wi-Fi router); also it can be used for Ethernet outlets and so on
        :param line_width:
            width of lines for `matplotlib`
        :param color:
            color to use for drawing the power outlet
        :return:
            freshly created instance of `PowerOutlet` class
        """
        self.anchor_point = anchor_point
        self.length = length
        self.orientation_angle = orientation_angle
        self.waterproof = waterproof
        self.high_voltage = high_voltage
        self.low_current = low_current
        self.line_width = line_width
        self.color = color

    def draw(self, ax: matplotlib.axes.Axes) -> None:
        """Draw power outlet."""
        arc = Arc(
            self.anchor_point,
            self.length,
            self.length,
            theta1=self.orientation_angle,
            theta2=self.orientation_angle + 2 * STRAIGHT_ANGLE_IN_DEGREES,
            lw=self.line_width,
            color=self.color
        )
        ax.add_patch(arc)

        half_length = 0.5 * self.length
        tip_angle_in_radians = math.radians(self.orientation_angle + STRAIGHT_ANGLE_IN_DEGREES)
        arc_middle = (
            self.anchor_point[0] + half_length * math.cos(tip_angle_in_radians),
            self.anchor_point[1] + half_length * math.sin(tip_angle_in_radians)
        )
        ax.plot(
            [self.anchor_point[0], arc_middle[0]],
            [self.anchor_point[1], arc_middle[1]],
            lw=self.line_width,
            color=self.color
        )

        orientation_angle_in_radians = math.radians(self.orientation_angle)
        bar_left_end = (
            arc_middle[0] - half_length * math.cos(orientation_angle_in_radians),
            arc_middle[1] - half_length * math.sin(orientation_angle_in_radians)
        )
        bar_right_end = (
            arc_middle[0] + half_length * math.cos(orientation_angle_in_radians),
            arc_middle[1] + half_length * math.sin(orientation_angle_in_radians)
        )
        ax.plot(
            [bar_left_end[0], bar_right_end[0]],
            [bar_left_end[1], bar_right_end[1]],
            lw=self.line_width,
            color=self.color
        )

        tip_end = (
            self.anchor_point[0] + self.length * math.cos(tip_angle_in_radians),
            self.anchor_point[1] + self.length * math.sin(tip_angle_in_radians)
        )
        ax.plot(
            [arc_middle[0], tip_end[0]],
            [arc_middle[1], tip_end[1]],
            lw=self.line_width,
            color=self.color
        )

        if self.waterproof:
            angle_in_degrees = self.orientation_angle + 1.5 * STRAIGHT_ANGLE_IN_DEGREES
            angle_in_radians = math.radians(angle_in_degrees)
            radius_end = (
                self.anchor_point[0] + half_length * math.cos(angle_in_radians),
                self.anchor_point[1] + half_length * math.sin(angle_in_radians)
            )
            ax.plot(
                [self.anchor_point[0], radius_end[0]],
                [self.anchor_point[1], radius_end[1]],
                lw=self.line_width,
                color=self.color
            )
