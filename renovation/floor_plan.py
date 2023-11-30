"""
Draw single floor plan.

Author: Nikolay Lysenko
"""


from typing import Optional

import matplotlib.pyplot as plt
import numpy as np


METERS_PER_INCH = 0.0254


class FloorPlan:
    """Floor plan."""

    def __init__(
            self,
            bottom_left_corner: tuple[float, float],
            top_right_corner: tuple[float, float],
            scale_numerator: int = 1,
            scale_denominator: int = 100,
            grid_major_step: Optional[float] = None,
            grid_minor_step: Optional[float] = None,
    ):
        """
        Initialize an instance.

        :param bottom_left_corner:
            coordinates (in meters before scaling) of the bottom left corner of the floor plan
        :param top_right_corner:
            coordinates (in meters before scaling) of the top right corner of the floor plan
        :param scale_numerator:
            scale numerator
        :param scale_denominator:
            scale denominator
        :param grid_major_step:
            step (in meters before scaling) between major grid lines
        :param grid_minor_step:
            step (in meters before scaling) between minor grid lines
        :return:
            freshly created instance of `FloorPlan` class
        """
        horizontal_len = top_right_corner[0] - bottom_left_corner[0]
        vertical_len = top_right_corner[1] - bottom_left_corner[1]
        scale = scale_numerator / scale_denominator
        fig_width = horizontal_len * scale / METERS_PER_INCH
        fig_height = vertical_len * scale / METERS_PER_INCH

        fig = plt.figure(figsize=(fig_width, fig_height))
        ax = fig.add_subplot(111)
        ax.set_aspect('equal')
        ax.tick_params(
            which='both',
            left=False, right=False, bottom=False, top=False,
            labelleft=False, labelright=False, labelbottom=False, labeltop=False,
        )
        ax.spines['left'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['top'].set_visible(False)

        if grid_major_step is not None:
            major_xticks = np.arange(bottom_left_corner[0], top_right_corner[0], grid_major_step)
            major_yticks = np.arange(bottom_left_corner[1], top_right_corner[1], grid_major_step)
            ax.set_xticks(major_xticks)
            ax.set_yticks(major_yticks)
            ax.grid(which='major', alpha=0.5)
        if grid_minor_step is not None:
            minor_xticks = np.arange(bottom_left_corner[0], top_right_corner[0], grid_minor_step)
            minor_yticks = np.arange(bottom_left_corner[1], top_right_corner[1], grid_minor_step)
            ax.set_xticks(minor_xticks, minor=True)
            ax.set_yticks(minor_yticks, minor=True)
            ax.grid(which='minor', alpha=0.2)

        self.fig = fig
        self.ax = ax
        self.title = None

    def add_title(
            self, text: str, font_size: int, rel_x: float = 0.5, rel_y: float = 0.95, **kwargs
    ) -> None:
        """
        Add title.

        :param text:
            title text
        :param font_size:
            font size
        :param rel_x:
            relative horizontal position of the text center;
            a float between 0 and 1;
            value of 0 corresponds to the left edge and value of 1 corresponds to the right edge
        :param rel_y:
            relative vertical position of the text center;
            a float between 0 and 1;
            value of 0 corresponds to the bottom edge and value of 1 corresponds to the top edge
        :return:
            None
        """
        self.fig.text(
            rel_x, rel_y, text,
            horizontalalignment='center', transform=self.fig.transFigure, size=font_size, **kwargs
        )
        self.title = text
