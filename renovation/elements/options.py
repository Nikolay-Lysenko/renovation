"""
Configuration options for floor plan elements.

Author: Krzysztof Bartczak
"""


# Global configuration for label colors
_label_colors = {}

# Global configuration for id colors
_id_colors = {}

# Global configuration for dimensions
_dimensions_enabled = False

# Global configuration for show_invisible
_show_invisible = False

# Global counter for element IDs
_id_counters = {}


def set_label_colors(label_colors: dict) -> None:
    """Set label colors configuration."""
    global _label_colors
    _label_colors = label_colors or {}


def get_label_color(element_type: str) -> str | None:
    """Get label color for element type, or None if not configured."""
    return _label_colors.get(element_type)


def set_id_colors(id_colors: dict) -> None:
    """Set id colors configuration."""
    global _id_colors
    _id_colors = id_colors or {}


def get_id_color(element_type: str) -> str | None:
    """Get id color for element type, or None if not configured."""
    return _id_colors.get(element_type)


def set_dimensions(enabled: bool) -> None:
    """Set dimensions configuration."""
    global _dimensions_enabled
    _dimensions_enabled = enabled


def get_dimensions() -> bool:
    """Get dimensions configuration."""
    return _dimensions_enabled


def set_show_invisible(enabled: bool) -> None:
    """Set show_invisible configuration."""
    global _show_invisible
    _show_invisible = enabled


def get_show_invisible() -> bool:
    """Get show_invisible configuration."""
    return _show_invisible


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
