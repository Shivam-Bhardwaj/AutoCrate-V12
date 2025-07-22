from left_panel_logic import calculate_left_panel_components as calculate_right_panel_components

__all__ = ["calculate_right_panel_components"]

def run_example():
    # quick self-test identical to left panel but different dimensions
    import json
    data = calculate_right_panel_components(
        left_panel_assembly_length=84.0,
        left_panel_assembly_height=40.0,
        panel_sheathing_thickness=0.5,
        cleat_material_thickness=1.25,
        cleat_material_member_width=3.5,
    )
    print(json.dumps(data, indent=4))

if __name__ == "__main__":
    run_example() 