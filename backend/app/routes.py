"""
Route registration for all API endpoints.
"""
from app.controllers import (
    auth_bp,
    camera_bp,
    alert_bp,
    activity_bp,
    dashboard_bp,
    video_bp
)


def register_routes(app):
    """Register all blueprints with the Flask app."""
    app.register_blueprint(auth_bp)
    app.register_blueprint(camera_bp)
    app.register_blueprint(alert_bp)
    app.register_blueprint(activity_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(video_bp)

