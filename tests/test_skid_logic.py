import pytest
from autocrate.skid_logic import calculate_skid_lumber_properties, calculate_skid_layout

# Test cases for calculate_skid_lumber_properties
# Each tuple contains: (product_weight, allow_3x4_skids, expected_lumber_callout)
skid_properties_test_cases = [
    (400, True, "3x4"),
    (500, True, "3x4"),
    (501, True, "4x4"),
    (4500, False, "4x4"),
    (4501, False, "4x6"),
    (6000, False, "4x6"),
    (12001, False, "4x6"),
    (20001, False, "6x6"),
    (30001, False, "6x6"),
    (40001, False, "8x8"),
    (70000, False, "8x8"), # Test fallback for very high weight
    (501, False, "4x4"), # Test case where 3x4 is not allowed
]

@pytest.mark.parametrize("product_weight, allow_3x4, expected_callout", skid_properties_test_cases)
def test_calculate_skid_lumber_properties(product_weight, allow_3x4, expected_callout):
    """
    Tests that the correct skid lumber callout is returned for various weights.
    """
    result = calculate_skid_lumber_properties(product_weight, allow_3x4)
    assert result["lumber_callout"] == expected_callout

# Test cases for calculate_skid_layout
# Each tuple contains: (crate_width, skid_width, max_spacing, expected_count, expected_pitch)
skid_layout_test_cases = [
    (100, 3.5, 30, 5, 24.125),
    (48, 3.5, 30, 3, 22.25),
    (124, 5.5, 23.7, 6, 23.7), # From an example .exp file
    (50, 2.5, 30, 3, 23.75),
    (90, 5.5, 28, 5, 21.125),
]

@pytest.mark.parametrize("crate_width, skid_width, max_spacing, expected_count, expected_pitch", skid_layout_test_cases)
def test_calculate_skid_layout(crate_width, skid_width, max_spacing, expected_count, expected_pitch):
    """
    Tests the skid layout calculation for count and pitch.
    """
    result = calculate_skid_layout(crate_width, skid_width, max_spacing)
    assert result["calc_skid_count"] == expected_count
    assert result["calc_skid_pitch_in"] == pytest.approx(expected_pitch, rel=1e-3)
