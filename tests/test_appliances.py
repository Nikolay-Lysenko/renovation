"""Test home appliance elements."""


import matplotlib.colors
import matplotlib.pyplot as plt
import pytest

from renovation.elements import Fridge, create_elements_registry


def test_fridge_draws_rotated_outline_and_label() -> None:
    """Test drawing a fridge and rotating its label with the footprint."""
    fridge = Fridge(
        pivot_point=(1.0, 2.0),
        width=0.8,
        depth=0.6,
        orientation_angle=90,
        line_width=1.25,
        font_size=12,
        color='red'
    )
    fig, ax = plt.subplots()
    try:
        fridge.draw(ax)

        assert len(ax.patches) == 1
        outline = ax.patches[0]
        assert outline.get_xy() == (1.0, 2.0)
        assert outline.get_width() == pytest.approx(0.8)
        assert outline.get_height() == pytest.approx(0.6)
        assert outline.angle == pytest.approx(90)
        assert not outline.get_fill()
        assert outline.get_edgecolor() == matplotlib.colors.to_rgba('red')
        assert outline.get_linewidth() == pytest.approx(1.25)

        assert len(ax.texts) == 1
        label = ax.texts[0]
        assert label.get_text() == "FR"
        assert label.get_position() == pytest.approx((0.7, 2.4))
        assert label.get_rotation() == pytest.approx(90)
        assert label.get_fontsize() == pytest.approx(12)
        assert label.get_color() == 'red'
    finally:
        plt.close(fig)


def test_fridge_provides_rotated_corner_anchors() -> None:
    """Test fridge corner anchors used to position dependent elements."""
    fridge = Fridge(
        pivot_point=(1.0, 2.0), width=0.8, depth=0.6, orientation_angle=90
    )

    assert fridge.calculate_anchor_coordinates('corner_one') == pytest.approx((1.0, 2.0))
    assert fridge.calculate_anchor_coordinates('corner_two') == pytest.approx((1.0, 2.8))
    assert fridge.calculate_anchor_coordinates('corner_three') == pytest.approx((0.4, 2.8))
    assert fridge.calculate_anchor_coordinates('corner_four') == pytest.approx((0.4, 2.0))


@pytest.mark.parametrize("width, depth", [(0, 0.6), (0.8, 0), (-0.8, 0.6), (0.8, -0.6)])
def test_fridge_rejects_non_positive_dimensions(width: float, depth: float) -> None:
    """Test that a fridge requires meaningful physical dimensions."""
    with pytest.raises(ValueError, match="Fridge width and depth must be positive"):
        Fridge(pivot_point=(0, 0), width=width, depth=depth)


def test_fridge_is_available_in_elements_registry() -> None:
    """Test that YAML projects can resolve the fridge element."""
    assert create_elements_registry()['fridge'] is Fridge
