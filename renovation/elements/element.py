"""
Define abstract element.

Author: Nikolay Lysenko
"""


from abc import ABC, abstractmethod

import matplotlib.axes


class Element(ABC):
    """Abstract element."""

    @abstractmethod
    def draw(self, ax: matplotlib.axes.Axes) -> None:
        """Draw the element."""
        pass

    @abstractmethod
    def calculate_anchor_coordinates(self, anchor_type: str) -> tuple[float, float]:
        """Calculate coordinates of a point that can be used as anchor for other elements."""
        pass
