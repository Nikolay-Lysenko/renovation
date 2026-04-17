"""
Define abstract element.

Author: Nikolay Lysenko
"""


from abc import ABC, abstractmethod

import matplotlib.axes

from .options import generate_element_id


class Element(ABC):
    """Abstract element."""

    def __init__(self, label: str | None = None):
        """
        Initialize an instance.

        :param label:
            optional label for the element
        """
        self.label = label
        # Generate unique ID based on class name and label
        self.id = generate_element_id(self.__class__.__name__, label)

    @abstractmethod
    def draw(self, ax: matplotlib.axes.Axes) -> None:
        """Draw the element."""
        pass
