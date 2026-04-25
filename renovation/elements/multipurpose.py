"""
Draw universal elements that have context-dependent meaning.

Author: Nikolay Lysenko
"""


import matplotlib.axes
from matplotlib import patches

from .element import Element


class Line(Element):
    """Line (solid, dashed, or dotted)."""

    style_to_matplotlib_code = {'solid': '-', 'dashed': '--', 'dotted': ':', 'dash_dot': '-.'}

    def __init__(
            self,
            pivot_point: tuple[float, float],
            another_pivot_point: tuple[float, float],
            width: float = 0.5,
            style: str = 'solid',
            color: str = 'black'
    ):
        """
        Initialize an instance.

        :param pivot_point:
            coordinates of the first end (in meters)
        :param another_pivot_point:
            coordinates of the second end (in meters)
        :param width:
            width of the line for `matplotlib`
        :param style:
            type of line ('solid', 'dashed', 'dotted', or 'dash_dot')
        :param color:
            color to use for drawing the line
        """
        self.first_pivot_point = pivot_point
        self.second_pivot_point = another_pivot_point
        self.width = width
        self.style = self.style_to_matplotlib_code[style]
        self.color = color

    def draw(self, ax: matplotlib.axes.Axes) -> None:
        """Draw line."""
        ax.plot(
            [self.first_pivot_point[0], self.second_pivot_point[0]],
            [self.first_pivot_point[1], self.second_pivot_point[1]],
            lw=self.width,
            ls=self.style,
            color=self.color
        )

    def calculate_anchor_coordinates(self, anchor_type: str) -> tuple[float, float]:
        """
        Calculate coordinates of a point that can be used as anchor for other elements.

        :param anchor_type:
            one of:
            * 'end_one' (the first pivot point),
            * 'end_two' (the second pivot point)
        :return:
            coordinates of the anchor point
        """
        if anchor_type == "end_one":
            return self.first_pivot_point
        elif anchor_type == "end_two":
            return self.second_pivot_point
        else:
            raise ValueError(f"Anchor type '{anchor_type}' is not supported by `Line` class.")


class Polygon(Element):
    """Polygon. In particular, it can be used for wall corners of acute or obtuse angles."""

    def __init__(
            self,
            vertices: list[tuple[float, float]],
            line_width: float = 0.1,
            color: str = 'black'
    ):
        """
        Initialize an instance.

        :param vertices:
            list of vertices coordinates (in meters)
        :param line_width:
            width of lines for `matplotlib`
        :param color:
            color to use for drawing the line
        :return:
            freshly created instance of `Polygon` class
        """
        self.vertices = vertices
        self.line_width = line_width
        self.color = color

    def draw(self, ax: matplotlib.axes.Axes) -> None:
        """Draw polygon."""
        polygon = patches.Polygon(
            self.vertices,
            lw=self.line_width,
            fill=True,
            facecolor=self.color,
            edgecolor=self.color
        )
        ax.add_patch(polygon)

    def calculate_anchor_coordinates(self, anchor_type: str) -> tuple[float, float]:
        """
        Calculate coordinates of a point that can be used as anchor for other elements.

        :param anchor_type:
            a value of the form "vertice_{i}" where `i` is an integer index
        :return:
            coordinates of the anchor point
        """
        split_anchor_type = anchor_type.split("vertice_")
        if len(split_anchor_type) != 2 or not split_anchor_type[0]:
            raise ValueError(f"Anchor type '{anchor_type}' is not supported by `Polygon` class.")
        try:
            index = int(split_anchor_type[1])
        except ValueError:
            raise ValueError(f"Can't parse index from anchor type '{anchor_type}'.")
        try:
            return self.vertices[index]
        except IndexError:
            raise ValueError(
                f"The polygon has only {len(self.vertices)} vertices, but index is set to {index}."
            )
