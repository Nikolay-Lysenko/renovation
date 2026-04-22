"""
Define mixins that calculate anchor points of an element.

Here, anchor means a point that affects dependent elements.

Author: Nikolay Lysenko
"""


from typing import Optional

from renovation.constants import RIGHT_ANGLE_IN_DEGREES
from renovation.utils import shift_in_direction


class PivotAnchorMixin:
    """Mixin that provides single anchor at the pivot point."""

    def calculate_anchor_coordinates(
            self, anchor_type: Optional[str] = None
    ) -> tuple[float, float]:
        """
        Calculate coordinates of a point that can be used as anchor for other elements.

        :param anchor_type:
            any string or `None`; it is not used at all
        :return:
            coordinates of the anchor point
        """
        return self.pivot_point


class CornerAnchorsMixin:
    """Mixin that provides anchors at the four corners of a rectangular object."""

    def calculate_anchor_coordinates(self, anchor_type: str) -> tuple[float, float]:
        """
        Calculate coordinates of a point that can be used as anchor for other elements.

        :param anchor_type:
            one of:
            * 'corner_one' (the pivot point),
            * 'corner_two' (the next corner in the counterclockwise direction),
            * 'corner_three' (the corner after the next one in the counterclockwise direction),
            * 'corner_four' (the next corner in the clockwise direction)
        :return:
            coordinates of the anchor point
        """
        if anchor_type == "corner_one":
            return self.pivot_point
        elif anchor_type == "corner_two":
            return shift_in_direction(self.pivot_point, self.length, self.orientation_angle)
        elif anchor_type == "corner_three":
            return shift_in_direction(
                shift_in_direction(self.pivot_point, self.length, self.orientation_angle),
                self.thickness,
                self.orientation_angle + RIGHT_ANGLE_IN_DEGREES
            )
        elif anchor_type == "corner_four":
            return shift_in_direction(
                self.pivot_point,
                self.overall_thickness,
                self.orientation_angle + RIGHT_ANGLE_IN_DEGREES
            )
        else:
            raise ValueError(
                f"Anchor type '{anchor_type}' is not supported by `{type(self)}` class."
            )
