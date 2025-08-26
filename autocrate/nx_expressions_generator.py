import datetime
import math
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import traceback # Added for robust error handling
import sys
import os

# Setup proper import path for PyInstaller and development
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Initialize logging system
try:
    from debug_logger import get_logger, debug_function, finalize_logging
    logger = get_logger("AutoCrate.NX_Generator")
    logger.info("NX Expressions Generator module loading...")
    
    # Run startup analysis
    try:
        from startup_analyzer import run_startup_analysis
        startup_result = run_startup_analysis(enable_console_output=True)
        if logger and startup_result.get('status') != 'no_sessions':
            logger.info("Startup analysis completed", {
                'previous_run_status': startup_result.get('status'),
                'previous_errors': startup_result.get('errors', 0),
                'previous_warnings': startup_result.get('warnings', 0)
            })
    except ImportError:
        if logger:
            logger.debug("Startup analyzer not available")
    except Exception as e:
        if logger:
            logger.warning(f"Startup analysis failed: {e}")
        
except ImportError as e:
    print(f"Warning: Debug logging not available: {e}")
    logger = None

# Import all required modules with robust error handling
if logger:
    logger.info("Starting module imports...", {'current_dir': current_dir})

try:
    # Try absolute imports with autocrate package first
    if logger:
        logger.debug("Attempting absolute imports with autocrate package...")
    from autocrate.front_panel_logic import calculate_front_panel_components
    from autocrate.back_panel_logic import calculate_back_panel_components
    from autocrate.end_panel_logic import calculate_end_panel_components
    from autocrate.top_panel_logic import calculate_top_panel_components
    from autocrate.skid_logic import calculate_skid_lumber_properties, calculate_skid_layout
    from autocrate.left_panel_logic import calculate_left_panel_components
    from autocrate.right_panel_logic import calculate_right_panel_components
    from autocrate.floorboard_logic import calculate_floorboard_layout
    from autocrate.plywood_layout_generator import calculate_layout as calculate_plywood_layout
    from autocrate.security_utils import validate_output_path, sanitize_filename, validate_numeric_input, create_secure_directory, is_safe_file_extension
    if logger:
        logger.info("Absolute imports with autocrate package successful")
except ImportError as e:
    if logger:
        logger.warning(f"Absolute import with package failed: {e}")
    try:
        # Try relative imports (when used as a module)
        if logger:
            logger.debug("Attempting relative imports...")
        from .front_panel_logic import calculate_front_panel_components
        from .back_panel_logic import calculate_back_panel_components
        from .end_panel_logic import calculate_end_panel_components
        from .top_panel_logic import calculate_top_panel_components
        from .skid_logic import calculate_skid_lumber_properties, calculate_skid_layout
        from .left_panel_logic import calculate_left_panel_components
        from .right_panel_logic import calculate_right_panel_components
        from .floorboard_logic import calculate_floorboard_layout
        from .plywood_layout_generator import calculate_layout as calculate_plywood_layout
        from .security_utils import validate_output_path, sanitize_filename, validate_numeric_input, create_secure_directory, is_safe_file_extension
        if logger:
            logger.info("Relative imports successful")
    except ImportError as e2:
        if logger:
            logger.warning(f"Relative import failed: {e2}")
        try:
            # Fall back to direct imports (when run as a script or PyInstaller)
            if logger:
                logger.debug("Attempting direct imports...")
            from front_panel_logic import calculate_front_panel_components
            from back_panel_logic import calculate_back_panel_components
            from end_panel_logic import calculate_end_panel_components
            from top_panel_logic import calculate_top_panel_components
            from skid_logic import calculate_skid_lumber_properties, calculate_skid_layout
            from left_panel_logic import calculate_left_panel_components
            from right_panel_logic import calculate_right_panel_components
            from floorboard_logic import calculate_floorboard_layout
            from plywood_layout_generator import calculate_layout as calculate_plywood_layout
            from security_utils import validate_output_path, sanitize_filename, validate_numeric_input, create_secure_directory, is_safe_file_extension
            if logger:
                logger.info("Direct imports successful")
        except ImportError as e3:
            error_msg = f"Could not import required modules. Package import error: {e}, Relative import error: {e2}, Direct import error: {e3}"
            debug_info = {
                'current_dir': current_dir,
                'parent_dir': parent_dir,
                'python_path': sys.path[:5],  # First 5 entries
                'available_files': os.listdir(current_dir) if os.path.exists(current_dir) else []
            }
            
            if logger:
                logger.critical(error_msg, e3, debug_info)
            else:
                print(f"All import methods failed: {e3}")
                print(f"Current directory: {current_dir}")
                print(f"Parent directory: {parent_dir}")
                print(f"Python path: {sys.path[:5]}")
            
            raise ImportError(error_msg)
from typing import List, Dict, Tuple

# --- Default Constants ---
DEFAULT_AVAILABLE_STD_LUMBER_WIDTHS = { 
    "2x6 (5.5 in)": 5.5, "2x8 (7.25 in)": 7.25,
    "2x10 (9.25 in)": 9.25, "2x12 (11.25 in)": 11.25
}
DEFAULT_MIN_CUSTOM_LUMBER_WIDTH = 2.5


DEFAULT_MAX_ALLOWABLE_MIDDLE_GAP = 0.25
MIN_FORCEABLE_CUSTOM_BOARD_WIDTH = 0.25 
MAX_NX_FLOORBOARD_INSTANCES = 20
MAX_FP_INTERMEDIATE_VERTICAL_CLEATS = 7 # Max instances for Front Panel Intermediate Vertical Cleats
MAX_FP_INTERMEDIATE_HORIZONTAL_CLEATS = 6 # Max instances for Front Panel Intermediate Horizontal Cleats
MAX_BP_INTERMEDIATE_VERTICAL_CLEATS = 7 # Added for Back Panel
MAX_BP_INTERMEDIATE_HORIZONTAL_CLEATS = 6 # Max instances for Back Panel Intermediate Horizontal Cleats
MAX_EP_INTERMEDIATE_VERTICAL_CLEATS = 5 # Placeholder, adjust as needed
MAX_TP_INTERMEDIATE_CLEATS = 7 # Set to 7 to match user requirement
MAX_TP_INTERMEDIATE_HORIZONTAL_CLEATS = 6 # Max instances for Top Panel Intermediate Horizontal Cleats
DEFAULT_CLEAT_MEMBER_WIDTH = 3.5 # Added default for cleat member width
MAX_LP_INTERMEDIATE_VERTICAL_CLEATS = 7  # Added for Left Panel
MAX_LP_INTERMEDIATE_HORIZONTAL_CLEATS = 6 # Max instances for Left Panel Intermediate Horizontal Cleats
MAX_RP_INTERMEDIATE_VERTICAL_CLEATS = 7  # Added for Right Panel
MAX_RP_INTERMEDIATE_HORIZONTAL_CLEATS = 6 # Max instances for Right Panel Intermediate Horizontal Cleats

# --- Klimp Constants ---
MAX_FRONT_PANEL_KLIMPS = 12  # Maximum number of klimp instances available in NX
DEFAULT_KLIMP_DIAMETER = 1.0  # Default klimp diameter in inches

# --- Plywood Layout Constants ---
MAX_PLYWOOD_DIMS = (96, 48)  # inches (width, height)
MAX_PLYWOOD_INSTANCES = 10   # Maximum number of plywood instances available in NX

# --- Plywood Layout Functions ---
def calculate_plywood_layout(panel_width: float, panel_height: float) -> List[Dict]:
    """
    Calculate the optimal layout of plywood sheets for the given panel dimensions.
    
    Args:
        panel_width: Width of the panel in inches
        panel_height: Height of the panel in inches
        
    Returns:
        List of dictionaries containing position and dimensions of each plywood sheet
    """
    # Determine how many sheets needed in each direction
    sheets_across = math.ceil(panel_width / MAX_PLYWOOD_DIMS[0])
    sheets_down = math.ceil(panel_height / MAX_PLYWOOD_DIMS[1])
    
    # Calculate total sheets needed for horizontal and vertical arrangements
    horizontal_priority_count = sheets_across * sheets_down
    
    # Try vertical arrangement (rotate sheets 90 degrees)
    rotated_sheets_across = math.ceil(panel_width / MAX_PLYWOOD_DIMS[1])
    rotated_sheets_down = math.ceil(panel_height / MAX_PLYWOOD_DIMS[0])
    vertical_priority_count = rotated_sheets_across * rotated_sheets_down
    
    # Choose the arrangement with fewer sheets, preferring vertical splices if tied
    sheets = []
    
    if vertical_priority_count <= horizontal_priority_count:
        # Use vertical arrangement (rotated sheets)
        # Calculate remainder height for splice positioning
        total_full_rows = rotated_sheets_down - 1
        remainder_height = panel_height - (total_full_rows * MAX_PLYWOOD_DIMS[0])
        
        for row in range(rotated_sheets_down):
            for col in range(rotated_sheets_across):
                x_pos = col * MAX_PLYWOOD_DIMS[1]
                
                # Reverse the row order: put smaller panels at bottom (row 0), larger panels at top
                if rotated_sheets_down > 1:
                    if row == 0:
                        # Bottom row: use remainder height (smaller)
                        y_pos = 0
                        sheet_height = min(remainder_height, panel_height)
                    else:
                        # Upper rows: use full sheet height (larger)
                        y_pos = remainder_height + (row - 1) * MAX_PLYWOOD_DIMS[0]
                        sheet_height = min(MAX_PLYWOOD_DIMS[0], panel_height - y_pos)
                else:
                    # Single row case - no change needed
                    y_pos = row * MAX_PLYWOOD_DIMS[0]
                    sheet_height = min(MAX_PLYWOOD_DIMS[0], panel_height - y_pos)
                
                # Calculate actual sheet width (may be smaller at edges)
                sheet_width = min(MAX_PLYWOOD_DIMS[1], panel_width - x_pos)
                
                # Only add if the sheet has positive dimensions
                if sheet_width > 0 and sheet_height > 0:
                    sheets.append({
                        'x': x_pos,
                        'y': y_pos,
                        'width': sheet_width,
                        'height': sheet_height
                    })
    else:
        # Use horizontal arrangement (standard orientation)
        # Calculate remainder height for splice positioning
        total_full_rows = sheets_down - 1
        remainder_height = panel_height - (total_full_rows * MAX_PLYWOOD_DIMS[1])
        
        for row in range(sheets_down):
            for col in range(sheets_across):
                x_pos = col * MAX_PLYWOOD_DIMS[0]
                
                # Reverse the row order: put smaller panels at bottom (row 0), larger panels at top
                if sheets_down > 1:
                    if row == 0:
                        # Bottom row: use remainder height (smaller)
                        y_pos = 0
                        sheet_height = min(remainder_height, panel_height)
                    else:
                        # Upper rows: use full sheet height (larger)
                        y_pos = remainder_height + (row - 1) * MAX_PLYWOOD_DIMS[1]
                        sheet_height = min(MAX_PLYWOOD_DIMS[1], panel_height - y_pos)
                else:
                    # Single row case - no change needed
                    y_pos = row * MAX_PLYWOOD_DIMS[1]
                    sheet_height = min(MAX_PLYWOOD_DIMS[1], panel_height - y_pos)
                
                # Calculate actual sheet width (may be smaller at edges)
                sheet_width = min(MAX_PLYWOOD_DIMS[0], panel_width - x_pos)
                
                # Only add if the sheet has positive dimensions
                if sheet_width > 0 and sheet_height > 0:
                    sheets.append({
                        'x': x_pos,
                        'y': y_pos,
                        'width': sheet_width,
                        'height': sheet_height
                    })
    
    return sheets

def generate_plywood_nx_expressions(sheets: List[Dict], panel_prefix: str = "") -> List[str]:
    """
    Generate NX expression statements for the calculated sheet layout.
    
    Args:
        sheets: List of sheet dictionaries with position and dimensions
        panel_prefix: Prefix for variable names (e.g., "FP_", "BP_")
        
    Returns:
        List of NX expression statements as strings
    """
    expressions = []
    
    # Set values for used plywood instances
    for i, sheet in enumerate(sheets[:MAX_PLYWOOD_INSTANCES]):
        instance_num = i + 1
        expressions.append(f'{panel_prefix}Plywood_{instance_num}_Active = 1')
        expressions.append(f'{panel_prefix}Plywood_{instance_num}_X_Position = {sheet["x"]}')
        expressions.append(f'{panel_prefix}Plywood_{instance_num}_Y_Position = {sheet["y"]}')
        expressions.append(f'{panel_prefix}Plywood_{instance_num}_Width = {sheet["width"]}')
        expressions.append(f'{panel_prefix}Plywood_{instance_num}_Height = {sheet["height"]}')
    
    # Set remaining unused instances to inactive
    for i in range(len(sheets), MAX_PLYWOOD_INSTANCES):
        instance_num = i + 1
        expressions.append(f'{panel_prefix}Plywood_{instance_num}_Active = 0')
    
    return expressions

