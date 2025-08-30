"""
Detailed comparison of NX expressions between desktop and web versions
This script generates expressions from both versions and compares them line by line
"""

import sys
import os
import json
import difflib
import subprocess
from datetime import datetime

# Add the autocrate module to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the desktop NX generator
from autocrate.nx_expressions_generator import generate_nx_expressions

def generate_desktop_expression(test_params):
    """Generate NX expression using desktop logic"""
    print("Generating desktop NX expression...")
    
    # Generate using desktop function
    content = generate_nx_expressions(
        product_length=test_params['productLength'],
        product_width=test_params['productWidth'],
        product_height=test_params['productHeight'],
        product_weight=test_params['productWeight'],
        clearance=test_params['clearance'],
        panel_thickness=test_params['panelThickness'],
        include_top=test_params['includeTop']
    )
    
    # Save to file
    desktop_file = f"desktop_nx_{datetime.now().strftime('%Y%m%d_%H%M%S')}.exp"
    with open(desktop_file, 'w') as f:
        f.write(content)
    
    print(f"Desktop expression saved to: {desktop_file}")
    return content, desktop_file

def generate_web_expression(test_params):
    """Generate NX expression using web API"""
    print("Generating web NX expression...")
    
    # Check if API server is running
    import requests
    
    try:
        # First, try the Python API server if running
        api_url = "http://localhost:5000/api/calculate"
        response = requests.post(api_url, json=test_params, timeout=5)
        
        if response.status_code == 200:
            result = response.json()
            if 'nx_expression' in result:
                content = result['nx_expression']
                web_file = f"web_nx_{datetime.now().strftime('%Y%m%d_%H%M%S')}.exp"
                with open(web_file, 'w') as f:
                    f.write(content)
                print(f"Web expression (from Python API) saved to: {web_file}")
                return content, web_file
    except:
        pass
    
    # If Python API not available, use Node.js calculation
    try:
        # Create a test script to run the web calculation
        test_script = """
const { performCalculation } = require('./web/src/lib/autocrate-calculations-fixed');
const fs = require('fs');

const params = %s;

const result = performCalculation(params);
if (result.nx_expression) {
    fs.writeFileSync('web_nx_temp.exp', result.nx_expression);
    console.log('Expression generated');
} else {
    console.error('No NX expression in result');
}
""" % json.dumps(test_params)
        
        with open('test_web_calc.js', 'w') as f:
            f.write(test_script)
        
        # Run the Node.js script
        result = subprocess.run(['node', 'test_web_calc.js'], capture_output=True, text=True)
        
        if os.path.exists('web_nx_temp.exp'):
            with open('web_nx_temp.exp', 'r') as f:
                content = f.read()
            web_file = f"web_nx_{datetime.now().strftime('%Y%m%d_%H%M%S')}.exp"
            os.rename('web_nx_temp.exp', web_file)
            print(f"Web expression (from Node.js) saved to: {web_file}")
            return content, web_file
            
    except Exception as e:
        print(f"Error generating web expression: {e}")
        return None, None
    
    print("Could not generate web expression - no API available")
    return None, None

