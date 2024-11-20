"""
Draw basic elements that represent walls, windows, and doors.

Author: Nikolay Lysenko
"""


import math

import matplotlib.axes
from matplotlib.patches import Arc, Rectangle

from renovation.constants import STRAIGHT_ANGLE_IN_DEGREES
from .element import Element


class Wall(Element):
    """Straight wall."""

    def __init__(
            self,
            anchor_point: tuple[float, float],
            length: float,
            thickness: float,
            orientation_angle: float = 0,
            color: str = 'black'
    ):
        """
        Initialize an instance.

        :param anchor_point:
            coordinates of anchor point (in meters);
            bottom left point is anchor point if `orientation_angle == 0`
        :param length:
            length of the wall (in meters)
        :param thickness:
            thickness of the wall (in meters)
        :param orientation_angle:
            angle (in degrees) that specifies orientation of the wall;
            it is measured between X-axis and the wall in positive direction (counterclockwise);
            initial wall is rotated around anchor point to get the desired orientation
        :param color:
            color to use for drawing the wall
        :return:
            freshly created instance of `Wall` class
        """
        self.anchor_point = anchor_point
        self.length = length
        self.thickness = thickness
        self.orientation_angle = orientation_angle
        self.color = color

    def draw(self, ax: matplotlib.axes.Axes) -> None:
        """Draw straight wall."""
        patch = Rectangle(
            self.anchor_point,
            self.length,
            self.thickness,
            angle=self.orientation_angle,
            facecolor=self.color
        )
        ax.add_patch(patch)


class Window(Element):
    """Window in a wall."""

    def __init__(
            self,
            anchor_point: tuple[float, float],
            length: float,
            overall_thickness: float,
            single_line_thickness: float,
            orientation_angle: float = 0,
            color: str = 'black',
    ):
        """
        Initialize an instance.

        :param anchor_point:
            coordinates (in meters) of anchor point;
            bottom left point is anchor point if `orientation_angle == 0`
        :param length:
            length of the window (in meters)
        :param overall_thickness:
            total thickness of the window (in meters)
        :param single_line_thickness:
            thickness of a single outer line forming window (in meters)
        :param orientation_angle:
            angle (in degrees) that specifies orientation of the window;
            it is measured between X-axis and the window in positive direction (counterclockwise);
            initial window is rotated around anchor point to get the desired orientation
        :param color:
            color to use for drawing the window
        :return:
            freshly created instance of `Window` class
        """
        internal_thickness = overall_thickness - 2 * single_line_thickness
        if internal_thickness <= 0:
            raise ValueError("Window can not be drawn due to invalid thicknesses.")

        self.anchor_point = anchor_point
        self.length = length
        self.overall_thickness = overall_thickness
        self.single_line_thickness = single_line_thickness
        self.orientation_angle = orientation_angle
        self.color = color

    def draw(self, ax: matplotlib.axes.Axes) -> None:
        """Draw window."""
        first_line = Rectangle(
            self.anchor_point,
            self.length,
            self.single_line_thickness,
            angle=self.orientation_angle,
            facecolor=self.color
        )
        ax.add_patch(first_line)

        orthogonal_angle_in_rad = math.radians(self.orientation_angle + STRAIGHT_ANGLE_IN_DEGREES)
        shift = self.overall_thickness - self.single_line_thickness
        second_anchor_point = (
            self.anchor_point[0] + math.cos(orthogonal_angle_in_rad) * shift,
            self.anchor_point[1] + math.sin(orthogonal_angle_in_rad) * shift
        )
        second_line = Rectangle(
            second_anchor_point,
            self.length,
            self.single_line_thickness,
            angle=self.orientation_angle,
            facecolor=self.color
        )
        ax.add_patch(second_line)


