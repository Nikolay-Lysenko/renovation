"""
Draw elements representing lighting-related objects.

Author: Nikolay Lysenko
"""


import math
from typing import Optional

import matplotlib.axes
from matplotlib.patches import Arc, Circle, Rectangle

from renovation.constants import RIGHT_ANGLE_IN_DEGREES
from renovation.utils import shift_in_direction
from .anchor_mixins import CornerAnchorsMixin, PivotAnchorMixin
from .element import Element


class CeilingLamp(PivotAnchorMixin, Element):
    """Ceiling lamp represented by a circle and a cross inside."""

    def __init__(
            self,
            pivot_point: tuple[float, float],
            symbol_diameter: float,
            line_width: float = 0.5,
            color: str = 'black'
    ):
        """
        Initialize an instance.

        :param pivot_point:
            coordinates (in meters) of pivot point; here, it is the center of the symbol
        :param symbol_diameter:
            diameter of the symbol (in meters)
        :param line_width:
            width of lines for `matplotlib`
        :param color:
            color to use for drawing the lamp
        :return:
            freshly created instance of `CeilingLamp` class
        """
        self.pivot_point = pivot_point
        self.symbol_diameter = symbol_diameter
        self.line_width = line_width
        self.color = color

    def draw(self, ax: matplotlib.axes.Axes) -> None:
        """Draw ceiling lamp."""
        radius = 0.5 * self.symbol_diameter
        circle = Circle(
            self.pivot_point,
            radius,
            fill=False,
            lw=self.line_width,
            edgecolor=self.color
        )
        ax.add_patch(circle)

        cross_ends = [
            shift_in_direction(self.pivot_point, radius, 1.5 * RIGHT_ANGLE_IN_DEGREES),
            shift_in_direction(self.pivot_point, radius, -0.5 * RIGHT_ANGLE_IN_DEGREES),
            shift_in_direction(self.pivot_point, radius, 2.5 * RIGHT_ANGLE_IN_DEGREES),
            shift_in_direction(self.pivot_point, radius, 0.5 * RIGHT_ANGLE_IN_DEGREES),
        ]
        ax.plot(
            [cross_ends[0][0], cross_ends[1][0]],
            [cross_ends[0][1], cross_ends[1][1]],
            lw=self.line_width,
            color=self.color
        )
        ax.plot(
            [cross_ends[2][0], cross_ends[3][0]],
            [cross_ends[2][1], cross_ends[3][1]],
            lw=self.line_width,
            color=self.color
        )


