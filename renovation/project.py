"""
Combine all floor plans.

Author: Nikolay Lysenko
"""


import os
from typing import Literal, Union

from matplotlib.backends.backend_pdf import PdfPages

from renovation.floor_plan import FloorPlan


class Project:
    """Collection of floor plans."""

    def __init__(
            self,
            floor_plans: list[FloorPlan],
            dpi: Union[float, Literal["figure"]] = "figure"
    ):
        """
        Initialize an instance.

        :param floor_plans:
            floor plans
        :param dpi:
            DPI (dots-per-inch), number of pixels per inch of space in output file
        :return:
            freshly created instance of `Project` class
        """
        self.floor_plans = floor_plans
        self.dpi = dpi

    def render_to_pdf(self, output_path: str) -> None:
        """
        Render floor plans to single PDF file with each floor plan on its page.

        :param output_path:
            path to output file
        :return:
            None
        """
        with PdfPages(output_path) as pdf:
            for floor_plan in self.floor_plans:
                pdf.savefig(floor_plan.fig, dpi=self.dpi)

    def render_to_png(self, output_dir: str) -> None:
        """
        Render floor plans to separate PNG files from the same directory.

        :param output_dir:
            path to output directory
        :return:
            None
        """
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
        for i, floor_plan in enumerate(self.floor_plans):
            title = floor_plan.title or f"{i}.png"
            if not title.endswith('png'):
                title += '.png'
            floor_plan.fig.savefig(os.path.join(output_dir, title), dpi=self.dpi)
