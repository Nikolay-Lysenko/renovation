"""
Configuration options for floor plan elements.

Author: Krzysztof Bartczak
"""


# Global configuration for label colors
_label_colors = {}

# Global configuration for dimensions
_dimensions_enabled = False


def set_label_colors(label_colors: dict) -> None:
    """Set label colors configuration."""
    global _label_colors
    _label_colors = label_colors or {}


def get_label_color(element_type: str) -> str | None:
    """Get label color for element type, or None if not configured."""
    return _label_colors.get(element_type)


def set_dimensions(enabled: bool) -> None:
    """Set dimensions configuration."""
    global _dimensions_enabled
    _dimensions_enabled = enabled


def get_dimensions() -> bool:
    """Get dimensions configuration."""
    return _dimensions_enabled
