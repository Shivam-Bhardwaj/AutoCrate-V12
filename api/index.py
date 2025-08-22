"""
AutoCrate Web API for Vercel
Serverless Python functions for crate design automation
"""

from flask import Flask, render_template, request, jsonify, session, send_file
from flask_cors import CORS
import os
import sys
import json
import secrets
from datetime import datetime, timedelta
import hashlib
import tempfile

# Add parent directory to path for AutoCrate modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = Flask(__name__, 
    template_folder='../web/templates',
    static_folder='../web/static'
)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))
CORS(app, supports_credentials=True)

# Password authentication - uses environment variable or default
PASSWORD_HASH = os.environ.get('AUTH_PASSWORD_HASH', 
    hashlib.sha256("autocrate2024".encode()).hexdigest())

@app.route('/')
def index():
    """Main application page"""
    # Check if authenticated via cookie
    auth_token = request.cookies.get('auth_token')
    if not auth_token or auth_token != PASSWORD_HASH[:32]:
        return render_template('login.html')
    return render_template('index.html')

@app.route('/login')
def login():
    """Login page"""
    return render_template('login.html')

@app.route('/api/login', methods=['POST'])
def api_login():
    """Handle login authentication"""
    data = request.get_json()
    password = data.get('password', '')
    
    # Hash the provided password and compare
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    if password_hash == PASSWORD_HASH:
        response = jsonify({'success': True})
        # Set cookie for authentication
        response.set_cookie('auth_token', PASSWORD_HASH[:32], 
                          max_age=86400,  # 24 hours
                          httponly=True,
                          secure=True,
                          samesite='Strict')
        return response
    else:
        return jsonify({'success': False, 'error': 'Invalid password'}), 401

@app.route('/api/logout', methods=['POST'])
def api_logout():
    """Handle logout"""
    response = jsonify({'success': True})
    response.set_cookie('auth_token', '', expires=0)
    return response

