"""
NX Expression Generation Service - Full Version
Generates complete NX expression files compatible with Siemens NX CAD
Matches desktop version variable naming exactly for CAD part compatibility
"""

import os
import sys
import datetime
from typing import Dict, List, Any, Optional

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import all the calculation modules
from autocrate.front_panel_logic import calculate_front_panel_components
from autocrate.back_panel_logic import calculate_back_panel_components  
from autocrate.left_panel_logic import calculate_left_panel_components
# Right panel uses left panel logic
from autocrate.end_panel_logic import calculate_end_panel_components
from autocrate.top_panel_logic import calculate_top_panel_components
from autocrate.floorboard_logic import calculate_floorboard_layout
from autocrate.skid_logic import calculate_skid_layout, calculate_skid_lumber_properties

def generate_full_nx_expression_content(
    product_weight: float,
    product_length: float,
    product_width: float,
    product_height: float,
    clearance: float = 2.0,
    panel_thickness: float = 0.75,
    cleat_thickness: float = 1.5,
    cleat_width: float = 3.5,
    include_top: bool = True,
    lumber_sizes: List[str] = None,
    ground_clearance: float = 4.0,
    floorboard_thickness: float = 1.5
) -> str:
    """
    Generate complete NX expression file content with all required variables
    matching desktop version exactly for CAD compatibility
    """
    
    if lumber_sizes is None:
        lumber_sizes = ["1.5x3.5", "1.5x5.5"]
    
    # Calculate crate dimensions - MUST match local version logic
    crate_internal_length = product_length + 2 * clearance
    crate_internal_width = product_width + 2 * clearance
    crate_internal_height = product_height + clearance
    
    # Panel assembly dimensions - MATCH LOCAL VERSION EXACTLY
    # Calculate panel total thickness (cleat + plywood)
    panel_total_thickness = cleat_thickness + panel_thickness
    
    # Front/Back panels calculation from local version
    front_panel_width = product_width + (2 * clearance) + (2 * panel_total_thickness)
    front_panel_height = crate_internal_height + cleat_width  # This stays the same
    back_panel_width = front_panel_width  # Back panel same as front
    back_panel_height = front_panel_height
    
    # Left/Right panels (End panels) fit between front and back
    left_panel_width = crate_internal_width + 2 * panel_thickness
    left_panel_height = front_panel_height
    right_panel_width = left_panel_width
    right_panel_height = left_panel_height
    
    # Top panel covers everything
    top_panel_length = crate_internal_length + 2 * (cleat_thickness + panel_thickness)
    top_panel_width = front_panel_width  # Should match front panel width
    
    # Calculate all panel components - match local version parameter names
    front_components = calculate_front_panel_components(
        front_panel_assembly_width=front_panel_width,
        front_panel_assembly_height=front_panel_height,
        panel_sheathing_thickness=panel_thickness,
        cleat_material_thickness=cleat_thickness,
        cleat_material_member_width=cleat_width,
        include_klimps=True
    )
    
    back_components = calculate_back_panel_components(
        back_panel_assembly_width=back_panel_width,
        back_panel_assembly_height=back_panel_height,
        panel_sheathing_thickness=panel_thickness,
        cleat_material_thickness=cleat_thickness,
        cleat_material_member_width=cleat_width
    )
    
    left_components = calculate_left_panel_components(
        left_panel_assembly_length=left_panel_width,
        left_panel_assembly_height=left_panel_height,
        panel_sheathing_thickness=panel_thickness,
        cleat_material_thickness=cleat_thickness,
        cleat_material_member_width=cleat_width
    )
    
    # Right panel uses left panel logic
    right_components = calculate_left_panel_components(
        left_panel_assembly_length=right_panel_width,
        left_panel_assembly_height=right_panel_height,
        panel_sheathing_thickness=panel_thickness,
        cleat_material_thickness=cleat_thickness,
        cleat_material_member_width=cleat_width
    )
    
    if include_top:
        top_components = calculate_top_panel_components(
            top_panel_assembly_width=top_panel_width,
            top_panel_assembly_length=top_panel_length,
            panel_sheathing_thickness=panel_thickness,
            cleat_material_thickness=cleat_thickness,
            cleat_material_member_width=cleat_width
        )
    else:
        top_components = None
    
    # Calculate skids using proper logic
    skid_props = calculate_skid_lumber_properties(
        product_weight_lbs=product_weight,
        allow_3x4_skids_bool=True
    )
    skid_actual_height_in = skid_props["skid_actual_height_in"]
    skid_actual_width_in = skid_props["skid_actual_width_in"]
    lumber_callout = skid_props["lumber_callout"]
    
    # Calculate skid layout
    skid_layout = calculate_skid_layout(
        crate_overall_width_od_in=crate_internal_width + 2 * panel_thickness,
        skid_actual_width_in=skid_actual_width_in,
        max_skid_spacing_rule_in=skid_props["max_skid_spacing_rule_in"]
    )
    
    skid_data = {
        'lumber_size': lumber_callout,
        'skid_height': skid_actual_height_in,
        'skid_width': skid_actual_width_in,
        'skid_count': skid_layout['calc_skid_count'],
        'skid_pitch': skid_layout['calc_skid_pitch_in'],
        'first_skid_pos': skid_layout['calc_first_skid_pos_x_in']
    }
    
    # Calculate floorboard layout with proper parameters
    # Usable coverage is the internal width of the crate
    fb_usable_coverage_y_in = crate_internal_width
    # Start offset calculation
    fb_initial_start_y_offset_abs = skid_actual_width_in / 2
    
    # Use default lumber widths if not provided
    selected_std_lumber_widths = [5.5, 3.5, 1.5]  # Standard lumber widths
    
    floorboard_data = calculate_floorboard_layout(
        fb_usable_coverage_y_in=fb_usable_coverage_y_in,
        fb_initial_start_y_offset_abs=fb_initial_start_y_offset_abs,
        selected_std_lumber_widths=selected_std_lumber_widths,
        min_custom_lumber_width_in=1.5,
        force_small_custom_board_bool=False
    )
    
    # Build expression file content
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = []
    
    # Header - NX style comments
    lines.append("// NX Expressions - AutoCrate V12 Web Edition")
    lines.append(f"// Generated: {timestamp}")
    lines.append("// Compatible with AutoCrate NX CAD Parts Library")
    lines.append("")
    
    # ============ USER INPUTS & CRATE CONSTANTS ============
    lines.append("// =========== USER INPUTS & CRATE CONSTANTS ===========")
    lines.append(f"[lbm]product_weight = {product_weight:.3f}")
    lines.append(f"[Inch]product_length_input = {product_length:.3f}")
    lines.append(f"[Inch]product_width_input = {product_width:.3f}")
    lines.append(f"[Inch]INPUT_Product_Actual_Height = {product_height:.3f}")
    lines.append("")
    
    lines.append(f"[Inch]clearance_side_input = {clearance:.3f}")
    lines.append(f"[Inch]INPUT_Clearance_Above_Product = {clearance:.3f}")
    lines.append(f"[Inch]INPUT_Ground_Clearance_End_Panels = {ground_clearance:.3f}")
    lines.append("")
    
    lines.append(f"[Inch]INPUT_Panel_Thickness = {panel_thickness:.3f}")
    lines.append(f"[Inch]INPUT_Cleat_Thickness = {cleat_thickness:.3f}")
    lines.append(f"[Inch]INPUT_Cleat_Member_Actual_Width = {cleat_width:.3f}")
    lines.append("")
    
    lines.append("BOOL_Allow_3x4_Skids_Input = 1")
    lines.append("BOOL_Force_Small_Custom_Floorboard = 0")
    lines.append(f"[Inch]INPUT_Floorboard_Actual_Thickness = {floorboard_thickness:.3f}")
    lines.append("[Inch]INPUT_Max_Allowable_Middle_Gap = 6.000")
    lines.append("[Inch]INPUT_Min_Custom_Lumber_Width = 1.500")
    lines.append("")
    
    # ============ CALCULATED CRATE DIMENSIONS ============
    lines.append("// =========== CALCULATED CRATE DIMENSIONS ===========")
    # Overall dimensions - external measurements
    crate_external_width = front_panel_width  # Width is along the front panel
    crate_external_length = top_panel_length  # Use top panel length for overall length
    lines.append(f"[Inch]crate_overall_width_OD = {crate_external_width:.3f}")
    lines.append(f"[Inch]crate_overall_length_OD = {crate_external_length:.3f}")
    lines.append("")
    
    # ============ SKID PARAMETERS ============
    if skid_data:
        lines.append("// =========== SKID PARAMETERS ===========")
        lines.append(f"// Skid Lumber: {skid_data.get('lumber_size', '4x4')}")
        lines.append(f"[Inch]Skid_Actual_Height = {skid_data.get('skid_height', 3.5):.3f}")
        lines.append(f"[Inch]Skid_Actual_Width = {skid_data.get('skid_width', 3.5):.3f}")
        lines.append(f"[Inch]Skid_Actual_Length = {front_panel_width:.3f}")
        lines.append(f"CALC_Skid_Count = {skid_data.get('skid_count', 3)}")
        
        # Calculate skid pitch using correct dimension
        if skid_data.get('skid_count', 3) > 1:
            skid_pitch = skid_data.get('skid_pitch', 0)
        else:
            skid_pitch = 0
        lines.append(f"[Inch]CALC_Skid_Pitch = {skid_pitch:.4f}")
        lines.append(f"[Inch]X_Master_Skid_Origin_Offset = {skid_data.get('first_skid_pos', 0):.4f}")
        lines.append("")
    
    # ============ FLOORBOARD PARAMETERS ============
    if floorboard_data:
        lines.append("// =========== FLOORBOARD PARAMETERS ===========")
        lines.append(f"[Inch]FB_Board_Actual_Length = {front_panel_width:.3f}")
        lines.append(f"[Inch]FB_Board_Actual_Thickness = {floorboard_thickness:.3f}")
        
        # Get floorboard configuration from correct structure
        boards = floorboard_data.get('floorboards_data', [])
        middle_gap = floorboard_data.get('actual_middle_gap', 0)
        
        lines.append(f"[Inch]CALC_FB_Actual_Middle_Gap = {middle_gap:.3f}")
        
        # Get center custom board width directly from data
        center_board_width = floorboard_data.get('center_custom_board_width', 0)
        lines.append(f"[Inch]CALC_FB_Center_Custom_Board_Width = {center_board_width:.3f}")
        
        # Calculate start Y offset
        if boards:
            min_y = min(board.get('y_position', 0) for board in boards)
            lines.append(f"[Inch]CALC_FB_Start_Y_Offset_Abs = {abs(min_y):.3f}")
        else:
            lines.append("[Inch]CALC_FB_Start_Y_Offset_Abs = 0.000")
        
        # Floorboard instances (1-20)
        for i in range(1, 21):
            if i <= len(boards):
                board = boards[i-1]
                lines.append(f"FB_Inst_{i}_Suppress_Flag = 1")  # 1 = show in NX
                lines.append(f"[Inch]FB_Inst_{i}_Actual_Width = {board.get('width', 5.5):.3f}")
                lines.append(f"[Inch]FB_Inst_{i}_Y_Pos_Abs = {abs(board.get('y_position', 0)):.3f}")
            else:
                lines.append(f"FB_Inst_{i}_Suppress_Flag = 0")  # 0 = hide in NX
                lines.append(f"[Inch]FB_Inst_{i}_Actual_Width = 0.001")
                lines.append(f"[Inch]FB_Inst_{i}_Y_Pos_Abs = 0.001")
        lines.append("")
    
    # ============ OVERALL PANEL ASSEMBLY DIMENSIONS ============
    lines.append("\n// --- OVERALL PANEL ASSEMBLY DIMENSIONS (Informational) ---")
    lines.append(f"[Inch]PANEL_Front_Assy_Overall_Width = {front_panel_width:.3f}")
    lines.append(f"[Inch]PANEL_Front_Assy_Overall_Height = {front_panel_height:.3f}")
    lines.append(f"[Inch]PANEL_Front_Assy_Overall_Depth = {panel_total_thickness:.3f}")
    lines.append(f"[Inch]PANEL_Back_Assy_Overall_Width = {back_panel_width:.3f}")
    lines.append(f"[Inch]PANEL_Back_Assy_Overall_Height = {back_panel_height:.3f}")
    lines.append(f"[Inch]PANEL_Back_Assy_Overall_Depth = {panel_total_thickness:.3f}")
    lines.append(f"[Inch]PANEL_End_Assy_Overall_Width = {left_panel_width:.3f} // For Left & Right End Panels")
    lines.append(f"[Inch]PANEL_End_Assy_Overall_Height = {left_panel_height:.3f}")
    lines.append(f"[Inch]PANEL_End_Assy_Overall_Depth_Thickness = {panel_total_thickness:.3f}")
    lines.append(f"[Inch]PANEL_Top_Assy_Overall_Width = {top_panel_width:.3f}")
    lines.append(f"[Inch]PANEL_Top_Assy_Overall_Length = {top_panel_length:.3f}")
    lines.append(f"[Inch]PANEL_Top_Assy_Overall_Depth_Thickness = {panel_total_thickness:.3f}")

    # ============ FRONT PANEL VARIABLES ============
    lines.append("\n// =========== FRONT PANEL (FP) ===========")
    lines.append(f"[Inch]FP_Panel_Assembly_Width = PANEL_Front_Assy_Overall_Width")
    lines.append(f"[Inch]FP_Panel_Assembly_Height = PANEL_Front_Assy_Overall_Height")
    lines.append(f"[Inch]FP_Panel_Assembly_Depth = PANEL_Front_Assy_Overall_Depth")
    lines.append("")
    lines.append(f"[Inch]FP_Plywood_Width = {front_components['plywood']['width']:.3f}")
    lines.append(f"[Inch]FP_Plywood_Height = {front_components['plywood']['height']:.3f}")
    lines.append(f"[Inch]FP_Plywood_Thickness = {panel_thickness:.3f}")
    lines.append("")
    add_panel_cleats_and_components(lines, "FP", front_components, front_panel_width, front_panel_height, cleat_thickness, cleat_width, panel_thickness)

    # ============ BACK PANEL VARIABLES ============
    lines.append("\n// =========== BACK PANEL (BP) ===========")
    lines.append(f"[Inch]BP_Panel_Assembly_Width = PANEL_Back_Assy_Overall_Width")
    lines.append(f"[Inch]BP_Panel_Assembly_Height = PANEL_Back_Assy_Overall_Height")
    lines.append(f"[Inch]BP_Panel_Assembly_Depth = PANEL_Back_Assy_Overall_Depth")
    lines.append("")
    # Note: Back panel components are not fully implemented in this service, using front for now
    lines.append(f"[Inch]BP_Plywood_Width = {back_components['plywood']['width']:.3f}")
    lines.append(f"[Inch]BP_Plywood_Height = {back_components['plywood']['height']:.3f}")
    lines.append(f"[Inch]BP_Plywood_Thickness = {panel_thickness:.3f}")
    lines.append("")
    add_panel_cleats_and_components(lines, "BP", back_components, back_panel_width, back_panel_height, cleat_thickness, cleat_width, panel_thickness)

    # ============ LEFT PANEL VARIABLES ============
    lines.append("\n// =========== LEFT PANEL (LP) ===========")
    lines.append(f"[Inch]LP_Panel_Assembly_Width = PANEL_End_Assy_Overall_Width")
    lines.append(f"[Inch]LP_Panel_Assembly_Height = PANEL_End_Assy_Overall_Height")
    lines.append(f"[Inch]LP_Panel_Assembly_Depth = PANEL_End_Assy_Overall_Depth_Thickness")
    lines.append("")
    lines.append(f"[Inch]LP_Plywood_Length = {left_components['plywood']['length']:.3f}") # Corrected from width
    lines.append(f"[Inch]LP_Plywood_Height = {left_components['plywood']['height']:.3f}")
    lines.append(f"[Inch]LP_Plywood_Thickness = {panel_thickness:.3f}")
    lines.append("")
    add_panel_cleats_and_components(lines, "LP", left_components, left_panel_width, left_panel_height, cleat_thickness, cleat_width, panel_thickness)

    # ============ RIGHT PANEL VARIABLES ============
    lines.append("\n// =========== RIGHT PANEL (RP) ===========")
    lines.append(f"[Inch]RP_Panel_Assembly_Width = PANEL_End_Assy_Overall_Width")
    lines.append(f"[Inch]RP_Panel_Assembly_Height = PANEL_End_Assy_Overall_Height")
    lines.append(f"[Inch]RP_Panel_Assembly_Depth = PANEL_End_Assy_Overall_Depth_Thickness")
    lines.append("")
    lines.append(f"[Inch]RP_Plywood_Length = {right_components['plywood']['length']:.3f}") # Corrected from width
    lines.append(f"[Inch]RP_Plywood_Height = {right_components['plywood']['height']:.3f}")
    lines.append(f"[Inch]RP_Plywood_Thickness = {panel_thickness:.3f}")
    lines.append("")
    add_panel_cleats_and_components(lines, "RP", right_components, right_panel_width, right_panel_height, cleat_thickness, cleat_width, panel_thickness)

    # ============ TOP PANEL VARIABLES ============
    lines.append("\n// =========== TOP PANEL (TP) ===========")
    lines.append(f"[Inch]TP_Panel_Assembly_Width = PANEL_Top_Assy_Overall_Width")
    lines.append(f"[Inch]TP_Panel_Assembly_Length = PANEL_Top_Assy_Overall_Length")
    lines.append(f"[Inch]TP_Panel_Assembly_Depth = PANEL_Top_Assy_Overall_Depth_Thickness")
    lines.append("")
    if top_components:
        lines.append(f"[Inch]TP_Plywood_Width = {top_components['plywood']['width']:.3f}")
        lines.append(f"[Inch]TP_Plywood_Length = {top_components['plywood']['length']:.3f}")
        lines.append(f"[Inch]TP_Plywood_Thickness = {panel_thickness:.3f}")
        lines.append("")
        add_top_panel_cleats(lines, top_components, top_panel_length, top_panel_width, cleat_thickness, cleat_width, panel_thickness)
    lines.append("")
    
    # Footer
    lines.append("// =========== END OF NX EXPRESSION FILE ===========")
    
    return "\n".join(lines)


