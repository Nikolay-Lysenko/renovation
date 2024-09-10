"""
Map element names to their classes.

Author: Nikolay Lysenko
"""


from .basic import Door, Wall, Window
from .element import Element
from .info import DimensionArrow


def create_elements_registry() -> dict[str, type(Element)]:
    """
    Create registry of implemented elements.

    :return:
        mapping from element type to element class
    """
    registry = {
        'dimension_arrow': DimensionArrow,
        'door': Door,
        'wall': Wall,
        'window': Window,
    }
    return registry