@app.route('/api/calculate', methods=['POST'])
def calculate_crate():
    """Calculate crate dimensions"""
    try:
        # Check authentication
        auth_token = request.cookies.get('auth_token')
        if not auth_token or auth_token != PASSWORD_HASH[:32]:
            return jsonify({'error': 'Authentication required'}), 401
            
        data = request.get_json()
        
        # Extract parameters
        params = {
            'product_weight': float(data.get('product_weight', 1000)),
            'product_length': float(data.get('product_length', 48)),
            'product_width': float(data.get('product_width', 36)),
            'product_height': float(data.get('product_height', 24)),
            'clearance_length': float(data.get('clearance_length', 4)),
            'clearance_width': float(data.get('clearance_width', 4)),
            'clearance_height': float(data.get('clearance_height', 4)),
            'panel_thickness': float(data.get('panel_thickness', 0.5)),
            'cleat_thickness': float(data.get('cleat_thickness', 1.5)),
            'cleat_width': float(data.get('cleat_width', 3.5)),
            'intermediate_cleat_width': float(data.get('intermediate_cleat_width', 1.5))
        }
        
        # Calculate skid properties (simplified)
        skid_properties = calculate_skid_properties_simple(params['product_weight'])
        
        # Calculate crate dimensions
        crate_length = params['product_length'] + (2 * params['clearance_length'])
        crate_width = params['product_width'] + (2 * params['clearance_width'])
        crate_height = params['product_height'] + params['clearance_height']
        
        # Calculate total height (KL_1_Z)
        total_height = crate_height + params['panel_thickness'] + params['cleat_thickness'] + params['cleat_width']
        
        # Generate response
        result = {
            'success': True,
            'crate_dimensions': {
                'length': crate_length,
                'width': crate_width,
                'height': crate_height,
                'total_height': total_height
            },
            'skid_properties': skid_properties,
            'skid_layout': {
                'count': calculate_skid_count(crate_width, skid_properties['max_spacing']),
                'spacing': skid_properties['max_spacing'],
                'positions': []
            },
            'material_summary': {
                'panel_thickness': params['panel_thickness'],
                'cleat_thickness': params['cleat_thickness'],
                'estimated_plywood_sheets': calculate_estimated_sheets(crate_length, crate_width, crate_height)
            }
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/generate_expressions', methods=['POST'])
def generate_expressions():
    """Generate NX expression file"""
    try:
        # Check authentication
        auth_token = request.cookies.get('auth_token')
        if not auth_token or auth_token != PASSWORD_HASH[:32]:
            return jsonify({'error': 'Authentication required'}), 401
            
        data = request.get_json()
        
        # Generate expressions
        expressions = generate_nx_expressions_simple(data)
        
        # Create temporary file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"Crate_{timestamp}.exp"
        
        # Create temp file content
        content = '\n'.join(expressions)
        
        # Return as downloadable content
        return jsonify({
            'success': True,
            'filename': filename,
            'content': content,
            'download_url': f'/api/download?filename={filename}'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/download')
def download_file():
    """Download expression file"""
    try:
        # Check authentication
        auth_token = request.cookies.get('auth_token')
        if not auth_token or auth_token != PASSWORD_HASH[:32]:
            return jsonify({'error': 'Authentication required'}), 401
            
        filename = request.args.get('filename', 'output.exp')
        content = request.args.get('content', '')
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.exp', delete=False) as f:
            f.write(content)
            temp_path = f.name
        
        return send_file(temp_path, as_attachment=True, download_name=filename)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Simplified calculation functions for Vercel
def calculate_skid_properties_simple(weight):
    """Simplified skid calculation"""
    if weight <= 1000:
        return {'width': 4, 'height': 4, 'max_spacing': 48}
    elif weight <= 3000:
        return {'width': 4, 'height': 6, 'max_spacing': 36}
    else:
        return {'width': 6, 'height': 6, 'max_spacing': 24}

def calculate_skid_count(width, max_spacing):
    """Calculate number of skids needed"""
    min_skids = max(2, int(width / max_spacing) + 1)
    return min_skids

def calculate_estimated_sheets(length, width, height):
    """Estimate plywood sheets needed"""
    total_area = 2 * (length * height) + 2 * (width * height) + (length * width)
    sheet_area = 48 * 96
    return max(1, int((total_area / sheet_area) + 1))

def generate_nx_expressions_simple(params):
    """Generate simplified NX expressions"""
    expressions = []
    expressions.append("# AutoCrate Web Generated Expressions")
    expressions.append(f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    expressions.append("# Vercel Deployment Version")
    expressions.append("")
    
    # Product dimensions
    expressions.append(f"[Inch]Product_Length={params.get('product_length', 48):.3f}")
    expressions.append(f"[Inch]Product_Width={params.get('product_width', 36):.3f}")
    expressions.append(f"[Inch]Product_Height={params.get('product_height', 24):.3f}")
    expressions.append(f"[Pound]Product_Weight={params.get('product_weight', 1000):.1f}")
    expressions.append("")
    
    # Clearances
    expressions.append(f"[Inch]Clearance_Length={params.get('clearance_length', 4):.3f}")
    expressions.append(f"[Inch]Clearance_Width={params.get('clearance_width', 4):.3f}")
    expressions.append(f"[Inch]Clearance_Height={params.get('clearance_height', 4):.3f}")
    expressions.append("")
    
    # Material properties
    expressions.append(f"[Inch]Panel_Thickness={params.get('panel_thickness', 0.5):.3f}")
    expressions.append(f"[Inch]Cleat_Thickness={params.get('cleat_thickness', 1.5):.3f}")
    expressions.append(f"[Inch]Cleat_Width={params.get('cleat_width', 3.5):.3f}")
    expressions.append("")
    
    # Crate dimensions
    if 'crate_dimensions' in params:
        dims = params['crate_dimensions']
        expressions.append(f"[Inch]Crate_Length={dims.get('length', 56):.3f}")
        expressions.append(f"[Inch]Crate_Width={dims.get('width', 44):.3f}")
        expressions.append(f"[Inch]Crate_Height={dims.get('height', 28):.3f}")
        expressions.append(f"[Inch]KL_1_Z={dims.get('total_height', 33):.3f}")
    
    return expressions

# Export handler for Vercel
handler = app