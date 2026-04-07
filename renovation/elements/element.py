"""
Define abstract element.

Author: Nikolay Lysenko
"""


from abc import ABC, abstractmethod

import matplotlib.axes


class Element(ABC):
    """Abstract element."""

    def __init__(self, label: str | None = None):
        """
        Initialize an instance.

        :param label:
            optional label for the element
        """
        self.label = label

    @abstractmethod
    def draw(self, ax: matplotlib.axes.Axes) -> None:
        """Draw the element."""
        pass
