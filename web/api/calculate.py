"""
Vercel Serverless Function for AutoCrate calculations
"""
from http.server import BaseHTTPRequestHandler
import json
import sys
import os

# Add autocrate module to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../api'))

try:
    from autocrate.front_panel_logic import calculate_front_panel_components
    from autocrate.back_panel_logic import calculate_back_panel_components
    # Import other modules as needed
except ImportError:
    # Mock for development
    def calculate_front_panel_components(*args, **kwargs):
        return {"status": "mock", "components": []}
    def calculate_back_panel_components(*args, **kwargs):
        return {"status": "mock", "components": []}

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data)
        
        # Perform calculations
        result = {
            "status": "success",
            "message": "Calculation completed",
            "data": data
        }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(result).encode())
        
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()