def add_panel_cleats_and_components(lines: List[str], prefix: str, components: Dict[str, Any],
                                   panel_width: float, panel_height: float,
                                   cleat_thickness: float, cleat_width: float,
                                   panel_thickness: float):
    """Add comprehensive cleat and component expressions for panels"""
    
    # Get cleat metadata (not lists, but dictionaries with properties)
    h_cleats_info = components.get('horizontal_cleats', {}) if components else {}
    v_cleats_info = components.get('vertical_cleats', {}) if components else {}
    
    # Horizontal cleats
    lines.append(f"[Inch]{prefix}_Horizontal_Cleat_Length = {panel_width:.3f}")
    lines.append(f"[Inch]{prefix}_Horizontal_Cleat_Material_Thickness = {cleat_thickness:.3f}")
    lines.append(f"[Inch]{prefix}_Horizontal_Cleat_Material_Member_Width = {cleat_width:.3f}")
    lines.append(f"{prefix}_Horizontal_Cleat_Count = {2}")  # Top and bottom always
    lines.append("")
    
    # Vertical cleats
    lines.append(f"[Inch]{prefix}_Vertical_Cleat_Length = {panel_height - 2 * cleat_width:.3f}")
    lines.append(f"[Inch]{prefix}_Vertical_Cleat_Material_Thickness = {cleat_thickness:.3f}")
    lines.append(f"[Inch]{prefix}_Vertical_Cleat_Material_Member_Width = {cleat_width:.3f}")
    lines.append(f"{prefix}_Vertical_Cleat_Count = {2}")  # Left and right always
    lines.append("")
    
    # Intermediate vertical cleats
    inter_v_cleats_info = components.get('intermediate_vertical_cleats', {}) if components else {}
    inter_v_cleat_count = inter_v_cleats_info.get('count', 0)
    inter_v_cleat_positions = inter_v_cleats_info.get('positions_x_centerline', [])
    inter_v_cleat_positions_left = inter_v_cleats_info.get('positions_x_left_edge', [])
    inter_v_cleat_suppress_flags = inter_v_cleats_info.get('suppress_flags', [])
    lines.append(f"{prefix}_Intermediate_Vertical_Cleat_Count = {inter_v_cleat_count}")
    if inter_v_cleat_count > 0:
        lines.append(f"[Inch]{prefix}_Intermediate_Vertical_Cleat_Length = {inter_v_cleats_info.get('length', panel_height - 2 * cleat_width):.3f}")
        lines.append(f"[Inch]{prefix}_Intermediate_Vertical_Cleat_Material_Thickness = {cleat_thickness:.3f}")
        lines.append(f"[Inch]{prefix}_Intermediate_Vertical_Cleat_Material_Member_Width = {cleat_width:.3f}")
    else:
        lines.append(f"[Inch]{prefix}_Intermediate_Vertical_Cleat_Length = 0.001")
        lines.append(f"[Inch]{prefix}_Intermediate_Vertical_Cleat_Material_Thickness = {cleat_thickness:.3f}")
        lines.append(f"[Inch]{prefix}_Intermediate_Vertical_Cleat_Material_Member_Width = {cleat_width:.3f}")
    lines.append(f"{prefix}_Intermediate_Vertical_Cleat_Orientation_Code = 0")  # 0=Vertical
    lines.append("")
    
    # Intermediate vertical cleat instances (1-7)
    for i in range(1, 8):
        # End panels (LP/RP) use explicit left-edge positions and per-instance suppress flags
        if prefix in ("LP", "RP"):
            if i <= inter_v_cleat_count:
                suppress_flag = inter_v_cleat_suppress_flags[i-1] if (i-1) < len(inter_v_cleat_suppress_flags) else 1
                lines.append(f"{prefix}_Inter_VC_Inst_{i}_Suppress_Flag = {suppress_flag}")
                x_pos_centerline = inter_v_cleat_positions[i-1] if (i-1) < len(inter_v_cleat_positions) else 0.0
                lines.append(f"[Inch]{prefix}_Inter_VC_Inst_{i}_X_Pos_Centerline = {x_pos_centerline:.3f}")
                # Prefer explicit left-edge position; fall back to derived if missing
                if (i-1) < len(inter_v_cleat_positions_left):
                    x_pos_left_edge = inter_v_cleat_positions_left[i-1]
                else:
                    x_pos_left_edge = x_pos_centerline - (cleat_width / 2.0)
                lines.append(f"[Inch]{prefix}_Inter_VC_Inst_{i}_X_Pos_From_Left_Edge = {x_pos_left_edge:.3f}")
            else:
                lines.append(f"{prefix}_Inter_VC_Inst_{i}_Suppress_Flag = 0")  # 0=hide
                lines.append(f"[Inch]{prefix}_Inter_VC_Inst_{i}_X_Pos_Centerline = 0.001")
                lines.append(f"[Inch]{prefix}_Inter_VC_Inst_{i}_X_Pos_From_Left_Edge = 0.001")
        else:
            # Front/Back panels compute left-edge from centerline and member width
            if i <= len(inter_v_cleat_positions):
                x_pos_centerline = inter_v_cleat_positions[i-1]
                lines.append(f"{prefix}_Inter_VC_Inst_{i}_Suppress_Flag = 1")  # 1=show
                lines.append(f"[Inch]{prefix}_Inter_VC_Inst_{i}_X_Pos_Centerline = {x_pos_centerline:.3f}")
                lines.append(f"[Inch]{prefix}_Inter_VC_Inst_{i}_X_Pos_From_Left_Edge = {x_pos_centerline - (cleat_width/2):.3f}")
            else:
                lines.append(f"{prefix}_Inter_VC_Inst_{i}_Suppress_Flag = 0")  # 0=hide
                lines.append(f"[Inch]{prefix}_Inter_VC_Inst_{i}_X_Pos_Centerline = 0.001")
                lines.append(f"[Inch]{prefix}_Inter_VC_Inst_{i}_X_Pos_From_Left_Edge = 0.001")
    lines.append("")
    
    # Intermediate horizontal cleats
    inter_h_cleats_info = components.get('intermediate_horizontal_cleats', {}) if components else {}
    inter_h_cleat_count = inter_h_cleats_info.get('count', 0)
    inter_h_cleat_positions = inter_h_cleats_info.get('positions_y_centerline', [])
    
    # For now, we'll treat all intermediate horizontal cleats as splice cleats
    all_h_cleats_count = inter_h_cleat_count
    
    lines.append(f"{prefix}_Intermediate_Horizontal_Cleat_Count = {all_h_cleats_count}")
    lines.append(f"[Inch]{prefix}_Intermediate_Horizontal_Cleat_Material_Thickness = {cleat_thickness:.3f}")
    lines.append(f"[Inch]{prefix}_Intermediate_Horizontal_Cleat_Material_Member_Width = {cleat_width:.3f}")
    lines.append(f"{prefix}_Intermediate_Horizontal_Cleat_Orientation_Code = 1")  # 1=Horizontal
    lines.append(f"{prefix}_Intermediate_Horizontal_Cleat_Pattern_Count = {all_h_cleats_count}")
    lines.append(f"{prefix}_Intermediate_Horizontal_Cleat_Horizontal_Splice_Count = {all_h_cleats_count}")
    lines.append("")
    
    # Intermediate horizontal cleat instances (1-6)
    for i in range(1, 7):
        if i <= len(inter_h_cleat_positions):
            y_pos_centerline = inter_h_cleat_positions[i-1]
            y_pos = y_pos_centerline - cleat_width/2
            lines.append(f"{prefix}_Inter_HC_Inst_{i}_Suppress_Flag = 1")  # 1=show
            lines.append(f"[Inch]{prefix}_Inter_HC_Inst_{i}_Height = {cleat_width:.3f}")
            lines.append(f"[Inch]{prefix}_Inter_HC_Inst_{i}_Width = {panel_width:.3f}")
            lines.append(f"[Inch]{prefix}_Inter_HC_Inst_{i}_Length = {panel_width:.3f}")
            lines.append(f"[Inch]{prefix}_Inter_HC_Inst_{i}_X_Pos = 0.000")
            lines.append(f"[Inch]{prefix}_Inter_HC_Inst_{i}_Y_Pos = {y_pos:.3f}")
            lines.append(f"[Inch]{prefix}_Inter_HC_Inst_{i}_Y_Pos_Centerline = {y_pos_centerline:.3f}")
        else:
            lines.append(f"{prefix}_Inter_HC_Inst_{i}_Suppress_Flag = 0")  # 0=hide
            lines.append(f"[Inch]{prefix}_Inter_HC_Inst_{i}_Height = 0.001")
            lines.append(f"[Inch]{prefix}_Inter_HC_Inst_{i}_Width = 0.001")
            lines.append(f"[Inch]{prefix}_Inter_HC_Inst_{i}_Length = 0.001")
            lines.append(f"[Inch]{prefix}_Inter_HC_Inst_{i}_X_Pos = 0.001")
            lines.append(f"[Inch]{prefix}_Inter_HC_Inst_{i}_Y_Pos = 0.001")
            lines.append(f"[Inch]{prefix}_Inter_HC_Inst_{i}_Y_Pos_Centerline = 0.001")
    lines.append("")
    
    # Klimps (only for front panel)
    if prefix == "FP":
        klimps_info = components.get('klimps', {}) if components else {}
        klimp_positions = klimps_info.get('positions', []) if isinstance(klimps_info, dict) else []
        lines.append(f"{prefix}_Klimp_Count = {len(klimp_positions)}")
        lines.append(f"[Inch]{prefix}_Klimp_Diameter = 0.500")  # Standard klimp diameter
        lines.append(f"{prefix}_Klimp_Orientation_Code = 3")  # 3=Front_Surface
        lines.append("")
        
        # Klimp instances (1-12)
        for i in range(1, 13):
            if i <= len(klimp_positions):
                klimp_pos = klimp_positions[i-1]
                lines.append(f"{prefix}_Klimp_Inst_{i}_Suppress_Flag = 1")  # 1=show
                # Check if klimp_pos is a dict or tuple/list
                if isinstance(klimp_pos, dict):
                    x_pos = klimp_pos.get('x_pos', 0)
                    y_pos = klimp_pos.get('y_pos', 0)
                else:
                    # Assume it's a tuple/list
                    x_pos = klimp_pos[0] if len(klimp_pos) > 0 else 0
                    y_pos = klimp_pos[1] if len(klimp_pos) > 1 else 0
                lines.append(f"[Inch]{prefix}_Klimp_Inst_{i}_X_Pos = {x_pos:.3f}")
                lines.append(f"[Inch]{prefix}_Klimp_Inst_{i}_Y_Pos = {y_pos:.3f}")
            else:
                lines.append(f"{prefix}_Klimp_Inst_{i}_Suppress_Flag = 0")  # 0=hide
                lines.append(f"[Inch]{prefix}_Klimp_Inst_{i}_X_Pos = 0.001")
                lines.append(f"[Inch]{prefix}_Klimp_Inst_{i}_Y_Pos = 0.001")
        lines.append("")
    
    # Plywood sections (1-10) - for now just create a single full panel
    # TODO: Integrate actual plywood layout calculation
    for i in range(1, 11):
        if i == 1:  # Just one plywood section covering the whole panel
            lines.append(f"{prefix}_Plywood_{i}_Active = 1")  # 1=active
            lines.append(f"[Inch]{prefix}_Plywood_{i}_X_Position = 0.000")
            lines.append(f"[Inch]{prefix}_Plywood_{i}_Y_Position = 0.000")
            lines.append(f"[Inch]{prefix}_Plywood_{i}_Width = {panel_width:.3f}")
            lines.append(f"[Inch]{prefix}_Plywood_{i}_Height = {panel_height:.3f}")
        else:
            lines.append(f"{prefix}_Plywood_{i}_Active = 0")  # 0=inactive
            lines.append(f"[Inch]{prefix}_Plywood_{i}_X_Position = 0.001")
            lines.append(f"[Inch]{prefix}_Plywood_{i}_Y_Position = 0.001")
            lines.append(f"[Inch]{prefix}_Plywood_{i}_Width = 0.001")
            lines.append(f"[Inch]{prefix}_Plywood_{i}_Height = 0.001")
    lines.append("")


