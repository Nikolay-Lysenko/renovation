"""
Configuration options for floor plan elements.

Author: Krzysztof Bartczak
"""


# Global configuration for label colors
_label_colors = {}


def set_label_colors(label_colors: dict) -> None:
    """Set label colors configuration."""
    global _label_colors
    _label_colors = label_colors or {}


def get_label_color(element_type: str) -> str | None:
    """Get label color for element type, or None if not configured."""
    return _label_colors.get(element_type)
