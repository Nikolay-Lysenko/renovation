"""

Author: Krzysztof Bartczak
"""

import re

def validate_constants(constants_dict: dict, scope_name: str = "global") -> None:
    """
    Validate that all constants are floating point numbers.

    :param constants_dict:
        dictionary of constant name -> value mappings
    :param scope_name:
        name of the scope (for error messages)
    :raises ValueError:
        if any constant is not a float
    """
    if not constants_dict:
        return

    for name, value in constants_dict.items():
        if not isinstance(value, (int, float)):
            raise ValueError(
                f"Constant '{name}' in {scope_name} scope must be a number, "
                f"got {type(value).__name__}: {value}"
            )


def resolve_constants(value, constants_dict: dict):
    """
    Resolve a constant reference or arithmetic expression to its actual value.

    Supports:
    - Direct constant references: "wall_thickness"
    - Arithmetic expressions: "wall_length + 0.5"
    - Expressions with multiple constants: "room1_x + wall_thickness * 2"

    :param value:
        the value to resolve (can be a string reference, number, list, or dict)
    :param constants_dict:
        dictionary of available constants
    :return:
        resolved value
    """
    if isinstance(value, str):
        # Check if it's a direct constant reference (no operators)
        if value in constants_dict:
            return float(constants_dict[value])

        # Otherwise, treat as arithmetic expression
        # Replace constant names with their values
        expression = value

        # Sort constants by length (descending) to avoid partial replacements
        # e.g., replace 'wall_thickness' before 'wall' to avoid issues
        sorted_constants = sorted(constants_dict.keys(), key=len, reverse=True)

        for const_name in sorted_constants:
            # Use word boundaries to match whole constant names
            pattern = r'\b' + re.escape(const_name) + r'\b'
            expression = re.sub(pattern, str(constants_dict[const_name]), expression)

        # Safely evaluate the expression
        try:
            # Use eval with restricted namespace for safety
            # Only allow basic math operations
            result = eval(expression, {"__builtins__": {}}, {})
            return float(result)
        except (SyntaxError, NameError, TypeError) as e:
            raise ValueError(
                f"Invalid expression: '{value}'. "
                f"After constant substitution: '{expression}'. Error: {e}"
            )
    elif isinstance(value, list):
        # Recursively resolve list elements
        return [resolve_constants(item, constants_dict) for item in value]
    elif isinstance(value, dict):
        # Recursively resolve dictionary values
        return {k: resolve_constants(v, constants_dict) for k, v in value.items()}
    elif isinstance(value, (int, float)):
        # Already a number, return as float
        return float(value)
    else:
        # For other types, return as-is
        return value


def resolve_element_params(params: dict, global_constants: dict, room_constants: dict = None, room_vars: dict = None) -> dict:
    """
    Resolve constant and variable references in element parameters.

    :param params:
        element parameters dictionary
    :param global_constants:
        global constants dictionary
    :param room_constants:
        room-scoped constants dictionary (optional)
    :param room_vars:
        room-scoped variables dictionary (optional)
    :return:
        params with constants and vars resolved
    """
    # Merge constants and vars: room-scoped override global
    merged_values = {**global_constants}
    if room_constants:
        merged_values.update(room_constants)
    if room_vars:
        merged_values.update(room_vars)

    # Resolve specific fields that can use constants/vars
    fields_to_resolve = ['anchor_point',
                            'thickness', 
                            'length',
                            'doorway_width', 
                            'door_width',
                            'overall_thickness',
                            'first_point',
                            'second_point',
                            'radius',
                            'width',
                            ]

    for field in fields_to_resolve:
        if field in params:
            params[field] = resolve_constants(params[field], merged_values)

    return params

