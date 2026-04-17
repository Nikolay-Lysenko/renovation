"""
Draw Doors

Author: Krzysztof Bartczak
"""


import math

import matplotlib.axes
from matplotlib.patches import Arc, Rectangle

from ..constants import RIGHT_ANGLE_IN_DEGREES
from ..utils import rotate_point, render_label_and_id
from .element import Element
from .info import DimensionArrow
from .options import get_element_option


class Door(Element):
    door_schematic_line_thickness = 0.04
    """Single door."""

    def __init__(
            self,
            anchor_point: tuple[float, float],
            doorway_width: float,
            door_width: float,
            thickness: float,
            orientation_angle: float = 0,
            to_the_right: bool = False,
            color: str = 'black',
            hinges_point: float = 0.95,
            opening_outside: bool = False,
            label: str | None = None
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
        :param hinges_point:
            relative position of the hinges along the doorway (0.0 = start, 1.0 = end, 0.5 = middle)
        :param label:
            optional label for the element
        :return:
            freshly created instance of `Door` class
        """
        super().__init__(label=label)
        self.anchor_point = anchor_point
        self.doorway_width = doorway_width
        self.door_width = door_width
        self.frame_width = (doorway_width - door_width) / 2
        self.thickness = thickness
        self.orientation_angle = orientation_angle
        self.to_the_right = to_the_right
		# If opening outside, take the opposite hinges point so "1.0" is always extended hinges
        self.hinges_point = 1 - hinges_point  if opening_outside else hinges_point
        self.opening_outside = opening_outside
        self.color = color

    def get_corners(self) -> list[tuple[float, float]]:
        """
        Calculate the 4 corners of the doorway considering rotation.

        :return:
            list of 4 (x, y) tuples representing corners in order:
            corners of the full doorway bounding box
        """
        angle_rad = math.radians(self.orientation_angle)
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)

        # Define corners relative to anchor point
        # The doorway spans doorway_width along orientation_angle direction
        # and thickness perpendicular to it (inward/negative perpendicular)
        corners_relative = [
            (0, 0),  # anchor
            (self.doorway_width * cos_a, self.doorway_width * sin_a),  # along orientation
            (self.doorway_width * cos_a - self.thickness * sin_a,
             self.doorway_width * sin_a + self.thickness * cos_a),  # opposite corner
            (-self.thickness * sin_a, self.thickness * cos_a)  # perpendicular from anchor
        ]

        # Translate each corner by anchor point
        corners = [
            (x + self.anchor_point[0], y + self.anchor_point[1])
            for x, y in corners_relative
        ]

        return corners

    def draw(self, ax: matplotlib.axes.Axes) -> None:
        """Draw the door, its opening trajectory, and the door frame."""
        orientation_angle_in_rad = math.radians(self.orientation_angle)

        frame_orientation_angle = self.orientation_angle

        # Draw a part of frame up to the hinges
        frame_with_hinges = Rectangle(
            self.anchor_point,
            self.frame_width,
            self.thickness,
            angle=frame_orientation_angle,
            facecolor=self.color
        )
        ax.add_patch(frame_with_hinges)
        # Draw a whole in the wall
        shift = self.frame_width
        whole_in_the_wall_anchor = (
            self.anchor_point[0] + math.cos(orientation_angle_in_rad) * shift,
            self.anchor_point[1] + math.sin(orientation_angle_in_rad) * shift
        )
        whole_in_a_wall = Rectangle(
            whole_in_the_wall_anchor,
            self.door_width,
            self.thickness,
            angle=frame_orientation_angle,
            facecolor='white'
        )
        ax.add_patch(whole_in_a_wall)
        # Draw a part of frame opposite to the hinges.
        shift = self.frame_width + self.door_width
        frame_without_hinges_anchor_point = (
            self.anchor_point[0] + math.cos(orientation_angle_in_rad) * shift,
            self.anchor_point[1] + math.sin(orientation_angle_in_rad) * shift
        )
        frame_without_hinges = Rectangle(
            frame_without_hinges_anchor_point,
            self.frame_width,
            self.thickness,
            angle=frame_orientation_angle,
            facecolor=self.color
        )
        ax.add_patch(frame_without_hinges)
        # Draw dimension arrow for the doorway width if specified in options
        if get_element_option("Door","dimensions"):
            dims_point = rotate_point(anchor_point=self.anchor_point,
                                    offset_x=self.frame_width,
                                    offset_y=self.thickness * 0.8 if self.opening_outside else self.thickness * 0.2,
                                    angle_rad=orientation_angle_in_rad)
            dimension = DimensionArrow(
                anchor_point=dims_point,
                length=self.door_width,
                orientation_angle=frame_orientation_angle,
                annotate_above=not self.opening_outside,
                color=get_element_option("Door","label_color", "black")
            )
            dimension.draw(ax)

        # If doors are opening outside, need to offset for thickness as the rectangle gets rotated additional 180
        if self.opening_outside:
            anchor_point_x_offset = self.door_schematic_line_thickness
        else:
            anchor_point_x_offset = 0

        if self.to_the_right:
            hinges_point = rotate_point(anchor_point=self.anchor_point,
                                     offset_x=-self.door_schematic_line_thickness +self.frame_width + self.door_width + anchor_point_x_offset,
                                     offset_y=self.thickness * self.hinges_point,
                                     angle_rad=orientation_angle_in_rad)
            arc_anchor_point = rotate_point(anchor_point=self.anchor_point,
                                     offset_x=-self.door_schematic_line_thickness +self.frame_width + self.door_width ,
                                     offset_y=self.thickness * self.hinges_point,
                                     angle_rad=orientation_angle_in_rad)
        else:
            hinges_point = rotate_point(anchor_point=self.anchor_point,
                                     offset_x=self.frame_width + anchor_point_x_offset,
                                     offset_y=self.thickness * self.hinges_point,
                                     angle_rad=orientation_angle_in_rad)
            arc_anchor_point = rotate_point(anchor_point=self.anchor_point,
                                     offset_x=self.frame_width + self.door_schematic_line_thickness,
                                     offset_y=self.thickness * self.hinges_point,
                                     angle_rad=orientation_angle_in_rad)

        door = Rectangle(
                        hinges_point,
                        self.door_schematic_line_thickness, self.door_width,
                        angle=self.orientation_angle + (180 if self.opening_outside else 0), # Additional rot if opening outside
                        facecolor=self.color
                        #facecolor='orange'
            )
        ax.add_patch(door)

        extra_degrees_for_smooth_connection = 2
        if self.opening_outside:
            if self.to_the_right:
                start_angle = RIGHT_ANGLE_IN_DEGREES + RIGHT_ANGLE_IN_DEGREES
                end_angle = RIGHT_ANGLE_IN_DEGREES *3 + extra_degrees_for_smooth_connection
            else:
                start_angle = -RIGHT_ANGLE_IN_DEGREES - extra_degrees_for_smooth_connection
                end_angle =  0
        else:
            if self.to_the_right:
                start_angle = RIGHT_ANGLE_IN_DEGREES - extra_degrees_for_smooth_connection
                end_angle = RIGHT_ANGLE_IN_DEGREES + RIGHT_ANGLE_IN_DEGREES
            else:
                start_angle = 0
                end_angle = RIGHT_ANGLE_IN_DEGREES + extra_degrees_for_smooth_connection
        arc = Arc(
            arc_anchor_point,
            2 * (self.door_width - self.door_schematic_line_thickness),
            2 * self.door_width,
            angle=self.orientation_angle,
            theta1=start_angle,
            theta2=end_angle,
            color=self.color,
            linewidth=1
        )
        ax.add_patch(arc)

        # Render label and ID at hinges point with rotation offset
        if self.opening_outside:
            textrotation = 40 + ( RIGHT_ANGLE_IN_DEGREES *2 if self.to_the_right else RIGHT_ANGLE_IN_DEGREES *3 )
        else:
            textrotation = 40 + ( RIGHT_ANGLE_IN_DEGREES if self.to_the_right else 0 )
        textrotation = (360 + textrotation + self.orientation_angle) % 360
        render_label_and_id(
            ax,
            self,
            'Door',
            hinges_point,
            textrotation,
            label_prefix="   ---",
            id_prefix="   ---"
        )


