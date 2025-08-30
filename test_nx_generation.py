"""Test NX Expression Generation - Compare web and local versions"""
import sys
import os
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_nx_generation():
    """Test both web and local NX expression generators with identical parameters"""
    
    # Test parameters
    test_params = {
        'product_length': 72,
        'product_width': 48, 
        'product_height': 36,
        'weight': 2000,
        'panel_grade': 5,
        'panel_thickness': 0.5,
        'cleat_thickness': 2.0,
        'lumber_type': 'ASTM',
        'include_top': True,
        'clearance': 0.5,
        'skid_height': 3.5,
        'floorboard_thickness': 1.0
    }
    
    print("Testing NX Expression Generation...")
    print(f"Test Parameters: {test_params}")
    print("-" * 80)
    
    # Test web version
    try:
        from api.nx_expression_service import generate_full_nx_expression_content
        web_result = generate_full_nx_expression_content(**test_params)
        print("[OK] Web version generated successfully")
        web_lines = web_result.split('\n')
        print(f"  - Total lines: {len(web_lines)}")
        
        # Check for key sections
        key_sections = [
            "// =========== NX EXPRESSION FILE",
            "// =========== INPUT PARAMETERS",
            "// =========== CALCULATED CRATE DIMENSIONS",
            "// =========== FRONT PANEL (FP)",
            "// =========== BACK PANEL (BP)",
            "// =========== LEFT PANEL (LP)",
            "// =========== RIGHT PANEL (RP)",
            "// =========== TOP PANEL (TP)",
            "// =========== END OF NX EXPRESSION FILE"
        ]
        
        for section in key_sections:
            if section in web_result:
                print(f"  [OK] Found section: {section}")
            else:
                print(f"  [MISSING] Missing section: {section}")
                
    except Exception as e:
        print(f"[ERROR] Web version failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    print("-" * 80)
    
    # Test local version
    try:
        from autocrate.nx_expressions_generator import generate_crate_nx_expression
        
        # Map parameters for local version
        local_params = {
            'product_length': test_params['product_length'],
            'product_width': test_params['product_width'],
            'product_height': test_params['product_height'],
            'product_weight': test_params['weight'],
            'lumber_type': test_params['lumber_type'],
            'panel_grade': f"PLY{test_params['panel_thickness']:.2f}".replace('.', '_'),
            'cleat_thickness': test_params['cleat_thickness'],
            'clearance': test_params['clearance'],
            'skid_height': test_params['skid_height'],
            'floorboard_thickness': test_params['floorboard_thickness'],
            'include_top': test_params['include_top']
        }
        
        local_result = generate_crate_nx_expression(**local_params)
        if local_result:
            print("[OK] Local version generated successfully")
            local_lines = local_result.split('\n')
            print(f"  - Total lines: {len(local_lines)}")
        else:
            print("[ERROR] Local version returned None")
            return False
            
    except Exception as e:
        print(f"[ERROR] Local version failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    print("-" * 80)
    
    # Compare critical values
    print("\nComparing critical values between versions:")
    
    def extract_value(content, variable_name):
        """Extract value for a specific variable from expression content"""
        for line in content.split('\n'):
            if variable_name in line and '=' in line:
                return line.split('=')[1].strip()
        return None
    
    critical_vars = [
        '[Inch]crate_overall_width_OD',
        '[Inch]crate_overall_length_OD',
        '[Inch]PANEL_Front_Assy_Overall_Width',
        '[Inch]PANEL_Front_Assy_Overall_Height',
        '[Inch]LP_Panel_Assembly_Length',
        '[Inch]LP_Panel_Assembly_Height',
        '[Inch]RP_Panel_Assembly_Length',
        '[Inch]RP_Panel_Assembly_Height',
        '[Inch]TP_Panel_Assembly_Width',
        '[Inch]TP_Panel_Assembly_Length'
    ]
    
    all_match = True
    for var in critical_vars:
        web_val = extract_value(web_result, var)
        local_val = extract_value(local_result, var)
        
        if web_val and local_val:
            if web_val == local_val:
                print(f"  [OK] {var}: {web_val} (match)")
            else:
                print(f"  [MISMATCH] {var}: Web={web_val}, Local={local_val} (mismatch)")
                all_match = False
        else:
            if not web_val:
                print(f"  [MISSING] {var}: Not found in web version")
            if not local_val:
                print(f"  [MISSING] {var}: Not found in local version")
            all_match = False
    
    print("-" * 80)
    
    if all_match:
        print("\n[SUCCESS] All critical values match between web and local versions!")
    else:
        print("\n[FAILURE] Some values don't match. Further investigation needed.")
        
        # Save outputs for manual comparison
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        web_file = f"test_output_web_{timestamp}.exp"
        local_file = f"test_output_local_{timestamp}.exp"
        
        with open(web_file, 'w') as f:
            f.write(web_result)
        print(f"\nWeb version output saved to: {web_file}")
        
        with open(local_file, 'w') as f:
            f.write(local_result)
        print(f"Local version output saved to: {local_file}")
        
    return all_match

if __name__ == "__main__":
    success = test_nx_generation()
    sys.exit(0 if success else 1)
