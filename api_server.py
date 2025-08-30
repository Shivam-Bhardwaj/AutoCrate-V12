"""
AutoCrate NX Expression API Server
Provides REST API for NX expression generation using the exact desktop calculation engine
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import sys
import os
import json
from datetime import datetime
import tempfile
import traceback
import math

# Add parent directory to path to import AutoCrate modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the exact desktop calculation engine logic function
from autocrate.nx_expressions_generator import generate_crate_expressions_logic

app = Flask(__name__)

# Configure CORS to allow requests from the web app with all necessary headers
CORS(app, origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002", "http://localhost:3003", "*"],
     allow_headers=["Content-Type", "Authorization", "Accept"],
     methods=["GET", "POST", "OPTIONS"],
     supports_credentials=True)

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'version': '1.1.0',
        'engine': 'desktop_python'
    })

@app.route('/api/calculate', methods=['POST'])
def calculate():
    """
    Calculate crate specifications using the desktop Python engine
    Returns the same calculations the desktop app uses
    """
    try:
        data = request.json
        
        # Extract parameters from request with defaults matching desktop
        product_length = float(data.get('productLength', 48))
        product_width = float(data.get('productWidth', 48))
        product_height = float(data.get('productHeight', 48))
        product_weight = float(data.get('productWeight', 1000))
        quantity = int(data.get('quantity', 1))
        panel_thickness = float(data.get('panelThickness', 0.75))
        cleat_thickness = float(data.get('cleatThickness', 0.75))  # Desktop default is 0.75
        cleat_member_width = float(data.get('cleatMemberWidth', 3.5))
        skid_height = float(data.get('skidHeight', 3.5))
        floorboard_thickness = float(data.get('floorboardThickness', 1.5))  # Desktop default is 1.5
        clearance = float(data.get('clearance', 2.0))
        clearance_above = float(data.get('clearanceAbove', 2.0))
        ground_clearance = float(data.get('groundClearance', 1.0))
        safety_factor = float(data.get('safetyFactor', 1.5))
        
        # Calculate total weight with safety factor
        total_weight = product_weight * quantity * safety_factor
        
        # Calculate basic dimensions (matching desktop logic)
        panel_assembly_thickness = panel_thickness + cleat_thickness
        
        # Overall dimensions
        overall_width = product_width + (2 * clearance) + (2 * panel_assembly_thickness)
        overall_length = product_length + (2 * clearance) + (2 * panel_assembly_thickness)
        overall_height = skid_height + floorboard_thickness + product_height + clearance_above
        
        # Panel dimensions
        front_panel_width = overall_width
        front_panel_height = overall_height - ground_clearance
        
        back_panel_width = overall_width
        back_panel_height = overall_height - ground_clearance
        
        end_panel_length = overall_length - (2 * panel_assembly_thickness)
        end_panel_height = overall_height - ground_clearance
        
        top_panel_length = overall_length
        top_panel_width = overall_width
        
        # Check for vertical cleat material additions (critical for matching desktop)
        if front_panel_width > 48:
            additional_cleats = math.ceil((front_panel_width - 48) / 48)
            material_needed = additional_cleats * cleat_member_width
            front_panel_width += material_needed
            back_panel_width += material_needed
            overall_width += material_needed
        
        # Return calculated dimensions
        return jsonify({
            'success': True,
            'calculations': {
                'overallDimensions': {
                    'width': overall_width,
                    'length': overall_length,
                    'height': overall_height
                },
                'panelDimensions': {
                    'front': {
                        'width': front_panel_width,
                        'height': front_panel_height
                    },
                    'back': {
                        'width': back_panel_width,
                        'height': back_panel_height
                    },
                    'end': {
                        'length': end_panel_length,
                        'height': end_panel_height
                    },
                    'top': {
                        'length': top_panel_length,
                        'width': top_panel_width
                    }
                },
                'weights': {
                    'productWeight': product_weight,
                    'quantity': quantity,
                    'totalWeight': product_weight * quantity,
                    'designLoad': total_weight
                },
                'materials': {
                    'panelThickness': panel_thickness,
                    'cleatThickness': cleat_thickness,
                    'panelAssemblyThickness': panel_assembly_thickness
                }
            },
            'engine': 'desktop_python',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/generate-nx', methods=['POST', 'OPTIONS'])
def generate_nx():
    # Handle CORS preflight request
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
    """
    Generate NX expression file using the desktop Python engine
    Returns the exact same expressions as the desktop application
    """
    try:
        data = request.json
        
        # Extract parameters with defaults matching desktop
        product_length = float(data.get('productLength', 48))
        product_width = float(data.get('productWidth', 48))
        product_height = float(data.get('productHeight', 48))
        product_weight = float(data.get('productWeight', 1000))
        quantity = int(data.get('quantity', 1))
        panel_thickness = float(data.get('panelThickness', 0.75))
        cleat_thickness = float(data.get('cleatThickness', 0.75))  # Desktop default is 0.75
        cleat_member_width = float(data.get('cleatMemberWidth', 3.5))
        clearance = float(data.get('clearance', 2.0))
        clearance_above = float(data.get('clearanceAbove', 2.0))
        ground_clearance = float(data.get('groundClearance', 1.0))
        floorboard_thickness = float(data.get('floorboardThickness', 1.5))  # Desktop default is 1.5
        allow_3x4_skids = data.get('allow3x4Skids', True)  # Desktop default is True
        safety_factor = float(data.get('safetyFactor', 1.5))
        
        # Don't apply safety factor here - desktop doesn't apply it for NX generation
        effective_weight = product_weight * quantity  # No safety factor for NX expressions
        
        # Default lumber widths (matching desktop)
        selected_lumber = [5.5, 7.25, 9.25, 11.25]  # Desktop default sizes
        
        # Default parameters for floorboards (matching desktop)
        max_gap = 0.25  # Maximum gap in inches (desktop default)
        min_custom = 2.5  # Minimum custom width (desktop default)
        force_custom = True  # Desktop default is True
        
        # Panel selections (all panels enabled by default)
        plywood_selections = {
            "FP": True,  # Front Panel
            "BP": True,  # Back Panel
            "LP": True,  # Left Panel
            "RP": True,  # Right Panel
            "TP": True   # Top Panel
        }
        
        # Create temporary file for output
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        material_type = "PLY" if panel_thickness >= 0.5 else "OSB"
        filename = (f"{timestamp}_Crate_"
                   f"{product_length:.0f}x{product_width:.0f}x{product_height:.0f}_"
                   f"W{product_weight:.0f}_"
                   f"5P_{material_type}{panel_thickness:.2f}_"
                   f"C{clearance:.1f}_ASTM.exp")
        
        temp_path = os.path.join(tempfile.gettempdir(), filename)
        
        # Call the actual desktop logic function
        success, message = generate_crate_expressions_logic(
            product_weight_lbs=effective_weight,
            product_length_in=product_length,
            product_width_in=product_width,
            clearance_each_side_in=clearance,
            allow_3x4_skids_bool=allow_3x4_skids,
            panel_thickness_in=panel_thickness,
            cleat_thickness_in=cleat_thickness,
            cleat_member_actual_width_in=cleat_member_width,
            product_actual_height_in=product_height,
            clearance_above_product_in=clearance_above,
            ground_clearance_in=ground_clearance,
            floorboard_actual_thickness_in=floorboard_thickness,
            selected_std_lumber_widths=selected_lumber,
            max_allowable_middle_gap_in=max_gap,
            min_custom_lumber_width_in=min_custom,
            force_small_custom_board_bool=force_custom,
            output_filename=temp_path,
            plywood_panel_selections=plywood_selections
        )
        
        if not success:
            return jsonify({
                'success': False,
                'error': message
            }), 400
        
        # Read the generated expression file
        with open(temp_path, 'r') as f:
            expression_content = f.read()
        
        # Always return JSON with the expressions
        # The client will handle creating the download
        response = jsonify({
            'success': True,
            'expressions': expression_content,
            'filename': filename,
            'engine': 'desktop_python_logic',
            'timestamp': datetime.now().isoformat()
        })
        
        # Add CORS headers explicitly for this response
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        
        return response
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/validate', methods=['POST'])
def validate():
    """
    Validate crate specifications against ASTM standards
    Uses the desktop validation logic
    """
    try:
        data = request.json
        
        # Extract parameters
        params = {
            'product_weight': float(data.get('productWeight', 0)),
            'quantity': int(data.get('quantity', 1)),
            'safety_factor': float(data.get('safetyFactor', 1.5))
        }
        
        # Perform validation
        total_weight = params['product_weight'] * params['quantity']
        design_load = total_weight * params['safety_factor']
        
        warnings = []
        if design_load > 10000:
            warnings.append("Design load exceeds 10,000 lbs - consider multiple crates")
        
        if params['safety_factor'] < 1.5:
            warnings.append("Safety factor below ASTM recommended minimum of 1.5")
        
        return jsonify({
            'success': True,
            'valid': len(warnings) == 0,
            'warnings': warnings,
            'design_load': design_load,
            'total_weight': total_weight
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Run the server
    print("="*60)
    print("AutoCrate NX Expression API Server")
    print("Using Desktop Python Calculation Engine")
    print("="*60)
    print("Server running at: http://localhost:5000")
    print("Health check: http://localhost:5000/health")
    print("")
    print("Endpoints:")
    print("  POST /api/calculate - Calculate crate dimensions")
    print("  POST /api/generate-nx - Generate NX expressions")
    print("  POST /api/validate - Validate specifications")
    print("="*60)
    
    app.run(host='0.0.0.0', port=5000, debug=True)