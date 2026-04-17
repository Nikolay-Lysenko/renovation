"""
Draw single floor plan.

Author: Nikolay Lysenko
"""


from typing import Optional

import matplotlib.pyplot as plt
import numpy as np

from .constants import METERS_PER_INCH
from .elements import Element, Room
from .elements.registry import element_sorter_by_type



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
        # Adjust margins (values are fractions of figure width/height, 0-1)
        fig.subplots_adjust(left=0.025, right=0.975, bottom=0.025, top=0.975)
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
        self.title = None
        self.elements: list[Element] = []

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

    def add_element(self, element: Element) -> None:
        """
        Add element.

        :param element:
            element to be added
        :return:
            None
        """
        self.elements.append(element)

    def draw_elements(self) -> None:
        """
        Draw elements added by add_element method.

        :param elements:
            None
        :return:
            None
        """
        print (f"Drawing floor plan {self.title} elements...")

        for element in sorted(self.elements, key=element_sorter_by_type):
            #print(f"  Drawing element: {element.__class__.__name__} with id {element.id}")
            element.draw(self.ax)

    def draw_report(
            self, 
            anchor_point: tuple[float, float],
            areas: bool = False,
            total_area: bool = False,
            notes: list[str] = None,
            fontsize: int = 11
    ) -> None:
        """
        Draw a report at the specified location on the floor plan.
        
        :param anchor_point:
            (x, y) coordinates where report should be drawn
        :param areas:
            if True, list all rooms with their areas
        :param total_area:
            if True, display sum of all room areas
        :param notes:
            optional list of note strings to display at the top of report
        :param fontsize:
            font size for the report text
        :return:
            None
        """
        x, y = anchor_point
        line_height = 0.3 * fontsize /11 # Spacing between lines
        current_y = y
        font_size = fontsize
        
        # Draw notes first
        if notes:
            for note in notes:
                self.ax.text(
                    x, current_y, note,
                    fontsize=font_size,
                    verticalalignment='top',
                    horizontalalignment='left',
                    style='italic'
                )
                current_y -= line_height
            
            # Add extra spacing after notes
            current_y -= line_height * 0.5
        
        # Get all Room elements
        rooms = [elem for elem in self.elements if isinstance(elem, Room)]
        
        # Filter rooms that have labels
        labeled_rooms = [room for room in rooms if room.label]
        
        # Draw room areas
        if areas and labeled_rooms:
            # Header
            self.ax.text(
                x, current_y, "Room Areas:",
                fontsize=font_size + 1,
                verticalalignment='top',
                horizontalalignment='left',
                weight='bold'
            )
            current_y -= line_height
            
            # List each room
            for room in labeled_rooms:
                area_text = f"  • {room.label}: {room.inner_area:.2f} m²"
                self.ax.text(
                    x, current_y, area_text,
                    fontsize=font_size,
                    verticalalignment='top',
                    horizontalalignment='left'
                )
                current_y -= line_height
            
            # Add spacing before total
            current_y -= line_height * 0.3
        
        # Draw total area
        if total_area and labeled_rooms:
            total = sum(room.inner_area for room in labeled_rooms)
            total_text = f"Total Area: {total:.2f} m²"
            self.ax.text(
                x, current_y, total_text,
                fontsize=font_size + 1,
                verticalalignment='top',
                horizontalalignment='left',
                weight='bold'
            )
   
