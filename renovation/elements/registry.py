"""
Map element names to their classes.

Author: Nikolay Lysenko
"""


from .basic import Door, Wall, Window
from .electricity import ElectricalCable, PowerOutlet
from .element import Element
from .info import DimensionArrow, TextBox


def create_elements_registry() -> dict[str, type(Element)]:
    """
    Create registry of implemented elements.

    :return:
        mapping from element type to element class
    """
    registry = {
        'dimension_arrow': DimensionArrow,
        'door': Door,
        'electrical_cable': ElectricalCable,
        'power_outlet': PowerOutlet,
        'text_box': TextBox,
        'wall': Wall,
        'window': Window,
    }
    return registry
