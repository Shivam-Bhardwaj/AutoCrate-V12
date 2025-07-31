import pytest
from autocrate.floorboard_logic import calculate_floorboard_layout

# Standard available lumber widths for tests
STD_LUMBER = [11.25, 9.25, 7.25, 5.5]

# Test cases for calculate_floorboard_layout
# Each tuple contains: (
#   usable_coverage, start_offset, lumber_widths, min_custom_width, force_custom,
#   expected_gap, expected_custom_width, expected_board_widths
# )
floorboard_layout_test_cases = [
    # Case 1: Exact fit, no gap or custom board
    (22.5, 1.0, STD_LUMBER, 2.5, False, 0.0, 0.0, [11.25, 11.25]),
    
    # Case 2: Small remainder, should become a gap
    (23.0, 1.0, STD_LUMBER, 2.5, False, 0.5, 0.0, [11.25, 11.25]),
    
    # Case 3: Large remainder, should become a custom board
    (26.0, 1.0, STD_LUMBER, 2.5, False, 0.0, 3.5, [11.25, 3.5, 11.25]),
    
    # Case 4: Small remainder, but forced to be a custom board
    (23.0, 1.0, STD_LUMBER, 2.5, True, 0.0, 0.5, [11.25, 0.5, 11.25]),
    
    # Case 5: Complex layout resulting in a small gap
    (42.0, 2.0, STD_LUMBER, 2.5, False, 1.0, 0.0, [11.25, 11.25, 11.25, 7.25]),

    # Case 6: No standard boards fit, results in one large custom board
    (5.0, 1.0, STD_LUMBER, 2.5, False, 0.0, 5.0, [5.0]),
]

@pytest.mark.parametrize(
    "usable_coverage, start_offset, lumber_widths, min_custom_width, force_custom, "
    "expected_gap, expected_custom_width, expected_board_widths",
    floorboard_layout_test_cases
)
def test_calculate_floorboard_layout(
    usable_coverage, start_offset, lumber_widths, min_custom_width, force_custom,
    expected_gap, expected_custom_width, expected_board_widths
):
    """
    Tests the floorboard layout calculation for various scenarios.
    """
    result = calculate_floorboard_layout(
        fb_usable_coverage_y_in=usable_coverage,
        fb_initial_start_y_offset_abs=start_offset,
        selected_std_lumber_widths=lumber_widths,
        min_custom_lumber_width_in=min_custom_width,
        force_small_custom_board_bool=force_custom
    )

    # Verify the gap and custom board calculations
    assert result["actual_middle_gap"] == pytest.approx(expected_gap)
    assert result["center_custom_board_width"] == pytest.approx(expected_custom_width)

    # Verify the number of boards and their widths
    board_widths = [board['width'] for board in result['floorboards_data']]
    assert board_widths == pytest.approx(expected_board_widths)

    # Verify the positioning of the boards
    expected_y_pos = start_offset
    gap_inserted = False
    for i, board in enumerate(result['floorboards_data']):
        assert board['y_pos'] == pytest.approx(expected_y_pos)
        expected_y_pos += board['width']
        
        # Check if the gap should be inserted after this board
        if expected_gap > 0 and not gap_inserted:
            num_boards = len(expected_board_widths)
            gap_insertion_index = pytest.approx((num_boards / 2.0) - 1)
            if i == gap_insertion_index:
                expected_y_pos += expected_gap
                gap_inserted = True
