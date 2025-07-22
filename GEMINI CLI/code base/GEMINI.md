DO NOT CHANGE THE NX VARAIBLES they are needed for the model generation.

# AutoCrate Project Summary

## Overview

This project, "AutoCrate," is a Python-based application designed to automate the generation of manufacturing data for shipping crates. It features a `tkinter` GUI for user input and produces Siemens NX expressions files (`.exp`) as its primary output. These files drive a parametric CAD model, enabling the automated creation of detailed 3D models and drawings.

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
*   `Crate_*.exp`: Example `.exp` output files for various crate sizes.
*   `EXECUTABLE_README.md`, `UI_MODERNIZATION_SUMMARY.md`: Documentation on the executable version and recent UI enhancements.

## Technical Details

*   **Language:** Python
*   **GUI:** `tkinter`
*   **Output Format:** Siemens NX Expressions (`.exp`)
*   **Key Concepts:**
    *   **CAD Automation:** Automating the generation of design data.
    *   **Parametric Modeling:** Using variables to control geometry in a CAD model.
    *   **Design Rules:** Encapsulating engineering and manufacturing constraints in code.

In summary, AutoCrate is a powerful tool that streamlines the crate design process, significantly improving efficiency and consistency.

# Core Logic Extraction

This section details the primary algorithms and logical flows within the AutoCrate system.

## 1. Main Orchestration (`nx_expressions_generator.py`)

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

## 2. Plywood Layout Logic (`plywood_layout_generator.py`)

*   **Goal**: Minimize the number of plywood sheets needed to cover a given panel area.
*   **Method**:
    1.  It calculates the number of sheets required for two primary orientations:
        *   **Standard**: Sheets laid with their 96-inch side horizontal.
        *   **Rotated**: Sheets laid with their 48-inch side horizontal.
    2.  It chooses the orientation that results in the fewest total sheets.
    3.  **Tie-Breaking**: If the sheet count is equal, the logic prefers the orientation that results in fewer horizontal splices, as these are structurally less desirable. Further tie-breaking can favor the layout that better matches the panel's aspect ratio.
    4.  It then calculates the precise X/Y coordinates, width, and height of each individual sheet required for the chosen layout.

## 3. Cleat Placement Logic

The system uses two primary strategies for placing intermediate cleats.

### a. Symmetric Spacing (Legacy / No Splices)

*   **Trigger**: Used when a panel is made from a single piece of plywood (no splices).
*   **Method**:
    1.  Calculates the center-to-center span between the two edge cleats.
    2.  If this span exceeds the `TARGET_INTERMEDIATE_CLEAT_SPACING` (typically 24 inches), it determines the minimum number of additional cleats required to bring the spacing below this target.
    3.  It then divides the span into equal segments to position the intermediate cleats perfectly symmetrically.

### b. Splice-Driven Placement (Current / With Splices)

*   **Trigger**: Used when a panel's plywood layout requires splices (seams between sheets).
*   **Method**:
    1.  **Mandatory Placement**: Places an intermediate cleat directly over the centerline of every vertical plywood splice. This is a structural requirement.
    2.  **Gap Filling**: After placing the mandatory splice cleats, it checks the spacing between all adjacent cleats (including the edge cleats).
    3.  If any gap is found to be larger than the 24-inch target, it adds one or more additional cleats within that gap to meet the spacing requirement.

## 4. Unified Panel Logic (`front_panel_logic_unified.py`)

This module represents the most advanced logic for handling complex scenarios, particularly how to handle cleats that need to be placed over splices that are very close to a panel's edge.

*   **Concept**: It introduces selectable "strategies" to resolve these conflicts.
*   **Hybrid Strategy (Default)**:
    *   It first calculates how much a panel's height would need to increase to fully cover a problematic splice with the standard edge cleat.
    *   If this adjustment is small (e.g., less than 2 inches), it opts for **Dimension Adjustment**, increasing the panel's overall height. This is often preferable as it maintains a standard build pattern.
    *   If the required adjustment is large, it opts for **Position Adjustment**, where the panel height is *not* changed, and instead, the intermediate cleat is simply moved slightly to avoid the conflict.
*   This adaptive approach provides an optimal solution that balances material usage and manufacturing simplicity.