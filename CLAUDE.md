DO NOT CHANGE THE NX VARIABLES they are needed for the model generation.

# AutoCrate Project Summary - Version 12.1.2

## Overview

This project, "AutoCrate," is a Python-based application designed to automate the generation of manufacturing data for shipping crates. It features a `tkinter` GUI for user input and produces Siemens NX expressions files (`.exp`) as its primary output. These files drive a parametric CAD model, enabling the automated creation of detailed 3D models and drawings.

## Recent Updates (Version 12.1.2)

### KL_1_Z Variable - Total Crate Height
- **New NX Expression Variable**: `KL_1_Z` now provides the total crate height measurement
- **Calculation**: `panel_height + panel_thickness + cleat_thickness + cleat_member_width`
- **Purpose**: Gives accurate Z-coordinate for the top of the complete crate assembly
- **Location**: Added in `nx_expressions_generator.py` at line 912

### Enhanced Build System
- **Verbose Output**: Build process now shows detailed progress with stage indicators (1/4, 2/4, etc.)
- **Color-Coded Messages**: Console output uses colors for better readability
- **Progress Tracking**: Each operation shows detailed status and file information
- **Success Indicators**: Checkmarks (✓) confirm completed steps
- **Build Scripts**: Enhanced `build.bat` and `scripts/run_build.ps1`

## Core Functionality

1.  **User Input:** The application captures product specifications (weight, dimensions), clearance requirements, and material details (panel thickness, cleat sizes) through its GUI.
2.  **Crate Design Logic:** It calculates the dimensions of all crate components, including:
    *   **Skids:** Sized and spaced based on product weight.
    *   **Floorboards:** Boards forming the crate's floor.
    *   **Panels:** The front, back, left, right, and top walls, each constructed from plywood sheathing and reinforcing cleats.
3.  **Component Calculation:** For each panel, the application determines:
    *   Plywood sheathing dimensions.
    *   The length and placement of edge cleats.
    *   The number, length, and position of intermediate cleats based on structural requirements (e.g., 24-inch spacing).
    *   An optimized layout of standard plywood sheets to minimize waste, including splice locations.
4.  **Output Generation:** The final output is an `.exp` file containing variables that define the geometry and positioning of all crate components in Siemens NX.

## Key Files

*   `nx_expressions_generator.py`: The main application file, containing the GUI, core logic, and `.exp` file generation.
*   `*_panel_logic.py`: Modules for calculating the components of each specific panel (e.g., `front_panel_logic.py`, `top_panel_logic.py`).
*   `front_panel_logic_unified.py`: An advanced, unified version of the front panel logic with adaptive strategies.
*   `skid_logic.py`: Logic for determining skid properties based on product weight.
*   `plywood_layout_generator.py`: A script and integrated module for calculating optimal plywood layouts.
*   `klimp_placement_logic.py`: Handles klimp placement calculations for structural support.
*   `build.bat` & `scripts/run_build.ps1`: Build system with enhanced verbose output.
*   `Crate_*.exp`: Example `.exp` output files for various crate sizes.

## Technical Details

*   **Language:** Python
*   **GUI:** `tkinter`
*   **Output Format:** Siemens NX Expressions (`.exp`)
*   **Key Concepts:**
    *   **CAD Automation:** Automating the generation of design data.
    *   **Parametric Modeling:** Using variables to control geometry in a CAD model.
    *   **Design Rules:** Encapsulating engineering and manufacturing constraints in code.
    *   **ASTM Compliance:** Following industry standards for crate design and construction.

## Development Tools

### Testing
- Run quick tests: `python quick_test.bat` or use the GUI's Quick Test button
- Comprehensive test suite in `tests/` directory
- Validation expressions in `expressions/validation/`

### Building
- Execute `build.bat` to create the standalone executable
- Build process now shows detailed progress with verbose output
- Creates `AutoCrate.exe` in the project root

### AI Development Support
- Token optimization system in `scripts/token_optimizer.py`
- Conversation state management for long development sessions
- Comprehensive logging system for debugging

## Important NX Expression Variables

### Critical Variables (DO NOT MODIFY)
- Panel assembly dimensions (e.g., `PANEL_Front_Assy_Overall_Height`)
- Component suppress flags (0 = hide/suppress, 1 = show)
- Instance positioning variables (`*_X_Pos_Abs`, `*_Y_Pos_Abs`)
- **KL_1_Z**: Total crate height including top assembly

### Variable Naming Convention
- Prefixes indicate component type (FP = Front Panel, BP = Back Panel, etc.)
- Suffixes indicate property type (_Width, _Height, _Thickness, etc.)
- Instance numbers for array components (e.g., `FP_Inter_HC_Inst_1`)

## Core Logic Extraction

### 1. Main Orchestration (`nx_expressions_generator.py`)

The main script follows a precise sequence to ensure all dependencies are met before generating the final output.

1.  **Input Gathering**: Collects all parameters from the `tkinter` GUI.
2.  **Skid Sizing**: Calls `skid_logic.calculate_skid_lumber_properties` to determine the required skid lumber size (e.g., 4x4, 4x6) and maximum spacing based on product weight.
3.  **Initial Crate Sizing**: Calculates the initial overall length and width of the crate based on product dimensions and clearances.
4.  **Panel Bounding Box Definition**: Defines the initial dimensions for all five panels (Front, Back, Left, Right, Top), accounting for how they assemble (e.g., end panels fit between front and back panels).
5.  **Iterative Dimension Stabilization (Critical Logic)**:
    *   The system enters a loop to account for the fact that adding intermediate cleats can increase a panel's dimensions, which in turn affects the overall crate size and the dimensions of adjacent panels.
    *   It calculates the material needed for cleats on one axis (e.g., width), adds that material to the overall crate dimensions, and then recalculates the dimensions of all affected panels.
    *   This process is repeated for all axes and panels until the dimensions stabilize and no more material needs to be added. This ensures the final design is manufacturable and all clearances are respected.