def generate_crate_expressions_logic(
    # Skid Inputs
    product_weight_lbs: float, product_length_in: float, product_width_in: float,
    clearance_each_side_in: float, allow_3x4_skids_bool: bool,
    # General Crate & Panel Inputs
    panel_thickness_in: float, cleat_thickness_in: float, cleat_member_actual_width_in: float, # Added cleat_member_actual_width_in
    product_actual_height_in: float, 
    clearance_above_product_in: float,
    ground_clearance_in: float,
    # Floorboard Inputs
    floorboard_actual_thickness_in: float, selected_std_lumber_widths: list[float], 
    max_allowable_middle_gap_in: float, min_custom_lumber_width_in: float,
    force_small_custom_board_bool: bool, 
    # Output
    output_filename: str,
    # Plywood Panel Selections
    plywood_panel_selections: dict = None
) -> tuple[bool, str]:
    import time
    start_time = time.time()
    
    # Log function entry with parameters
    if logger:
        input_params = {
            'product_weight_lbs': product_weight_lbs,
            'product_length_in': product_length_in,
            'product_width_in': product_width_in,
            'clearance_each_side_in': clearance_each_side_in,
            'allow_3x4_skids_bool': allow_3x4_skids_bool,
            'panel_thickness_in': panel_thickness_in,
            'output_filename': output_filename
        }
        logger.info("Starting crate expression generation", input_params)
    
    try:
        # --- Input Validations ---
        if product_weight_lbs < 0: 
            return False, "Product weight cannot be negative."
        if product_length_in <=0: 
            return False, "Product length must be positive."
        if product_width_in <=0: 
            return False, "Product width must be positive."
        if clearance_each_side_in < 0: 
            return False, "Side clearance cannot be negative."
        if panel_thickness_in <=0: 
            return False, "Panel thickness must be positive."
        if cleat_thickness_in <0: # Allow 0 for no cleats, though logic might need adjustment
            return False, "Cleat thickness cannot be negative."
        if cleat_member_actual_width_in <=0: 
            return False, "Cleat member actual width must be positive."
        if product_actual_height_in <=0: 
            return False, "Product actual height must be positive."
        if clearance_above_product_in <0: 
            return False, "Clearance above product cannot be negative."
        if ground_clearance_in <0: 
            return False, "Ground clearance cannot be negative."
        if floorboard_actual_thickness_in <=0: 
            return False, "Floorboard actual thickness must be positive."
        if not selected_std_lumber_widths: 
            return False, "At least one standard lumber width must be selected/available."
        if max_allowable_middle_gap_in < 0: 
            return False, "Max allowable middle gap cannot be negative."
        if min_custom_lumber_width_in <= 0: 
            return False, "Minimum custom lumber width must be positive."
        if min_custom_lumber_width_in < MIN_FORCEABLE_CUSTOM_BOARD_WIDTH and force_small_custom_board_bool:
            return False, f"If forcing small custom board, the 'Minimum Custom Lumber Width' ({min_custom_lumber_width_in}\") must be >= 'Min Forceable Width' ({MIN_FORCEABLE_CUSTOM_BOARD_WIDTH}\")."
             

        # This must be calculated first, as it's passed into the skid logic
        crate_overall_width_od_in = product_width_in + (2 * clearance_each_side_in)

        # === SKID LUMBER PROPERTIES (STEP 1) ===
        skid_props = calculate_skid_lumber_properties(
            product_weight_lbs=product_weight_lbs,
            allow_3x4_skids_bool=allow_3x4_skids_bool
        )
        skid_actual_height_in = skid_props["skid_actual_height_in"]
        skid_actual_width_in = skid_props["skid_actual_width_in"]
        lumber_callout = skid_props["lumber_callout"]
        max_skid_spacing_rule_in = skid_props["max_skid_spacing_rule_in"]

        # === INITIAL CRATE DIMENSIONS (STEP 2) ===
        crate_overall_width_od_in = product_width_in + (2 * clearance_each_side_in)
        skid_model_length_in = product_length_in + (2 * clearance_each_side_in) # Skids run along Y
        crate_overall_length_od_in = skid_model_length_in
        
        # === PANEL BOUNDING BOX CALCULATIONS (Corrected Assembly Logic) ===
        panel_assembly_overall_thickness = panel_thickness_in + cleat_thickness_in 
        
        # Front/Back panels have a depth/thickness
        front_panel_calc_depth = panel_assembly_overall_thickness
        back_panel_calc_depth = panel_assembly_overall_thickness
        
        # End Panels are sandwiched between Front and Back
        end_panel_calc_length = crate_overall_length_od_in - front_panel_calc_depth - back_panel_calc_depth
        end_panel_calc_height_base = floorboard_actual_thickness_in + product_actual_height_in + clearance_above_product_in
        # End panel height should extend from ground clearance to top of crate
        # Height = skid_height + floorboard_thickness + product_height + clearance_above - ground_clearance
        end_panel_calc_height = skid_actual_height_in + floorboard_actual_thickness_in + product_actual_height_in + clearance_above_product_in - ground_clearance_in
        end_panel_calc_depth = panel_assembly_overall_thickness
        
        # Front/Back panel width calculation:
        # Base width = product_width + 2 * side_clearance  
        # Extension = 2 * panel_thickness (cleat_thickness + plywood_thickness) to cover left/right panels
        panel_total_thickness = cleat_thickness_in + panel_thickness_in
        front_panel_calc_width = product_width_in + (2 * clearance_each_side_in) + (2 * panel_total_thickness)
        front_panel_calc_height = end_panel_calc_height_base 
        
        # Back Panel Assy (Same as Front for now, component details can be separated later if different)
        back_panel_calc_width = front_panel_calc_width
        back_panel_calc_height = front_panel_calc_height
        
        # Top Panel Assy (covers all vertical panels)
        top_panel_calc_width = front_panel_calc_width 
        top_panel_calc_length = crate_overall_length_od_in
        top_panel_calc_depth = panel_assembly_overall_thickness

        # === VERTICAL CLEAT MATERIAL CALCULATIONS ===
        # Step 1: Front/Back Panels (identical) - Calculate material needed for vertical cleat spacing
        front_back_material_needed = calculate_vertical_cleat_material_needed(
            front_panel_calc_width, front_panel_calc_height, cleat_member_actual_width_in
        )
        
        # Add material to front/back panels and update crate width
        front_panel_calc_width += front_back_material_needed
        back_panel_calc_width += front_back_material_needed
        crate_overall_width_od_in += front_back_material_needed
        
        # Step 2: Left/Right Panels - Calculate material needed for vertical cleat spacing
        
        # Calculate material needed based on current end panel dimensions
        left_right_material_needed = calculate_vertical_cleat_material_needed(
            end_panel_calc_length, end_panel_calc_height, cleat_member_actual_width_in
        )
        
        # If material is needed, expand the crate and recalculate dimensions
        if left_right_material_needed > 0:
            # Add material to overall crate length 
            crate_overall_length_od_in += left_right_material_needed
            
            # Update end panel length after material addition
            end_panel_calc_length = crate_overall_length_od_in - front_panel_calc_depth - back_panel_calc_depth
        
        # Step 3: Update top panel dimensions with new crate dimensions
        top_panel_calc_width = front_panel_calc_width
        top_panel_calc_length = crate_overall_length_od_in
        
        # Step 4: Top Panel - Calculate material needed for vertical cleats in both directions
        top_width_material_needed = calculate_vertical_cleat_material_needed(
            top_panel_calc_width, top_panel_calc_length, cleat_member_actual_width_in
        )
        top_length_material_needed = calculate_vertical_cleat_material_needed(
            top_panel_calc_length, top_panel_calc_width, cleat_member_actual_width_in
        )
        
        # Apply top panel material additions (cascades to other panels)
        if top_width_material_needed > 0:
            front_panel_calc_width += top_width_material_needed
            back_panel_calc_width += top_width_material_needed
            crate_overall_width_od_in += top_width_material_needed
            top_panel_calc_width += top_width_material_needed
            
        if top_length_material_needed > 0:
            end_panel_calc_length += top_length_material_needed
            crate_overall_length_od_in += top_length_material_needed
            top_panel_calc_length += top_length_material_needed

        # === FINAL SKID LAYOUT (STEP 5) ===
        # Now that all dimensions are final, calculate the skid layout
        skid_layout_results = calculate_skid_layout(
            crate_overall_width_od_in=crate_overall_width_od_in,
            skid_actual_width_in=skid_actual_width_in,
            max_skid_spacing_rule_in=max_skid_spacing_rule_in
        )
        calc_skid_count = skid_layout_results["calc_skid_count"]
        calc_skid_pitch_in = skid_layout_results["calc_skid_pitch_in"]
        calc_first_skid_pos_x_in = skid_layout_results["calc_first_skid_pos_x_in"]
        x_master_skid_origin_offset_in = skid_layout_results["x_master_skid_origin_offset_in"]

        # === FINAL FLOORBOARD AND PANEL CALCULATIONS (STEP 6) ===
        skid_model_length_in = crate_overall_length_od_in
        fb_actual_length_in = crate_overall_width_od_in

        # === FLOORBOARD CALCULATIONS ===
        fb_actual_length_in = crate_overall_width_od_in
        fb_actual_thickness_in = floorboard_actual_thickness_in
        cap_end_gap_each_side = panel_thickness_in + cleat_thickness_in
        fb_usable_coverage_y_in = skid_model_length_in - (2 * cap_end_gap_each_side)
        fb_initial_start_y_offset_abs = cap_end_gap_each_side
        
        floorboard_results = calculate_floorboard_layout(
            fb_usable_coverage_y_in=fb_usable_coverage_y_in,
            fb_initial_start_y_offset_abs=fb_initial_start_y_offset_abs,
            selected_std_lumber_widths=selected_std_lumber_widths,
            min_custom_lumber_width_in=min_custom_lumber_width_in,
            force_small_custom_board_bool=force_small_custom_board_bool
        )
        floorboards_data = floorboard_results["floorboards_data"]
        actual_middle_gap = floorboard_results["actual_middle_gap"]
        center_custom_board_width = floorboard_results["center_custom_board_width"]

        # === DETAILED PANEL COMPONENT CALCULATIONS ===
        
        # --- Left & Right Panel Components (NEW) ---
        # IMPORTANT: Calculate AFTER material additions to use updated end_panel_calc_length
        # Using same bounding box as End Panels (face length = end_panel_calc_length)
        left_panel_components_data = calculate_left_panel_components(
            left_panel_assembly_length=end_panel_calc_length,
            left_panel_assembly_height=end_panel_calc_height,
            panel_sheathing_thickness=panel_thickness_in,
            cleat_material_thickness=cleat_thickness_in,
            cleat_material_member_width=cleat_member_actual_width_in
        )
        # Update with splice-based cleat positioning
        # For left panel: width = length (along which cleats are spaced), height = height
        left_panel_components_data = update_panel_components_with_splice_cleats(
            left_panel_components_data, end_panel_calc_length, end_panel_calc_height, cleat_member_actual_width_in
        )

        right_panel_components_data = calculate_right_panel_components(
            left_panel_assembly_length=end_panel_calc_length,  # same length as LEFT
            left_panel_assembly_height=end_panel_calc_height,
            panel_sheathing_thickness=panel_thickness_in,
            cleat_material_thickness=cleat_thickness_in,
            cleat_material_member_width=cleat_member_actual_width_in
        )
        # Update with splice-based cleat positioning  
        # For right panel: width = length (along which cleats are spaced), height = height
        right_panel_components_data = update_panel_components_with_splice_cleats(
            right_panel_components_data, end_panel_calc_length, end_panel_calc_height, cleat_member_actual_width_in
        )
        
        # --- Front Panel Components ---
        front_panel_components_data = calculate_front_panel_components(
            front_panel_assembly_width=front_panel_calc_width,
            front_panel_assembly_height=front_panel_calc_height,
            panel_sheathing_thickness=panel_thickness_in,
            cleat_material_thickness=cleat_thickness_in,
            cleat_material_member_width=cleat_member_actual_width_in,
            include_klimps=True,
            klimp_diameter=DEFAULT_KLIMP_DIAMETER
        )
        # Update with splice-based cleat positioning
        front_panel_components_data = update_panel_components_with_splice_cleats(
            front_panel_components_data, front_panel_calc_width, front_panel_calc_height, cleat_member_actual_width_in
        )

        # --- Back Panel Components ---
        back_panel_components_data = calculate_back_panel_components( 
            back_panel_assembly_width=back_panel_calc_width,
            back_panel_assembly_height=back_panel_calc_height,
            panel_sheathing_thickness=panel_thickness_in,
            cleat_material_thickness=cleat_thickness_in,
            cleat_material_member_width=cleat_member_actual_width_in
        )
        # Update with splice-based cleat positioning
        back_panel_components_data = update_panel_components_with_splice_cleats(
            back_panel_components_data, back_panel_calc_width, back_panel_calc_height, cleat_member_actual_width_in
        )

        # --- End Panel Components (for Left & Right, assumed identical) ---
        # Overall dimensions for end panels are already calculated:
        # end_panel_calc_length (this is the "face width" of the end panel)
        # end_panel_calc_height
        # Material properties are the same.
        # NOTE: End panels are not needed - using Left/Right panels instead

        # --- Top Panel Components ---
        top_panel_components_data = calculate_top_panel_components(
            top_panel_assembly_width=top_panel_calc_width,
            top_panel_assembly_length=top_panel_calc_length,
            panel_sheathing_thickness=panel_thickness_in,
            cleat_material_thickness=cleat_thickness_in,
            cleat_material_member_width=cleat_member_actual_width_in
        )
        # Update with splice-based cleat positioning (top panel has cleats in both directions)
        top_panel_components_data = update_panel_components_with_splice_cleats(
            top_panel_components_data, top_panel_calc_width, top_panel_calc_length, cleat_member_actual_width_in
        )

        # Extract intermediate cleat data for Front Panel
        fp_intermediate_cleats_data = front_panel_components_data.get('intermediate_vertical_cleats', {})
        fp_inter_vc_count = fp_intermediate_cleats_data.get('count', 0)
        fp_inter_vc_length = fp_intermediate_cleats_data.get('length', 0.0)
        fp_inter_vc_material_thickness = fp_intermediate_cleats_data.get('material_thickness', cleat_thickness_in)
        fp_inter_vc_material_member_width = fp_intermediate_cleats_data.get('material_member_width', cleat_member_actual_width_in)
        fp_inter_vc_orientation_str = fp_intermediate_cleats_data.get('orientation', "None")
        fp_inter_vc_positions_centerline = fp_intermediate_cleats_data.get('positions_x_centerline', [])

        fp_inter_vc_orientation_code = 2  # Default to None/Other
        if fp_inter_vc_orientation_str.lower() == "vertical":
            fp_inter_vc_orientation_code = 0
        elif fp_inter_vc_orientation_str.lower() == "horizontal":
            fp_inter_vc_orientation_code = 1

        # Extract intermediate horizontal cleat data for Front Panel
        fp_intermediate_horizontal_cleats_data = front_panel_components_data.get('intermediate_horizontal_cleats', {})
        # fp_inter_hc_count will be set after sections are finalized
        fp_inter_hc_sections_original = fp_intermediate_horizontal_cleats_data.get('sections', []) # Get original sections from front_panel_logic
        fp_inter_hc_material_thickness = fp_intermediate_horizontal_cleats_data.get('material_thickness', cleat_thickness_in)
        fp_inter_hc_material_member_width = fp_intermediate_horizontal_cleats_data.get('material_member_width', cleat_member_actual_width_in)
        fp_inter_hc_pattern_count = fp_intermediate_horizontal_cleats_data.get('pattern_count', 1)
        fp_inter_hc_horizontal_splice_count = fp_intermediate_horizontal_cleats_data.get('horizontal_splice_count', 0)

        # Extract intermediate horizontal cleat data for Back Panel
        bp_intermediate_horizontal_cleats_data = back_panel_components_data.get('intermediate_horizontal_cleats', {})
        bp_inter_hc_sections_original = bp_intermediate_horizontal_cleats_data.get('sections', [])
        bp_inter_hc_material_thickness = bp_intermediate_horizontal_cleats_data.get('material_thickness', cleat_thickness_in)
        bp_inter_hc_material_member_width = bp_intermediate_horizontal_cleats_data.get('material_member_width', cleat_member_actual_width_in)
        bp_inter_hc_pattern_count = bp_intermediate_horizontal_cleats_data.get('pattern_count', 1)
        bp_inter_hc_horizontal_splice_count = bp_intermediate_horizontal_cleats_data.get('horizontal_splice_count', 0)

        # Extract intermediate horizontal cleat data for Left Panel
        lp_intermediate_horizontal_cleats_data = left_panel_components_data.get('intermediate_horizontal_cleats', {})
        lp_inter_hc_sections_original = lp_intermediate_horizontal_cleats_data.get('sections', [])
        lp_inter_hc_material_thickness = lp_intermediate_horizontal_cleats_data.get('material_thickness', cleat_thickness_in)
        lp_inter_hc_material_member_width = lp_intermediate_horizontal_cleats_data.get('material_member_width', cleat_member_actual_width_in)
        lp_inter_hc_pattern_count = lp_intermediate_horizontal_cleats_data.get('pattern_count', 1)
        lp_inter_hc_horizontal_splice_count = lp_intermediate_horizontal_cleats_data.get('horizontal_splice_count', 0)

        # Extract intermediate horizontal cleat data for Right Panel
        rp_intermediate_horizontal_cleats_data = right_panel_components_data.get('intermediate_horizontal_cleats', {})
        rp_inter_hc_sections_original = rp_intermediate_horizontal_cleats_data.get('sections', [])
        rp_inter_hc_material_thickness = rp_intermediate_horizontal_cleats_data.get('material_thickness', cleat_thickness_in)
        rp_inter_hc_material_member_width = rp_intermediate_horizontal_cleats_data.get('material_member_width', cleat_member_actual_width_in)
        rp_inter_hc_pattern_count = rp_intermediate_horizontal_cleats_data.get('pattern_count', 1)
        rp_inter_hc_horizontal_splice_count = rp_intermediate_horizontal_cleats_data.get('horizontal_splice_count', 0)
        fp_inter_hc_orientation_str = fp_intermediate_horizontal_cleats_data.get('orientation', "None")

        # Initialize fp_inter_hc_sections for the expressions. This will be recalculated or remain empty.
        fp_inter_hc_sections = [] 

        # RECALCULATE horizontal cleat sections using actual vertical cleat positions.
        # This is done if horizontal splices (and thus initial horizontal cleat sections) were identified by front_panel_logic.py.
        # The Y position for these cleats should be based on actual plywood splices.
        if fp_inter_hc_sections_original:
            # Use the Y position from the original calculation in front_panel_logic.py.
            # This Y position corresponds to the first horizontal plywood splice's centerline,
            # measured from the bottom edge of the panel (which is also Plywood_1's bottom edge, as Plywood_1_Y_Position is 0).
            actual_splice_y_pos = fp_inter_hc_sections_original[0]['y_pos_centerline']
            
            # Recalculate sections using the actual vertical cleat positions and the determined splice_y_pos
            # Note: If there are no intermediate vertical cleats, pass empty list
            fp_inter_hc_sections = calculate_horizontal_cleat_sections_from_vertical_positions(
                panel_width=front_panel_components_data['plywood']['width'],
                cleat_member_width=fp_inter_hc_material_member_width,
                intermediate_vc_positions=fp_inter_vc_positions_centerline if fp_inter_vc_positions_centerline else [],
                splice_y_position=actual_splice_y_pos, # Use the Y from front_panel_logic's splice calculation
                min_cleat_width=0.25
            )
        # Update the count based on the (potentially recalculated) sections
        fp_inter_hc_count = len(fp_inter_hc_sections)

        fp_inter_hc_orientation_code = 2  # Default to None/Other
        if fp_inter_hc_orientation_str.lower() == "vertical":
            fp_inter_hc_orientation_code = 0
        elif fp_inter_hc_orientation_str.lower() == "horizontal":
            fp_inter_hc_orientation_code = 1

        # Initialize sections for other panels
        bp_inter_hc_sections = []
        lp_inter_hc_sections = []
        rp_inter_hc_sections = []

        # Extract intermediate cleat data for Back Panel
        bp_intermediate_cleats_data = back_panel_components_data.get('intermediate_vertical_cleats', {})
        bp_inter_vc_count = bp_intermediate_cleats_data.get('count', 0)
        bp_inter_vc_length = bp_intermediate_cleats_data.get('length', 0.0)
        bp_inter_vc_material_thickness = bp_intermediate_cleats_data.get('material_thickness', cleat_thickness_in)
        bp_inter_vc_material_member_width = bp_intermediate_cleats_data.get('material_member_width', cleat_member_actual_width_in)
        bp_inter_vc_orientation_str = bp_intermediate_cleats_data.get('orientation', "None")
        bp_inter_vc_positions_centerline = bp_intermediate_cleats_data.get('positions_x_centerline', [])

        bp_inter_vc_orientation_code = 2
        if bp_inter_vc_orientation_str.lower() == "vertical":
            bp_inter_vc_orientation_code = 0
        elif bp_inter_vc_orientation_str.lower() == "horizontal":
            bp_inter_vc_orientation_code = 1

        # RECALCULATE back panel horizontal cleat sections using actual vertical cleat positions
        if bp_inter_hc_sections_original:
            actual_splice_y_pos = bp_inter_hc_sections_original[0]['y_pos_centerline']
            bp_inter_hc_sections = calculate_horizontal_cleat_sections_from_vertical_positions(
                panel_width=back_panel_components_data['plywood']['width'],
                cleat_member_width=bp_inter_hc_material_member_width,
                intermediate_vc_positions=bp_inter_vc_positions_centerline if bp_inter_vc_positions_centerline else [],
                splice_y_position=actual_splice_y_pos,
                min_cleat_width=0.25
            )
        bp_inter_hc_count = len(bp_inter_hc_sections)

        # Extract intermediate cleat data for Left Panel
        lp_intermediate_cleats_data = left_panel_components_data.get('intermediate_vertical_cleats', {})
        lp_inter_vc_count = lp_intermediate_cleats_data.get('count', 0)
        lp_inter_vc_length = lp_intermediate_cleats_data.get('length', 0.0)
        lp_inter_vc_material_thickness = lp_intermediate_cleats_data.get('material_thickness', cleat_thickness_in)
        lp_inter_vc_material_member_width = lp_intermediate_cleats_data.get('material_member_width', cleat_member_actual_width_in)
        lp_inter_vc_orientation_str = lp_intermediate_cleats_data.get('orientation', "None")
        lp_inter_vc_positions_centerline = lp_intermediate_cleats_data.get('positions_x_centerline', [])
        lp_inter_vc_positions_left_edge = lp_intermediate_cleats_data.get('positions_x_left_edge', [])
        lp_suppress_flags = lp_intermediate_cleats_data.get('suppress_flags', [0] * MAX_LP_INTERMEDIATE_VERTICAL_CLEATS)

        lp_inter_vc_orientation_code = 2
        if lp_inter_vc_orientation_str.lower() == "vertical":
            lp_inter_vc_orientation_code = 0
        elif lp_inter_vc_orientation_str.lower() == "horizontal":
            lp_inter_vc_orientation_code = 1

        # RECALCULATE left panel horizontal cleat sections using actual vertical cleat positions
        if lp_inter_hc_sections_original:
            actual_splice_y_pos = lp_inter_hc_sections_original[0]['y_pos_centerline']
            lp_inter_hc_sections = calculate_horizontal_cleat_sections_from_vertical_positions(
                panel_width=left_panel_components_data['plywood']['length'],  # Left panel uses length as width
                cleat_member_width=lp_inter_hc_material_member_width,
                intermediate_vc_positions=lp_inter_vc_positions_centerline if lp_inter_vc_positions_centerline else [],
                splice_y_position=actual_splice_y_pos,
                min_cleat_width=0.25
            )
        lp_inter_hc_count = len(lp_inter_hc_sections)

        # Extract intermediate cleat data for Right Panel  
        rp_intermediate_cleats_data = right_panel_components_data.get('intermediate_vertical_cleats', {})
        rp_inter_vc_count = rp_intermediate_cleats_data.get('count', 0)
        rp_inter_vc_length = rp_intermediate_cleats_data.get('length', 0.0)
        rp_inter_vc_material_thickness = rp_intermediate_cleats_data.get('material_thickness', cleat_thickness_in)
        rp_inter_vc_material_member_width = rp_intermediate_cleats_data.get('material_member_width', cleat_member_actual_width_in)
        rp_inter_vc_orientation_str = rp_intermediate_cleats_data.get('orientation', "None")
        rp_inter_vc_positions_centerline = rp_intermediate_cleats_data.get('positions_x_centerline', [])
        rp_inter_vc_positions_left_edge = rp_intermediate_cleats_data.get('positions_x_left_edge', [])
        rp_suppress_flags = rp_intermediate_cleats_data.get('suppress_flags', [0] * MAX_RP_INTERMEDIATE_VERTICAL_CLEATS)

        rp_inter_vc_orientation_code = 2
        if rp_inter_vc_orientation_str.lower() == "vertical":
            rp_inter_vc_orientation_code = 0
        elif rp_inter_vc_orientation_str.lower() == "horizontal":
            rp_inter_vc_orientation_code = 1

        # RECALCULATE right panel horizontal cleat sections using actual vertical cleat positions
        if rp_inter_hc_sections_original:
            actual_splice_y_pos = rp_inter_hc_sections_original[0]['y_pos_centerline']
            rp_inter_hc_sections = calculate_horizontal_cleat_sections_from_vertical_positions(
                panel_width=right_panel_components_data['plywood']['length'],  # Right panel uses length as width
                cleat_member_width=rp_inter_hc_material_member_width,
                intermediate_vc_positions=rp_inter_vc_positions_centerline if rp_inter_vc_positions_centerline else [],
                splice_y_position=actual_splice_y_pos,
                min_cleat_width=0.25
            )
        rp_inter_hc_count = len(rp_inter_hc_sections)

        # Extract and write Top Panel intermediate cleat data
        tp_secondary_cleats_data = top_panel_components_data.get('secondary_cleats', {})
        tp_secondary_length = tp_secondary_cleats_data.get('length', 0.0)
        tp_secondary_count = tp_secondary_cleats_data.get('count', 0)
        
        tp_intermediate_cleats_data = top_panel_components_data.get('intermediate_cleats', {})
        tp_inter_count = tp_intermediate_cleats_data.get('count', 0)
        tp_inter_length = tp_intermediate_cleats_data.get('length', 0.0)
        tp_inter_material_thickness = tp_intermediate_cleats_data.get('material_thickness', cleat_thickness_in)
        tp_inter_material_member_width = tp_intermediate_cleats_data.get('material_member_width', cleat_member_actual_width_in)
        tp_inter_orientation_str = tp_intermediate_cleats_data.get('orientation', "None")
        tp_inter_positions_centerline = tp_intermediate_cleats_data.get('positions_x_centerline', [])
        tp_inter_positions_left_edge = tp_intermediate_cleats_data.get('positions_x_left_edge', [])
        tp_suppress_flags = tp_intermediate_cleats_data.get('suppress_flags', [0] * MAX_TP_INTERMEDIATE_CLEATS)

        tp_inter_orientation_code = 2
        if tp_inter_orientation_str.lower() == "vertical":
            tp_inter_orientation_code = 0
        elif tp_inter_orientation_str.lower() == "horizontal":
            tp_inter_orientation_code = 1
            
        # Extract intermediate horizontal cleat data for Top Panel
        tp_intermediate_horizontal_cleats_data = top_panel_components_data.get('intermediate_horizontal_cleats', {})
        tp_inter_hc_count = tp_intermediate_horizontal_cleats_data.get('count', 0)
        tp_inter_hc_instances = tp_intermediate_horizontal_cleats_data.get('instances', [])
        tp_inter_hc_material_thickness = tp_intermediate_horizontal_cleats_data.get('material_thickness', cleat_thickness_in)
        tp_inter_hc_material_member_width = tp_intermediate_horizontal_cleats_data.get('material_member_width', cleat_member_actual_width_in)
        tp_inter_hc_orientation_str = tp_intermediate_horizontal_cleats_data.get('orientation', "None")
        tp_inter_hc_suppress_flags = tp_intermediate_horizontal_cleats_data.get('suppress_flags', [0] * MAX_TP_INTERMEDIATE_HORIZONTAL_CLEATS)
        tp_inter_hc_pattern_count = tp_intermediate_horizontal_cleats_data.get('pattern_count', 1)
        tp_inter_hc_horizontal_splice_count = tp_intermediate_horizontal_cleats_data.get('horizontal_splice_count', 0)
        
        tp_inter_hc_orientation_code = 2
        if tp_inter_hc_orientation_str.lower() == "vertical":
            tp_inter_hc_orientation_code = 0
        elif tp_inter_hc_orientation_str.lower() == "horizontal":
            tp_inter_hc_orientation_code = 1
            
        # RECALCULATE top panel horizontal cleat sections using actual vertical cleat positions
        tp_inter_hc_sections = []
        if tp_inter_hc_count > 0 and tp_inter_hc_instances:
            # Get the splice Y position from the original instances
            actual_splice_y_pos = tp_inter_hc_instances[0].get('y_pos_centerline', 0.0)
            tp_inter_hc_sections = calculate_horizontal_cleat_sections_from_vertical_positions(
                panel_width=top_panel_components_data['plywood']['width'],
                cleat_member_width=tp_inter_hc_material_member_width,
                intermediate_vc_positions=tp_inter_positions_centerline if tp_inter_positions_centerline else [],
                splice_y_position=actual_splice_y_pos,
                min_cleat_width=0.25
            )
        
        # Update count and instances based on recalculated sections
        if tp_inter_hc_sections:
            tp_inter_hc_count = len(tp_inter_hc_sections)
            # Create new instances array with recalculated data
            tp_inter_hc_instances = []
            for i in range(MAX_TP_INTERMEDIATE_HORIZONTAL_CLEATS):
                if i < len(tp_inter_hc_sections):
                    section = tp_inter_hc_sections[i]
                    instance = {
                        "suppress_flag": 1,
                        "height": tp_inter_hc_material_member_width,
                        "width": section["width"],
                        "length": tp_inter_hc_material_thickness,
                        "x_pos": section["x_pos"],
                        "y_pos": section["y_pos_bottom_edge"],
                        "y_pos_centerline": section["y_pos_centerline"]
                    }
                else:
                    instance = {
                        "suppress_flag": 0,
                        "height": tp_inter_hc_material_member_width,
                        "width": 0.25,
                        "length": tp_inter_hc_material_thickness,
                        "x_pos": 0.25,
                        "y_pos": 0.25,
                        "y_pos_centerline": 0.375
                    }
                tp_inter_hc_instances.append(instance)

        # --- Prepare expressions file content ---
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        expressions_content = [
            f"// NX Expressions - Skids, Floorboards & Detailed Panels", # Updated title
            f"// Generated: {timestamp}\n",
            f"// --- USER INPUTS & CRATE CONSTANTS ---",
            f"[lbm]product_weight = {product_weight_lbs:.3f}",
            f"[Inch]product_length_input = {product_length_in:.3f}",
            f"[Inch]product_width_input = {product_width_in:.3f}", 
            f"[Inch]clearance_side_input = {clearance_each_side_in:.3f}", 
            f"BOOL_Allow_3x4_Skids_Input = {1 if allow_3x4_skids_bool else 0}",
            f"[Inch]INPUT_Panel_Thickness = {panel_thickness_in:.3f}",
            f"[Inch]INPUT_Cleat_Thickness = {cleat_thickness_in:.3f}",
            f"[Inch]INPUT_Cleat_Member_Actual_Width = {cleat_member_actual_width_in:.3f}", # Added input echo
            f"[Inch]INPUT_Product_Actual_Height = {product_actual_height_in:.3f}",
            f"[Inch]INPUT_Clearance_Above_Product = {clearance_above_product_in:.3f}",
            f"[Inch]INPUT_Ground_Clearance_End_Panels = {ground_clearance_in:.3f}",
            f"BOOL_Force_Small_Custom_Floorboard = {1 if force_small_custom_board_bool else 0}",
            f"[Inch]INPUT_Floorboard_Actual_Thickness = {floorboard_actual_thickness_in:.3f}",
            f"[Inch]INPUT_Max_Allowable_Middle_Gap = {max_allowable_middle_gap_in:.3f}",
            f"[Inch]INPUT_Min_Custom_Lumber_Width = {min_custom_lumber_width_in:.3f}\n",
            
            f"// --- CALCULATED CRATE DIMENSIONS ---",
            f"[Inch]crate_overall_width_OD = {crate_overall_width_od_in:.3f}", 
            f"[Inch]crate_overall_length_OD = {crate_overall_length_od_in:.3f}\n",
            
            f"// --- SKID PARAMETERS ---",
            f"// Skid Lumber Callout: {lumber_callout}",
            f"[Inch]Skid_Actual_Height = {skid_actual_height_in:.3f}",
            f"[Inch]Skid_Actual_Width = {skid_actual_width_in:.3f}",
            f"[Inch]Skid_Actual_Length = {skid_model_length_in:.3f}",
            f"CALC_Skid_Count = {calc_skid_count}",
            f"[Inch]CALC_Skid_Pitch = {calc_skid_pitch_in:.4f}", 
            f"[Inch]X_Master_Skid_Origin_Offset = {x_master_skid_origin_offset_in:.4f}\n",
            
            f"// --- FLOORBOARD PARAMETERS ---",
            f"[Inch]FB_Board_Actual_Length = {fb_actual_length_in:.3f}", 
            f"[Inch]FB_Board_Actual_Thickness = {fb_actual_thickness_in:.3f}",
            f"[Inch]CALC_FB_Actual_Middle_Gap = {actual_middle_gap:.4f}", 
            f"[Inch]CALC_FB_Center_Custom_Board_Width = {center_custom_board_width if center_custom_board_width > 0.001 else 0.0:.4f}",
            f"[Inch]CALC_FB_Start_Y_Offset_Abs = {fb_initial_start_y_offset_abs:.3f}\n",
            f"// Floorboard Instance Data"
        ]
        for i in range(MAX_NX_FLOORBOARD_INSTANCES):
            instance_num = i + 1
            if i < len(floorboards_data):
                board = floorboards_data[i]
                expressions_content.append(f"FB_Inst_{instance_num}_Suppress_Flag = 1") # Corrected: 1 to show
                expressions_content.append(f"[Inch]FB_Inst_{instance_num}_Actual_Width = {board['width']:.4f}")
                expressions_content.append(f"[Inch]FB_Inst_{instance_num}_Y_Pos_Abs = {board['y_pos']:.4f}")
            else:
                expressions_content.append(f"FB_Inst_{instance_num}_Suppress_Flag = 0") # Corrected: 0 to suppress/hide
                expressions_content.append(f"[Inch]FB_Inst_{instance_num}_Actual_Width = 0.0001")
                expressions_content.append(f"[Inch]FB_Inst_{instance_num}_Y_Pos_Abs = 0.0000")
            
        expressions_content.extend([
            f"\n// --- OVERALL PANEL ASSEMBLY DIMENSIONS (Informational) ---",
            f"[Inch]PANEL_Front_Assy_Overall_Width = {front_panel_calc_width:.3f}",
            f"[Inch]PANEL_Front_Assy_Overall_Height = {front_panel_calc_height:.3f}",
            f"[Inch]PANEL_Front_Assy_Overall_Depth = {front_panel_calc_depth:.3f}\n",
            
            f"[Inch]PANEL_Back_Assy_Overall_Width = {back_panel_calc_width:.3f}", # Assuming same as front for now
            f"[Inch]PANEL_Back_Assy_Overall_Height = {back_panel_calc_height:.3f}",
            f"[Inch]PANEL_Back_Assy_Overall_Depth = {back_panel_calc_depth:.3f}\n",

            f"[Inch]PANEL_End_Assy_Overall_Length_Face = {end_panel_calc_length:.3f} // For Left & Right End Panels",
            f"[Inch]PANEL_End_Assy_Overall_Height = {end_panel_calc_height:.3f}",
            f"[Inch]PANEL_End_Assy_Overall_Depth_Thickness = {end_panel_calc_depth:.3f}\n",

            f"[Inch]PANEL_Top_Assy_Overall_Width = {top_panel_calc_width:.3f}",
            f"[Inch]PANEL_Top_Assy_Overall_Length = {top_panel_calc_length:.3f}",
            f"[Inch]PANEL_Top_Assy_Overall_Depth_Thickness = {top_panel_calc_depth:.3f}\n",

            f"// --- FRONT PANEL ASSEMBLY DIMENSIONS ---",
            f"[Inch]FP_Panel_Assembly_Width = PANEL_Front_Assy_Overall_Width",
            f"[Inch]FP_Panel_Assembly_Height = PANEL_Front_Assy_Overall_Height",
            f"[Inch]FP_Panel_Assembly_Depth = PANEL_Front_Assy_Overall_Depth\n",

            f"// --- FRONT PANEL COMPONENT DETAILS ---",
            f"// Plywood Sheathing",
            f"[Inch]FP_Plywood_Width = {front_panel_components_data['plywood']['width']:.3f}",
            f"[Inch]FP_Plywood_Height = {front_panel_components_data['plywood']['height']:.3f}",
            f"[Inch]FP_Plywood_Thickness = {front_panel_components_data['plywood']['thickness']:.3f}\n",
            
            f"// Horizontal Cleats (Top & Bottom)",
            f"[Inch]FP_Horizontal_Cleat_Length = {front_panel_components_data['horizontal_cleats']['length']:.3f}",
            f"[Inch]FP_Horizontal_Cleat_Material_Thickness = {front_panel_components_data['horizontal_cleats']['material_thickness']:.3f}",
            f"[Inch]FP_Horizontal_Cleat_Material_Member_Width = {front_panel_components_data['horizontal_cleats']['material_member_width']:.3f}",
            f"FP_Horizontal_Cleat_Count = {front_panel_components_data['horizontal_cleats']['count']}\n",

            f"// Vertical Cleats (Left & Right)",
            f"[Inch]FP_Vertical_Cleat_Length = {front_panel_components_data['vertical_cleats']['length']:.3f}",
            f"[Inch]FP_Vertical_Cleat_Material_Thickness = {front_panel_components_data['vertical_cleats']['material_thickness']:.3f}",
            f"[Inch]FP_Vertical_Cleat_Material_Member_Width = {front_panel_components_data['vertical_cleats']['material_member_width']:.3f}",
            f"FP_Vertical_Cleat_Count = {front_panel_components_data['vertical_cleats']['count']}\n",

            f"// Intermediate Vertical Cleats (Front Panel)",
            f"FP_Intermediate_Vertical_Cleat_Count = {fp_inter_vc_count}",
            f"[Inch]FP_Intermediate_Vertical_Cleat_Length = {fp_inter_vc_length:.3f}",
            f"[Inch]FP_Intermediate_Vertical_Cleat_Material_Thickness = {fp_inter_vc_material_thickness:.3f}",
            f"[Inch]FP_Intermediate_Vertical_Cleat_Material_Member_Width = {fp_inter_vc_material_member_width:.3f}",
            f"FP_Intermediate_Vertical_Cleat_Orientation_Code = {fp_inter_vc_orientation_code} // 0=Vertical, 1=Horizontal, 2=None\n",
            f"// Front Panel Intermediate Vertical Cleat Instance Data (Max {MAX_FP_INTERMEDIATE_VERTICAL_CLEATS} instances)"
        ])

        for i in range(MAX_FP_INTERMEDIATE_VERTICAL_CLEATS):
            instance_num = i + 1
            if i < fp_inter_vc_count:
                expressions_content.append(f"FP_Inter_VC_Inst_{instance_num}_Suppress_Flag = 1") # Corrected: 1 to show
                x_pos_centerline = fp_inter_vc_positions_centerline[i] # This is ALREADY relative to plywood's left edge
                expressions_content.append(f"[Inch]FP_Inter_VC_Inst_{instance_num}_X_Pos_Centerline = {x_pos_centerline:.4f}")
                # Calculate X position from the left edge of the Front Panel Plywood to the LEFT EDGE of the cleat
                # x_pos_centerline is the position of the cleat's centerline from the plywood's left edge.
                # To get the cleat's left edge from the plywood's left edge:
                # subtract half the cleat's width from its centerline position.
                x_pos_from_left_edge = x_pos_centerline - (fp_inter_vc_material_member_width / 2.0)
                expressions_content.append(f"[Inch]FP_Inter_VC_Inst_{instance_num}_X_Pos_From_Left_Edge = {x_pos_from_left_edge:.4f}")
            else:
                expressions_content.append(f"FP_Inter_VC_Inst_{instance_num}_Suppress_Flag = 0") # Corrected: 0 to suppress/hide
                expressions_content.append(f"[Inch]FP_Inter_VC_Inst_{instance_num}_X_Pos_Centerline = 0.0000")
                expressions_content.append(f"[Inch]FP_Inter_VC_Inst_{instance_num}_X_Pos_From_Left_Edge = 0.0000") # Add for consistency when suppressed

        # --- Front Panel Klimps ---
        klimps_data = front_panel_components_data.get('klimps', {})
        fp_klimp_count = klimps_data.get('count', 0)
        fp_klimp_diameter = klimps_data.get('diameter', DEFAULT_KLIMP_DIAMETER)
        fp_klimp_positions = klimps_data.get('positions', [])
        fp_klimp_orientation_code = 3 if klimps_data.get('orientation') == "Front_Panel_Surface" else 2  # 3=Front Surface, 2=None

        expressions_content.extend([
            f"\n// Front Panel Klimps (Clamps/Fasteners)",
            f"FP_Klimp_Count = {fp_klimp_count}",
            f"[Inch]FP_Klimp_Diameter = {fp_klimp_diameter:.3f}",
            f"FP_Klimp_Orientation_Code = {fp_klimp_orientation_code} // 0=Vertical, 1=Horizontal, 2=None, 3=Front_Surface",
            f"// Front Panel Klimp Instance Data (Max {MAX_FRONT_PANEL_KLIMPS} instances)"
        ])

        for i in range(MAX_FRONT_PANEL_KLIMPS):
            instance_num = i + 1
            if i < fp_klimp_count and i < len(fp_klimp_positions):
                klimp = fp_klimp_positions[i]
                expressions_content.append(f"FP_Klimp_Inst_{instance_num}_Suppress_Flag = 1") # 1 to show
                expressions_content.append(f"[Inch]FP_Klimp_Inst_{instance_num}_X_Pos = {klimp['x_pos']:.4f}")
                expressions_content.append(f"[Inch]FP_Klimp_Inst_{instance_num}_Y_Pos = {klimp['y_pos']:.4f}")
            else:
                expressions_content.append(f"FP_Klimp_Inst_{instance_num}_Suppress_Flag = 0") # 0 to suppress/hide
                expressions_content.append(f"[Inch]FP_Klimp_Inst_{instance_num}_X_Pos = 0.0000")
                expressions_content.append(f"[Inch]FP_Klimp_Inst_{instance_num}_Y_Pos = 0.0000")

        
        expressions_content.extend([
            f"\n// --- BACK PANEL ASSEMBLY DIMENSIONS ---",
            f"[Inch]BP_Panel_Assembly_Width = PANEL_Back_Assy_Overall_Width",
            f"[Inch]BP_Panel_Assembly_Height = PANEL_Back_Assy_Overall_Height",
            f"[Inch]BP_Panel_Assembly_Depth = PANEL_Back_Assy_Overall_Depth\n",
            
            f"// --- BACK PANEL COMPONENT DETAILS ---",
            f"// Plywood Sheathing",
            f"[Inch]BP_Plywood_Width = {back_panel_components_data['plywood']['width']:.3f}",
            f"[Inch]BP_Plywood_Height = {back_panel_components_data['plywood']['height']:.3f}",
            f"[Inch]BP_Plywood_Thickness = {back_panel_components_data['plywood']['thickness']:.3f}\n",
            
            f"// Horizontal Cleats (Top & Bottom)",
            f"[Inch]BP_Horizontal_Cleat_Length = {back_panel_components_data['horizontal_cleats']['length']:.3f}",
            f"[Inch]BP_Horizontal_Cleat_Material_Thickness = {back_panel_components_data['horizontal_cleats']['material_thickness']:.3f}",
            f"[Inch]BP_Horizontal_Cleat_Material_Member_Width = {back_panel_components_data['horizontal_cleats']['material_member_width']:.3f}",
            f"BP_Horizontal_Cleat_Count = {back_panel_components_data['horizontal_cleats']['count']}\n",

            f"// Vertical Cleats (Left & Right)",
            f"[Inch]BP_Vertical_Cleat_Length = {back_panel_components_data['vertical_cleats']['length']:.3f}",
            f"[Inch]BP_Vertical_Cleat_Material_Thickness = {back_panel_components_data['vertical_cleats']['material_thickness']:.3f}",
            f"[Inch]BP_Vertical_Cleat_Material_Member_Width = {back_panel_components_data['vertical_cleats']['material_member_width']:.3f}",
            f"BP_Vertical_Cleat_Count = {back_panel_components_data['vertical_cleats']['count']}",

            f"// Intermediate Vertical Cleats (Back Panel)",
            f"BP_Intermediate_Vertical_Cleat_Count = {bp_inter_vc_count}",
            f"[Inch]BP_Intermediate_Vertical_Cleat_Length = {bp_inter_vc_length:.3f}",
            f"[Inch]BP_Intermediate_Vertical_Cleat_Material_Thickness = {bp_inter_vc_material_thickness:.3f}",
            f"[Inch]BP_Intermediate_Vertical_Cleat_Material_Member_Width = {bp_inter_vc_material_member_width:.3f}",
            f"BP_Intermediate_Vertical_Cleat_Orientation_Code = {bp_inter_vc_orientation_code} // 0=Vertical, 1=Horizontal, 2=None",
            f"// Back Panel Intermediate Vertical Cleat Instance Data (Max {MAX_BP_INTERMEDIATE_VERTICAL_CLEATS} instances)"
        ]);

        for i in range(MAX_BP_INTERMEDIATE_VERTICAL_CLEATS):
            instance_num = i + 1
            if i < bp_inter_vc_count:
                expressions_content.append(f"BP_Inter_VC_Inst_{instance_num}_Suppress_Flag = 1") # 1 to show
                x_pos_centerline = bp_inter_vc_positions_centerline[i]
                expressions_content.append(f"[Inch]BP_Inter_VC_Inst_{instance_num}_X_Pos_Centerline = {x_pos_centerline:.4f}")
                # Calculate X position from the left edge of the Back Panel Plywood to the LEFT EDGE of the cleat
                x_pos_from_left_edge = x_pos_centerline - (bp_inter_vc_material_member_width / 2.0)
                expressions_content.append(f"[Inch]BP_Inter_VC_Inst_{instance_num}_X_Pos_From_Left_Edge = {x_pos_from_left_edge:.4f}")
            else:
                expressions_content.append(f"BP_Inter_VC_Inst_{instance_num}_Suppress_Flag = 0") # 0 to suppress/hide
                expressions_content.append(f"[Inch]BP_Inter_VC_Inst_{instance_num}_X_Pos_Centerline = 0.0000")
                expressions_content.append(f"[Inch]BP_Inter_VC_Inst_{instance_num}_X_Pos_From_Left_Edge = 0.0000")

        expressions_content.extend([
            f"\n// --- TOP PANEL ASSEMBLY DIMENSIONS ---",
            f"[Inch]TP_Panel_Assembly_Width = PANEL_Top_Assy_Overall_Width",
            f"[Inch]TP_Panel_Assembly_Length = PANEL_Top_Assy_Overall_Length",
            f"[Inch]TP_Panel_Assembly_Depth = PANEL_Top_Assy_Overall_Depth_Thickness\n",
            
            f"// --- TOP PANEL COMPONENT DETAILS ---",
            f"// Plywood Sheathing",
            f"[Inch]TP_Plywood_Width = {top_panel_components_data['plywood']['width']:.3f}", # Across crate width
            f"[Inch]TP_Plywood_Length = {top_panel_components_data['plywood']['length']:.3f}", # Along crate length
            f"[Inch]TP_Plywood_Thickness = {top_panel_components_data['plywood']['thickness']:.3f}\n",
            
            f"// Primary Cleats (along length)",
            f"[Inch]TP_Primary_Cleat_Length = {top_panel_components_data['primary_cleats']['length']:.3f}",
            f"[Inch]TP_Primary_Cleat_Material_Thickness = {top_panel_components_data['primary_cleats']['material_thickness']:.3f}",
            f"[Inch]TP_Primary_Cleat_Material_Member_Width = {top_panel_components_data['primary_cleats']['material_member_width']:.3f}",
            f"TP_Primary_Cleat_Count = {top_panel_components_data['primary_cleats']['count']}\n",
        ])
        
        expressions_content.extend([
            f"// Secondary Cleats (across width at ends)",
            f"TP_Secondary_Cleat_Length = {tp_secondary_length:.3f}",
            f"TP_Secondary_Cleat_Count = {tp_secondary_count}\n",

            f"// Intermediate Cleats (across width)",
            f"TP_Intermediate_Cleat_Count = {tp_inter_count}",
            f"[Inch]TP_Intermediate_Cleat_Length = {tp_inter_length:.3f}",
            f"[Inch]TP_Intermediate_Cleat_Material_Thickness = {tp_inter_material_thickness:.3f}",
            f"[Inch]TP_Intermediate_Cleat_Material_Member_Width = {tp_inter_material_member_width:.3f}",
            f"TP_Intermediate_Cleat_Orientation_Code = {tp_inter_orientation_code} // 0=Vertical, 1=Horizontal, 2=None",
            f"// Top Panel Intermediate Cleat Instance Data (Max {MAX_TP_INTERMEDIATE_CLEATS} instances)"
        ]);
        
        for i in range(MAX_TP_INTERMEDIATE_CLEATS):
            instance_num = i + 1
            if i < tp_inter_count:
                expressions_content.append(f"TP_Inter_Cleat_Inst_{instance_num}_Suppress_Flag = {tp_suppress_flags[i]}")
                x_pos_centerline = tp_inter_positions_centerline[i]
                expressions_content.append(f"[Inch]TP_Inter_Cleat_Inst_{instance_num}_X_Pos_Centerline = {x_pos_centerline:.4f}")
                x_pos_left_edge = tp_inter_positions_left_edge[i]
                expressions_content.append(f"[Inch]TP_Inter_Cleat_Inst_{instance_num}_X_Pos_From_Left_Edge = {x_pos_left_edge:.4f}")
            else:
                expressions_content.append(f"TP_Inter_Cleat_Inst_{instance_num}_Suppress_Flag = 0")
                expressions_content.append(f"[Inch]TP_Inter_Cleat_Inst_{instance_num}_X_Pos_Centerline = 0.0000")
                expressions_content.append(f"[Inch]TP_Inter_Cleat_Inst_{instance_num}_X_Pos_From_Left_Edge = 0.0000")

        # Add Top Panel Intermediate Horizontal Cleats
        expressions_content.extend([
            f"\n// Top Panel Intermediate Horizontal Cleats (Sections Between Vertical Cleats)",
            f"TP_Intermediate_Horizontal_Cleat_Count = {tp_inter_hc_count}",
            f"[Inch]TP_Intermediate_Horizontal_Cleat_Material_Thickness = {tp_inter_hc_material_thickness:.3f}",
            f"[Inch]TP_Intermediate_Horizontal_Cleat_Material_Member_Width = {tp_inter_hc_material_member_width:.3f}",
            f"TP_Intermediate_Horizontal_Cleat_Orientation_Code = {tp_inter_hc_orientation_code} // 0=Vertical, 1=Horizontal, 2=None",
            f"TP_Intermediate_Horizontal_Cleat_Pattern_Count = {tp_inter_hc_pattern_count} // Pattern count for NX (1 or 2 based on splices)",
            f"TP_Intermediate_Horizontal_Cleat_Horizontal_Splice_Count = {tp_inter_hc_horizontal_splice_count} // Number of horizontal splices",
            f"",
            f"// Top Panel Intermediate Horizontal Cleat Instance Data (Max {MAX_TP_INTERMEDIATE_HORIZONTAL_CLEATS} instances)"
        ])
        
        for i in range(MAX_TP_INTERMEDIATE_HORIZONTAL_CLEATS):
            instance_num = i + 1
            if i < tp_inter_hc_count and i < len(tp_inter_hc_instances):
                instance = tp_inter_hc_instances[i]
                expressions_content.append(f"TP_Inter_HC_Inst_{instance_num}_Suppress_Flag = {instance.get('suppress_flag', 0)}")
                expressions_content.append(f"[Inch]TP_Inter_HC_Inst_{instance_num}_Height = {instance.get('height', 0.0):.3f}")
                expressions_content.append(f"[Inch]TP_Inter_HC_Inst_{instance_num}_Width = {instance.get('width', 0.0):.3f}")
                expressions_content.append(f"[Inch]TP_Inter_HC_Inst_{instance_num}_Length = {instance.get('length', 0.0):.3f}")
                expressions_content.append(f"[Inch]TP_Inter_HC_Inst_{instance_num}_X_Pos = {instance.get('x_pos', 0.0):.3f}")
                expressions_content.append(f"[Inch]TP_Inter_HC_Inst_{instance_num}_Y_Pos = {instance.get('y_pos', 0.0):.4f}")
                expressions_content.append(f"[Inch]TP_Inter_HC_Inst_{instance_num}_Y_Pos_Centerline = {instance.get('y_pos_centerline', 0.0):.4f}")
            else:
                expressions_content.append(f"TP_Inter_HC_Inst_{instance_num}_Suppress_Flag = 0")
                expressions_content.append(f"[Inch]TP_Inter_HC_Inst_{instance_num}_Height = {tp_inter_hc_material_member_width:.3f}")
                expressions_content.append(f"[Inch]TP_Inter_HC_Inst_{instance_num}_Width = 0.250")
                expressions_content.append(f"[Inch]TP_Inter_HC_Inst_{instance_num}_Length = {tp_inter_hc_material_thickness:.3f}")
                expressions_content.append(f"[Inch]TP_Inter_HC_Inst_{instance_num}_X_Pos = 0.250")
                expressions_content.append(f"[Inch]TP_Inter_HC_Inst_{instance_num}_Y_Pos = 0.2500")
                expressions_content.append(f"[Inch]TP_Inter_HC_Inst_{instance_num}_Y_Pos_Centerline = 0.3750")

        expressions_content.extend([
            f"\n// --- LEFT PANEL ASSEMBLY DIMENSIONS ---",
            f"[Inch]LP_Panel_Assembly_Length = PANEL_End_Assy_Overall_Length_Face",
            f"[Inch]LP_Panel_Assembly_Height = PANEL_End_Assy_Overall_Height", 
            f"[Inch]LP_Panel_Assembly_Depth = PANEL_End_Assy_Overall_Depth_Thickness\n",
            
            f"// --- LEFT PANEL COMPONENT DETAILS ---",
            f"// Plywood Sheathing",
            f"[Inch]LP_Plywood_Length = {left_panel_components_data['plywood']['length']:.3f}",
            f"[Inch]LP_Plywood_Height = {left_panel_components_data['plywood']['height']:.3f}",
            f"[Inch]LP_Plywood_Thickness = {left_panel_components_data['plywood']['thickness']:.3f}\n",

            f"// Horizontal Cleats (Top & Bottom)",
            f"[Inch]LP_Horizontal_Cleat_Length = {left_panel_components_data['horizontal_cleats']['length']:.3f}",
            f"[Inch]LP_Horizontal_Cleat_Material_Thickness = {left_panel_components_data['horizontal_cleats']['material_thickness']:.3f}",
            f"[Inch]LP_Horizontal_Cleat_Material_Member_Width = {left_panel_components_data['horizontal_cleats']['material_member_width']:.3f}",
            f"LP_Horizontal_Cleat_Count = {left_panel_components_data['horizontal_cleats']['count']}\n",

            f"// Vertical Cleats (Front & Back edges)",
            f"[Inch]LP_Vertical_Cleat_Length = {left_panel_components_data['vertical_cleats']['length']:.3f}",
            f"[Inch]LP_Vertical_Cleat_Material_Thickness = {left_panel_components_data['vertical_cleats']['material_thickness']:.3f}",
            f"[Inch]LP_Vertical_Cleat_Material_Member_Width = {left_panel_components_data['vertical_cleats']['material_member_width']:.3f}",
            f"LP_Vertical_Cleat_Count = {left_panel_components_data['vertical_cleats']['count']}",

            f"// Intermediate Vertical Cleats (Left Panel)",
            f"LP_Intermediate_Vertical_Cleat_Count = {lp_inter_vc_count}",
            f"[Inch]LP_Intermediate_Vertical_Cleat_Length = {lp_inter_vc_length:.3f}",
            f"[Inch]LP_Intermediate_Vertical_Cleat_Material_Thickness = {lp_inter_vc_material_thickness:.3f}",
            f"[Inch]LP_Intermediate_Vertical_Cleat_Material_Member_Width = {lp_inter_vc_material_member_width:.3f}",
            f"LP_Intermediate_Vertical_Cleat_Orientation_Code = {lp_inter_vc_orientation_code} // 0=Vertical, 1=Horizontal, 2=None",
            f"// Left Panel Intermediate Vertical Cleat Instance Data (Max {MAX_LP_INTERMEDIATE_VERTICAL_CLEATS} instances)"
        ]);

        for i in range(MAX_LP_INTERMEDIATE_VERTICAL_CLEATS):
            instance_num = i + 1
            if i < lp_inter_vc_count:
                expressions_content.append(f"LP_Inter_VC_Inst_{instance_num}_Suppress_Flag = {lp_suppress_flags[i]}")
                x_pos_centerline = lp_inter_vc_positions_centerline[i]
                expressions_content.append(f"[Inch]LP_Inter_VC_Inst_{instance_num}_X_Pos_Centerline = {x_pos_centerline:.4f}")
                x_pos_left_edge = lp_inter_vc_positions_left_edge[i]
                expressions_content.append(f"[Inch]LP_Inter_VC_Inst_{instance_num}_X_Pos_From_Left_Edge = {x_pos_left_edge:.4f}")
            else:
                expressions_content.append(f"LP_Inter_VC_Inst_{instance_num}_Suppress_Flag = 0")
                expressions_content.append(f"[Inch]LP_Inter_VC_Inst_{instance_num}_X_Pos_Centerline = 0.0000")
                expressions_content.append(f"[Inch]LP_Inter_VC_Inst_{instance_num}_X_Pos_From_Left_Edge = 0.0000")

        expressions_content.extend([
            f"\n// --- RIGHT PANEL ASSEMBLY DIMENSIONS ---",
            f"[Inch]RP_Panel_Assembly_Length = PANEL_End_Assy_Overall_Length_Face",
            f"[Inch]RP_Panel_Assembly_Height = PANEL_End_Assy_Overall_Height",
            f"[Inch]RP_Panel_Assembly_Depth = PANEL_End_Assy_Overall_Depth_Thickness\n",
            
            f"// --- RIGHT PANEL COMPONENT DETAILS ---",
            f"// Plywood Sheathing",
            f"[Inch]RP_Plywood_Length = {right_panel_components_data['plywood']['length']:.3f}",
            f"[Inch]RP_Plywood_Height = {right_panel_components_data['plywood']['height']:.3f}",
            f"[Inch]RP_Plywood_Thickness = {right_panel_components_data['plywood']['thickness']:.3f}\n",

            f"// Horizontal Cleats (Top & Bottom)",
            f"[Inch]RP_Horizontal_Cleat_Length = {right_panel_components_data['horizontal_cleats']['length']:.3f}",
            f"[Inch]RP_Horizontal_Cleat_Material_Thickness = {right_panel_components_data['horizontal_cleats']['material_thickness']:.3f}",
            f"[Inch]RP_Horizontal_Cleat_Material_Member_Width = {right_panel_components_data['horizontal_cleats']['material_member_width']:.3f}",
            f"RP_Horizontal_Cleat_Count = {right_panel_components_data['horizontal_cleats']['count']}\n",

            f"// Vertical Cleats (Front & Back edges)",
            f"[Inch]RP_Vertical_Cleat_Length = {right_panel_components_data['vertical_cleats']['length']:.3f}",
            f"[Inch]RP_Vertical_Cleat_Material_Thickness = {right_panel_components_data['vertical_cleats']['material_thickness']:.3f}",
            f"[Inch]RP_Vertical_Cleat_Material_Member_Width = {right_panel_components_data['vertical_cleats']['material_member_width']:.3f}",
            f"RP_Vertical_Cleat_Count = {right_panel_components_data['vertical_cleats']['count']}",

            f"// Intermediate Vertical Cleats (Right Panel)",
            f"RP_Intermediate_Vertical_Cleat_Count = {rp_inter_vc_count}",
            f"[Inch]RP_Intermediate_Vertical_Cleat_Length = {rp_inter_vc_length:.3f}",
            f"[Inch]RP_Intermediate_Vertical_Cleat_Material_Thickness = {rp_inter_vc_material_thickness:.3f}",
            f"[Inch]RP_Intermediate_Vertical_Cleat_Material_Member_Width = {rp_inter_vc_material_member_width:.3f}",
            f"RP_Intermediate_Vertical_Cleat_Orientation_Code = {rp_inter_vc_orientation_code} // 0=Vertical, 1=Horizontal, 2=None",
            f"// Right Panel Intermediate Vertical Cleat Instance Data (Max {MAX_RP_INTERMEDIATE_VERTICAL_CLEATS} instances)"
        ]);

        for i in range(MAX_RP_INTERMEDIATE_VERTICAL_CLEATS):
            instance_num = i + 1
            if i < rp_inter_vc_count:
                expressions_content.append(f"RP_Inter_VC_Inst_{instance_num}_Suppress_Flag = {rp_suppress_flags[i]}")
                x_pos_centerline = rp_inter_vc_positions_centerline[i]
                expressions_content.append(f"[Inch]RP_Inter_VC_Inst_{instance_num}_X_Pos_Centerline = {x_pos_centerline:.4f}")
                x_pos_left_edge = rp_inter_vc_positions_left_edge[i]
                expressions_content.append(f"[Inch]RP_Inter_VC_Inst_{instance_num}_X_Pos_From_Left_Edge = {x_pos_left_edge:.4f}")
            else:
                expressions_content.append(f"RP_Inter_VC_Inst_{instance_num}_Suppress_Flag = 0")
                expressions_content.append(f"[Inch]RP_Inter_VC_Inst_{instance_num}_X_Pos_Centerline = 0.0000")
                expressions_content.append(f"[Inch]RP_Inter_VC_Inst_{instance_num}_X_Pos_From_Left_Edge = 0.0000")

        # Calculate plywood layout for each panel
        plywood_layouts = {}
        if plywood_panel_selections is not None:
            for panel_code, selected in plywood_panel_selections.items():
                if selected:
                    if panel_code == "FP":
                        plywood_layouts[panel_code] = calculate_plywood_layout(front_panel_calc_width, front_panel_calc_height)
                    elif panel_code == "BP":
                        plywood_layouts[panel_code] = calculate_plywood_layout(back_panel_calc_width, back_panel_calc_height)
                    elif panel_code == "TP":
                        plywood_layouts[panel_code] = calculate_plywood_layout(top_panel_calc_width, top_panel_calc_length)
                    elif panel_code == "LP":
                        # Left panel: length goes horizontally (width for plywood), height goes vertically
                        plywood_layouts[panel_code] = calculate_plywood_layout(end_panel_calc_length, end_panel_calc_height)
                    elif panel_code == "RP":
                        # Right panel: same orientation as left panel
                        plywood_layouts[panel_code] = calculate_plywood_layout(end_panel_calc_length, end_panel_calc_height)

        # Generate NX expressions for plywood layout
        plywood_expressions = {}
        for panel_code, sheets in plywood_layouts.items():
            plywood_expressions[panel_code] = generate_plywood_nx_expressions(sheets, panel_code + "_")

        # Add plywood expressions to the main expressions content
        for panel_code, expressions in plywood_expressions.items():
            expressions_content.extend([
                f"\n// --- {panel_code} PANEL PLYWOOD LAYOUT ---",
                f"// Plywood Instance Data"
            ])
            expressions_content.extend(expressions)

        # Add Front Panel Intermediate Horizontal Cleat Data
        expressions_content.extend([
            f"\n// Front Panel Intermediate Horizontal Cleats (Sections Between Vertical Cleats)",
            f"FP_Intermediate_Horizontal_Cleat_Count = {fp_inter_hc_count}",
            f"[Inch]FP_Intermediate_Horizontal_Cleat_Material_Thickness = {fp_inter_hc_material_thickness:.3f}",
            f"[Inch]FP_Intermediate_Horizontal_Cleat_Material_Member_Width = {fp_inter_hc_material_member_width:.3f}",
            f"FP_Intermediate_Horizontal_Cleat_Orientation_Code = {fp_inter_hc_orientation_code} // 0=Vertical, 1=Horizontal, 2=None",
            f"FP_Intermediate_Horizontal_Cleat_Pattern_Count = {fp_inter_hc_pattern_count} // Pattern count for NX (1 or 2 based on splices)",
            f"FP_Intermediate_Horizontal_Cleat_Horizontal_Splice_Count = {fp_inter_hc_horizontal_splice_count} // Number of horizontal splices\n",
            f"// Front Panel Intermediate Horizontal Cleat Instance Data (Max {MAX_FP_INTERMEDIATE_HORIZONTAL_CLEATS} instances)"
        ])

        for i in range(MAX_FP_INTERMEDIATE_HORIZONTAL_CLEATS):
            instance_num = i + 1
            if i < fp_inter_hc_count and i < len(fp_inter_hc_sections):
                section = fp_inter_hc_sections[i]
                
                expressions_content.append(f"FP_Inter_HC_Inst_{instance_num}_Suppress_Flag = 1") # 1 to show
                
                # Extract section data
                x_pos = section.get('x_pos', 0.0)
                section_width = section.get('width', 0.0)
                y_pos_centerline = section.get('y_pos_centerline', 0.0)
                y_pos_bottom_edge = section.get('y_pos_bottom_edge', 0.0)
                
                # Dimensions for this section
                cleat_height = fp_inter_hc_material_member_width  # 3.5"
                cleat_width = section_width  # Variable based on gap between vertical cleats
                cleat_length = fp_inter_hc_material_thickness  # 1.5"
                
                expressions_content.append(f"[Inch]FP_Inter_HC_Inst_{instance_num}_Height = {cleat_height:.3f}")
                expressions_content.append(f"[Inch]FP_Inter_HC_Inst_{instance_num}_Width = {cleat_width:.3f}")
                expressions_content.append(f"[Inch]FP_Inter_HC_Inst_{instance_num}_Length = {cleat_length:.3f}")
                expressions_content.append(f"[Inch]FP_Inter_HC_Inst_{instance_num}_X_Pos = {x_pos:.3f}")
                expressions_content.append(f"[Inch]FP_Inter_HC_Inst_{instance_num}_Y_Pos = {y_pos_bottom_edge:.4f}")
                expressions_content.append(f"[Inch]FP_Inter_HC_Inst_{instance_num}_Y_Pos_Centerline = {y_pos_centerline:.4f}")
            else:
                expressions_content.append(f"FP_Inter_HC_Inst_{instance_num}_Suppress_Flag = 0") # 0 to suppress/hide
                expressions_content.append(f"[Inch]FP_Inter_HC_Inst_{instance_num}_Height = 0.001")  # Minimal non-zero for NX
                expressions_content.append(f"[Inch]FP_Inter_HC_Inst_{instance_num}_Width = 0.001")   # Minimal non-zero for NX
                expressions_content.append(f"[Inch]FP_Inter_HC_Inst_{instance_num}_Length = 0.001")  # Minimal non-zero for NX
                expressions_content.append(f"[Inch]FP_Inter_HC_Inst_{instance_num}_X_Pos = 0.001")    # Minimal non-zero for NX
                expressions_content.append(f"[Inch]FP_Inter_HC_Inst_{instance_num}_Y_Pos = 0.0010")   # Minimal non-zero for NX
                expressions_content.append(f"[Inch]FP_Inter_HC_Inst_{instance_num}_Y_Pos_Centerline = 0.0010")  # Minimal non-zero for NX

        # Add Back Panel Intermediate Horizontal Cleat Data
        expressions_content.extend([
            f"\n// Back Panel Intermediate Horizontal Cleats (Sections Between Vertical Cleats)",
            f"BP_Intermediate_Horizontal_Cleat_Count = {bp_inter_hc_count}",
            f"[Inch]BP_Intermediate_Horizontal_Cleat_Material_Thickness = {bp_inter_hc_material_thickness:.3f}",
            f"[Inch]BP_Intermediate_Horizontal_Cleat_Material_Member_Width = {bp_inter_hc_material_member_width:.3f}",
            f"BP_Intermediate_Horizontal_Cleat_Orientation_Code = 1 // 0=Vertical, 1=Horizontal, 2=None",
            f"BP_Intermediate_Horizontal_Cleat_Pattern_Count = {bp_inter_hc_pattern_count} // Pattern count for NX (1 or 2 based on splices)",
            f"BP_Intermediate_Horizontal_Cleat_Horizontal_Splice_Count = {bp_inter_hc_horizontal_splice_count} // Number of horizontal splices\n",
            f"// Back Panel Intermediate Horizontal Cleat Instance Data (Max {MAX_BP_INTERMEDIATE_HORIZONTAL_CLEATS} instances)"
        ])

        for i in range(MAX_BP_INTERMEDIATE_HORIZONTAL_CLEATS):
            instance_num = i + 1
            if i < bp_inter_hc_count and i < len(bp_inter_hc_sections):
                section = bp_inter_hc_sections[i]
                
                expressions_content.append(f"BP_Inter_HC_Inst_{instance_num}_Suppress_Flag = 1")
                
                # Extract section data
                x_pos = section.get('x_pos', 0.0)
                section_width = section.get('width', 0.0)
                y_pos_centerline = section.get('y_pos_centerline', 0.0)
                y_pos_bottom_edge = section.get('y_pos_bottom_edge', 0.0)
                
                # Dimensions for this section
                cleat_height = bp_inter_hc_material_member_width
                cleat_width = section_width
                cleat_length = bp_inter_hc_material_thickness
                
                expressions_content.append(f"[Inch]BP_Inter_HC_Inst_{instance_num}_Height = {cleat_height:.3f}")
                expressions_content.append(f"[Inch]BP_Inter_HC_Inst_{instance_num}_Width = {cleat_width:.3f}")
                expressions_content.append(f"[Inch]BP_Inter_HC_Inst_{instance_num}_Length = {cleat_length:.3f}")
                expressions_content.append(f"[Inch]BP_Inter_HC_Inst_{instance_num}_X_Pos = {x_pos:.3f}")
                expressions_content.append(f"[Inch]BP_Inter_HC_Inst_{instance_num}_Y_Pos = {y_pos_bottom_edge:.4f}")
                expressions_content.append(f"[Inch]BP_Inter_HC_Inst_{instance_num}_Y_Pos_Centerline = {y_pos_centerline:.4f}")
            else:
                expressions_content.append(f"BP_Inter_HC_Inst_{instance_num}_Suppress_Flag = 0")
                expressions_content.append(f"[Inch]BP_Inter_HC_Inst_{instance_num}_Height = 0.001")  # Minimal non-zero for NX
                expressions_content.append(f"[Inch]BP_Inter_HC_Inst_{instance_num}_Width = 0.001")   # Minimal non-zero for NX
                expressions_content.append(f"[Inch]BP_Inter_HC_Inst_{instance_num}_Length = 0.001")  # Minimal non-zero for NX
                expressions_content.append(f"[Inch]BP_Inter_HC_Inst_{instance_num}_X_Pos = 0.001")    # Minimal non-zero for NX
                expressions_content.append(f"[Inch]BP_Inter_HC_Inst_{instance_num}_Y_Pos = 0.0010")   # Minimal non-zero for NX
                expressions_content.append(f"[Inch]BP_Inter_HC_Inst_{instance_num}_Y_Pos_Centerline = 0.0010")  # Minimal non-zero for NX

        # Add Left Panel Intermediate Horizontal Cleat Data
        expressions_content.extend([
            f"\n// Left Panel Intermediate Horizontal Cleats (Sections Between Vertical Cleats)",
            f"LP_Intermediate_Horizontal_Cleat_Count = {lp_inter_hc_count}",
            f"[Inch]LP_Intermediate_Horizontal_Cleat_Material_Thickness = {lp_inter_hc_material_thickness:.3f}",
            f"[Inch]LP_Intermediate_Horizontal_Cleat_Material_Member_Width = {lp_inter_hc_material_member_width:.3f}",
            f"LP_Intermediate_Horizontal_Cleat_Orientation_Code = 1 // 0=Vertical, 1=Horizontal, 2=None",
            f"LP_Intermediate_Horizontal_Cleat_Pattern_Count = {lp_inter_hc_pattern_count} // Pattern count for NX (1 or 2 based on splices)",
            f"LP_Intermediate_Horizontal_Cleat_Horizontal_Splice_Count = {lp_inter_hc_horizontal_splice_count} // Number of horizontal splices\n",
            f"// Left Panel Intermediate Horizontal Cleat Instance Data (Max {MAX_LP_INTERMEDIATE_HORIZONTAL_CLEATS} instances)"
        ])

        for i in range(MAX_LP_INTERMEDIATE_HORIZONTAL_CLEATS):
            instance_num = i + 1
            if i < lp_inter_hc_count and i < len(lp_inter_hc_sections):
                section = lp_inter_hc_sections[i]
                
                expressions_content.append(f"LP_Inter_HC_Inst_{instance_num}_Suppress_Flag = 1")
                
                # Extract section data
                x_pos = section.get('x_pos', 0.0)
                section_width = section.get('width', 0.0)
                y_pos_centerline = section.get('y_pos_centerline', 0.0)
                y_pos_bottom_edge = section.get('y_pos_bottom_edge', 0.0)
                
                # Dimensions for this section
                cleat_height = lp_inter_hc_material_member_width
                cleat_width = section_width
                cleat_length = lp_inter_hc_material_thickness
                
                expressions_content.append(f"[Inch]LP_Inter_HC_Inst_{instance_num}_Height = {cleat_height:.3f}")
                expressions_content.append(f"[Inch]LP_Inter_HC_Inst_{instance_num}_Width = {cleat_width:.3f}")
                expressions_content.append(f"[Inch]LP_Inter_HC_Inst_{instance_num}_Length = {cleat_length:.3f}")
                expressions_content.append(f"[Inch]LP_Inter_HC_Inst_{instance_num}_X_Pos = {x_pos:.3f}")
                expressions_content.append(f"[Inch]LP_Inter_HC_Inst_{instance_num}_Y_Pos = {y_pos_bottom_edge:.4f}")
                expressions_content.append(f"[Inch]LP_Inter_HC_Inst_{instance_num}_Y_Pos_Centerline = {y_pos_centerline:.4f}")
            else:
                expressions_content.append(f"LP_Inter_HC_Inst_{instance_num}_Suppress_Flag = 0")
                expressions_content.append(f"[Inch]LP_Inter_HC_Inst_{instance_num}_Height = 0.001")  # Minimal non-zero for NX
                expressions_content.append(f"[Inch]LP_Inter_HC_Inst_{instance_num}_Width = 0.001")   # Minimal non-zero for NX
                expressions_content.append(f"[Inch]LP_Inter_HC_Inst_{instance_num}_Length = 0.001")  # Minimal non-zero for NX
                expressions_content.append(f"[Inch]LP_Inter_HC_Inst_{instance_num}_X_Pos = 0.001")    # Minimal non-zero for NX
                expressions_content.append(f"[Inch]LP_Inter_HC_Inst_{instance_num}_Y_Pos = 0.0010")   # Minimal non-zero for NX
                expressions_content.append(f"[Inch]LP_Inter_HC_Inst_{instance_num}_Y_Pos_Centerline = 0.0010")  # Minimal non-zero for NX

        # Add Right Panel Intermediate Horizontal Cleat Data
        expressions_content.extend([
            f"\n// Right Panel Intermediate Horizontal Cleat Sections Between Vertical Cleats)",
            f"RP_Intermediate_Horizontal_Cleat_Count = {rp_inter_hc_count}",
            f"[Inch]RP_Intermediate_Horizontal_Cleat_Material_Thickness = {rp_inter_hc_material_thickness:.3f}",
            f"[Inch]RP_Intermediate_Horizontal_Cleat_Material_Member_Width = {rp_inter_hc_material_member_width:.3f}",
            f"RP_Intermediate_Horizontal_Cleat_Orientation_Code = 1 // 0=Vertical, 1=Horizontal, 2=None",
            f"RP_Intermediate_Horizontal_Cleat_Pattern_Count = {rp_inter_hc_pattern_count} // Pattern count for NX (1 or 2 based on splices)",
            f"RP_Intermediate_Horizontal_Cleat_Horizontal_Splice_Count = {rp_inter_hc_horizontal_splice_count} // Number of horizontal splices\n",
            f"// Right Panel Intermediate Horizontal Cleat Instance Data (Max {MAX_RP_INTERMEDIATE_HORIZONTAL_CLEATS} instances)"
        ])

        for i in range(MAX_RP_INTERMEDIATE_HORIZONTAL_CLEATS):
            instance_num = i + 1
            if i < rp_inter_hc_count and i < len(rp_inter_hc_sections):
                section = rp_inter_hc_sections[i]
                
                expressions_content.append(f"RP_Inter_HC_Inst_{instance_num}_Suppress_Flag = 1")
                
                # Extract section data
                x_pos = section.get('x_pos', 0.0)
                section_width = section.get('width', 0.0)
                y_pos_centerline = section.get('y_pos_centerline', 0.0)
                y_pos_bottom_edge = section.get('y_pos_bottom_edge', 0.0)
                
                # Dimensions for this section
                cleat_height = rp_inter_hc_material_member_width
                cleat_width = section_width
                cleat_length = rp_inter_hc_material_thickness
                
                expressions_content.append(f"[Inch]RP_Inter_HC_Inst_{instance_num}_Height = {cleat_height:.3f}")
                expressions_content.append(f"[Inch]RP_Inter_HC_Inst_{instance_num}_Width = {cleat_width:.3f}")
                expressions_content.append(f"[Inch]RP_Inter_HC_Inst_{instance_num}_Length = {cleat_length:.3f}")
                expressions_content.append(f"[Inch]RP_Inter_HC_Inst_{instance_num}_X_Pos = {x_pos:.3f}")
                expressions_content.append(f"[Inch]RP_Inter_HC_Inst_{instance_num}_Y_Pos = {y_pos_bottom_edge:.4f}")
                expressions_content.append(f"[Inch]RP_Inter_HC_Inst_{instance_num}_Y_Pos_Centerline = {y_pos_centerline:.4f}")
            else:
                expressions_content.append(f"RP_Inter_HC_Inst_{instance_num}_Suppress_Flag = 0")
                expressions_content.append(f"[Inch]RP_Inter_HC_Inst_{instance_num}_Height = 0.001")  # Minimal non-zero for NX
                expressions_content.append(f"[Inch]RP_Inter_HC_Inst_{instance_num}_Width = 0.001")   # Minimal non-zero for NX
                expressions_content.append(f"[Inch]RP_Inter_HC_Inst_{instance_num}_Length = 0.001")  # Minimal non-zero for NX
                expressions_content.append(f"[Inch]RP_Inter_HC_Inst_{instance_num}_X_Pos = 0.001")    # Minimal non-zero for NX
                expressions_content.append(f"[Inch]RP_Inter_HC_Inst_{instance_num}_Y_Pos = 0.0010")   # Minimal non-zero for NX
                expressions_content.append(f"[Inch]RP_Inter_HC_Inst_{instance_num}_Y_Pos_Centerline = 0.0010")  # Minimal non-zero for NX

        expressions_content.append(f"// End of Expressions")

        # Validate output path for security
        safe_filename = validate_output_path(output_filename, os.path.dirname(output_filename))
        
        # Ensure file has safe extension
        if not is_safe_file_extension(safe_filename, ['.exp']):
            raise ValueError("Invalid file extension. Only .exp files are allowed.")
        
        with open(safe_filename, "w") as f:
            for line in expressions_content: f.write(line + "\n")
        
        duration = time.time() - start_time
        success_msg = f"Successfully generated: {output_filename}"
        
        if logger:
            result_info = {
                'output_file': safe_filename,
                'expressions_count': len(expressions_content),
                'file_size_bytes': os.path.getsize(safe_filename) if os.path.exists(safe_filename) else 0,
                'duration_seconds': round(duration, 3)
            }
            logger.info("Expression generation completed successfully", result_info)
            logger.log_performance("generate_crate_expressions", duration, result_info)
        
        return True, success_msg
    except Exception as e:
        duration = time.time() - start_time
        error_msg = f"Error: {e}"
        
        if logger:
            error_info = {
                'duration_seconds': round(duration, 3),
                'output_filename': output_filename,
                'traceback': traceback.format_exc()
            }
            logger.error("Expression generation failed", e, error_info)
        else:
            print(f"Error in logic: {e}\\n{traceback.format_exc()}")
        
        return False, error_msg

