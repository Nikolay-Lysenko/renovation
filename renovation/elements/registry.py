"""
Map element names to their classes.

Author: Nikolay Lysenko
"""


from .basic import Wall, WallND, Window
from .door import Door
from .electricity import ElectricalCable, PowerOutlet
from .element import Element
from .info import DimensionArrow, TextBox
from .lighting import CeilingLamp, LEDStrip, Switch, WallLamp
from .multipurpose import Line, Polygon, Circle
from .room import Room


def create_elements_registry() -> dict[str, type(Element)]:
    """
    Create registry of implemented elements.

    :return:
        mapping from element type to element class
    """
    registry = {
        'ceiling_lamp': CeilingLamp,
        'dimension_arrow': DimensionArrow,
        'door': Door,
        'electrical_cable': ElectricalCable,
        'led_strip': LEDStrip,
        'line': Line,
        'polygon': Polygon,
        'power_outlet': PowerOutlet,
        'room': Room,
        'switch': Switch,
        'text_box': TextBox,
        'wall': Wall,
        'wallnd': WallND,
        'wall_lamp': WallLamp,
        'window': Window,
        'circle': Circle
    }
    return registry

def element_sorter_by_type(element: Element) -> int:
    """
    Provide a sorting key for elements based on their type.
    :param element:
        element to be sorted
    :return:
        sorting key (lower values are sorted first)
    """

    if isinstance(element, (Wall, WallND)):
        return 0  # Walls first
    elif isinstance(element, Door):
        return 1  # Doors second
    elif isinstance(element, Window):
        return 2  # Windows third
    else:
        return 3  # Other elements last