6.  **Final Skid Layout**: With the final, stable crate width, it calls `skid_logic.calculate_skid_layout` to determine the exact count, pitch, and starting position of the skids.
7.  **Floorboard Calculation**:
    *   It calculates the usable area for floorboards.
    *   It greedily places the largest available standard lumber widths.
    *   The remaining space is handled as either a smaller custom-width board or a central gap, based on user settings.
8.  **Detailed Panel Component Calculation**: For each of the five panels, it calls the appropriate `calculate_*_panel_components` function to determine the final geometry of plywood and cleats.
9.  **Splice-Driven Cleat Placement**: It calls `update_panel_components_with_splice_cleats`, which overrides the default symmetric cleat placement with a more robust strategy. This function ensures that if plywood splices exist, cleats are placed directly over them for structural integrity, and additional cleats are added to fill any remaining large gaps.
10. **Plywood Layout Optimization**: Calls `calculate_plywood_layout` for each panel to determine the most efficient arrangement of standard 4'x8' plywood sheets.
11. **NX Expression Formatting**: All calculated dimensions, positions, and counts are formatted into specific string variables that the Siemens NX model expects. This includes setting "suppress flags" to 0 or 1 to turn unused components (like extra cleat instances) off or on.
12. **File Output**: The final list of expression strings is written to the `.exp` file.

### 2. Plywood Layout Logic (`plywood_layout_generator.py`)

*   **Goal**: Minimize the number of plywood sheets needed to cover a given panel area.
*   **Method**:
    1.  It calculates the number of sheets required for two primary orientations:
        *   **Standard**: Sheets laid with their 96-inch side horizontal.
        *   **Rotated**: Sheets laid with their 48-inch side horizontal.
    2.  It chooses the orientation that results in the fewest total sheets.
    3.  **Tie-Breaking**: If the sheet count is equal, the logic prefers the orientation that results in fewer horizontal splices, as these are structurally less desirable. Further tie-breaking can favor the layout that better matches the panel's aspect ratio.
    4.  It then calculates the precise X/Y coordinates, width, and height of each individual sheet required for the chosen layout.

### 3. Cleat Placement Logic

The system uses two primary strategies for placing intermediate cleats.

#### a. Symmetric Spacing (Legacy / No Splices)

*   **Trigger**: Used when a panel is made from a single piece of plywood (no splices).
*   **Method**:
    1.  Calculates the center-to-center span between the two edge cleats.
    2.  If this span exceeds the `TARGET_INTERMEDIATE_CLEAT_SPACING` (typically 24 inches), it determines the minimum number of additional cleats required to bring the spacing below this target.
    3.  It then divides the span into equal segments to position the intermediate cleats perfectly symmetrically.

#### b. Splice-Driven Placement (Current / With Splices)

*   **Trigger**: Used when a panel's plywood layout requires splices (seams between sheets).
*   **Method**:
    1.  **Mandatory Placement**: Places an intermediate cleat directly over the centerline of every vertical plywood splice. This is a structural requirement.
    2.  **Gap Filling**: After placing the mandatory splice cleats, it checks the spacing between all adjacent cleats (including the edge cleats).
    3.  If any gap is found to be larger than the 24-inch target, it adds one or more additional cleats within that gap to meet the spacing requirement.

### 4. Unified Panel Logic (`front_panel_logic_unified.py`)

This module represents the most advanced logic for handling complex scenarios, particularly how to handle cleats that need to be placed over splices that are very close to a panel's edge.

*   **Concept**: It introduces selectable "strategies" to resolve these conflicts.
*   **Hybrid Strategy (Default)**:
    *   It first calculates how much a panel's height would need to increase to fully cover a problematic splice with the standard edge cleat.
    *   If this adjustment is small (e.g., less than 2 inches), it opts for **Dimension Adjustment**, increasing the panel's overall height. This is often preferable as it maintains a standard build pattern.
    *   If the required adjustment is large, it opts for **Position Adjustment**, where the panel height is *not* changed, and instead, the intermediate cleat is simply moved slightly to avoid the conflict.
*   This adaptive approach provides an optimal solution that balances material usage and manufacturing simplicity.

## AI Assistant Notes

When working with AutoCrate:

1. **Preserve NX Variables**: Never change variable names or their calculation logic without understanding the CAD model dependencies.
2. **Test Changes**: Always run quick_test.bat after modifications to verify calculations.
3. **Build Verbosity**: The build system now provides detailed output - check for any warnings or errors.
4. **Expression Files**: Generated .exp files are timestamped and stored in the expressions/ directory.
5. **Suppress Flags**: 0 = suppress/hide component, 1 = show component in the NX model.
6. **KL_1_Z Usage**: This variable represents the absolute top of the crate assembly, useful for stacking calculations or clearance checks.

## Version History

- **12.1.2**: Added KL_1_Z variable for total crate height, enhanced build system verbosity
- **12.1.1**: Added comprehensive AI token optimization system
- **12.0.9**: Comprehensive AI-powered testing system and infrastructure improvements
- **12.0.8**: Major architecture cleanup with intelligent expression management