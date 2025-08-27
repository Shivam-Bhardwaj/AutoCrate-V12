"""
Vercel Serverless Function Handler for AutoCrate API
"""
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the FastAPI app
from api.main import app

# Export handler for Vercel
handler = app