def compare_expressions(desktop_content, web_content, desktop_file, web_file):
    """Compare two NX expression files line by line"""
    print("\n" + "="*80)
    print("COMPARING NX EXPRESSIONS")
    print("="*80)
    
    desktop_lines = desktop_content.splitlines()
    web_lines = web_content.splitlines() if web_content else []
    
    if not web_lines:
        print("ERROR: No web content to compare")
        return False
    
    # Basic statistics
    print(f"\nDesktop expression: {len(desktop_lines)} lines")
    print(f"Web expression: {len(web_lines)} lines")
    
    # Find differences
    differ = difflib.unified_diff(
        desktop_lines, 
        web_lines,
        fromfile=desktop_file,
        tofile=web_file,
        lineterm='',
        n=3
    )
    
    differences = list(differ)
    
    if not differences:
        print("\n✅ PERFECT MATCH! Expressions are identical.")
        return True
    else:
        print(f"\n❌ DIFFERENCES FOUND: {len(differences)} lines differ")
        print("\nDetailed differences:")
        print("-"*80)
        
        # Show first 50 differences
        for i, line in enumerate(differences[:50]):
            print(line)
            if i >= 49 and len(differences) > 50:
                print(f"\n... and {len(differences) - 50} more differences")
                break
        
        # Analyze specific differences
        print("\n" + "-"*80)
        print("ANALYZING KEY DIFFERENCES:")
        print("-"*80)
        
        # Check key values
        key_params = [
            'Overall_Length_OD',
            'Overall_Width_OD', 
            'Overall_Height_OD',
            'Front_Panel_Width',
            'Front_Panel_Height',
            'End_Panel_Length',
            'End_Panel_Height',
            'Top_Panel_Width',
            'Top_Panel_Length',
            'Panel_Thickness',
            'Cleat_Thickness'
        ]
        
        for param in key_params:
            desktop_val = None
            web_val = None
            
            for line in desktop_lines:
                if param in line and '=' in line:
                    desktop_val = line.split('=')[1].strip()
                    break
            
            for line in web_lines:
                if param in line and '=' in line:
                    web_val = line.split('=')[1].strip()
                    break
            
            if desktop_val != web_val:
                print(f"  {param}:")
                print(f"    Desktop: {desktop_val}")
                print(f"    Web:     {web_val}")
        
        return False

def run_comprehensive_test():
    """Run comprehensive test with multiple test cases"""
    
    test_cases = [
        {
            'name': 'Standard Crate (96x48x30 @ 1000lbs)',
            'params': {
                'productLength': 96,
                'productWidth': 48,
                'productHeight': 30,
                'productWeight': 1000,
                'clearance': 2,
                'panelThickness': 0.25,  # 1/4" plywood
                'includeTop': True
            }
        },
        {
            'name': 'Small Crate (24x18x20 @ 150lbs)',
            'params': {
                'productLength': 24,
                'productWidth': 18,
                'productHeight': 20,
                'productWeight': 150,
                'clearance': 1,
                'panelThickness': 0.25,
                'includeTop': True
            }
        },
        {
            'name': 'Large Crate (120x60x48 @ 3000lbs)',
            'params': {
                'productLength': 120,
                'productWidth': 60,
                'productHeight': 48,
                'productWeight': 3000,
                'clearance': 3,
                'panelThickness': 0.75,  # 3/4" plywood
                'includeTop': True
            }
        }
    ]
    
    print("="*80)
    print("NX EXPRESSION COMPARISON TEST SUITE")
    print("="*80)
    
    all_passed = True
    results = []
    
    for test_case in test_cases:
        print(f"\n\nTEST CASE: {test_case['name']}")
        print("-"*80)
        
        # Generate expressions
        desktop_content, desktop_file = generate_desktop_expression(test_case['params'])
        web_content, web_file = generate_web_expression(test_case['params'])
        
        # Compare
        if web_content:
            passed = compare_expressions(desktop_content, web_content, desktop_file, web_file)
            results.append({
                'name': test_case['name'],
                'passed': passed,
                'desktop_file': desktop_file,
                'web_file': web_file
            })
            if not passed:
                all_passed = False
        else:
            print("⚠️ SKIPPED: Could not generate web expression")
            results.append({
                'name': test_case['name'],
                'passed': False,
                'desktop_file': desktop_file,
                'web_file': None,
                'error': 'Could not generate web expression'
            })
            all_passed = False
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    for result in results:
        status = "✅ PASSED" if result['passed'] else "❌ FAILED"
        print(f"{result['name']}: {status}")
        if 'error' in result:
            print(f"  Error: {result['error']}")
    
    print("\n" + "="*80)
    if all_passed:
        print("🎉 ALL TESTS PASSED! Expressions match perfectly.")
    else:
        print("⚠️ SOME TESTS FAILED. Review the differences above.")
    print("="*80)
    
    # Save detailed report
    report_file = f"nx_comparison_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nDetailed report saved to: {report_file}")
    
    return all_passed

if __name__ == "__main__":
    # Run the comprehensive test
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)