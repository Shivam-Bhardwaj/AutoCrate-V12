# TODO: Implement Klimp Placement Logic

This document outlines the tasks required to implement the automated placement of Klimps (fasteners) on the Front Panel of the AutoCrate model.

**Primary Goal:** Create a new Python module (`klimp_placement_logic.py`) that calculates the precise position and orientation of Klimps on the top, left, and right edges of the Front Panel. This logic must account for the positions of cleats on adjacent panels (Top, Left, and Right panels) to ensure proper assembly.

---


## 1. Create New Module: `autocrate/klimp_placement_logic.py`

This new file will contain all the core logic for calculating Klimp positions.

### 1.1. Main Function: `calculate_klimp_placements`

This will be the primary function called by the main generator.

**Function Signature:**
```python
def calculate_klimp_placements(
    front_panel_width: float,
    front_panel_height: float,
    top_panel_cleat_positions: list[float],
    end_panel_cleat_positions: list[float],
    cleat_width: float = 3.5,
    klimp_width: float = 1.5
) -> dict:
```

**Inputs:**
- `front_panel_width`: The final overall width of the front panel assembly (X-dimension).
- `front_panel_height`: The final overall height of the front panel assembly (Z-dimension).
- `top_panel_cleat_positions`: A list of Z-coordinates for the centerlines of the intermediate cleats on the **Top Panel**.
- `end_panel_cleat_positions`: A list of X-coordinates for the centerlines of the intermediate cleats on the **Left/Right End Panels**.
- `cleat_width`: The width of the cleat material (default 3.5 inches).
- `klimp_width`: The physical width of a Klimp fastener (default 1.5 inches).

**Return Value:**
The function should return a dictionary containing a list of all calculated Klimps.
```python
{
    "klimps": [
        {"side": "top", "position": 13.875, "angle": 0},
        {"side": "top", "position": 45.0, "angle": 0},
        {"side": "left", "position": 18.875, "angle": -90},
        {"side": "left", "position": 65.0, "angle": -90},
        {"side": "right", "position": 18.875, "angle": 90},
        {"side": "right", "position": 65.0, "angle": 90}
    ]
}
```

### 1.2. Core Calculation Logic

