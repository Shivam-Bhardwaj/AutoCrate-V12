from http.server import BaseHTTPRequestHandler
import json
import hashlib
from urllib.parse import parse_qs, urlparse
from datetime import datetime

# Password hash for "autocrate2024"
PASSWORD_HASH = hashlib.sha256("autocrate2024".encode()).hexdigest()

# HTML Templates
LOGIN_HTML = """<!DOCTYPE html>
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
    </style>
</head>
<body>
    <div class="login-box">
        <h1>AutoCrate Web</h1>
        <p>Professional CAD Automation Platform</p>
        <form method="POST" action="/login">
            <input type="password" name="password" placeholder="Enter password" required>
            <button type="submit">Sign In</button>
        </form>
    </div>
</body>
</html>"""

MAIN_HTML = """<!DOCTYPE html>
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
        }
        .container {
            max-width: 1200px;
            margin: 30px auto;
            padding: 20px;
        }
        .panel {
            background: white;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            margin-bottom: 20px;
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
        button {
            padding: 12px 24px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 15px;
            font-weight: 600;
            cursor: pointer;
            margin-right: 10px;
        }
        .result-box {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>AutoCrate v12</h1>
    </div>
    
    <div class="container">
        <div class="panel">
            <h2>Crate Parameters</h2>
            <form method="POST" action="/calculate">
                <div class="form-group">
                    <label>Product Weight (lbs)</label>
                    <input type="number" name="weight" value="1000" required>
                </div>
                <div class="form-group">
                    <label>Product Length (inches)</label>
                    <input type="number" name="length" value="48" required>
                </div>
                <div class="form-group">
                    <label>Product Width (inches)</label>
                    <input type="number" name="width" value="36" required>
                </div>
                <div class="form-group">
                    <label>Product Height (inches)</label>
                    <input type="number" name="height" value="24" required>
                </div>
                <button type="submit">Calculate Design</button>
            </form>
        </div>
        
        <div class="panel">
            <h2>Results</h2>
            <div id="results">
                <p style="color: #666;">Enter parameters and click Calculate to see results.</p>
            </div>
        </div>
    </div>
</body>
</html>"""

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = urlparse(self.path).path
        
        if path == '/' or path == '/login':
            # Check for auth cookie
            cookies = self.headers.get('Cookie', '')
            if 'auth=true' in cookies and path == '/':
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(MAIN_HTML.encode())
            else:
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(LOGIN_HTML.encode())
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Not Found')
    
    def do_POST(self):
        path = urlparse(self.path).path
        
        if path == '/login':
            # Read form data
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            params = parse_qs(post_data)
            
            password = params.get('password', [''])[0]
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            
            if password_hash == PASSWORD_HASH:
                # Set cookie and redirect to main page
                self.send_response(303)
                self.send_header('Location', '/')
                self.send_header('Set-Cookie', 'auth=true; Max-Age=86400; Path=/')
                self.end_headers()
            else:
                # Invalid password
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                error_html = LOGIN_HTML.replace('</form>', '<p style="color:red;">Invalid password</p></form>')
                self.wfile.write(error_html.encode())
                
        elif path == '/calculate':
            # Read form data
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            params = parse_qs(post_data)
            
            # Get parameters
            weight = float(params.get('weight', [1000])[0])
            length = float(params.get('length', [48])[0])
            width = float(params.get('width', [36])[0])
            height = float(params.get('height', [24])[0])
            
            # Calculate crate dimensions
            crate_length = length + 8  # 4 inches clearance on each side
            crate_width = width + 8
            crate_height = height + 4
            total_height = crate_height + 0.5 + 1.5 + 3.5  # panel + cleat thickness + cleat width
            
            # Generate results HTML
            results_html = MAIN_HTML.replace(
                '<p style="color: #666;">Enter parameters and click Calculate to see results.</p>',
                f'''
                <div class="result-box">
                    <h3>Crate Dimensions</h3>
                    <p>Length: {crate_length:.2f}"</p>
                    <p>Width: {crate_width:.2f}"</p>
                    <p>Height: {crate_height:.2f}"</p>
                    <p>Total Height (KL_1_Z): {total_height:.2f}"</p>
                    <br>
                    <h3>Materials</h3>
                    <p>Estimated Plywood Sheets: {int((crate_length * crate_height * 4) / (48 * 96)) + 1}</p>
                </div>
                '''
            )
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(results_html.encode())
        else:
            self.send_response(404)
            self.end_headers()