class WallLamp(PivotAnchorMixin, Element):
    """Wall lamp (e.g., sconce)."""

    def __init__(
            self,
            pivot_point: tuple[float, float],
            symbol_diameter: float,
            orientation_angle: float = 0.0,
            stub_relative_depth: float = 0.3,
            line_width: float = 0.5,
            color: str = 'black'
    ):
        """
        Initialize an instance.

        :param pivot_point:
            coordinates (in meters) of pivot point;
            here, it is the center of wall connection segment
        :param symbol_diameter:
            diameter of the symbol (in meters)
        :param orientation_angle:
            angle (in degrees) that specifies orientation of the lamp;
            it is measured between X-axis and the lamp in positive direction (counterclockwise);
            initial lamp is rotated around pivot point to get the desired orientation
        :param stub_relative_depth:
            ratio of stub depth to its width
        :param line_width:
            width of lines for `matplotlib`
        :param color:
            color to use for drawing the lamp
        :return:
            freshly created instance of `WallLamp` class
        """
        self.pivot_point = pivot_point
        self.symbol_diameter = symbol_diameter
        self.orientation_angle = orientation_angle
        self.stub_relative_depth = stub_relative_depth
        self.line_width = line_width
        self.color = color

    def draw(self, ax: matplotlib.axes.Axes) -> None:
        """Draw wall lamp."""
        stub_width = 0.5 * math.sqrt(2) * self.symbol_diameter
        stub_depth = self.stub_relative_depth * stub_width
        stub_pivot_point = shift_in_direction(
            self.pivot_point, -0.5 * stub_width, self.orientation_angle
        )
        stub = Rectangle(
            stub_pivot_point,
            stub_width,
            stub_depth,
            angle=self.orientation_angle,
            fill=False,
            lw=self.line_width,
            edgecolor=self.color
        )
        ax.add_patch(stub)

        shift = stub_depth + 0.5 * stub_width
        orthogonal_angle = self.orientation_angle + RIGHT_ANGLE_IN_DEGREES
        arc_center = shift_in_direction(self.pivot_point, shift, orthogonal_angle)
        arc = Arc(
            arc_center,
            self.symbol_diameter,
            self.symbol_diameter,
            theta1=self.orientation_angle - 0.5 * RIGHT_ANGLE_IN_DEGREES,
            theta2=self.orientation_angle + 2.5 * RIGHT_ANGLE_IN_DEGREES,
            lw=self.line_width,
            color=self.color
        )
        ax.add_patch(arc)

        radius = 0.5 * self.symbol_diameter
        cross_ends = [
            shift_in_direction(
                arc_center, radius, self.orientation_angle + 1.5 * RIGHT_ANGLE_IN_DEGREES
            ),
            shift_in_direction(
                arc_center, radius, self.orientation_angle - 0.5 * RIGHT_ANGLE_IN_DEGREES
            ),
            shift_in_direction(
                arc_center, radius, self.orientation_angle + 2.5 * RIGHT_ANGLE_IN_DEGREES
            ),
            shift_in_direction(
                arc_center, radius, self.orientation_angle + 0.5 * RIGHT_ANGLE_IN_DEGREES
            )
        ]
        ax.plot(
            [cross_ends[0][0], cross_ends[1][0]],
            [cross_ends[0][1], cross_ends[1][1]],
            lw=self.line_width,
            color=self.color
        )
        ax.plot(
            [cross_ends[2][0], cross_ends[3][0]],
            [cross_ends[2][1], cross_ends[3][1]],
            lw=self.line_width,
            color=self.color
        )


class LEDStrip(CornerAnchorsMixin, Element):
    """LED strip."""

    def __init__(
            self,
            pivot_point: tuple[float, float],
            width: float,
            length: Optional[float] = None,
            orientation_angle: float = 0.0,
            another_pivot_point: Optional[tuple[float, float]] = None,
            line_width: float = 0.5,
            color: str = 'black'
    ):
        """
        Initialize an instance.

        :param pivot_point:
            coordinates (in meters) of the pivot point;
            here, it is the corner that is the bottom left one prior to rotation specified by
            `orientation_angle`
        :param width:
            width of the strip (in meters)
        :param length:
            length of the strip (in meters);
            this argument is used only if `another_pivot_point` is not passed
        :param orientation_angle:
            angle (in degrees) that specifies orientation of the strip;
            it is measured between X-axis and the strip in positive direction (counterclockwise);
            initial strip is rotated around pivot point to get the desired orientation;
            this argument is used only if `another_pivot_point` is not passed
        :param line_width:
            width of lines for `matplotlib`
        :param color:
            color to use for drawing the strip
        :return:
            freshly created instance of `LEDStrip` class
        """
        if another_pivot_point is not None:
            x_shift = another_pivot_point[0] - pivot_point[0]
            y_shift = another_pivot_point[1] - pivot_point[1]
            length = math.sqrt(x_shift ** 2 + y_shift ** 2)
            orientation_angle = math.degrees(math.atan2(y_shift, x_shift))
        self.pivot_point = pivot_point
        self.width = width
        self.thickness = width  # This attribute is needed by `CornerAnchorsMixin`.
        self.length = length
        self.orientation_angle = orientation_angle
        self.line_width = line_width
        self.color = color
        self.circle_diameter_to_width = 0.6

    def draw(self, ax: matplotlib.axes.Axes) -> None:
        """Draw LED strip."""
        rectangle = Rectangle(
            self.pivot_point,
            self.length,
            self.width,
            angle=self.orientation_angle,
            fill=False,
            edgecolor=self.color,
            lw=self.line_width
        )
        ax.add_patch(rectangle)

        orientation_angle_in_radians = math.radians(self.orientation_angle)
        n_circles = math.floor(self.length / self.width)
        x_offset = 0.5 * self.length / n_circles
        y_offset = 0.5 * self.width
        for i in range(n_circles):
            circle_center = (
                self.pivot_point[0]
                + math.cos(orientation_angle_in_radians) * (2 * i + 1) * x_offset
                + math.cos(orientation_angle_in_radians + math.pi / 2) * y_offset,
                self.pivot_point[1]
                + math.sin(orientation_angle_in_radians) * (2 * i + 1) * x_offset
                + math.sin(orientation_angle_in_radians + math.pi / 2) * y_offset
            )
            circle = Circle(
                circle_center,
                0.5 * self.circle_diameter_to_width * self.width,
                fill=False,
                lw=self.line_width,
                edgecolor=self.color
            )
            ax.add_patch(circle)


