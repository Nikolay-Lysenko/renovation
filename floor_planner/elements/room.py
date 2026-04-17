"""
Room element composed of 4 walls forming a rectangle.

Author: Krzysztof Bartczak
"""


import math
import matplotlib.axes

from ..variables import validate_constants, resolve_constants, resolve_element_params
from .element import Element
from .info import DimensionArrow, TextBox
from .options import get_id_color, get_label_color, get_element_option


class Room(Element):
    """
    Room defined by 4 walls forming a rectangle, with optional other elements.

    A room consists of 2 horizontal walls (rotation 0 or 180) and
    2 vertical walls (rotation 90 or 270), plus any number of additional elements.
    """

    def __init__(
            self,
            walls: list,
            other_elements: list | None = None,
            anchor_point: tuple[float, float] = (0, 0),
            color: str = 'black',
            label: str | None = None
    ):
        """
        Initialize a room from walls and optional other elements.

        :param walls:
            list of wall objects (Wall or WallND); exactly 4 must have room_edge=True
        :param other_elements:
            optional list of other element objects (windows, doors, etc.) inside the room
        :param anchor_point:
            coordinates (x, y) of the room's reference point (bottom-left corner)
        :param color:
            default color for room walls if they don't have explicit color
        :param label:
            optional label for the room
        :raises ValueError:
            if walls don't form a valid rectangle or exactly 4 walls don't have room_edge=True
        """
        super().__init__(label=label)

        self.anchor_point = anchor_point
        self.color = color
        self.walls = walls
        self.other_elements = other_elements or []

        # Mark walls as room walls
        for wall in walls:
            wall.is_room_wall = True
            wall.room_id = self.id

        # Validate and organize walls
        self._validate_and_organize_walls()

        # Calculate room properties
        self._calculate_properties()


    @classmethod
    def create_from_params(cls, params: dict, elements_registry: dict, floor_plan, all_elements: list, elements_by_id: dict, global_constants: dict = None):
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
            # start and and for lines
            if 'first_point' in element_def:
                rel_x, rel_y = element_def['first_point']
                element_def['first_point'] = (
                    rel_x + room_anchor_point[0],
                    rel_y + room_anchor_point[1]
                )
            if 'second_point' in element_def:
                rel_x, rel_y = element_def['second_point']
                element_def['second_point'] = (
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

        return cls(
            walls=room_walls,
            other_elements=room_other_elements,
            anchor_point=room_anchor_point,
            color=room_color,
            label=label
        )



    def _validate_and_organize_walls(self):
        """Validate walls form a rectangle and organize them."""
        # Filter walls that are marked as room edges
        room_edge_walls = [wall for wall in self.walls if wall.room_edge]

        # Validate exactly 4 walls are marked as room_edge
        if len(room_edge_walls) != 4:
            raise ValueError(
                f"Room requires exactly 4 walls with room_edge=True, got {len(room_edge_walls)}. "
                f"Total walls in room: {len(self.walls)}"
            )

        # Separate walls by orientation
        horizontal_walls = []  # 0 or 180 degrees
        vertical_walls = []    # 90 or 270 degrees

        for edge_wall in room_edge_walls:
            angle = edge_wall.orientation_angle % 360

            # edge walls must be either horizontal (0 or 180) or vertical (90 or 270)
            if angle == 0 or angle == 180 :
                horizontal_walls.append(edge_wall)
            elif angle == 90 or angle == 270:
                vertical_walls.append(edge_wall)
            else:
                raise ValueError(
                    f"Wall with orientation {edge_wall.orientation_angle}° is neither horizontal nor vertical"
                )

        if len(horizontal_walls) != 2:
            raise ValueError(f"Room requires exactly 2 horizontal walls, got {len(horizontal_walls)}")
        if len(vertical_walls) != 2:
            raise ValueError(f"Room requires exactly 2 vertical walls, got {len(vertical_walls)}")

        self.room_edge_walls = room_edge_walls

        # Validate walls form a proper rectangle by checking corner alignment
        # This will also identify and store specific wall positions (bottom, top, left, right)
        self._validate_corner_alignment()

    def _validate_corner_alignment(self):
        """Validate that wall corners align to form a rectangle."""
        # Get all corners from room edge walls only
        all_corners = []
        for wall in self.room_edge_walls:
            corners = wall.get_corners()
            all_corners.extend(corners)

        # Find the 4 external rectangle corners based on min/max coordinates
        x_coords = [c[0] for c in all_corners]
        y_coords = [c[1] for c in all_corners]

        min_x = min(x_coords)
        max_x = max(x_coords)
        min_y = min(y_coords)
        max_y = max(y_coords)

        # Define and store the 4 external rectangle corners
        self.external_corners = [
            (min_x, min_y),  # 0: bottom-left
            (max_x, min_y),  # 1: bottom-right
            (max_x, max_y),  # 2: top-right
            (min_x, max_y)   # 3: top-left
        ]

        # Initialize wall position references
        self.bottom_wall = None
        self.top_wall = None
        self.left_wall = None
        self.right_wall = None

        # Validate that each edge wall has exactly 2 of its corners matching external  corners
        # and identify which position each wall occupies
        for wall in self.room_edge_walls:
            wall_corners = wall.get_corners()

            # For each wall corner, check if it matches any external corner exactly
            matched_external_corners = set()

            for wall_corner in wall_corners:
                # Check if wall corner matches any external corner exactly
                for i, ext_corner in enumerate(self.external_corners):
                    # Use math.isclose for floating point comparison
                    if (math.isclose(wall_corner[0], ext_corner[0], abs_tol=1e-9) and
                        math.isclose(wall_corner[1], ext_corner[1], abs_tol=1e-9)):
                        matched_external_corners.add(i)
                        break

            matches = len(matched_external_corners)

            if matches != 2:
                print(f"DEBUG: Wall '{wall.label}' has {matches} corners matching external corners (expected 2)")
                print(f"       Wall corners: {[(f'({c[0]:.3f}, {c[1]:.3f})') for c in wall_corners]}")
                print(f"       External corners: {[(f'({c[0]:.3f}, {c[1]:.3f})') for c in self.external_corners]}")

                raise ValueError(
                    f"Invalid rectangle: Wall '{wall.label}' has {matches} corners matching "
                    f"external rectangle corners (expected exactly 2). "
                    f"Check that the wall connects properly at room corners."
                )

            # Identify wall position based on which external corners it matches
            # Bottom wall: corners 0 (bottom-left) and 1 (bottom-right)
            if matched_external_corners == {0, 1}:
                self.bottom_wall = wall
            # Right wall: corners 1 (bottom-right) and 2 (top-right)
            elif matched_external_corners == {1, 2}:
                self.right_wall = wall
            # Top wall: corners 2 (top-right) and 3 (top-left)
            elif matched_external_corners == {2, 3}:
                self.top_wall = wall
            # Left wall: corners 3 (top-left) and 0 (bottom-left)
            elif matched_external_corners == {0, 3}:
                self.left_wall = wall

        # Verify all walls were identified
        if not all([self.bottom_wall, self.top_wall, self.left_wall, self.right_wall]):
            raise ValueError(
                f"Failed to identify all wall positions. "
                f"Bottom: {self.bottom_wall is not None}, "
                f"Top: {self.top_wall is not None}, "
                f"Left: {self.left_wall is not None}, "
                f"Right: {self.right_wall is not None}"
            )

    def _calculate_properties(self):
        """Calculate room dimensions and areas."""
        # Use external corners already calculated in _validate_corner_alignment
        # external_corners[0] = bottom-left, [1] = bottom-right, [2] = top-right, [3] = top-left
        outer_x_min = self.external_corners[0][0]
        outer_x_max = self.external_corners[1][0]
        outer_y_min = self.external_corners[0][1]
        outer_y_max = self.external_corners[2][1]

        # Calculate outer dimensions
        self.outer_horizontal_length = outer_x_max - outer_x_min
        self.outer_vertical_length = outer_y_max - outer_y_min
        self.outer_area = self.outer_horizontal_length * self.outer_vertical_length

        # Calculate inner bounds
        inner_x_min = outer_x_min + self.left_wall.thickness
        inner_x_max = outer_x_max - self.right_wall.thickness
        inner_y_min = outer_y_min + self.bottom_wall.thickness
        inner_y_max = outer_y_max - self.top_wall.thickness

        # Calculate inner dimensions
        self.inner_horizontal_length = inner_x_max - inner_x_min
        self.inner_vertical_length = inner_y_max - inner_y_min
        self.inner_area = self.inner_horizontal_length * self.inner_vertical_length

        # Internal corners (inner bounds)
        self.internal_corners = [
            (inner_x_min, inner_y_min),  # bottom-left
            (inner_x_max, inner_y_min),  # bottom-right
            (inner_x_max, inner_y_max),  # top-right
            (inner_x_min, inner_y_max)   # top-left
        ]

    def draw(self, ax: matplotlib.axes.Axes) -> None:
        """
        Draw room label and dimensions if options are configured.
        Room walls are drawn separately.
        """

        # Draw room label if label color option is configured
        label_color = get_label_color('Room')
        if label_color is not None and self.label is not None:
            # Calculate position: bottom-left inner corner + offset (0.3, 0.3)
            label_x = self.internal_corners[0][0] + 0.2
            label_y = self.internal_corners[0][1] + 0.2

            # Render the room label
            ax.text(
                label_x,
                label_y,
                self.label,
                fontsize=14,
                color=label_color,
                horizontalalignment='left',
                verticalalignment='bottom'
            )

        # Draw dimensions if dimensions option is configured
        dimensions_enabled = get_element_option('Room', 'dimensions', False)
        if dimensions_enabled:

            # Horizontal dimension: offset from inner bottom edge by 1/5th of inner height
            horizontal_offset = self.inner_vertical_length / 5
            horizontal_anchor = (
                self.internal_corners[0][0],  # bottom-left inner corner x
                self.internal_corners[0][1] + horizontal_offset  # offset up by 1/5th height
            )
            horizontal_dimension = DimensionArrow(
                anchor_point=horizontal_anchor,
                length=self.inner_horizontal_length,
                orientation_angle=0,
                color='black',
                annotate_above=True
            )
            horizontal_dimension.draw(ax)

            # Vertical dimension: offset from inner left edge by 4/5th of inner width
            vertical_offset = self.inner_horizontal_length * 4 / 5
            vertical_anchor = (
                self.internal_corners[0][0] + vertical_offset,  # offset right by 4/5th width
                self.internal_corners[0][1]  # bottom-left inner corner y
            )
            vertical_dimension = DimensionArrow(
                anchor_point=vertical_anchor,
                length=self.inner_vertical_length,
                orientation_angle=90,
                color='black',
                annotate_above=True

            )
            vertical_dimension.draw(ax)

        # Draw inner area if inner_area option is configured
        inner_area_enabled = get_element_option('Room', 'inner_area', False)
        if inner_area_enabled:

            # Calculate center of the room from internal corners
            # internal_corners[0] = bottom-left, internal_corners[2] = top-right
            center_x = (self.internal_corners[0][0] + self.internal_corners[2][0]) / 2
            center_y = (self.internal_corners[0][1] + self.internal_corners[2][1]) / 2

            area_text = f"{round(self.inner_area,1):.1f}m²"

            area_textbox = TextBox(
                anchor_point=(center_x, center_y),
                lines=[area_text],
                font_size=14,
                color='gray',
                edgecolor='none'
            )
            area_textbox.draw(ax)

        # Draw inner corner labels if inner_corner_label_color option is configured
        inner_corner_color = get_element_option('Room', 'inner_corner_label_color')
        if inner_corner_color is not None:
            corner_parameters = [ (45, 'left', 'bottom'), (135, 'right', 'bottom'), (225, 'right', 'top'), (315, 'left', 'top') ]

            for i, corner in enumerate(self.internal_corners):
                label_text = f" ({round(corner[0],2)}, {round(corner[1],2)})"
                ax.text(
                    corner[0],
                    corner[1],
                    label_text,
                    fontsize=6,
                    color=inner_corner_color,
                    rotation=corner_parameters[i][0],
                    horizontalalignment=corner_parameters[i][1],
                    verticalalignment=corner_parameters[i][2]
                 )

        # Draw outer corner labels if outer_corner_label_color option is configured
        outer_corner_color = get_element_option('Room', 'outer_corner_label_color')
        if outer_corner_color is not None:
            corner_parameters = [ (225, 'right', 'top'), (315, 'left', 'top'), (45, 'left', 'bottom'), (135, 'right', 'bottom') ]

            for i, corner in enumerate(self.external_corners):
                label_text = f" ({round(corner[0],2)}, {round(corner[1],2)})"
                ax.text(
                    corner[0],
                    corner[1],
                    label_text,
                    fontsize=6,
                    color=outer_corner_color,
                    rotation=corner_parameters[i][0],
                    horizontalalignment=corner_parameters[i][1],
                    verticalalignment=corner_parameters[i][2]
                )
