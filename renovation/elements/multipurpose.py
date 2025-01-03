"""
Draw universal elements that have context-dependent meaning.

Author: Nikolay Lysenko
"""


import matplotlib.axes
from matplotlib import patches

from .element import Element


class Line(Element):
    """Line (solid, dashed, or dotted)"""

    style_to_matplotlib_code = {'solid': '-', 'dashed': '--', 'dotted': '.', 'dash_dot': '-.'}

    def __init__(
            self,
            first_point: tuple[float, float],
            second_point: tuple[float, float],
            width: float = 0.5,
            style: str = 'solid',
            color: str = 'black'
    ):
        """
        Initialize an instance.

        :param first_point:
            coordinates of the first end (in meters)
        :param second_point:
            coordinates of the second end (in meters)
        :param width:
            width of the line for `matplotlib`
        :param style:
            type of line ('solid', 'dashed', 'dotted', or 'dash_dot')
        :param color:
            color to use for drawing the line
        """
        self.first_point = first_point
        self.second_point = second_point
        self.width = width
        self.style = self.style_to_matplotlib_code[style]
        self.color = color

    def draw(self, ax: matplotlib.axes.Axes) -> None:
        """Draw line."""
        ax.plot(
            [self.first_point[0], self.second_point[0]],
            [self.first_point[1], self.second_point[1]],
            lw=self.width,
            ls=self.style,
            color=self.color
        )


class Polygon(Element):
    """Polygon. In particular, it can be used for wall corners or acute or obtuse angles."""

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
        """Draw polygon"""
        polygon = patches.Polygon(
            self.vertices,
            lw=self.line_width,
            fill=True,
            facecolor=self.color,
            edgecolor=self.color
        )
        ax.add_patch(polygon)
