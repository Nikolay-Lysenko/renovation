"""
Render project.

Author: Nikolay Lysenko
"""


import argparse
import copy
from pathlib import Path
from collections import defaultdict

import yaml

from floor_planner import elements
from floor_planner.elements import create_elements_registry
from floor_planner.floor_plan import FloorPlan
from floor_planner.project import Project
from floor_planner.markdown_report import generate_elements_report
from floor_planner.variables import validate_constants, resolve_constants, resolve_element_params
from floor_planner.elements.room import Room

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
                    room_params = copy.deepcopy(element_params)
                    room = Room.create_from_params(room_params, elements_registry, floor_plan, all_elements, elements_by_id, global_constants)
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
            element_params_copy = copy.deepcopy(element_params)
            element_type = element_params_copy.get('type')
            if element_type == 'room':
                # Create room with nested elements
                room = Room.create_from_params(element_params_copy, elements_registry, floor_plan, all_elements, elements_by_id, global_constants)
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
                notes=report_params.get('notes', None),
                fontsize=report_params.get('fontsize', 11)
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