The implementation must follow the **centered coordinate system** used by the rest of the application (`X=0` is the crate's width center).

The calculation should be broken into three parts:

**A. Top Edge Klimps:**
- **Driving Dimension:** `front_panel_width` (e.g., from -65 to +65 for a 130" wide panel).
- **Obstacles:** `end_panel_cleat_positions` (the X-coordinates of vertical cleats on the side panels).
- **Logic:**
    1. Define "Exclusion Zones" around each `end_panel_cleat_positions` by adding `(cleat_width / 2) + 0.5"` to each side of the centerline.
    2. Identify the "Placing Zones" (the clear spaces between exclusion zones and panel edges).
    3. For each Placing Zone, calculate the number of Klimps needed to keep spacing between 16" and 24".
    4. Calculate the precise, evenly-spaced X-positions for the Klimps within each zone.
    5. The `angle` for all top Klimps is **0**.

**B. Left Edge Klimps:**
- **Driving Dimension:** `front_panel_height` (e.g., from 0 to 84).
- **Obstacles:** `top_panel_cleat_positions` (the Z-coordinates of horizontal cleats on the top panel).
- **Logic:**
    1. Same as above, but applied to the Z-axis. Define Exclusion Zones around `top_panel_cleat_positions`.
    2. Identify Placing Zones along the Z-axis.
    3. Calculate the Z-positions for the Klimps within each zone.
    4. The `angle` for all left-side Klimps is **-90**.

**C. Right Edge Klimps:**
- The calculation for the Z-positions is **identical** to the Left Edge.
- The `angle` for all right-side Klimps is **+90**.

---


## 2. Integrate into `autocrate/nx_expressions_generator.py`

Modify the `generate_crate_expressions_logic` function to use the new module.

### 2.1. Import the New Module
```python
# At the top with other imports
from autocrate.klimp_placement_logic import calculate_klimp_placements
```

### 2.2. Define New Constants
Add a constant for the maximum number of Klimp instances available in the NX model for each side.
```python
# Near other MAX constants
MAX_KLIMPS_PER_SIDE = 15 # Example value, adjust to match NX model
```

### 2.3. Call the Calculation Function
This call should be placed **after** all panel component data dictionaries (`top_panel_components_data`, `left_panel_components_data`, etc.) have been calculated and finalized.

```python
# ... after all panel components are calculated ...

# === KLIMP PLACEMENT CALCULATIONS (STEP 7) ===
top_panel_cleat_positions = top_panel_components_data.get('intermediate_cleats', {}).get('positions_x_centerline', [])
end_panel_cleat_positions = left_panel_components_data.get('intermediate_vertical_cleats', {}).get('positions_x_centerline', [])

klimp_data = calculate_klimp_placements(
    front_panel_width=front_panel_calc_width,
    front_panel_height=front_panel_calc_height,
    top_panel_cleat_positions=top_panel_cleat_positions,
    end_panel_cleat_positions=end_panel_cleat_positions,
    cleat_width=cleat_member_actual_width_in
)

# Separate the calculated klimps by side
top_klimps = [k for k in klimp_data['klimps'] if k['side'] == 'top']
left_klimps = [k for k in klimp_data['klimps'] if k['side'] == 'left']
right_klimps = [k for k in klimp_data['klimps'] if k['side'] == 'right']

# ... continue to expression generation ...
```

### 2.4. Generate NX Expressions
Add a new section to the `expressions_content` list to write out the Klimp data. This involves three loops, one for each side.

```python
# ... inside the expressions_content list generation ...

# --- FRONT PANEL KLIMP PARAMETERS ---
expressions_content.extend([
    f"\n// --- FRONT PANEL KLIMP PARAMETERS ---",
    f"// Top Edge Klimps (Max {MAX_KLIMPS_PER_SIDE} instances)"
])
for i in range(MAX_KLIMPS_PER_SIDE):
    instance_num = i + 1
    if i < len(top_klimps):
        klimp = top_klimps[i]
        expressions_content.append(f"FP_Top_Klimp_{instance_num}_Suppress = 0") # 0 to show
        expressions_content.append(f"[Inch]FP_Top_Klimp_{instance_num}_X_Pos = {klimp['position']:.4f}")
        expressions_content.append(f"FP_Top_Klimp_{instance_num}_Angle = {klimp['angle']}")
    else:
        expressions_content.append(f"FP_Top_Klimp_{instance_num}_Suppress = 1") # 1 to suppress
        expressions_content.append(f"[Inch]FP_Top_Klimp_{instance_num}_X_Pos = 0")
        expressions_content.append(f"FP_Top_Klimp_{instance_num}_Angle = 0")

expressions_content.extend([
    f"\n// Left Edge Klimps (Max {MAX_KLIMPS_PER_SIDE} instances)"
])
for i in range(MAX_KLIMPS_PER_SIDE):
    instance_num = i + 1
    if i < len(left_klimps):
        klimp = left_klimps[i]
        expressions_content.append(f"FP_Left_Klimp_{instance_num}_Suppress = 0") # 0 to show
        expressions_content.append(f"[Inch]FP_Left_Klimp_{instance_num}_Z_Pos = {klimp['position']:.4f}")
        expressions_content.append(f"FP_Left_Klimp_{instance_num}_Angle = {klimp['angle']}")
    else:
        expressions_content.append(f"FP_Left_Klimp_{instance_num}_Suppress = 1") # 1 to suppress
        expressions_content.append(f"[Inch]FP_Left_Klimp_{instance_num}_Z_Pos = 0")
        expressions_content.append(f"FP_Left_Klimp_{instance_num}_Angle = 0")

expressions_content.extend([
    f"\n// Right Edge Klimps (Max {MAX_KLIMPS_PER_SIDE} instances)"
])
for i in range(MAX_KLIMPS_PER_SIDE):
    instance_num = i + 1
    if i < len(right_klimps):
        klimp = right_klimps[i]
        expressions_content.append(f"FP_Right_Klimp_{instance_num}_Suppress = 0") # 0 to show
        expressions_content.append(f"[Inch]FP_Right_Klimp_{instance_num}_Z_Pos = {klimp['position']:.4f}")
        expressions_content.append(f"FP_Right_Klimp_{instance_num}_Angle = {klimp['angle']}")
    else:
        expressions_content.append(f"FP_Right_Klimp_{instance_num}_Suppress = 1") # 1 to suppress
        expressions_content.append(f"[Inch]FP_Right_Klimp_{instance_num}_Z_Pos = 0")
        expressions_content.append(f"FP_Right_Klimp_{instance_num}_Angle = 0")

```

**Note:** The NX expression variable names (`FP_Top_Klimp_1_Suppress`, etc.) must exactly match the names used in the Siemens NX model.

---


## 3. Token/Efficiency Savings

The "token saving" aspect of this task is achieved by implementing the logic efficiently. The "Pre-place and Toggle" method is inherently less efficient in the expression file than a pattern-based approach, but it is required due to the non-uniform spacing.

To be maximally efficient:
- The `klimp_placement_logic.py` module should be pure calculation with no side effects.
- The data structures passed between modules should be simple and minimal (lists of numbers and strings).
- The loops in the generator should be clean and directly create the required expression strings without complex intermediate steps.

By following this guide, the resulting code will be clean, correct, and integrated properly into the existing application structure.
