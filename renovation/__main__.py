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
        
        # Combine Wall and WallND into single section, excluding invisible walls
        all_walls = grouped.get('Wall', []) + grouped.get('WallND', [])
        # Filter out walls with color='invisible'
        all_walls = [w for w in all_walls if w.color != 'invisible']
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
        
        # Report invisible walls in separate section
        all_walls_combined = grouped.get('Wall', []) + grouped.get('WallND', [])
        invisible_walls = [w for w in all_walls_combined if w.color == 'invisible']
        if invisible_walls:
            f.write("## Invisible Walls\n\n")
            f.write("| ID | Length (m) | Thickness (m) | Corner 1 (x,y) | Corner 2 (x,y) | Corner 3 (x,y) | Corner 4 (x,y) |\n")
            f.write("|---|---|---|---|---|---|---|\n")
            for element in invisible_walls:
                corners = element.get_corners()
                corner_strs = [f"({c[0]:.3f}, {c[1]:.3f})" for c in corners]
                f.write(f"| {element.id} | {element.length} | {element.thickness} | "
                       f"{corner_strs[0]} | {corner_strs[1]} | {corner_strs[2]} | {corner_strs[3]} |\n")
            f.write("\n")
        
        # Report Rooms
        if 'Room' in grouped:
            f.write("## Rooms\n\n")
            for room in grouped['Room']:
                f.write(f"### {room.id}\n\n")
                if room.label:
                    f.write(f"**Label:** {room.label}\n\n")
                
                # Room properties
                f.write(f"**Anchor Point:** ({room.anchor_point[0]:.3f}, {room.anchor_point[1]:.3f})\n\n")
                f.write(f"**Color:** {room.color}\n\n")
                
                # Room dimensions and areas
                f.write("**Dimensions:**\n\n")
                f.write(f"- Inner horizontal length: {room.inner_horizontal_length:.3f} m\n")
                f.write(f"- Inner vertical length: {room.inner_vertical_length:.3f} m\n")
                f.write(f"- Outer horizontal length: {room.outer_horizontal_length:.3f} m\n")
                f.write(f"- Outer vertical length: {room.outer_vertical_length:.3f} m\n")
                f.write(f"- Inner area: {room.inner_area:.3f} m²\n")
                f.write(f"- Outer area: {room.outer_area:.3f} m²\n\n")
                
                # Corner coordinates
                f.write("**External Corners:**\n\n")
                for i, corner in enumerate(room.external_corners, 1):
                    f.write(f"- Corner {i}: ({corner[0]:.3f}, {corner[1]:.3f})\n")
                f.write("\n")
                
                f.write("**Internal Corners:**\n\n")
                for i, corner in enumerate(room.internal_corners, 1):
                    f.write(f"- Corner {i}: ({corner[0]:.3f}, {corner[1]:.3f})\n")
                f.write("\n")
                
                # List room edge walls (walls with room_edge=True)
                edge_walls = [w for w in room.walls if w.room_edge]
                f.write("**Room Edge Walls:**\n\n")
                f.write("| Wall ID | Orientation | Length (m) | Thickness (m) |\n")
                f.write("|---|---|---|---|\n")
                for wall in edge_walls:
                    # Determine orientation from angle: 0/180 = Horizontal, 90/270 = Vertical
                    orientation = "Horizontal" if wall.orientation_angle % 180 == 0 else "Vertical"
                    f.write(f"| {wall.id} | {orientation} | {wall.length:.3f} | {wall.thickness:.3f} |\n")
                f.write("\n")
                
                # List internal walls (walls with room_edge=False)
                internal_walls = [w for w in room.walls if not w.room_edge]
                if internal_walls:
                    f.write("**Internal Walls:**\n\n")
                    f.write("| Wall ID | Orientation | Length (m) | Thickness (m) |\n")
                    f.write("|---|---|---|---|\n")
                    for wall in internal_walls:
                        orientation = "Horizontal" if wall.orientation_angle % 180 == 0 else "Vertical"
                        f.write(f"| {wall.id} | {orientation} | {wall.length:.3f} | {wall.thickness:.3f} |\n")
                    f.write("\n")
                
                # List other elements in room (windows, doors, etc.)
                if room.other_elements:
                    f.write("**Other Elements in Room:**\n\n")
                    f.write("| Element ID | Type |\n")
                    f.write("|---|---|\n")
                    for element in room.other_elements:
                        element_type = element.__class__.__name__
                        f.write(f"| {element.id} | {element_type} |\n")
                    f.write("\n")
        
        # Report other element types
        other_types = [t for t in grouped.keys() if t not in ['Wall', 'WallND', 'Window', 'Door', 'Room']]
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
        
        # Combine Wall and WallND in summary, excluding invisible walls
        all_walls_for_count = grouped.get('Wall', []) + grouped.get('WallND', [])
        wall_count = len([w for w in all_walls_for_count if w.color != 'invisible'])
        invisible_wall_count = len([w for w in all_walls_for_count if w.color == 'invisible'])
        
        if wall_count > 0:
            f.write(f"| Wall | {wall_count} |\n")
        
        if invisible_wall_count > 0:
            f.write(f"| Invisible Wall | {invisible_wall_count} |\n")
        
        # Report Rooms
        room_count = len(grouped.get('Room', []))
        if room_count > 0:
            f.write(f"| Room | {room_count} |\n")
        
        # Report other types
        for element_type in sorted(grouped.keys()):
            if element_type not in ['Wall', 'WallND', 'Room']:
                f.write(f"| {element_type} | {len(grouped[element_type])} |\n")


def create_room_from_params(params: dict, elements_registry: dict, floor_plan, all_elements: list, elements_by_id: dict):
    """
    Create a Room from YAML parameters with nested elements.
    
    :param params:
        dictionary with 'elements' list containing wall/window/door definitions,
        optional 'anchor_point', 'color', and 'label'
    :param elements_registry:
        registry mapping element type names to classes
    :param floor_plan:
        floor plan to add child elements to
    :param all_elements:
        list to track all created elements
    :param elements_by_id:
        dictionary to track elements by ID
    :return:
        Room instance
    """
    from renovation.elements import Room
    
    label = params.get('label')
    room_anchor_point = params.get('anchor_point', (0, 0))
    room_color = params.get('color', 'black')
    element_defs = params.get('elements', [])
    
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
            for element_params in settings['reusable_elements'].get(set_name, []):
                element_type = element_params.get('type')
                if element_type == 'room':
                    # Create room with nested elements
                    import copy
                    room_params = copy.deepcopy(element_params)
                    room = create_room_from_params(room_params, elements_registry, floor_plan, all_elements, elements_by_id)
                    all_elements.append(room)
                    elements_by_id[room.id] = room
                else:
                    # Create regular element
                    element_class = elements_registry[element_type]
                    element_params_clean = {k: v for k, v in element_params.items() if k != 'type'}
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
                room = create_room_from_params(element_params_copy, elements_registry, floor_plan, all_elements, elements_by_id)
                all_elements.append(room)
                elements_by_id[room.id] = room
            else:
                # Create regular element
                element_params_copy.pop('type')
                element_class = elements_registry[element_type]
                element = element_class(**element_params_copy)
                floor_plan.add_element(element)
                all_elements.append(element)
                elements_by_id[element.id] = element
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
