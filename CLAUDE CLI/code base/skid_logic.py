import math

def calculate_skid_lumber_properties(
    product_weight_lbs: float,
    allow_3x4_skids_bool: bool
) -> dict:
    """
    Determines the physical properties of the skid lumber based on product weight.
    """
    skid_actual_height_in: float
    skid_actual_width_in: float
    lumber_callout: str
    max_skid_spacing_rule_in: float

    # 3x4 Skids
    if allow_3x4_skids_bool and product_weight_lbs < 501:
        skid_actual_height_in = 3.5
        skid_actual_width_in = 2.5
        lumber_callout = "3x4"
        max_skid_spacing_rule_in = 30.0
    
    # 4x4 Skids
    elif 501 <= product_weight_lbs <= 4500:
        skid_actual_height_in = 3.5
        skid_actual_width_in = 3.5
        lumber_callout = "4x4"
        max_skid_spacing_rule_in = 30.0

    # 4x6 Skids
    elif 4501 <= product_weight_lbs <= 20000:
        skid_actual_height_in = 3.5
        skid_actual_width_in = 5.5
        lumber_callout = "4x6"
        if product_weight_lbs < 6000:
            max_skid_spacing_rule_in = 41.0
        elif 6000 <= product_weight_lbs <= 12000:
            max_skid_spacing_rule_in = 28.0
        else: # 12,001 to 20,000 lbs
            max_skid_spacing_rule_in = 24.0

    # 6x6 Skids
    elif 20001 <= product_weight_lbs <= 40000:
        skid_actual_height_in = 5.5
        skid_actual_width_in = 5.5
        lumber_callout = "6x6"
        if product_weight_lbs <= 30000:
            max_skid_spacing_rule_in = 24.0
        else: # 30,001 to 40,000 lbs
            max_skid_spacing_rule_in = 20.0

    # 8x8 Skids
    elif 40001 <= product_weight_lbs <= 60000:
        skid_actual_height_in = 7.5
        skid_actual_width_in = 7.5
        lumber_callout = "8x8"
        max_skid_spacing_rule_in = 24.0
        
    # Fallback for weights outside the defined ranges
    else:
        skid_actual_height_in = 7.5
        skid_actual_width_in = 7.5
        lumber_callout = "8x8"
        max_skid_spacing_rule_in = 24.0

    return {
        "skid_actual_height_in": skid_actual_height_in,
        "skid_actual_width_in": skid_actual_width_in,
        "lumber_callout": lumber_callout,
        "max_skid_spacing_rule_in": max_skid_spacing_rule_in,
    }

def calculate_skid_layout(
    crate_overall_width_od_in: float,
    skid_actual_width_in: float,
    max_skid_spacing_rule_in: float
) -> dict:
    """
    Calculates the count and pitch of skids based on the final crate width.
    """
    # Determine skid count (always >= 2)
    span_for_skids_centerlines = crate_overall_width_od_in - skid_actual_width_in
    
    if span_for_skids_centerlines <= 0: 
        calc_skid_count = 2 
    else:
        num_gaps = math.ceil(span_for_skids_centerlines / max_skid_spacing_rule_in)
        if num_gaps == 0:
            num_gaps = 1
        calc_skid_count = num_gaps + 1

    if calc_skid_count < 2:
        calc_skid_count = 2
        
    if (calc_skid_count - 1) == 0:
        calc_skid_pitch_in = 0.0
    else:
        calc_skid_pitch_in = (crate_overall_width_od_in - skid_actual_width_in) / (calc_skid_count - 1)

    # Determine skid X-positions based on centered crate origin
    x_master_skid_origin_offset_in = -crate_overall_width_od_in / 2.0
    calc_first_skid_pos_x_in = x_master_skid_origin_offset_in + (skid_actual_width_in / 2.0)

    return {
        "calc_skid_count": calc_skid_count,
        "calc_skid_pitch_in": calc_skid_pitch_in,
        "calc_first_skid_pos_x_in": calc_first_skid_pos_x_in,
        "x_master_skid_origin_offset_in": x_master_skid_origin_offset_in,
    }