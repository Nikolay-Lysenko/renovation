"""
Render project.

Author: Nikolay Lysenko
"""


import argparse
from pathlib import Path
from collections import defaultdict

import yaml

from renovation.elements import create_elements_registry
from renovation.floor_plan import FloorPlan
from renovation.project import Project
from renovation.markdown_report import generate_elements_report

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
        import re
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
    fields_to_resolve = ['anchor_point', 'thickness', 'length', 'doorway_width', 'door_width', 'overall_thickness']

    for field in fields_to_resolve:
        if field in params:
            params[field] = resolve_constants(params[field], merged_values)

    return params


def create_room_from_params(params: dict, elements_registry: dict, floor_plan, all_elements: list, elements_by_id: dict, global_constants: dict = None):
    """
    Create a Room from YAML parameters with nested elements.

    :param params:
        dictionary with 'elements' list containing wall/window/door definitions,
        optional 'anchor_point', 'color', 'label', 'constants', and 'vars'
    :param elements_registry:
        registry mapping element type names to classes
    :param floor_plan:
        floor plan to add child elements to
    :param all_elements:
        list to track all created elements
    :param elements_by_id:
        dictionary to track elements by ID
    :param global_constants:
        global constants dictionary (optional)
    :return:
        Room instance
    """
    from renovation.elements import Room

    if global_constants is None:
        global_constants = {}

    # Extract room-scoped constants
    room_constants = params.get('constants', {})
    validate_constants(room_constants, f"room '{params.get('label', 'unnamed')}'")

    # Extract and resolve room-scoped vars
    # Vars are like constants but can be expressions themselves
    room_vars_definitions = params.get('vars', {})
    room_vars = {}

    # Resolve each var expression using constants and previously resolved vars
    merged_constants = {**global_constants, **room_constants}
    for var_name, var_expression in room_vars_definitions.items():
        # Each var can reference constants and previously defined vars
        available_values = {**merged_constants, **room_vars}
        room_vars[var_name] = resolve_constants(var_expression, available_values)

    label = params.get('label')
    room_anchor_point = params.get('anchor_point', (0, 0))
    room_color = params.get('color', 'black')
    element_defs = params.get('elements', [])

    # Resolve constants/vars in room's own parameters
    if 'anchor_point' in params:
        available_values = {**merged_constants, **room_vars}
        room_anchor_point = resolve_constants(params['anchor_point'], available_values)

    if not element_defs:
        raise ValueError("Room must have 'elements' list containing wall and other element definitions")

    # Create all child elements
    room_walls = []
    room_other_elements = []

    for element_def in element_defs:
        element_type = element_def.pop('type')
        element_class = elements_registry.get(element_type)

        if not element_class:
            raise ValueError(f"Unknown element type: {element_type}")

        # Resolve constants/vars in element parameters (room constants/vars override global)
        element_def = resolve_element_params(element_def, global_constants, room_constants, room_vars)

        # Adjust anchor_point to be relative to room's anchor_point
        if 'anchor_point' in element_def:
            rel_x, rel_y = element_def['anchor_point']
            element_def['anchor_point'] = (
                rel_x + room_anchor_point[0],
                rel_y + room_anchor_point[1]
            )

        # For walls without explicit color, use room's color
        is_wall = element_type in ['wall', 'wallnd']
        if is_wall and 'color' not in element_def:
            element_def['color'] = room_color

        # Create the element
        element = element_class(**element_def)

        # Add to floor plan for rendering
        floor_plan.add_element(element)

        # Track in global lists
        all_elements.append(element)
        elements_by_id[element.id] = element

        # Organize by type
        if element.__class__.__name__ in ['Wall', 'WallND']:
            room_walls.append(element)
        else:
            room_other_elements.append(element)

    # Validate we have at least some walls
    # The Room class will validate that exactly 4 have room_edge=True
    if len(room_walls) == 0:
        raise ValueError("Room must contain at least one wall")

    return Room(
        walls=room_walls,
        other_elements=room_other_elements,
        anchor_point=room_anchor_point,
        color=room_color,
        label=label
    )


def load_reusable_elements(reusable_elements_config: dict, config_dir: Path) -> dict:
    """
    Load reusable elements from configuration, including external files.

    :param reusable_elements_config:
        reusable_elements section from main config, can contain inline definitions
        or file references (string values pointing to external YAML files)
    :param config_dir:
        directory containing the main config file (for resolving relative paths)
    :return:
        dictionary of reusable element sets with all external files loaded
    """
    if not reusable_elements_config:
        return {}

    loaded_elements = {}

    for set_name, content in reusable_elements_config.items():
        if isinstance(content, str):
            # It's a file reference - load the external file
            file_path = config_dir / content

            if not file_path.exists():
                raise FileNotFoundError(f"Reusable elements file not found: {file_path}")

            print(f"Loading reusable elements '{set_name}' from {content}")

            with open(file_path) as ext_file:
                external_content = yaml.load(ext_file, Loader=yaml.FullLoader)

            # The external file should contain a list of element definitions
            if not isinstance(external_content, list):
                raise ValueError(
                    f"External reusable elements file '{content}' must contain a list of elements, "
                    f"got {type(external_content).__name__}"
                )

            loaded_elements[set_name] = external_content
        elif isinstance(content, list):
            # It's an inline definition - use as-is
            loaded_elements[set_name] = content
        else:
            raise ValueError(
                f"Reusable element set '{set_name}' must be either a list of elements "
                f"or a string (file path), got {type(content).__name__}"
            )

    return loaded_elements


