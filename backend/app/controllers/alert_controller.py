"""
Alert controller for managing security alerts.
"""
from flask import Blueprint, request, jsonify
from app.services.alert_service import AlertService
from app.middleware.auth_middleware import require_auth, require_admin

alert_bp = Blueprint('alert', __name__, url_prefix='/api/alerts')


@alert_bp.route('', methods=['GET'])
@require_auth
def get_alerts(current_user):
    """Get alerts (filtered by user's cameras unless admin)."""
    camera_id = request.args.get('camera_id', type=int)
    status = request.args.get('status')
    severity = request.args.get('severity')
    limit = request.args.get('limit', type=int, default=100)
    offset = request.args.get('offset', type=int, default=0)
    
    if camera_id:
        # Check access
        from app.repositories.camera_repository import CameraRepository
        camera = CameraRepository.find_by_id(camera_id)
        if not camera:
            return jsonify({'error': 'Camera not found'}), 404
        if not current_user.is_admin() and camera.user_id != current_user.id:
            return jsonify({'error': 'Access denied'}), 403
        
        result, status_code = AlertService.get_alerts_by_camera(camera_id, limit, offset)
        return jsonify(result), status_code
    
    if status == 'pending':
        result, status_code = AlertService.get_pending_alerts(limit, offset)
        return jsonify(result), status_code
    
    if severity:
        result, status_code = AlertService.get_alerts_by_severity(severity, limit, offset)
        return jsonify(result), status_code
    
    # Get recent alerts
    result, status_code = AlertService.get_recent_alerts(limit)
    return jsonify(result), status_code


@alert_bp.route('/<int:alert_id>', methods=['GET'])
@require_auth
def get_alert(alert_id, current_user):
    """Get alert by ID."""
    result, status_code = AlertService.get_alert(alert_id)
    return jsonify(result), status_code


@alert_bp.route('/<int:alert_id>/resolve', methods=['POST'])
@require_auth
def resolve_alert(alert_id, current_user):
    """Resolve an alert."""
    result, status_code = AlertService.resolve_alert(alert_id)
    return jsonify(result), status_code


@alert_bp.route('/statistics', methods=['GET'])
@require_auth
@require_admin
def get_alert_statistics(current_user):
    """Get alert statistics for dashboard (admin only)."""
    result, status_code = AlertService.get_alert_statistics()
    return jsonify(result), status_code