# --- Vertical Cleat Helper Functions ---
def extract_vertical_splice_positions(plywood_sheets: List[Dict]) -> List[float]:
    """
    Extract vertical splice positions from plywood layout.
    Vertical splices occur where plywood sheets meet side-by-side.
    """
    splice_positions = []
    
    # Group sheets by row (same Y position)
    rows = {}
    for sheet in plywood_sheets:
        y_pos = sheet['y']
        if y_pos not in rows:
            rows[y_pos] = []
        rows[y_pos].append(sheet)
    
    # For each row, find splice positions
    for y_pos, sheets_in_row in rows.items():
        # Sort sheets by X position
        sheets_in_row.sort(key=lambda s: s['x'])
        
        # Splice occurs at the right edge of each sheet (except the last one)
        for i in range(len(sheets_in_row) - 1):
            splice_x = sheets_in_row[i]['x'] + sheets_in_row[i]['width']
            splice_positions.append(splice_x)
    
    # Remove duplicates and sort
    unique_splices = sorted(list(set(splice_positions)))
    return unique_splices


def calculate_vertical_cleat_positions(panel_width: float, vertical_splices: List[float], 
                                     cleat_member_width: float) -> List[float]:
    """
    Calculate vertical cleat positions based on splices and 24" spacing requirements.
    Ensures no overlap with edge cleats.
    """
    TARGET_SPACING = 24.0
    MIN_EDGE_CLEARANCE = cleat_member_width  # Minimum clearance from edge cleats
    MIN_CLEAT_SPACING = 0.25  # Minimum gap between cleats to avoid interference
    
    # Calculate edge cleat positions (centerlines)
    left_edge_cleat_centerline = cleat_member_width / 2.0
    right_edge_cleat_centerline = panel_width - (cleat_member_width / 2.0)
    
    # Available width for intermediate cleats (between edge cleats)
    available_width = right_edge_cleat_centerline - left_edge_cleat_centerline
    
    cleat_positions = []
    
    # CRITICAL: Add cleats at ALL vertical splice positions - structural integrity is mandatory
    # Splices must always have cleat support regardless of spacing considerations
    for splice_x in vertical_splices:
        # Check if splice cleat would have adequate clearance from edge cleats
        left_clearance = splice_x - left_edge_cleat_centerline - cleat_member_width
        right_clearance = right_edge_cleat_centerline - splice_x - cleat_member_width
        
        # Only add splice cleat if it has minimum clearance from both edge cleats
        if left_clearance >= MIN_CLEAT_SPACING and right_clearance >= MIN_CLEAT_SPACING:
            cleat_positions.append(splice_x)
    
    # Sort splice-based cleat positions
    cleat_positions.sort()
    
    # Fill gaps larger than TARGET_SPACING with additional intermediate cleats
    final_positions = []
    last_pos = left_edge_cleat_centerline
    
    for cleat_pos in cleat_positions:
        # Fill gap before this cleat if needed
        gap = cleat_pos - last_pos
        while gap > TARGET_SPACING:
            new_cleat_pos = last_pos + TARGET_SPACING
            # Ensure new cleat doesn't conflict with edge cleats or other cleats
            left_clearance = new_cleat_pos - left_edge_cleat_centerline - cleat_member_width
            right_clearance = right_edge_cleat_centerline - new_cleat_pos - cleat_member_width
            
            if left_clearance >= MIN_CLEAT_SPACING and right_clearance >= MIN_CLEAT_SPACING:
                # Also check spacing from the next splice cleat
                if cleat_pos - new_cleat_pos - cleat_member_width >= MIN_CLEAT_SPACING:
                    final_positions.append(new_cleat_pos)
                    last_pos = new_cleat_pos
                else:
                    break  # Can't fit cleat here, stop trying
            else:
                break  # Can't fit cleat here
            gap = cleat_pos - last_pos
        
        final_positions.append(cleat_pos)
        last_pos = cleat_pos
    
    # Fill remaining gap to right edge if needed
    gap = right_edge_cleat_centerline - last_pos
    while gap > TARGET_SPACING:
        new_cleat_pos = last_pos + TARGET_SPACING
        # Ensure new cleat doesn't conflict with right edge cleat
        right_clearance = right_edge_cleat_centerline - new_cleat_pos - cleat_member_width
        if right_clearance >= MIN_CLEAT_SPACING:
            final_positions.append(new_cleat_pos)
            last_pos = new_cleat_pos
            gap = right_edge_cleat_centerline - last_pos
        else:
            break  # Can't fit more cleats
    
    return final_positions


