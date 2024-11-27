"""
Map element names to their classes.

Author: Nikolay Lysenko
"""


from .basic import Door, Wall, Window
from .electricity import ElectricalCable, PowerOutlet
from .element import Element
from .info import DimensionArrow, TextBox
from .lighting import CeilingLamp, LEDStrip, Switch, WallLamp
from .multipurpose import Line, Polygon


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
        'switch': Switch,
        'text_box': TextBox,
        'wall': Wall,
        'wall_lamp': WallLamp,
        'window': Window,
    }
    return registry
