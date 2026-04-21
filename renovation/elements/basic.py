"""
Draw basic elements that represent walls, windows, and doors.

Author: Nikolay Lysenko
"""


import math
from typing import Optional

import matplotlib.axes
from matplotlib.patches import Arc, Rectangle

from renovation.constants import RIGHT_ANGLE_IN_DEGREES
from renovation.utils import shift_in_direction
from .element import Element


class Wall(Element):
    """
    Straight wall.

    For corners of acute or obtuse angles please consider `renovation.elements.Polygon` class.
    """

    def __init__(
            self,
            pivot_point: tuple[float, float],
            thickness: float,
            length: Optional[float] = None,
            orientation_angle: float = 0,
            another_pivot_point: Optional[tuple[float, float]] = None,
            color: str = 'black'
    ):
        """
        Initialize an instance.

        :param pivot_point:
            coordinates of pivot point (in meters);
            bottom left point is pivot point if `orientation_angle == 0`
        :param thickness:
            thickness of the wall (in meters)
        :param length:
            length of the wall (in meters);
            this argument is used only if `another_pivot_point` is not passed
        :param orientation_angle:
            angle (in degrees) that specifies orientation of the wall;
            it is measured between X-axis and the wall in positive direction (counterclockwise);
            initial wall is rotated around pivot point to get the desired orientation;
            this argument is used only if `another_pivot_point` is not passed
        :param another_pivot_point:
            coordinates of additional pivot point (in meters);
            bottom right point is this pivot point if `orientation_angle == 0`
        :param color:
            color to use for drawing the wall
        :return:
            freshly created instance of `Wall` class
        """
        if another_pivot_point is not None:
            x_shift = another_pivot_point[0] - pivot_point[0]
            y_shift = another_pivot_point[1] - pivot_point[1]
            length = math.sqrt(x_shift ** 2 + y_shift ** 2)
            orientation_angle = math.degrees(math.atan2(y_shift, x_shift))
        self.pivot_point = pivot_point
        self.thickness = thickness
        self.length = length
        self.orientation_angle = orientation_angle
        self.color = color

    def draw(self, ax: matplotlib.axes.Axes) -> None:
        """Draw straight wall."""
        patch = Rectangle(
            self.pivot_point,
            self.length,
            self.thickness,
            angle=self.orientation_angle,
            facecolor=self.color
        )
        ax.add_patch(patch)

    def calculate_anchor_coordinates(self, anchor_type: str) -> tuple[float, float]:
        """
        Calculate coordinates of a point that can be used as anchor for other elements.

        :param anchor_type:
            one of 'corner_one' (the pivot point),
            'corner_two' (the next corner in the counter-clockwise direction),
            'corner_three' (again, the next corner in the counter-clockwise direction),
            and 'corner_four'
        :return:
            coordinates of the anchor point
        """
        if anchor_type == "corner_one":
            return self.pivot_point
        elif anchor_type == "corner_two":
            return shift_in_direction(self.pivot_point, self.length, self.orientation_angle)
        elif anchor_type == "corner_three":
            return shift_in_direction(
                shift_in_direction(self.pivot_point, self.length, self.orientation_angle),
                self.thickness,
                self.orientation_angle + RIGHT_ANGLE_IN_DEGREES
            )
        elif anchor_type == "corner_four":
            return shift_in_direction(
                self.pivot_point, self.thickness, self.orientation_angle + RIGHT_ANGLE_IN_DEGREES
            )
        else:
            raise ValueError(f"Anchor type '{anchor_type}' is not supported by `Wall` class.")


