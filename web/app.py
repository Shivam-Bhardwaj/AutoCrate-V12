"""
AutoCrate Web Application
Flask backend for web-based crate design automation
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_file, send_from_directory
from flask_cors import CORS
from functools import wraps
import os
import sys
import json
import secrets
from datetime import datetime, timedelta
import hashlib

# Add parent directory to path for AutoCrate modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import AutoCrate core functionality
from nx_expressions_generator import (
    calculate_crate_dimensions,
    generate_nx_expressions,
    save_expressions_to_file
)
from skid_logic import calculate_skid_lumber_properties, calculate_skid_layout

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = secrets.token_hex(32)
CORS(app)

# Simple password authentication (for production, use Firebase Auth)
# Password hash for "autocrate2024" - change this in production
PASSWORD_HASH = hashlib.sha256("autocrate2024".encode()).hexdigest()

def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'authenticated' not in session or not session['authenticated']:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    """Main application page"""
    if 'authenticated' not in session or not session['authenticated']:
        return redirect(url_for('login'))
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
        session['authenticated'] = True
        session.permanent = True
        app.permanent_session_lifetime = timedelta(hours=24)
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': 'Invalid password'}), 401

@app.route('/api/logout', methods=['POST'])
def api_logout():
    """Handle logout"""
    session.clear()
    return jsonify({'success': True})

@app.route('/api/calculate', methods=['POST'])
@login_required
def calculate_crate():
    """Calculate crate dimensions and generate NX expressions"""
    try:
        data = request.get_json()
        
        # Extract parameters from request
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
            'intermediate_cleat_width': float(data.get('intermediate_cleat_width', 1.5)),
            'plywood_standard_width': float(data.get('plywood_standard_width', 48)),
            'plywood_standard_length': float(data.get('plywood_standard_length', 96))
        }
        
        # Calculate skid properties
        skid_properties = calculate_skid_lumber_properties(params['product_weight'])
        
        # Calculate crate dimensions
        crate_length = params['product_length'] + (2 * params['clearance_length'])
        crate_width = params['product_width'] + (2 * params['clearance_width'])
        crate_height = params['product_height'] + params['clearance_height']
        
        # Calculate skid layout
        skid_layout = calculate_skid_layout(
            crate_width,
            skid_properties['max_spacing'],
            skid_properties['width']
        )
        
        # Generate basic response with calculations
        result = {
            'success': True,
            'crate_dimensions': {
                'length': crate_length,
                'width': crate_width,
                'height': crate_height,
                'total_height': crate_height + params['panel_thickness'] + params['cleat_thickness'] + params['cleat_width']
            },
            'skid_properties': skid_properties,
            'skid_layout': {
                'count': skid_layout['skid_count'],
                'spacing': skid_layout['skid_pitch'],
                'positions': skid_layout['skid_positions']
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
@login_required
def generate_expressions():
    """Generate and download NX expression file"""
    try:
        data = request.get_json()
        
        # Generate expressions (simplified for web version)
        expressions = generate_nx_expressions_web(data)
        
        # Save to temporary file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"Crate_{timestamp}.exp"
        filepath = os.path.join('web', 'temp', filename)
        
        # Ensure temp directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Write expressions to file
        with open(filepath, 'w') as f:
            for expr in expressions:
                f.write(expr + '\n')
        
        return jsonify({
            'success': True,
            'filename': filename,
            'download_url': f'/api/download/{filename}'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/download/<filename>')
@login_required
def download_file(filename):
    """Download generated expression file"""
    try:
        filepath = os.path.join('web', 'temp', filename)
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=True, download_name=filename)
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/docs')
@app.route('/docs/<path:path>')
def serve_docs(path='index.html'):
    """Serve documentation files"""
    if 'authenticated' not in session or not session['authenticated']:
        return redirect(url_for('login'))
    
    docs_path = os.path.join(os.path.dirname(__file__), '..', 'docs')
    if path == '' or path == '/':
        path = 'index.html'
    return send_from_directory(docs_path, path)

def calculate_estimated_sheets(length, width, height):
    """Estimate number of plywood sheets needed"""
    # Simple estimation - in production would use actual layout calculator
    total_area = 2 * (length * height) + 2 * (width * height) + (length * width)
    sheet_area = 48 * 96  # Standard 4x8 sheet
    return int((total_area / sheet_area) + 1)

def generate_nx_expressions_web(params):
    """Generate NX expressions for web (simplified version)"""
    expressions = []
    expressions.append("# AutoCrate Web Generated Expressions")
    expressions.append(f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    expressions.append("")
    
    # Add basic dimensions
    expressions.append(f"[Inch]Product_Length={params.get('product_length', 48):.3f}")
    expressions.append(f"[Inch]Product_Width={params.get('product_width', 36):.3f}")
    expressions.append(f"[Inch]Product_Height={params.get('product_height', 24):.3f}")
    expressions.append(f"[Pound]Product_Weight={params.get('product_weight', 1000):.1f}")
    
    # Add more expressions as needed...
    
    return expressions

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)