def calculate_vertical_cleat_material_needed(panel_width: float, panel_height: float, 
                                           cleat_member_width: float) -> float:
    """
    Calculate material needed to resolve vertical cleat spacing conflicts.
    """
    MIN_CLEAT_SPACING = 0.25  # Minimum gap between cleats to avoid interference
    
    # Generate plywood layout
    plywood_sheets = calculate_plywood_layout(panel_width, panel_height)
    
    # Extract vertical splice positions
    vertical_splices = extract_vertical_splice_positions(plywood_sheets)
    
    if not vertical_splices:
        return 0.0
    
    # Calculate edge cleat positions
    left_edge_cleat_centerline = cleat_member_width / 2.0
    right_edge_cleat_centerline = panel_width - (cleat_member_width / 2.0)
    
    # Check if any splice is too close to the right edge
    material_needed = 0.0
    for splice_x in vertical_splices:
        # Check clearance from right edge cleat
        right_clearance = right_edge_cleat_centerline - splice_x - cleat_member_width
        
        # If splice cleat would be too close to right edge cleat, calculate material needed
        if right_clearance < MIN_CLEAT_SPACING:
            # Calculate how much we need to extend the panel
            extension_needed = MIN_CLEAT_SPACING - right_clearance + cleat_member_width
            # Round up to nearest 0.25"
            extension_needed = math.ceil(extension_needed / 0.25) * 0.25
            material_needed = max(material_needed, extension_needed)
    
    return material_needed


