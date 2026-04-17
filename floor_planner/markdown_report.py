"""

Author: Krzysztof Bartczak
"""


from collections import defaultdict

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