def add_top_panel_cleats(lines: List[str], components: Dict[str, Any],
                        panel_length: float, panel_width: float,
                        cleat_thickness: float, cleat_width: float,
                        panel_thickness: float):
    """Add top panel specific cleat expressions"""
    
    if not components:
        # No top panel
        for param in ["TP_Primary_Cleat_Length", "TP_Primary_Cleat_Material_Thickness",
                     "TP_Primary_Cleat_Material_Member_Width"]:
            lines.append(f"[Inch]{param} = 0.001")
        lines.append("TP_Primary_Cleat_Count = 0")
        lines.append("TP_Secondary_Cleat_Length = 0.001")
        lines.append("TP_Secondary_Cleat_Count = 0")
        return
    
    # Primary cleats (along width)
    primary_cleats_info = components.get('primary_cleats', {})
    primary_cleat_count = primary_cleats_info.get('count', 2) if isinstance(primary_cleats_info, dict) else 2
    lines.append(f"[Inch]TP_Primary_Cleat_Length = {panel_width:.3f}")
    lines.append(f"[Inch]TP_Primary_Cleat_Material_Thickness = {cleat_thickness:.3f}")
    lines.append(f"[Inch]TP_Primary_Cleat_Material_Member_Width = {cleat_width:.3f}")
    lines.append(f"TP_Primary_Cleat_Count = {primary_cleat_count}")
    lines.append("")
    
    # Secondary cleats (along length) 
    secondary_cleats_info = components.get('secondary_cleats', {})
    secondary_cleat_count = secondary_cleats_info.get('count', 2) if isinstance(secondary_cleats_info, dict) else 2
    lines.append(f"TP_Secondary_Cleat_Length = {panel_length:.3f}")
    lines.append(f"TP_Secondary_Cleat_Count = {secondary_cleat_count}")
    lines.append("")
    
    # Intermediate cleats
    inter_cleats_info = components.get('intermediate_cleats', {})
    inter_cleat_count = inter_cleats_info.get('count', 0) if isinstance(inter_cleats_info, dict) else 0
    inter_cleat_positions = inter_cleats_info.get('positions_x_centerline', []) if isinstance(inter_cleats_info, dict) else []
    lines.append(f"TP_Intermediate_Cleat_Count = {inter_cleat_count}")
    if inter_cleat_count > 0:
        lines.append(f"[Inch]TP_Intermediate_Cleat_Length = {inter_cleats_info.get('length', panel_width):.3f}")
        lines.append(f"[Inch]TP_Intermediate_Cleat_Material_Thickness = {cleat_thickness:.3f}")
        lines.append(f"[Inch]TP_Intermediate_Cleat_Material_Member_Width = {cleat_width:.3f}")
    else:
        lines.append("[Inch]TP_Intermediate_Cleat_Length = 0.001")
        lines.append(f"[Inch]TP_Intermediate_Cleat_Material_Thickness = {cleat_thickness:.3f}")
        lines.append(f"[Inch]TP_Intermediate_Cleat_Material_Member_Width = {cleat_width:.3f}")
    lines.append("TP_Intermediate_Cleat_Orientation_Code = 1")  # 1=Horizontal for top
    lines.append("")
    
    # Intermediate cleat instances (1-7)
    for i in range(1, 8):
        if i <= len(inter_cleat_positions):
            x_pos_centerline = inter_cleat_positions[i-1]
            lines.append(f"TP_Inter_Cleat_Inst_{i}_Suppress_Flag = 1")
            lines.append(f"[Inch]TP_Inter_Cleat_Inst_{i}_X_Pos_Centerline = {x_pos_centerline:.3f}")
            lines.append(f"[Inch]TP_Inter_Cleat_Inst_{i}_X_Pos_From_Left_Edge = {x_pos_centerline - cleat_thickness/2:.3f}")
        else:
            lines.append(f"TP_Inter_Cleat_Inst_{i}_Suppress_Flag = 0")
            lines.append(f"[Inch]TP_Inter_Cleat_Inst_{i}_X_Pos_Centerline = 0.001")
            lines.append(f"[Inch]TP_Inter_Cleat_Inst_{i}_X_Pos_From_Left_Edge = 0.001")
    lines.append("")
    
    # Top panel horizontal cleats (splice cleats)
    h_cleats_info = components.get('horizontal_cleats', {})
    h_cleat_count = h_cleats_info.get('count', 0) if isinstance(h_cleats_info, dict) else 0
    h_cleat_positions = h_cleats_info.get('positions_y_centerline', []) if isinstance(h_cleats_info, dict) else []
    
    lines.append(f"TP_Intermediate_Horizontal_Cleat_Count = {h_cleat_count}")
    lines.append(f"[Inch]TP_Intermediate_Horizontal_Cleat_Material_Thickness = {cleat_thickness:.3f}")
    lines.append(f"[Inch]TP_Intermediate_Horizontal_Cleat_Material_Member_Width = {cleat_width:.3f}")
    lines.append("TP_Intermediate_Horizontal_Cleat_Orientation_Code = 1")
    lines.append(f"TP_Intermediate_Horizontal_Cleat_Pattern_Count = {h_cleat_count}")
    lines.append(f"TP_Intermediate_Horizontal_Cleat_Horizontal_Splice_Count = {h_cleat_count}")
    lines.append("")
    
    # Horizontal cleat instances (1-6)
    for i in range(1, 7):
        if i <= len(h_cleat_positions):
            y_pos_centerline = h_cleat_positions[i-1]
            y_pos = y_pos_centerline - cleat_width/2
            lines.append(f"TP_Inter_HC_Inst_{i}_Suppress_Flag = 1")
            lines.append(f"[Inch]TP_Inter_HC_Inst_{i}_Height = {cleat_width:.3f}")
            lines.append(f"[Inch]TP_Inter_HC_Inst_{i}_Width = {panel_width:.3f}")
            lines.append(f"[Inch]TP_Inter_HC_Inst_{i}_Length = {panel_length:.3f}")
            lines.append(f"[Inch]TP_Inter_HC_Inst_{i}_X_Pos = 0.000")
            lines.append(f"[Inch]TP_Inter_HC_Inst_{i}_Y_Pos = {y_pos:.3f}")
            lines.append(f"[Inch]TP_Inter_HC_Inst_{i}_Y_Pos_Centerline = {y_pos_centerline:.3f}")
        else:
            lines.append(f"TP_Inter_HC_Inst_{i}_Suppress_Flag = 0")
            lines.append(f"[Inch]TP_Inter_HC_Inst_{i}_Height = 0.001")
            lines.append(f"[Inch]TP_Inter_HC_Inst_{i}_Width = 0.001")
            lines.append(f"[Inch]TP_Inter_HC_Inst_{i}_Length = 0.001")
            lines.append(f"[Inch]TP_Inter_HC_Inst_{i}_X_Pos = 0.001")
            lines.append(f"[Inch]TP_Inter_HC_Inst_{i}_Y_Pos = 0.001")
            lines.append(f"[Inch]TP_Inter_HC_Inst_{i}_Y_Pos_Centerline = 0.001")
    lines.append("")
    
    # Top panel plywood sections - for now just create a single full panel
    for i in range(1, 11):
        if i == 1:  # Just one plywood section covering the whole panel
            lines.append(f"TP_Plywood_{i}_Active = 1")
            lines.append(f"[Inch]TP_Plywood_{i}_X_Position = 0.000")
            lines.append(f"[Inch]TP_Plywood_{i}_Y_Position = 0.000")
            lines.append(f"[Inch]TP_Plywood_{i}_Width = {panel_width:.3f}")
            lines.append(f"[Inch]TP_Plywood_{i}_Height = {panel_length:.3f}")
        else:
            lines.append(f"TP_Plywood_{i}_Active = 0")
            lines.append(f"[Inch]TP_Plywood_{i}_X_Position = 0.001")
            lines.append(f"[Inch]TP_Plywood_{i}_Y_Position = 0.001")
            lines.append(f"[Inch]TP_Plywood_{i}_Width = 0.001")
            lines.append(f"[Inch]TP_Plywood_{i}_Height = 0.001")
    lines.append("")