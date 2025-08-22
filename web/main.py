"""
Firebase Functions entry point for AutoCrate Web
"""

from firebase_functions import https_fn
from firebase_admin import initialize_app
from app import app as flask_app

# Initialize Firebase Admin
initialize_app()

# Export the Flask app as a Firebase Function
@https_fn.on_request(
    region="us-central1",
    max_instances=100,
    memory=512,
    timeout_sec=60
)
def app(req: https_fn.Request) -> https_fn.Response:
    """Handle all HTTP requests through Flask app"""
    with flask_app.request_context(req.environ):
        return flask_app.full_dispatch_request()

# Export API endpoints as separate function for better performance
@https_fn.on_request(
    region="us-central1",
    max_instances=100,
    memory=1024,
    timeout_sec=120
)
def api(req: https_fn.Request) -> https_fn.Response:
    """Handle API requests with more resources"""
    with flask_app.request_context(req.environ):
        return flask_app.full_dispatch_request()