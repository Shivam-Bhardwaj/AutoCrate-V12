import math
from typing import List, Dict

def calculate_floorboard_layout(
    fb_usable_coverage_y_in: float,
    fb_initial_start_y_offset_abs: float,
    selected_std_lumber_widths: List[float],
    min_custom_lumber_width_in: float,
    force_small_custom_board_bool: bool,
) -> Dict:
    """
    Calculates the layout of floorboards based on available space and lumber.

    Args:
        fb_usable_coverage_y_in: The total length to be covered by floorboards.
        fb_initial_start_y_offset_abs: The starting position of the first board.
        selected_std_lumber_widths: A list of available standard lumber widths.
        min_custom_lumber_width_in: The minimum width for a custom board.
        force_small_custom_board_bool: If true, any remainder becomes a custom board.

    Returns:
        A dictionary containing the list of floorboards with their positions,
        the calculated middle gap, and the width of any custom board.
    """
    sorted_std_lumber_widths_available = sorted(selected_std_lumber_widths, reverse=True)

    # Step 1: Greedily select standard lumber pieces
    standard_lumber_pieces = []
    y_remaining_for_lumber = fb_usable_coverage_y_in
    for std_w in sorted_std_lumber_widths_available:
        if y_remaining_for_lumber >= std_w:
            num_boards_of_this_width = math.floor(y_remaining_for_lumber / std_w)
            if num_boards_of_this_width > 0:
                standard_lumber_pieces.extend([std_w] * num_boards_of_this_width)
                y_remaining_for_lumber -= num_boards_of_this_width * std_w

    # Step 2: Determine if the remaining space is a custom board or a gap
    center_custom_board_width = 0.0
    actual_middle_gap = 0.0
    if y_remaining_for_lumber > 0.001:  # If there is any remaining space
        if force_small_custom_board_bool:
            # If forcing, the entire remainder is a custom board.
            center_custom_board_width = y_remaining_for_lumber
        else:
            # Otherwise, check against the minimum custom width.
            if y_remaining_for_lumber >= min_custom_lumber_width_in:
                center_custom_board_width = y_remaining_for_lumber
            else:
                actual_middle_gap = y_remaining_for_lumber

    # Step 3: Assemble the final board layout with the custom board in the center
    final_board_layout = list(standard_lumber_pieces)
    if center_custom_board_width > 0.001:
        insertion_point = math.ceil(len(final_board_layout) / 2)
        final_board_layout.insert(insertion_point, center_custom_board_width)

    # Step 4: Calculate board positions and insert the gap in the center
    floorboards_data = []
    current_y_pos = fb_initial_start_y_offset_abs
    num_boards = len(final_board_layout)
    gap_insertion_index = -1

    if actual_middle_gap > 0.001:
        gap_insertion_index = math.ceil(num_boards / 2.0) - 1

    for i, board_w_val in enumerate(final_board_layout):
        floorboards_data.append({'width': board_w_val, 'y_pos': current_y_pos})
        current_y_pos += board_w_val
        if i == gap_insertion_index:
            current_y_pos += actual_middle_gap
            
    return {
        "floorboards_data": floorboards_data,
        "actual_middle_gap": actual_middle_gap,
        "center_custom_board_width": center_custom_board_width,
    }