def update_panel_components_with_splice_cleats(panel_components: dict, panel_width: float, 
                                             panel_height: float, cleat_member_width: float) -> dict:
    """
    Update panel components with splice-based vertical cleat positions.
    """
    # Generate plywood layout
    plywood_sheets = calculate_plywood_layout(panel_width, panel_height)
    
    # Extract vertical splice positions
    vertical_splices = extract_vertical_splice_positions(plywood_sheets)
    
    # If there are no vertical splices, use the symmetric logic from the panel logic files
    if not vertical_splices:
        return panel_components
    
    # Calculate vertical cleat positions
    vertical_cleat_positions = calculate_vertical_cleat_positions(panel_width, vertical_splices, cleat_member_width)
    
    # Check if this is a top panel (has 'intermediate_cleats' instead of 'intermediate_vertical_cleats')
    if 'intermediate_cleats' in panel_components:
        # Top panel - update intermediate_cleats
        if vertical_cleat_positions:
            panel_components['intermediate_cleats']['count'] = len(vertical_cleat_positions)
            panel_components['intermediate_cleats']['orientation'] = "Vertical"
            panel_components['intermediate_cleats']['positions_x_centerline'] = [round(pos, 4) for pos in vertical_cleat_positions]
            # Calculate positions from left edge
            positions_left_edge = [round(pos - cleat_member_width/2, 4) for pos in vertical_cleat_positions]
            panel_components['intermediate_cleats']['positions_x_left_edge'] = positions_left_edge
            # Update suppress flags
            suppress_flags = [1] * len(vertical_cleat_positions) + [0] * (7 - len(vertical_cleat_positions))
            panel_components['intermediate_cleats']['suppress_flags'] = suppress_flags[:7]
        else:
            panel_components['intermediate_cleats']['count'] = 0
            panel_components['intermediate_cleats']['orientation'] = "None"
            panel_components['intermediate_cleats']['positions_x_centerline'] = []
            panel_components['intermediate_cleats']['positions_x_left_edge'] = []
            panel_components['intermediate_cleats']['suppress_flags'] = [0] * 7
    else:
        # Side panels - update intermediate_vertical_cleats
        if 'intermediate_vertical_cleats' not in panel_components:
            # Initialize with default values if missing
            panel_components['intermediate_vertical_cleats'] = {
                'count': 0,
                'length': panel_height - (2 * cleat_member_width),  # Between horizontal cleats
                'material_thickness': panel_components.get('vertical_cleats', {}).get('material_thickness', 1.25),
                'material_member_width': cleat_member_width,
                'positions_x_centerline': [],
                'positions_x_left_edge': [],
                'edge_to_edge_distances': [],
                'suppress_flags': [0] * 7,
                'orientation': "None"
            }
        
        if vertical_cleat_positions:
            # Update all required fields for intermediate vertical cleats
            panel_components['intermediate_vertical_cleats']['count'] = len(vertical_cleat_positions)
            panel_components['intermediate_vertical_cleats']['orientation'] = "Vertical"
            
            # Set centerline positions
            panel_components['intermediate_vertical_cleats']['positions_x_centerline'] = [round(pos, 4) for pos in vertical_cleat_positions]
            
            # Calculate left edge positions
            positions_left_edge = [round(pos - cleat_member_width/2, 4) for pos in vertical_cleat_positions]
            panel_components['intermediate_vertical_cleats']['positions_x_left_edge'] = positions_left_edge
            
            # Calculate edge-to-edge distances
            edge_to_edge_distances = []
            prev_right_edge = 0.0  # Start from left edge of plywood
            for left_pos in positions_left_edge:
                gap = round(left_pos - prev_right_edge, 4)
                edge_to_edge_distances.append(gap)
                prev_right_edge = left_pos + cleat_member_width
            panel_components['intermediate_vertical_cleats']['edge_to_edge_distances'] = edge_to_edge_distances
            
            # Update suppress flags (1 = active, 0 = suppressed)
            suppress_flags = [1] * len(vertical_cleat_positions) + [0] * (7 - len(vertical_cleat_positions))
            panel_components['intermediate_vertical_cleats']['suppress_flags'] = suppress_flags[:7]
        else:
            # No intermediate cleats needed
            panel_components['intermediate_vertical_cleats']['count'] = 0
            panel_components['intermediate_vertical_cleats']['orientation'] = "None"
            panel_components['intermediate_vertical_cleats']['positions_x_centerline'] = []
            panel_components['intermediate_vertical_cleats']['positions_x_left_edge'] = []
            panel_components['intermediate_vertical_cleats']['edge_to_edge_distances'] = []
            panel_components['intermediate_vertical_cleats']['suppress_flags'] = [0] * 7
    
    return panel_components

