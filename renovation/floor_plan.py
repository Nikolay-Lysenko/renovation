"""
Draw single floor plan.

Author: Nikolay Lysenko
"""


from dataclasses import dataclass
from typing import Any, Optional

import matplotlib.pyplot as plt
import numpy as np

from renovation.constants import METERS_PER_INCH
from renovation.elements import Element


@dataclass
class AnchoredPivotPoint:
    """Pivot point that depends on an outer element."""
    anchor_id: str
    x_shift: float = 0
    y_shift: float = 0


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
            major_xticks = np.arange(
                bottom_left_corner[0],
                top_right_corner[0] + 0.5 * grid_major_step,
                grid_major_step
            )
            major_yticks = np.arange(
                bottom_left_corner[1],
                top_right_corner[1] + 0.5 * grid_major_step,
                grid_major_step
            )
            ax.set_xticks(major_xticks)
            ax.set_yticks(major_yticks)
            ax.grid(which='major', color='orange', alpha=0.25)
        if grid_minor_step is not None:
            minor_xticks = np.arange(
                bottom_left_corner[0],
                top_right_corner[0] + 0.5 * grid_minor_step,
                grid_minor_step
            )
            minor_yticks = np.arange(
                bottom_left_corner[1],
                top_right_corner[1] + 0.5 * grid_minor_step,
                grid_minor_step
            )
            ax.set_xticks(minor_xticks, minor=True)
            ax.set_yticks(minor_yticks, minor=True)
            ax.grid(which='minor', color='orange', alpha=0.1)

        ax.set_xlim(bottom_left_corner[0], top_right_corner[0])
        ax.set_ylim(bottom_left_corner[1], top_right_corner[1])

        self.fig = fig
        self.ax = ax
        self.title: Optional[str] = None
        self.anchors: dict[str, tuple[float, float]] = {}

    def add_title(
            self, text: str, font_size: int, rel_x: float = 0.5, rel_y: float = 0.95, **kwargs
    ) -> None:
        """
        Add title to the floor plan.

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

    def _get_coordinates_of_anchored_pivot_point(
            self, pivot_point_params: dict[str, Any]
    ) -> tuple[float, float]:
        """
        Calculate coordinates of anchored pivot point.

        :param pivot_point_params:
            parameters of anchored pivot point
        :return:
            coordinates of the pivot point
        """
        try:
            anchored_pivot_point = AnchoredPivotPoint(**pivot_point_params)
        except TypeError:
            raise RuntimeError(
                f"Wrong anchored pivot point configuration: {pivot_point_params}"
            )
        try:
            anchor = self.anchors[anchored_pivot_point.anchor_id]
        except KeyError:
            raise RuntimeError(
                f"Anchor with id={anchored_pivot_point.anchor_id} is referenced before assignment."
            )
        return anchor[0] + anchored_pivot_point.x_shift, anchor[1] + anchored_pivot_point.y_shift

    def _dereference_anchors(self, element_params: dict[str, Any]) -> dict[str, Any]:
        """
        Replace all anchor-dependent positions with exact coordinates.

        :param element_params:
            original parameters of an element to be drawn
        :return:
            parameters without anchor-dependent positions
        """
        if isinstance(element_params.get("pivot_point"), dict):
            element_params["pivot_point"] = self._get_coordinates_of_anchored_pivot_point(
                element_params["pivot_point"]
            )
        if isinstance(element_params.get("another_pivot_point"), dict):
            element_params["another_pivot_point"] = self._get_coordinates_of_anchored_pivot_point(
                element_params["another_pivot_point"]
            )
        vertices_params = element_params.get("vertices")
        if isinstance(vertices_params, list) and isinstance(vertices_params[0], dict):
            element_params["vertices"] = [
                self._get_coordinates_of_anchored_pivot_point(vertice_params)
                for vertice_params in vertices_params
            ]
        return element_params

    def add_element(self, element_class: type[Element], element_params: dict[str, Any]) -> None:
        """
        Add element.

        :param element_class:
            class of the element to be added
        :param element_params:
            parameters of the element to be added
        :return:
            None
        """
        element_params = self._dereference_anchors(element_params)
        anchors_params = element_params.pop("anchors", [])
        element = element_class(**element_params)
        element.draw(self.ax)

        for anchor_params in anchors_params:
            if anchor_params["id"] in self.anchors:
                raise RuntimeError(f"Anchor id={anchor_params['id']} is used twice.")
            self.anchors[anchor_params["id"]] = element.calculate_anchor_coordinates(
                anchor_params.get("type")
            )