class Door(Element):
    """Single door."""

    def __init__(
            self,
            anchor_point: tuple[float, float],
            doorway_width: float,
            door_width: float,
            thickness: float,
            orientation_angle: float = 0,
            to_the_right: bool = False,
            color: str = 'black'
    ):
        """
        Initialize an instance.

        :param anchor_point:
            coordinates (in meters) of anchor point; here, it is the door frame corner
            that is on the same side with hinges and is on the side where the door opens
            (given `to_the_right` is set to `False`, else it is on the opposite side)
        :param doorway_width:
            width of the doorway (in meters), i.e. width of the door itself
            plus the width of both sides of the door frame
        :param door_width:
            width of the door itself (in meters)
        :param thickness:
            thickness of the door (in meters)
        :param orientation_angle:
            angle (in degrees) that specifies orientation of the doorway;
            it is measured between X-axis and the doorway in positive direction (counterclockwise);
            initial doorway is rotated around anchor point to get the desired orientation
        :param to_the_right:
            binary indicator whether the door opens to the right if someone looks at it
            from the hinges point along the doorway
        :param color:
            color to use for drawing the window
        :return:
            freshly created instance of `Door` class
        """
        self.anchor_point = anchor_point
        self.doorway_width = doorway_width
        self.door_width = door_width
        self.frame_width = (doorway_width - door_width) / 2
        self.thickness = thickness
        self.orientation_angle = orientation_angle
        self.to_the_right = to_the_right
        self.color = color

    def draw(self, ax: matplotlib.axes.Axes) -> None:
        """Draw the door, its opening trajectory, and the door frame."""
        orientation_angle_in_rad = math.radians(self.orientation_angle)

        frame_orientation_angle = self.orientation_angle - STRAIGHT_ANGLE_IN_DEGREES
        frame_with_hinges = Rectangle(
            self.anchor_point,
            self.thickness,
            self.frame_width,
            angle=frame_orientation_angle,
            facecolor=self.color
        )
        ax.add_patch(frame_with_hinges)

        shift = self.frame_width + self.door_width
        frame_without_hinges_anchor_point = (
            self.anchor_point[0] + math.cos(orientation_angle_in_rad) * shift,
            self.anchor_point[1] + math.sin(orientation_angle_in_rad) * shift
        )
        frame_without_hinges = Rectangle(
            frame_without_hinges_anchor_point,
            self.thickness,
            self.frame_width,
            angle=frame_orientation_angle,
            facecolor=self.color
        )
        ax.add_patch(frame_without_hinges)

        hinges_point = (
            self.anchor_point[0] + math.cos(orientation_angle_in_rad) * self.frame_width,
            self.anchor_point[1] + math.sin(orientation_angle_in_rad) * self.frame_width
        )
        if self.to_the_right:
            hinges_point = (
                hinges_point[0] + math.sin(orientation_angle_in_rad) * self.thickness,
                hinges_point[1] - math.cos(orientation_angle_in_rad) * self.thickness
            )
            door = Rectangle(
                hinges_point,
                self.door_width,
                self.thickness,
                angle=self.orientation_angle - STRAIGHT_ANGLE_IN_DEGREES,
                facecolor=self.color
            )
        else:
            door = Rectangle(
                hinges_point,
                self.thickness,
                self.door_width,
                angle=self.orientation_angle,
                facecolor=self.color
            )
        ax.add_patch(door)

        arc_anchor_point = (
            hinges_point[0] + math.cos(orientation_angle_in_rad) * self.thickness,
            hinges_point[1] + math.sin(orientation_angle_in_rad) * self.thickness
        )
        extra_degrees_for_smooth_connection = 2
        if self.to_the_right:
            start_angle = -STRAIGHT_ANGLE_IN_DEGREES - extra_degrees_for_smooth_connection
            end_angle = 0
        else:
            start_angle = 0
            end_angle = STRAIGHT_ANGLE_IN_DEGREES + extra_degrees_for_smooth_connection
        arc = Arc(
            arc_anchor_point,
            2 * (self.door_width - self.thickness),
            2 * self.door_width,
            angle=self.orientation_angle,
            theta1=start_angle,
            theta2=end_angle,
            color=self.color,
            linewidth=1
        )
        ax.add_patch(arc)
