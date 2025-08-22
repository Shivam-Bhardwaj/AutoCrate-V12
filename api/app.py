"""
AutoCrate Web API for Vercel
Simplified Flask app for serverless deployment
"""

from flask import Flask, render_template_string, request, jsonify, make_response
from flask_cors import CORS
import os
import hashlib
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'autocrate-secret-key-2024')
CORS(app, supports_credentials=True)

# Password hash for "autocrate2024"
DEFAULT_PASSWORD_HASH = hashlib.sha256("autocrate2024".encode()).hexdigest()
PASSWORD_HASH = os.environ.get('AUTH_PASSWORD_HASH', DEFAULT_PASSWORD_HASH)

# HTML Templates embedded for simplicity
LOGIN_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>AutoCrate - Login</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .login-box {
            background: white;
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            width: 90%;
            max-width: 400px;
        }
        h1 { color: #667eea; margin-bottom: 10px; }
        p { color: #666; margin-bottom: 30px; font-size: 14px; }
        input {
            width: 100%;
            padding: 12px;
            margin-bottom: 20px;
            border: 2px solid #e1e8ed;
            border-radius: 10px;
            font-size: 16px;
        }
        button {
            width: 100%;
            padding: 14px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
        }
        button:hover { opacity: 0.9; }
        .error { color: red; margin-bottom: 20px; display: none; }
    </style>
</head>
<body>
    <div class="login-box">
        <h1>AutoCrate Web</h1>
        <p>Professional CAD Automation Platform</p>
        <div class="error" id="error"></div>
        <form onsubmit="login(event)">
            <input type="password" id="password" placeholder="Enter password" required>
            <button type="submit">Sign In</button>
        </form>
    </div>
    <script>
        async function login(e) {
            e.preventDefault();
            const password = document.getElementById('password').value;
            const response = await fetch('/api/login', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({password})
            });
            const data = await response.json();
            if (data.success) {
                window.location.href = '/';
            } else {
                document.getElementById('error').style.display = 'block';
                document.getElementById('error').textContent = 'Invalid password';
            }
        }
    </script>
</body>
</html>
"""

MAIN_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>AutoCrate - CAD Automation</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f7fa;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .container {
            max-width: 1200px;
            margin: 30px auto;
            padding: 0 20px;
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
        }
        .panel {
            background: white;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }
        h2 { margin-bottom: 20px; color: #333; }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            color: #666;
            font-size: 14px;
        }
        input {
            width: 100%;
            padding: 10px;
            border: 2px solid #e1e8ed;
            border-radius: 8px;
            font-size: 14px;
        }
        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            font-size: 15px;
            font-weight: 600;
            cursor: pointer;
            margin-right: 10px;
        }
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .btn-secondary {
            background: #f0f4f8;
            color: #667eea;
            border: 2px solid #667eea;
        }
        .result-box {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            margin-top: 20px;
        }
        .result-item {
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid #e1e8ed;
        }
        @media (max-width: 768px) {
            .container { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>AutoCrate v12</h1>
        <div>
            <button class="btn btn-secondary" onclick="logout()">Sign Out</button>
        </div>
    </div>
    
    <div class="container">
        <div class="panel">
            <h2>Crate Parameters</h2>
            <form id="crateForm">
                <div class="form-group">
                    <label>Product Weight (lbs)</label>
                    <input type="number" id="weight" value="1000" required>
                </div>
                <div class="form-group">
                    <label>Product Length (inches)</label>
                    <input type="number" id="length" value="48" required>
                </div>
                <div class="form-group">
                    <label>Product Width (inches)</label>
                    <input type="number" id="width" value="36" required>
                </div>
                <div class="form-group">
                    <label>Product Height (inches)</label>
                    <input type="number" id="height" value="24" required>
                </div>
                <button type="submit" class="btn btn-primary">Calculate</button>
                <button type="button" class="btn btn-secondary" onclick="generateFile()">Generate NX File</button>
            </form>
        </div>
        
        <div class="panel">
            <h2>Results</h2>
            <div id="results">
                <p style="color: #666;">Enter parameters and click Calculate to see results.</p>
            </div>
        </div>
    </div>
    
    <script>
        let currentResults = null;
        
        document.getElementById('crateForm').onsubmit = async (e) => {
            e.preventDefault();
            const data = {
                product_weight: parseFloat(document.getElementById('weight').value),
                product_length: parseFloat(document.getElementById('length').value),
                product_width: parseFloat(document.getElementById('width').value),
                product_height: parseFloat(document.getElementById('height').value),
                clearance_length: 4,
                clearance_width: 4,
                clearance_height: 4,
                panel_thickness: 0.5,
                cleat_thickness: 1.5,
                cleat_width: 3.5
            };
            
            const response = await fetch('/api/calculate', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            });
            
            currentResults = await response.json();
            
            if (currentResults.success) {
                document.getElementById('results').innerHTML = `
                    <div class="result-box">
                        <h3>Crate Dimensions</h3>
                        <div class="result-item">
                            <span>Length:</span>
                            <strong>${currentResults.crate_dimensions.length.toFixed(2)}"</strong>
                        </div>
                        <div class="result-item">
                            <span>Width:</span>
                            <strong>${currentResults.crate_dimensions.width.toFixed(2)}"</strong>
                        </div>
                        <div class="result-item">
                            <span>Height:</span>
                            <strong>${currentResults.crate_dimensions.height.toFixed(2)}"</strong>
                        </div>
                        <div class="result-item">
                            <span>Total Height (KL_1_Z):</span>
                            <strong>${currentResults.crate_dimensions.total_height.toFixed(2)}"</strong>
                        </div>
                    </div>
                    <div class="result-box">
                        <h3>Materials</h3>
                        <div class="result-item">
                            <span>Plywood Sheets:</span>
                            <strong>${currentResults.material_summary.estimated_plywood_sheets}</strong>
                        </div>
                        <div class="result-item">
                            <span>Skid Size:</span>
                            <strong>${currentResults.skid_properties.width}" × ${currentResults.skid_properties.height}"</strong>
                        </div>
                    </div>
                `;
            }
        };
        
        async function generateFile() {
            if (!currentResults) {
                alert('Please calculate first');
                return;
            }
            
            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(currentResults)
            });
            
            const data = await response.json();
            if (data.success) {
                // Download file
                const blob = new Blob([data.content], {type: 'text/plain'});
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = data.filename;
                a.click();
            }
        }
        
        async function logout() {
            await fetch('/api/logout', {method: 'POST'});
            window.location.href = '/login';
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    auth_cookie = request.cookies.get('auth_token')
    if auth_cookie != PASSWORD_HASH[:32]:
        return render_template_string(LOGIN_HTML)
    return render_template_string(MAIN_HTML)

@app.route('/login')
def login():
    return render_template_string(LOGIN_HTML)

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    password = data.get('password', '')
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    if password_hash == PASSWORD_HASH:
        response = make_response(jsonify({'success': True}))
        response.set_cookie('auth_token', PASSWORD_HASH[:32], max_age=86400)
        return response
    return jsonify({'success': False, 'error': 'Invalid password'}), 401

@app.route('/api/logout', methods=['POST'])
def api_logout():
    response = make_response(jsonify({'success': True}))
    response.set_cookie('auth_token', '', expires=0)
    return response

@app.route('/api/calculate', methods=['POST'])
def calculate_crate():
    data = request.get_json()
    
    # Simple calculations
    crate_length = data['product_length'] + (2 * data['clearance_length'])
    crate_width = data['product_width'] + (2 * data['clearance_width'])
    crate_height = data['product_height'] + data['clearance_height']
    total_height = crate_height + data['panel_thickness'] + data['cleat_thickness'] + data['cleat_width']
    
    # Skid properties
    weight = data['product_weight']
    if weight <= 1000:
        skid_props = {'width': 4, 'height': 4, 'max_spacing': 48}
    elif weight <= 3000:
        skid_props = {'width': 4, 'height': 6, 'max_spacing': 36}
    else:
        skid_props = {'width': 6, 'height': 6, 'max_spacing': 24}
    
    # Estimate sheets
    total_area = 2 * (crate_length * crate_height) + 2 * (crate_width * crate_height) + (crate_length * crate_width)
    sheets = max(1, int((total_area / (48 * 96)) + 1))
    
    return jsonify({
        'success': True,
        'crate_dimensions': {
            'length': crate_length,
            'width': crate_width,
            'height': crate_height,
            'total_height': total_height
        },
        'skid_properties': skid_props,
        'material_summary': {
            'panel_thickness': data['panel_thickness'],
            'cleat_thickness': data['cleat_thickness'],
            'estimated_plywood_sheets': sheets
        }
    })

@app.route('/api/generate', methods=['POST'])
def generate_expressions():
    data = request.get_json()
    
    # Generate NX expressions
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"Crate_{timestamp}.exp"
    
    expressions = [
        "# AutoCrate Web Generated Expressions",
        f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        f"[Inch]Product_Length={data.get('product_length', 48):.3f}",
        f"[Inch]Product_Width={data.get('product_width', 36):.3f}",
        f"[Inch]Product_Height={data.get('product_height', 24):.3f}",
        f"[Pound]Product_Weight={data.get('product_weight', 1000):.1f}",
        "",
        f"[Inch]Crate_Length={data['crate_dimensions']['length']:.3f}",
        f"[Inch]Crate_Width={data['crate_dimensions']['width']:.3f}",
        f"[Inch]Crate_Height={data['crate_dimensions']['height']:.3f}",
        f"[Inch]KL_1_Z={data['crate_dimensions']['total_height']:.3f}"
    ]
    
    content = '\n'.join(expressions)
    
    return jsonify({
        'success': True,
        'filename': filename,
        'content': content
    })

# Vercel requires the Flask app to be available as 'app'
# The app variable is already defined above and will be automatically detected