class Window(Element):
    """Window in a wall."""

    def __init__(
            self,
            pivot_point: tuple[float, float],
            length: float,
            overall_thickness: float,
            single_line_thickness: float,
            orientation_angle: float = 0,
            color: str = 'black',
    ):
        """
        Initialize an instance.

        :param pivot_point:
            coordinates (in meters) of pivot point;
            bottom left point is pivot point if `orientation_angle == 0`
        :param length:
            length of the window (in meters)
        :param overall_thickness:
            total thickness of the window (in meters)
        :param single_line_thickness:
            thickness of a single outer line forming window (in meters)
        :param orientation_angle:
            angle (in degrees) that specifies orientation of the window;
            it is measured between X-axis and the window in positive direction (counterclockwise);
            initial window is rotated around pivot point to get the desired orientation
        :param color:
            color to use for drawing the window
        :return:
            freshly created instance of `Window` class
        """
        internal_thickness = overall_thickness - 2 * single_line_thickness
        if internal_thickness <= 0:
            raise ValueError("Window can not be drawn due to invalid thicknesses.")

        self.pivot_point = pivot_point
        self.length = length
        self.overall_thickness = overall_thickness
        self.single_line_thickness = single_line_thickness
        self.orientation_angle = orientation_angle
        self.color = color

    def draw(self, ax: matplotlib.axes.Axes) -> None:
        """Draw window."""
        first_line = Rectangle(
            self.pivot_point,
            self.length,
            self.single_line_thickness,
            angle=self.orientation_angle,
            facecolor=self.color
        )
        ax.add_patch(first_line)

        orthogonal_angle_in_rad = math.radians(self.orientation_angle + RIGHT_ANGLE_IN_DEGREES)
        shift = self.overall_thickness - self.single_line_thickness
        second_pivot_point = (
            self.pivot_point[0] + math.cos(orthogonal_angle_in_rad) * shift,
            self.pivot_point[1] + math.sin(orthogonal_angle_in_rad) * shift
        )
        second_line = Rectangle(
            second_pivot_point,
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
            pivot_point: tuple[float, float],
            doorway_width: float,
            door_width: float,
            thickness: float,
            orientation_angle: float = 0,
            to_the_right: bool = False,
            color: str = 'black'
    ):
        """
        Initialize an instance.

        :param pivot_point:
            coordinates (in meters) of pivot point; here, it is the door frame corner
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
            initial doorway is rotated around pivot point to get the desired orientation
        :param to_the_right:
            binary indicator whether the door opens to the right if someone looks at it
            from the hinges point along the doorway
        :param color:
            color to use for drawing the window
        :return:
            freshly created instance of `Door` class
        """
        self.pivot_point = pivot_point
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

        frame_orientation_angle = self.orientation_angle - RIGHT_ANGLE_IN_DEGREES
        frame_with_hinges = Rectangle(
            self.pivot_point,
            self.thickness,
            self.frame_width,
            angle=frame_orientation_angle,
            facecolor=self.color
        )
        ax.add_patch(frame_with_hinges)

        shift = self.frame_width + self.door_width
        frame_without_hinges_pivot_point = (
            self.pivot_point[0] + math.cos(orientation_angle_in_rad) * shift,
            self.pivot_point[1] + math.sin(orientation_angle_in_rad) * shift
        )
        frame_without_hinges = Rectangle(
            frame_without_hinges_pivot_point,
            self.thickness,
            self.frame_width,
            angle=frame_orientation_angle,
            facecolor=self.color
        )
        ax.add_patch(frame_without_hinges)

        hinges_point = (
            self.pivot_point[0] + math.cos(orientation_angle_in_rad) * self.frame_width,
            self.pivot_point[1] + math.sin(orientation_angle_in_rad) * self.frame_width
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
                angle=self.orientation_angle - RIGHT_ANGLE_IN_DEGREES,
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

        arc_pivot_point = (
            hinges_point[0] + math.cos(orientation_angle_in_rad) * self.thickness,
            hinges_point[1] + math.sin(orientation_angle_in_rad) * self.thickness
        )
        extra_degrees_for_smooth_connection = 2
        if self.to_the_right:
            start_angle = -RIGHT_ANGLE_IN_DEGREES - extra_degrees_for_smooth_connection
            end_angle = 0
        else:
            start_angle = 0
            end_angle = RIGHT_ANGLE_IN_DEGREES + extra_degrees_for_smooth_connection
        arc = Arc(
            arc_pivot_point,
            2 * (self.door_width - self.thickness),
            2 * self.door_width,
            angle=self.orientation_angle,
            theta1=start_angle,
            theta2=end_angle,
            color=self.color,
            linewidth=1
        )
        ax.add_patch(arc)
