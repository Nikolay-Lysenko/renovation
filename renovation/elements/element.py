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
