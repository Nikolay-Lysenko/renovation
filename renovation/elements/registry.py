"""
Map element names to their classes.

Author: Nikolay Lysenko
"""


from renovation.elements.basic import Door, Wall, Window
from renovation.elements.element import Element
from renovation.elements.info import DimensionArrow


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
