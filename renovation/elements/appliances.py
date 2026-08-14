"""Draw elements representing home appliances."""


import matplotlib.axes
from matplotlib.patches import Rectangle

from renovation.constants import RIGHT_ANGLE_IN_DEGREES
from renovation.utils import shift_in_direction
from .anchor_mixins import CornerAnchorsMixin
from .element import Element


class Fridge(CornerAnchorsMixin, Element):
    """Fridge footprint represented by an outlined and labelled rectangle."""

    def __init__(
            self,
            pivot_point: tuple[float, float],
            width: float,
            depth: float,
            orientation_angle: float = 0,
            line_width: float = 0.5,
            font_size: float = 10,
            color: str = 'black'
    ):
        """
        Initialize an instance.

        :param pivot_point:
            coordinates (in meters) of the pivot point;
            here, it is the bottom left corner prior to rotation
        :param width:
            width of the fridge (in meters)
        :param depth:
            depth of the fridge (in meters)
        :param orientation_angle:
            angle (in degrees) that specifies orientation of the fridge;
            it is measured between X-axis and the width in positive direction
            (counterclockwise)
        :param line_width:
            width of lines for `matplotlib`
        :param font_size:
            font size of the ``FR`` label for `matplotlib`
        :param color:
            color to use for drawing the fridge
        :return:
            freshly created instance of `Fridge` class
        """
        if width <= 0 or depth <= 0:
            raise ValueError("Fridge width and depth must be positive.")

        self.pivot_point = pivot_point
        self.width = width
        self.depth = depth
        self.length = width  # This attribute is needed by `CornerAnchorsMixin`.
        self.thickness = depth  # This attribute is needed by `CornerAnchorsMixin`.
        self.orientation_angle = orientation_angle
        self.line_width = line_width
        self.font_size = font_size
        self.color = color

    def draw(self, ax: matplotlib.axes.Axes) -> None:
        """Draw the fridge footprint and its label."""
        outline = Rectangle(
            self.pivot_point,
            self.width,
            self.depth,
            angle=self.orientation_angle,
            fill=False,
            edgecolor=self.color,
            lw=self.line_width
        )
        ax.add_patch(outline)

        label_center = shift_in_direction(
            self.pivot_point, 0.5 * self.width, self.orientation_angle
        )
        label_center = shift_in_direction(
            label_center,
            0.5 * self.depth,
            self.orientation_angle + RIGHT_ANGLE_IN_DEGREES
        )
        ax.text(
            *label_center,
            "FR",
            color=self.color,
            fontsize=self.font_size,
            horizontalalignment='center',
            verticalalignment='center',
            rotation=self.orientation_angle,
            rotation_mode='anchor'
        )
