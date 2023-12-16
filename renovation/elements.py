"""
Draw basic elements.

Author: Nikolay Lysenko
"""


import math
from abc import ABC, abstractmethod

import matplotlib.axes
from matplotlib.patches import Arc, Rectangle


STRAIGHT_ANGLE_IN_DEGREES = 90


class Element(ABC):
    """Abstract element."""

    @abstractmethod
    def draw(self, ax: matplotlib.axes.Axes) -> None:
        """Draw the element."""
        pass


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
            width: float,
            thickness: float,
            orientation_angle: float = 0,
            to_the_right: bool = False,
            color: str = 'black'
    ):
        """
        Initialize an instance.

        :param anchor_point:
            coordinates (in meters) of anchor point; here, it is the door hinges point
        :param width:
            width of the door and the doorway (in meters)
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
        self.width = width
        self.thickness = thickness
        self.orientation_angle = orientation_angle
        self.to_the_right = to_the_right
        self.color = color

    def draw(self, ax: matplotlib.axes.Axes) -> None:
        """Draw door and its opening trajectory."""
        if self.to_the_right:
            door_orientation_angle = self.orientation_angle - STRAIGHT_ANGLE_IN_DEGREES
            orientation_angle_in_rad = math.radians(self.orientation_angle)
            anchor_point = (
                self.anchor_point[0] - math.cos(orientation_angle_in_rad) * self.thickness,
                self.anchor_point[1] - math.sin(orientation_angle_in_rad) * self.thickness
            )
        else:
            door_orientation_angle = self.orientation_angle + STRAIGHT_ANGLE_IN_DEGREES
            anchor_point = self.anchor_point
        door = Rectangle(
            anchor_point,
            self.width,
            self.thickness,
            angle=door_orientation_angle,
            facecolor=self.color
        )
        ax.add_patch(door)

        if self.to_the_right:
            start_angle = door_orientation_angle - 1  # Smoother connection.
            end_angle = self.orientation_angle
        else:
            start_angle = self.orientation_angle
            end_angle = door_orientation_angle + 1  # Smoother connection.
        arc = Arc(
            self.anchor_point,
            2 * self.width,
            2 * self.width,
            theta1=start_angle,
            theta2=end_angle,
            color=self.color
        )
        ax.add_patch(arc)


def create_elements_registry() -> dict[str, type(Element)]:
    """
    Create registry of implemented elements.

    :return:
        mapping from element type to element class
    """
    registry = {
        'door': Door,
        'wall': Wall,
        'window': Window,
    }
    return registry