class CrateApp: 
    def __init__(self, master):
        self.master = master
        master.title("NX Crate Exporter (Updated Cleat Logic)")
        master.geometry("550x880")
        master.resizable(True, True)
        style = ttk.Style()
        style.theme_use('clam')
        main_frame = ttk.Frame(master, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Product Inputs Section
        product_frame = ttk.LabelFrame(main_frame, text="Product Specifications", padding="10")
        product_frame.grid(row=0, column=0, columnspan=2, pady=10, sticky="ew") 
        ttk.Label(product_frame, text="Product Weight (lbs):").grid(row=0, column=0, sticky="w", pady=2); self.weight_entry = ttk.Entry(product_frame, width=25); self.weight_entry.grid(row=0, column=1, sticky="ew", pady=2); self.weight_entry.insert(0, "8000.0")
        ttk.Label(product_frame, text="Product Length (in):").grid(row=1, column=0, sticky="w", pady=2); self.length_entry = ttk.Entry(product_frame, width=25); self.length_entry.grid(row=1, column=1, sticky="ew", pady=2); self.length_entry.insert(0, "96.0")
        ttk.Label(product_frame, text="Product Width (in):").grid(row=2, column=0, sticky="w", pady=2); self.width_entry = ttk.Entry(product_frame, width=25); self.width_entry.grid(row=2, column=1, sticky="ew", pady=2); self.width_entry.insert(0, "100.0")
        ttk.Label(product_frame, text="Side Clearance (in):").grid(row=3, column=0, sticky="w", pady=2); self.clearance_entry = ttk.Entry(product_frame, width=25); self.clearance_entry.grid(row=3, column=1, sticky="ew", pady=2); self.clearance_entry.insert(0, "2.0")
        self.allow_3x4_skids_var = tk.BooleanVar(value=True); ttk.Checkbutton(product_frame, text="Allow 3x4 skids", variable=self.allow_3x4_skids_var).grid(row=4, column=0, columnspan=2, sticky="w", pady=2)
        product_frame.columnconfigure(1, weight=1)

        # Crate Inputs Section
        crate_frame = ttk.LabelFrame(main_frame, text="Crate & Panel Specifications", padding="10")
        crate_frame.grid(row=1, column=0, columnspan=2, pady=10, sticky="ew")
        ttk.Label(crate_frame, text="Panel Thickness (in):").grid(row=0, column=0, sticky="w", pady=2); self.panel_thickness_entry = ttk.Entry(crate_frame, width=25); self.panel_thickness_entry.grid(row=0, column=1, sticky="ew", pady=2); self.panel_thickness_entry.insert(0, "0.25")
        ttk.Label(crate_frame, text="Cleat Thickness (in):").grid(row=1, column=0, sticky="w", pady=2); self.cleat_thickness_entry = ttk.Entry(crate_frame, width=25); self.cleat_thickness_entry.grid(row=1, column=1, sticky="ew", pady=2); self.cleat_thickness_entry.insert(0, "0.75")
        ttk.Label(crate_frame, text="Cleat Member Width (in):").grid(row=2, column=0, sticky="w", pady=2); self.cleat_member_width_entry = ttk.Entry(crate_frame, width=25); self.cleat_member_width_entry.grid(row=2, column=1, sticky="ew", pady=2); self.cleat_member_width_entry.insert(0, "3.5")
        ttk.Label(crate_frame, text="Product Height (in):").grid(row=3, column=0, sticky="w", pady=2); self.product_height_entry = ttk.Entry(crate_frame, width=25); self.product_height_entry.grid(row=3, column=1, sticky="ew", pady=2); self.product_height_entry.insert(0, "30.0")
        ttk.Label(crate_frame, text="Clearance Above Product (in):").grid(row=4, column=0, sticky="w", pady=2); self.clearance_above_entry = ttk.Entry(crate_frame, width=25); self.clearance_above_entry.grid(row=4, column=1, sticky="ew", pady=2); self.clearance_above_entry.insert(0, "2.0")
        ttk.Label(crate_frame, text="Ground Clearance (in):").grid(row=5, column=0, sticky="w", pady=2); self.ground_clearance_entry = ttk.Entry(crate_frame, width=25); self.ground_clearance_entry.grid(row=5, column=1, sticky="ew", pady=2); self.ground_clearance_entry.insert(0, "1.0")
        crate_frame.columnconfigure(1, weight=1)

        # Floorboard Inputs Section
        floorboard_frame = ttk.LabelFrame(main_frame, text="Floorboard Specifications", padding="10")
        floorboard_frame.grid(row=2, column=0, columnspan=2, pady=10, sticky="ew")
        ttk.Label(floorboard_frame, text="Floorboard Thickness (in):").grid(row=0, column=0, sticky="w", pady=2); self.floorboard_thickness_entry = ttk.Entry(floorboard_frame, width=25); self.floorboard_thickness_entry.grid(row=0, column=1, sticky="ew", pady=2); self.floorboard_thickness_entry.insert(0, "1.5")
        ttk.Label(floorboard_frame, text="Max Middle Gap (in):").grid(row=1, column=0, sticky="w", pady=2); self.max_gap_entry = ttk.Entry(floorboard_frame, width=25); self.max_gap_entry.grid(row=1, column=1, sticky="ew", pady=2); self.max_gap_entry.insert(0, "0.25")
        ttk.Label(floorboard_frame, text="Min Custom Width (in):").grid(row=2, column=0, sticky="w", pady=2); self.min_custom_entry = ttk.Entry(floorboard_frame, width=25); self.min_custom_entry.grid(row=2, column=1, sticky="ew", pady=2); self.min_custom_entry.insert(0, "2.5")
        self.force_custom_var = tk.BooleanVar(value=True); ttk.Checkbutton(floorboard_frame, text="Force small custom board", variable=self.force_custom_var).grid(row=3, column=0, columnspan=2, sticky="w", pady=2)
        floorboard_frame.columnconfigure(1, weight=1)

        # Lumber Selection Section
        lumber_frame = ttk.LabelFrame(main_frame, text="Available Lumber Widths", padding="10")
        lumber_frame.grid(row=3, column=0, columnspan=2, pady=10, sticky="ew")
        self.lumber_vars = {}
        lumber_widths = {"2x6 (5.5 in)": 5.5, "2x8 (7.25 in)": 7.25, "2x10 (9.25 in)": 9.25, "2x12 (11.25 in)": 11.25}
        for i, (name, width) in enumerate(lumber_widths.items()):
            var = tk.BooleanVar(value=True); self.lumber_vars[width] = var; ttk.Checkbutton(lumber_frame, text=name, variable=var).grid(row=i//2, column=i%2, sticky="w", pady=2)

        # Plywood panels are always enabled for all 5 panels (FP, BP, LP, RP, TP)

        # Output Section
        output_frame = ttk.LabelFrame(main_frame, text="Output", padding="10")
        output_frame.grid(row=4, column=0, columnspan=2, pady=10, sticky="ew")
        self.generate_button = ttk.Button(output_frame, text="Generate NX Expressions", command=self.generate_expressions)
        self.generate_button.grid(row=0, column=0, pady=10, padx=(0, 5), sticky="ew")
        self.test_button = ttk.Button(output_frame, text="Quick Test Suite", command=self.run_quick_test_suite)
        self.test_button.grid(row=0, column=1, pady=10, padx=(5, 0), sticky="ew")
        output_frame.columnconfigure(0, weight=1)
        output_frame.columnconfigure(1, weight=1)

        # Status Section
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=5, column=0, columnspan=2, pady=10, sticky="ew")
        self.status_text = tk.Text(status_frame, height=8, width=60)
        self.status_text.grid(row=0, column=0, sticky="ew")
        scrollbar = ttk.Scrollbar(status_frame, orient="vertical", command=self.status_text.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.status_text.configure(yscrollcommand=scrollbar.set)
        status_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(5, weight=1)
        master.columnconfigure(0, weight=1)
        master.rowconfigure(0, weight=1)
        
        # Ensure buttons are properly configured and focusable
        self.generate_button.configure(state='normal')
        self.test_button.configure(state='normal')
        master.focus_force()
        master.update_idletasks()

    def log_message(self, message): 
        self.status_text.insert(tk.END, f"{datetime.datetime.now().strftime('%H:%M:%S')} - {message}\\n"); self.status_text.see(tk.END); self.master.update_idletasks()

    def generate_expressions(self):
        try:
            # Get and validate inputs with proper error handling
            product_weight = validate_numeric_input(self.weight_entry.get(), 1, 100000, "Product Weight")
            product_length = validate_numeric_input(self.length_entry.get(), 12, 130, "Product Length")
            product_width = validate_numeric_input(self.width_entry.get(), 12, 130, "Product Width")
            clearance = validate_numeric_input(self.clearance_entry.get(), 0.1, 50, "Clearance")
            panel_thickness = validate_numeric_input(self.panel_thickness_entry.get(), 0.1, 5, "Panel Thickness")
            cleat_thickness = validate_numeric_input(self.cleat_thickness_entry.get(), 0.1, 5, "Cleat Thickness")
            cleat_member_width = validate_numeric_input(self.cleat_member_width_entry.get(), 0.5, 20, "Cleat Member Width")
            product_height = validate_numeric_input(self.product_height_entry.get(), 12, 130, "Product Height")
            clearance_above = validate_numeric_input(self.clearance_above_entry.get(), 0.1, 50, "Clearance Above")
            ground_clearance = validate_numeric_input(self.ground_clearance_entry.get(), 0.1, 50, "Ground Clearance")
            floorboard_thickness = validate_numeric_input(self.floorboard_thickness_entry.get(), 0.5, 10, "Floorboard Thickness")
            max_gap = validate_numeric_input(self.max_gap_entry.get(), 0, 50, "Max Gap")
            min_custom = validate_numeric_input(self.min_custom_entry.get(), 0.5, 50, "Min Custom")
           
            # Create expressions folder in the main application directory
            import os
            import sys
            from datetime import datetime
            
            # Get the main application directory (where the main.py or executable is located)
            if getattr(sys, 'frozen', False):
                # Running as compiled executable
                root_dir = os.path.dirname(sys.executable)
            else:
                # Running as script - go up one level from autocrate folder
                current_file = os.path.abspath(__file__)
                autocrate_dir = os.path.dirname(current_file)
                root_dir = os.path.dirname(autocrate_dir)
            
            expressions_dir = os.path.join(root_dir, "expressions")
            if not create_secure_directory(expressions_dir):
                raise Exception(f"Failed to create expressions directory: {expressions_dir}")
            self.log_message(f"Using expressions directory: {expressions_dir}")
            
            # Generate timestamp prefix for sorting (YYYYMMDD_HHMMSS format)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Determine material type based on panel thickness
            material_type = "PLY" if panel_thickness >= 0.5 else "OSB"
            
            # Generate enhanced filename with more parameters
            # Include: timestamp, dimensions, weight, material type, panel thickness, clearance
            # Enhanced to include more parameters for better identification
            panel_count = 5  # Always 5 panels (Front, Back, Left, Right, Top)
            base_filename = (f"{timestamp}_Crate_"
                           f"{product_length:.0f}x{product_width:.0f}x{product_height:.0f}_"
                           f"W{product_weight:.0f}_"
                           f"{panel_count}P_"
                           f"{material_type}{panel_thickness:.2f}_"
                           f"C{clearance:.1f}_"
                           f"ASTM.exp")
            
            # Sanitize and ensure we stay within Windows path limits
            safe_filename = sanitize_filename(base_filename)
            # Truncate if necessary to stay within Windows limits (260 chars total path)
            max_filename_length = 200  # Leave room for path
            if len(safe_filename) > max_filename_length:
                # Keep timestamp and extension, truncate middle
                safe_filename = safe_filename[:max_filename_length-4] + ".exp"
            
            # Check if file exists and replace it (no timestamp suffix for duplicates)
            output_filename = os.path.join(expressions_dir, safe_filename)
            
            selected_lumber = [width for width, var in self.lumber_vars.items() if var.get()]
            # Always enable all 5 panels: Front, Back, Left, Right, Top (no End Panel)
            plywood_selections = {"FP": True, "BP": True, "LP": True, "RP": True, "TP": True}
            self.log_message("Starting expression generation...")
            self.log_message(f"Output file: {output_filename}")
            success, message = generate_crate_expressions_logic(product_weight, product_length, product_width, clearance, self.allow_3x4_skids_var.get(), panel_thickness, cleat_thickness, cleat_member_width, product_height, clearance_above, ground_clearance, floorboard_thickness, selected_lumber, max_gap, min_custom, self.force_custom_var.get(), output_filename, plywood_selections)
            if success: self.log_message(f"SUCCESS: {message}"); messagebox.showinfo("Success", message)
            else: self.log_message(f"ERROR: {message}"); messagebox.showerror("Error", message)
        except ValueError as e: self.log_message(f"INPUT ERROR: {e}"); messagebox.showerror("Input Error", f"Invalid input: {e}")
        except Exception as e: self.log_message(f"UNEXPECTED ERROR: {e}"); messagebox.showerror("Error", f"Unexpected error: {e}")

    def run_quick_test_suite(self):
        """Generate multiple test cases for corner cases and edge scenarios."""
        try:
            import os
            import sys
            from datetime import datetime
            
            # Get the main application directory (where the main.py or executable is located)
            if getattr(sys, 'frozen', False):
                # Running as compiled executable
                root_dir = os.path.dirname(sys.executable)
            else:
                # Running as script - go up one level from autocrate folder
                current_file = os.path.abspath(__file__)
                autocrate_dir = os.path.dirname(current_file)
                root_dir = os.path.dirname(autocrate_dir)
            
            # Create expressions folder and quick_test subfolder
            expressions_dir = os.path.join(root_dir, "expressions")
            quick_test_dir = os.path.join(expressions_dir, "quick_test")
            
            if not create_secure_directory(expressions_dir):
                raise Exception(f"Failed to create expressions directory: {expressions_dir}")
            if not create_secure_directory(quick_test_dir):
                raise Exception(f"Failed to create quick test directory: {quick_test_dir}")
                
            self.log_message(f"Using quick test directory: {quick_test_dir}")
            
            # Define test cases with corner cases and edge scenarios
            test_cases = [
                # Format: (product_weight, product_length, product_width, product_height, clearance, description)
                # All dimensions must be within 12-130 inches as per constraints
                (1000, 20, 20, 100, 1.0, "Very Tall Thin - Horizontal Splice Bug Test"),
                (500, 96, 48, 30, 2.0, "Standard Plywood Size"),
                (2000, 120, 120, 48, 1.5, "Large Square Heavy"),
                (100, 12, 12, 24, 0.5, "Very Small Light"),  # Updated description
                (5000, 130, 120, 60, 3.0, "Very Large Heavy"),
                (800, 30, 30, 80, 1.0, "Medium Square Tall"),
                (1500, 100, 50, 40, 2.5, "Long Narrow"),
                (300, 48, 48, 48, 1.0, "Perfect Cube"),
                (10000, 130, 130, 72, 4.0, "Maximum Size Heavy"),
                (50, 12, 12, 12, 0.25, "Minimum Size Light"),
            ]
            
            self.log_message("Starting Quick Test Suite generation...")
            self.log_message(f"Generating {len(test_cases)} test cases...")
            
            # Use current GUI settings for common parameters
            panel_thickness = float(self.panel_thickness_entry.get())
            cleat_thickness = float(self.cleat_thickness_entry.get()) 
            cleat_member_width = float(self.cleat_member_width_entry.get())
            clearance_above = float(self.clearance_above_entry.get())
            ground_clearance = float(self.ground_clearance_entry.get())
            floorboard_thickness = float(self.floorboard_thickness_entry.get())
            max_gap = float(self.max_gap_entry.get())
            min_custom = float(self.min_custom_entry.get())
            selected_lumber = [width for width, var in self.lumber_vars.items() if var.get()]
            plywood_selections = {"FP": True, "BP": True, "LP": True, "RP": True, "TP": True}
            
            successful_tests = 0
            failed_tests = 0
            
            for i, (weight, length, width, height, clearance, description) in enumerate(test_cases, 1):
                try:
                    # Generate timestamp for this test
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    
                    # Generate enhanced filename with timestamp and parameters
                    # Include all relevant parameters for better test identification
                    material_type = "PLY" if panel_thickness >= 0.5 else "OSB"
                    filename = (f"{timestamp}_QuickTest_{i:02d}_"
                              f"{length:.0f}x{width:.0f}x{height:.0f}_"
                              f"W{weight:.0f}_"
                              f"{material_type}{panel_thickness:.2f}_"
                              f"C{clearance:.1f}_"
                              f"{description.replace(' ', '_').replace('-', '')}.exp")
                    
                    # Sanitize and truncate if necessary
                    safe_filename = sanitize_filename(filename)
                    if len(safe_filename) > 200:
                        safe_filename = safe_filename[:196] + ".exp"
                    
                    output_filename = os.path.join(quick_test_dir, safe_filename)
                    
                    self.log_message(f"Test {i}/10: {description}")
                    
                    # Generate expressions
                    success, message = generate_crate_expressions_logic(
                        weight, length, width, clearance, self.allow_3x4_skids_var.get(),
                        panel_thickness, cleat_thickness, cleat_member_width, height,
                        clearance_above, ground_clearance, floorboard_thickness,
                        selected_lumber, max_gap, min_custom, self.force_custom_var.get(),
                        output_filename, plywood_selections
                    )
                    
                    if success:
                        successful_tests += 1
                        self.log_message(f"  [SUCCESS] Generated: {filename}")
                    else:
                        failed_tests += 1
                        self.log_message(f"  [FAILED] {message}")
                        
                except Exception as e:
                    failed_tests += 1
                    self.log_message(f"  [ERROR] Test {i} failed: {e}")
            
            # Summary
            self.log_message("=" * 50)
            self.log_message(f"Quick Test Suite Complete!")
            self.log_message(f"Successful: {successful_tests}/{len(test_cases)}")
            self.log_message(f"Failed: {failed_tests}/{len(test_cases)}")
            self.log_message(f"Output directory: {quick_test_dir}")
            
            if failed_tests == 0:
                messagebox.showinfo("Quick Test Suite", 
                    f"All {successful_tests} test cases generated successfully!\n\n"
                    f"Files saved to: quick_test_expressions/")
            else:
                messagebox.showwarning("Quick Test Suite", 
                    f"Generated {successful_tests} test cases successfully.\n"
                    f"{failed_tests} tests failed - see log for details.\n\n"
                    f"Files saved to: quick_test_expressions/")
                    
        except Exception as e:
            self.log_message(f"QUICK TEST ERROR: {e}")
            messagebox.showerror("Quick Test Error", f"Error running quick test suite: {e}")

def calculate_horizontal_cleat_sections_from_vertical_positions(
    panel_width: float,
    cleat_member_width: float,
    intermediate_vc_positions: list,
    splice_y_position: float,
    min_cleat_width: float = 0.25
) -> list:
    """
    Calculate horizontal cleat sections based on actual vertical cleat positions.
    Uses the same positions that generate the NX expressions for vertical cleats.
    
    Args:
        panel_width: Width of the panel in inches
        cleat_member_width: Width of cleat member (3.5")
        intermediate_vc_positions: List of intermediate vertical cleat centerline positions
        splice_y_position: Y position where horizontal splice occurs
        min_cleat_width: Minimum cleat section width (default 0.25")
        
    Returns:
        List of cleat section dictionaries with x_pos, width, y_pos data
    """
    sections = []
    
    # Get ALL vertical cleat positions (edge cleats + intermediate cleats)
    vertical_positions = []
    
    # Add left edge cleat centerline at cleat_member_width/2 from left edge
    vertical_positions.append(cleat_member_width / 2.0)
    
    # Add intermediate vertical cleats
    vertical_positions.extend(intermediate_vc_positions)
    
    # Add right edge cleat centerline at (panel_width - cleat_member_width/2)
    vertical_positions.append(panel_width - (cleat_member_width / 2.0))
    
    # Sort positions to ensure proper order
    vertical_positions.sort()
    
    # Calculate sections between adjacent vertical cleats
    for i in range(len(vertical_positions) - 1):
        left_cleat_center = vertical_positions[i]
        right_cleat_center = vertical_positions[i + 1]
        
        # Calculate the gap between cleats
        # Left edge of section = right edge of left cleat
        section_left_edge = left_cleat_center + (cleat_member_width / 2.0)
        # Right edge of section = left edge of right cleat  
        section_right_edge = right_cleat_center - (cleat_member_width / 2.0)
        
        # Calculate section width
        section_width = section_right_edge - section_left_edge
        
        # Since panel width is adjusted to accommodate proper spacing,
        # any negative width indicates we should calculate the actual gap differently
        if section_width < 0:
            # Calculate the actual gap as center-to-center distance minus cleat width
            center_to_center_distance = right_cleat_center - left_cleat_center
            section_width = center_to_center_distance - cleat_member_width
            # Position remains at the right edge of the left cleat
            section_left_edge = left_cleat_center + (cleat_member_width / 2.0)
        
        # Only add section if it meets minimum width requirement and is positive
        if section_width >= min_cleat_width and section_width > 0:
            sections.append({
                'x_pos': section_left_edge,  # Left edge position
                'width': section_width,
                'y_pos_centerline': splice_y_position,
                'y_pos_bottom_edge': splice_y_position - (cleat_member_width / 2.0)
            })
    
    return sections
        

if __name__ == "__main__":
    # Use the original UI (reverted from fast modern UI)
    root = tk.Tk()
    app = CrateApp(root)
    root.mainloop()
