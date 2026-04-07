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


def generate_elements_report(all_elements: list, output_path: str) -> None:
    """
    Generate markdown report with all elements grouped by type.
    
    :param all_elements:
        list of all element instances
    :param output_path:
        path to output markdown file
    """
    # Group elements by type
    grouped = defaultdict(list)
    for element in all_elements:
        element_type = element.__class__.__name__
        grouped[element_type].append(element)
    
    # Generate report
    with open(output_path, 'w') as f:
        f.write("# Floor Plan Elements Report\n\n")
        
        # Combine Wall and WallND into single section
        all_walls = grouped.get('Wall', []) + grouped.get('WallND', [])
        if all_walls:
            f.write("## Walls\n\n")
            f.write("| ID | Length (m) | Thickness (m) | Corner 1 (x,y) | Corner 2 (x,y) | Corner 3 (x,y) | Corner 4 (x,y) |\n")
            f.write("|---|---|---|---|---|---|---|\n")
            for element in all_walls:
                corners = element.get_corners()
                corner_strs = [f"({c[0]:.3f}, {c[1]:.3f})" for c in corners]
                f.write(f"| {element.id} | {element.length} | {element.thickness} | "
                       f"{corner_strs[0]} | {corner_strs[1]} | {corner_strs[2]} | {corner_strs[3]} |\n")
            f.write("\n")
        
        # Report Windows
        if 'Window' in grouped:
            f.write("## Windows\n\n")
            f.write("| ID | Length (m) | Overall Thickness (m) | Corner 1 (x,y) | Corner 2 (x,y) | Corner 3 (x,y) | Corner 4 (x,y) |\n")
            f.write("|---|---|---|---|---|---|---|\n")
            for element in grouped['Window']:
                corners = element.get_corners()
                corner_strs = [f"({c[0]:.3f}, {c[1]:.3f})" for c in corners]
                f.write(f"| {element.id} | {element.length} | {element.overall_thickness} | "
                       f"{corner_strs[0]} | {corner_strs[1]} | {corner_strs[2]} | {corner_strs[3]} |\n")
            f.write("\n")
        
        # Report Doors
        if 'Door' in grouped:
            f.write("## Doors\n\n")
            f.write("| ID | Doorway Width (m) | Door Width (m) | Opens to Right | Corner 1 (x,y) | Corner 2 (x,y) | Corner 3 (x,y) | Corner 4 (x,y) |\n")
            f.write("|---|---|---|---|---|---|---|---|\n")
            for element in grouped['Door']:
                to_right = "Yes" if element.to_the_right else "No"
                corners = element.get_corners()
                corner_strs = [f"({c[0]:.3f}, {c[1]:.3f})" for c in corners]
                f.write(f"| {element.id} | {element.doorway_width} | {element.door_width} | {to_right} | "
                       f"{corner_strs[0]} | {corner_strs[1]} | {corner_strs[2]} | {corner_strs[3]} |\n")
            f.write("\n")
        
        # Report other element types
        other_types = [t for t in grouped.keys() if t not in ['Wall', 'WallND', 'Window', 'Door']]
        if other_types:
            f.write("## Other Elements\n\n")
            for element_type in sorted(other_types):
                f.write(f"### {element_type}\n\n")
                f.write(f"Total count: {len(grouped[element_type])}\n\n")
                f.write("| ID |\n")
                f.write("|---|\n")
                for element in grouped[element_type]:
                    f.write(f"| {element.id} |\n")
                f.write("\n")
        
        # Summary
        f.write("## Summary\n\n")
        f.write("| Element Type | Count |\n")
        f.write("|---|---|\n")
        
        # Combine Wall and WallND in summary
        wall_count = len(grouped.get('Wall', [])) + len(grouped.get('WallND', []))
        if wall_count > 0:
            f.write(f"| Wall | {wall_count} |\n")
        
        # Report other types
        for element_type in sorted(grouped.keys()):
            if element_type not in ['Wall', 'WallND']:
                f.write(f"| {element_type} | {len(grouped[element_type])} |\n")


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
    
    # Set label colors configuration if available
    from renovation import elements
    
    # Reset ID counters for consistent IDs
    elements.reset_id_counters()
    
    options = settings.get('options', {})
    label_colors = options.get('label_colors', {})
    elements.set_label_colors(label_colors)
    
    # Set id colors configuration if available
    id_colors = options.get('id_colors', {})
    elements.set_id_colors(id_colors)
    
    # Set dimensions configuration if available
    dimensions = options.get('dimensions', False)
    elements.set_dimensions(dimensions)

    elements_registry = create_elements_registry()

    # Track all elements for report
    all_elements = []

    floor_plans = []
    for floor_plan_params in settings['floor_plans']:
        layout_params = floor_plan_params.get('layout') or settings['default_layout']
        floor_plan = FloorPlan(**layout_params)
        title_params = floor_plan_params.get('title')
        if title_params:
            floor_plan.add_title(**title_params)
        for set_name in floor_plan_params.get('inherited_elements', []):
            for element_params in settings['reusable_elements'].get(set_name, []):
                element_class = elements_registry[element_params['type']]
                element_params = {k: v for k, v in element_params.items() if k != 'type'}
                element = element_class(**element_params)
                floor_plan.add_element(element)
                all_elements.append(element)
        for element_params in floor_plan_params.get('elements', []):
            element_class = elements_registry[element_params.pop('type')]
            element = element_class(**element_params)
            floor_plan.add_element(element)
            all_elements.append(element)
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
    report_path = config_dir / 'elements_report.md'
    generate_elements_report(all_elements, str(report_path))
    print(f"Elements report generated: {report_path}")


if __name__ == '__main__':
    main()