class Switch(PivotAnchorMixin, Element):
    """Lighting switch."""

    def __init__(
            self,
            pivot_point: tuple[float, float],
            symbol_length: float,
            orientation_angle: float = 0,
            two_key: bool = False,
            pass_through: bool = False,
            line_width: float = 0.5,
            color: str = 'black'
    ):
        """
        Initialize an instance.

        :param pivot_point:
            coordinates (in meters) of pivot point;
            the point shared with a wall is the pivot point
        :param symbol_length:
            length of the symbol, not of the real switch
        :param orientation_angle:
            angle (in degrees) that specifies orientation of the switch;
            it is measured between X-axis and the symbol in positive direction (counterclockwise);
            initial symbol is rotated around pivot point to get the desired orientation
        :param two_key:
            binary indicator whether the switch has two keys
        :param pass_through:
            binary indicator whether there are other switches controlling the same lamp (or lamps)
        :param line_width:
            width of lines for `matplotlib`
        :param color:
            color to use for drawing the switch
        :return:
            freshly created instance of `Switch` class
        """
        self.pivot_point = pivot_point
        self.symbol_length = symbol_length
        self.orientation_angle = orientation_angle
        self.two_key = two_key
        self.pass_through = pass_through
        self.line_width = line_width
        self.color = color

    def __draw_key_symbol__(
            self,
            ax: matplotlib.axes.Axes,
            circle_center: tuple[float, float],
            radius: float,
            key_angle: float
    ) -> None:
        """Draw key symbol."""
        key_corner = shift_in_direction(circle_center, 3 * radius, key_angle)
        ax.plot(
            [circle_center[0], key_corner[0]],
            [circle_center[1], key_corner[1]],
            lw=self.line_width,
            color=self.color
        )
        key_tip = shift_in_direction(
            key_corner, 4 / 3 * radius, key_angle - RIGHT_ANGLE_IN_DEGREES
        )
        ax.plot(
            [key_corner[0], key_tip[0]],
            [key_corner[1], key_tip[1]],
            lw=self.line_width,
            color=self.color
        )
        if self.pass_through:
            middle_point = shift_in_direction(circle_center, 2 * radius, key_angle)
            second_tip_end = shift_in_direction(
                middle_point, 2 / 3 * radius, key_angle - RIGHT_ANGLE_IN_DEGREES
            )
            ax.plot(
                [middle_point[0], second_tip_end[0]],
                [middle_point[1], second_tip_end[1]],
                lw=self.line_width,
                color=self.color
            )

    def draw(self, ax: matplotlib.axes.Axes) -> None:
        """Draw switch."""
        radius = self.symbol_length / 4
        tip_angle = self.orientation_angle + RIGHT_ANGLE_IN_DEGREES

        circle_center = shift_in_direction(self.pivot_point, radius, tip_angle)
        circle = Circle(
            circle_center, radius, fill=True, facecolor=self.color, edgecolor=self.color, lw=0.1
        )
        ax.add_patch(circle)

        key_angle = self.orientation_angle + RIGHT_ANGLE_IN_DEGREES
        self.__draw_key_symbol__(ax, circle_center, radius, key_angle)
        if self.two_key:
            key_angle = self.orientation_angle + RIGHT_ANGLE_IN_DEGREES / 2
            self.__draw_key_symbol__(ax, circle_center, radius, key_angle)
