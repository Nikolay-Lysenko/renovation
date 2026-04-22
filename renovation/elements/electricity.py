"""
Draw elements representing electricity-related objects.

Author: Nikolay Lysenko
"""


import matplotlib.axes
from matplotlib.patches import Arc, Circle

from renovation.constants import RIGHT_ANGLE_IN_DEGREES
from renovation.utils import shift_in_direction
from .anchor_mixins import PivotAnchorMixin
from .element import Element


class PowerOutlet(PivotAnchorMixin, Element):
    """Power outlet."""

    def __init__(
            self,
            pivot_point: tuple[float, float],
            length: float,
            orientation_angle: float = 0,
            waterproof: bool = False,
            high_voltage: bool = False,
            low_current: bool = False,
            line_width: float = 0.5,
            color: str = 'black'
    ):
        """
        Initialize an instance.

        :param pivot_point:
            coordinates (in meters) of pivot point;
            the center of the segment shared with a wall is pivot point
        :param length:
            length of the power outlet (in meters)
        :param orientation_angle:
            angle (in degrees) that specifies orientation of the power outlet;
            it is measured between X-axis and the outlet in positive direction (counterclockwise);
            initial outlet is rotated around pivot point to get the desired orientation
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
        self.pivot_point = pivot_point
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
            self.pivot_point,
            self.length,
            self.length,
            theta1=self.orientation_angle,
            theta2=self.orientation_angle + 2 * RIGHT_ANGLE_IN_DEGREES,
            lw=self.line_width,
            color=self.color
        )
        ax.add_patch(arc)

        half_length = 0.5 * self.length
        tip_angle = self.orientation_angle + RIGHT_ANGLE_IN_DEGREES
        arc_middle = shift_in_direction(self.pivot_point, half_length, tip_angle)
        ax.plot(
            [self.pivot_point[0], arc_middle[0]],
            [self.pivot_point[1], arc_middle[1]],
            lw=self.line_width,
            color=self.color
        )

        bar_left_end = shift_in_direction(arc_middle, -half_length, self.orientation_angle)
        bar_right_end = shift_in_direction(arc_middle, half_length, self.orientation_angle)
        ax.plot(
            [bar_left_end[0], bar_right_end[0]],
            [bar_left_end[1], bar_right_end[1]],
            lw=self.line_width,
            color=self.color
        )

        tip_end = shift_in_direction(self.pivot_point, self.length, tip_angle)
        ax.plot(
            [arc_middle[0], tip_end[0]],
            [arc_middle[1], tip_end[1]],
            lw=self.line_width,
            color=self.color
        )

        if self.waterproof:
            angle_in_degrees = self.orientation_angle + 1.5 * RIGHT_ANGLE_IN_DEGREES
            radius_end = shift_in_direction(self.pivot_point, half_length, angle_in_degrees)
            ax.plot(
                [self.pivot_point[0], radius_end[0]],
                [self.pivot_point[1], radius_end[1]],
                lw=self.line_width,
                color=self.color
            )

        if self.high_voltage:
            left_tip_end = shift_in_direction(tip_end, -0.5 * half_length, self.orientation_angle)
            right_tip_end = shift_in_direction(tip_end, 0.5 * half_length, self.orientation_angle)
            ax.plot(
                [arc_middle[0], left_tip_end[0]],
                [arc_middle[1], left_tip_end[1]],
                lw=self.line_width,
                color=self.color
            )
            ax.plot(
                [arc_middle[0], right_tip_end[0]],
                [arc_middle[1], right_tip_end[1]],
                lw=self.line_width,
                color=self.color
            )

        if self.low_current:
            circle = Circle(
                tip_end,
                0.25 * self.length,
                fill=False,
                lw=self.line_width,
                edgecolor=self.color
            )
            ax.add_patch(circle)


class ElectricalCable(PivotAnchorMixin, Element):
    """Electrical cable for direct power supply without any outlets."""

    def __init__(
            self,
            pivot_point: tuple[float, float],
            symbol_length: float,
            orientation_angle: float = 0,
            n_arcs: int = 4,
            line_width: float = 0.5,
            color: str = 'black'
    ):
        """
        Initialize an instance.

        :param pivot_point:
            coordinates (in meters) of pivot point;
            the center of the segment shared with a wall is pivot point
        :param symbol_length:
            length of the symbol, not of the real cable
        :param orientation_angle:
            angle (in degrees) that specifies orientation of the electrical cable;
            it is measured between X-axis and the symbol in positive direction (counterclockwise);
            initial symbol is rotated around pivot point to get the desired orientation
        :param n_arcs:
            number of turns representing a curved cable
        :param line_width:
            width of lines for `matplotlib`
        :param color:
            color to use for drawing the power outlet
        :return:
            freshly created instance of `ElectricalCable` class
        """
        self.pivot_point = pivot_point
        self.symbol_length = symbol_length
        self.orientation_angle = orientation_angle
        self.n_arcs = n_arcs
        self.line_width = line_width
        self.color = color

    def draw(self, ax: matplotlib.axes.Axes) -> None:
        """Draw electrical cable."""
        radius = self.symbol_length / (2 * (self.n_arcs + 1))
        tip_angle = self.orientation_angle + RIGHT_ANGLE_IN_DEGREES
        circle_center = shift_in_direction(self.pivot_point, radius, tip_angle)
        circle = Circle(
            circle_center, radius, fill=True, facecolor=self.color, edgecolor=self.color, lw=0.1
        )
        ax.add_patch(circle)

        for i in range(self.n_arcs):
            arc_center = shift_in_direction(self.pivot_point, (3 + 2 * i) * radius, tip_angle)
            arc = Arc(
                arc_center,
                2 * radius,
                2 * radius,
                theta1=self.orientation_angle + (2 * (i % 2) - 1) * RIGHT_ANGLE_IN_DEGREES,
                theta2=self.orientation_angle + (2 * (i % 2) + 1) * RIGHT_ANGLE_IN_DEGREES,
                lw=self.line_width,
                color=self.color
            )
            ax.add_patch(arc)
