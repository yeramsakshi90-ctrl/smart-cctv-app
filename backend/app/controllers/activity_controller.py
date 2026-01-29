"""
Activity controller for managing detected activities.
"""
from flask import Blueprint, request, jsonify
from app.repositories.activity_repository import ActivityRepository
from app.repositories.camera_repository import CameraRepository
from app.middleware.auth_middleware import require_auth

activity_bp = Blueprint('activity', __name__, url_prefix='/api/activities')


@activity_bp.route('', methods=['GET'])
@require_auth
def get_activities(current_user):
    """Get activities (filtered by user's cameras unless admin)."""
    camera_id = request.args.get('camera_id', type=int)
    activity_type = request.args.get('activity_type')
    limit = request.args.get('limit', type=int, default=100)
    offset = request.args.get('offset', type=int, default=0)
    
    if camera_id:
        # Check access
        camera = CameraRepository.find_by_id(camera_id)
        if not camera:
            return jsonify({'error': 'Camera not found'}), 404
        if not current_user.is_admin() and camera.user_id != current_user.id:
            return jsonify({'error': 'Access denied'}), 403
        
        if activity_type:
            activities = ActivityRepository.find_by_camera_and_type(camera_id, activity_type, limit, offset)
        else:
            activities = ActivityRepository.find_by_camera_id(camera_id, limit, offset)
    elif activity_type:
        activities = ActivityRepository.find_by_type(activity_type, limit, offset)
    else:
        activities = ActivityRepository.find_recent(limit, offset)
    
    return jsonify({
        'activities': [activity.to_dict() for activity in activities],
        'count': len(activities)
    }), 200


@activity_bp.route('/<int:activity_id>', methods=['GET'])
@require_auth
def get_activity(activity_id, current_user):
    """Get activity by ID."""
    activity = ActivityRepository.find_by_id(activity_id)
    
    if not activity:
        return jsonify({'error': 'Activity not found'}), 404
    
    # Check access
    camera = CameraRepository.find_by_id(activity.camera_id)
    if not current_user.is_admin() and camera.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    return jsonify({'activity': activity.to_dict()}), 200