def parse_cli_args() -> argparse.Namespace:
    """
    Parse arguments passed via Command Line Interface (CLI).

    :return:
        namespace with arguments
    """
    parser = argparse.ArgumentParser(description='Rendering of renovation project floor plans.')
    parser.add_argument(
        '-c', '--config_path', type=str, default=None, help='path to configuration file'
    )
    cli_args = parser.parse_args()
    return cli_args


def main() -> None:
    """Parse CLI arguments and run requested tasks."""
    cli_args = parse_cli_args()
    config_path = cli_args.config_path
    config_dir = Path(config_path).parent

    with open(config_path) as config_file:
        settings = yaml.load(config_file, Loader=yaml.FullLoader)

    from renovation import elements

    # Reset ID counters for consistent IDs
    elements.reset_id_counters()

    # Load and validate global constants
    global_constants = settings.get('constants', {})
    validate_constants(global_constants, "global")

    # Load default options (hierarchical structure)
    default_options = settings.get('default_options', {})

    # Remove element types with None values (from commented-out YAML properties)
    cleaned_options = {}
    for element_type, options in default_options.items():
        if options is not None and isinstance(options, dict):
            cleaned_options[element_type] = options
    default_options = cleaned_options

    # Set default options globally
    elements.set_element_options(default_options)

    elements_registry = create_elements_registry()

    # Load reusable elements (including external files)
    reusable_elements = load_reusable_elements(
        settings.get('reusable_elements', {}),
        config_dir
    )

    # Track all elements for report
    all_elements = []
    # Track elements by ID for room creation
    elements_by_id = {}

    floor_plans = []
    for floor_plan_params in settings['floor_plans']:
        # Merge floor plan options with defaults (floor plan options override defaults)
        floor_plan_options = floor_plan_params.get('options', {})
        if floor_plan_options:
            # Create a merged options dict
            import copy
            merged_options = copy.deepcopy(default_options)
            for element_type, type_options in floor_plan_options.items():
                # Skip if type_options is None (all properties commented out in YAML)
                if type_options is None or not isinstance(type_options, dict):
                    continue
                # Ensure element_type exists in merged_options as a dict
                if element_type not in merged_options or not isinstance(merged_options.get(element_type), dict):
                    merged_options[element_type] = {}
                merged_options[element_type].update(type_options)
            # Apply merged options for this floor plan
            elements.set_element_options(merged_options)
        else:
            # Use default options
            elements.set_element_options(default_options)

        layout_params = floor_plan_params.get('layout') or settings['default_layout']
        floor_plan = FloorPlan(**layout_params)
        title_params = floor_plan_params.get('title')
        if title_params:
            floor_plan.add_title(**title_params)
        for set_name in floor_plan_params.get('inherited_elements', []):
            for element_params in reusable_elements.get(set_name, []):
                element_type = element_params.get('type')
                if element_type == 'room':
                    # Create room with nested elements
                    import copy
                    room_params = copy.deepcopy(element_params)
                    room = create_room_from_params(room_params, elements_registry, floor_plan, all_elements, elements_by_id, global_constants)
                    floor_plan.add_element(room)
                    all_elements.append(room)
                    elements_by_id[room.id] = room
                else:
                    # Create regular element
                    element_class = elements_registry[element_type]
                    element_params_clean = {k: v for k, v in element_params.items() if k != 'type'}
                    # Resolve constants in element parameters
                    element_params_clean = resolve_element_params(element_params_clean, global_constants)
                    element = element_class(**element_params_clean)
                    floor_plan.add_element(element)
                    all_elements.append(element)
                    elements_by_id[element.id] = element
        for element_params in floor_plan_params.get('elements', []):
            import copy
            element_params_copy = copy.deepcopy(element_params)
            element_type = element_params_copy.get('type')
            if element_type == 'room':
                # Create room with nested elements
                room = create_room_from_params(element_params_copy, elements_registry, floor_plan, all_elements, elements_by_id, global_constants)
                floor_plan.add_element(room)
                all_elements.append(room)
                elements_by_id[room.id] = room
            else:
                # Create regular element
                element_params_copy.pop('type')
                element_class = elements_registry[element_type]
                # Resolve constants in element parameters
                element_params_copy = resolve_element_params(element_params_copy, global_constants)
                element = element_class(**element_params_copy)
                floor_plan.add_element(element)
                all_elements.append(element)
                elements_by_id[element.id] = element
        floor_plan.draw_elements()

        # Draw report if specified
        report_params = floor_plan_params.get('report')
        if report_params:
            # Resolve anchor_point with constants if needed
            anchor_point = report_params.get('anchor_point', [0, 0])
            if isinstance(anchor_point, list):
                # Resolve constants in anchor_point
                anchor_point = resolve_constants(anchor_point, global_constants)

            floor_plan.draw_report(
                anchor_point=anchor_point,
                areas=report_params.get('areas', False),
                total_area=report_params.get('total_area', False),
                notes=report_params.get('notes', None)
            )

        floor_plans.append(floor_plan)

    project = Project(floor_plans, settings['project']['dpi'])
    pdf_path = settings['project'].get('pdf_file')
    if pdf_path is not None:
        pdf_path = config_dir / pdf_path
        project.render_to_pdf(str(pdf_path))
    png_path = settings['project'].get('png_dir')
    if png_path is not None:
        png_path = config_dir / png_path
        project.render_to_png(str(png_path))

    # Generate elements report
    report_path = Path(config_path).with_suffix(".md")
    generate_elements_report(all_elements, str(report_path))
    print(f"Elements report generated: {report_path}")


if __name__ == '__main__':
    main()
