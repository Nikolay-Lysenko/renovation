"""
Configuration options for floor plan elements.

Author: Krzysztof Bartczak
"""


# Global configuration for element-specific options
# Structure: {element_type: {option_name: value}}
_element_options = {}

# Global counter for element IDs
_id_counters = {}


def set_element_options(options: dict) -> None:
    """
    Set options for element types.
    
    :param options:
        dictionary with element type as key and option dict as value
        Example: {'Wall': {'label_color': 'blue', 'dimensions': True}, 'Door': {'id_color': 'red'}}
    """
    global _element_options
    _element_options = options or {}


def get_element_option(element_type: str, option_name: str, default=None):
    """
    Get specific option value for an element type.
    
    :param element_type:
        type of the element (e.g., 'Wall', 'Door')
    :param option_name:
        name of the option (e.g., 'label_color', 'dimensions')
    :param default:
        default value if option not found
    :return:
        option value or default
    """
    type_options = _element_options.get(element_type)
    if type_options is None or not isinstance(type_options, dict):
        return default
    return type_options.get(option_name, default)


def get_label_color(element_type: str) -> str | None:
    """Get label color for element type, or None if not configured."""
    return get_element_option(element_type, 'label_color')


def get_id_color(element_type: str) -> str | None:
    """Get id color for element type, or None if not configured."""
    color = get_element_option(element_type, 'id_color')
    # Handle None value explicitly set in YAML
    return None if color == 'None' else color


def get_dimensions() -> bool:
    """Get dimensions configuration for Wall elements."""
    return get_element_option('Wall', 'dimensions', False)


def get_show_invisible() -> bool:
    """Get show_invisible configuration for Wall elements."""
    return get_element_option('Wall', 'show_invisible', False)


def generate_element_id(element_type: str, label: str | None = None) -> str:
    """Generate unique ID for an element.
    
    :param element_type:
        type of the element (class name)
    :param label:
        optional label of the element
    :return:
        unique ID in format <label>_<number> or <lowercase_type>_<number>
    """
    global _id_counters
    
    # Determine prefix based on label or type
    if label:
        prefix = label
    else:
        prefix = element_type.lower()
    
    # Increment counter for this prefix
    if prefix not in _id_counters:
        _id_counters[prefix] = 0
    _id_counters[prefix] += 1
    
    return f"{prefix}_{_id_counters[prefix]}"


def reset_id_counters() -> None:
    """Reset all ID counters."""
    global _id_counters
    _id_counters = {}
