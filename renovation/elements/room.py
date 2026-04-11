"""
Room element composed of 4 walls forming a rectangle.

Author: Krzysztof Bartczak
"""


import math
import matplotlib.axes

from .element import Element


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
        from renovation.elements.options import get_id_color,get_label_color, get_element_option

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
            from renovation.elements.info import DimensionArrow

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
            from renovation.elements.info import TextBox

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
