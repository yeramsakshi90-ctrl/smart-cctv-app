"""
Video processing controller for handling video uploads and analysis.
"""
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from app.services.video_processing_service import VideoProcessingService
from app.repositories.camera_repository import CameraRepository
from app.middleware.auth_middleware import require_auth
import os

video_bp = Blueprint('video', __name__, url_prefix='/api/videos')


@video_bp.route('/upload', methods=['POST'])
@require_auth
def upload_video(current_user):
    """Upload and process a video file."""
    if 'video' not in request.files:
        return jsonify({'error': 'No video file provided'}), 400
    
    file = request.files['video']
    camera_id = request.form.get('camera_id', type=int)
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not camera_id:
        return jsonify({'error': 'Camera ID is required'}), 400
    
    # Verify camera access
    camera = CameraRepository.find_by_id(camera_id)
    if not camera:
        return jsonify({'error': 'Camera not found'}), 404
    
    if not current_user.is_admin() and camera.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    # Validate file
    video_service = VideoProcessingService()
    if not video_service.validate_video_file(file.filename):
        return jsonify({'error': 'Invalid file type. Allowed: mp4, avi, mov, mkv'}), 400
    
    try:
        # Save video
        filename = secure_filename(file.filename)
        video_path = video_service.save_video(file, filename)
        
        # Process video (this can be done asynchronously in production)
        results, status_code = video_service.process_video(video_path, camera_id)
        
        if status_code == 200:
            return jsonify({
                'message': 'Video processed successfully',
                'video_path': video_path,
                'results': results
            }), 200
        else:
            return jsonify(results), status_code
    
    except Exception as e:
        return jsonify({'error': f'Video processing failed: {str(e)}'}), 500


@video_bp.route('/process/<int:camera_id>', methods=['POST'])
@require_auth
def process_video_for_camera(camera_id, current_user):
    """Process an already uploaded video for a specific camera."""
    data = request.get_json()
    
    if not data or 'video_path' not in data:
        return jsonify({'error': 'Video path is required'}), 400
    
    video_path = data['video_path']
    
    # Verify camera access
    camera = CameraRepository.find_by_id(camera_id)
    if not camera:
        return jsonify({'error': 'Camera not found'}), 404
    
    if not current_user.is_admin() and camera.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    # Verify file exists
    if not os.path.exists(video_path):
        return jsonify({'error': 'Video file not found'}), 404
    
    try:
        video_service = VideoProcessingService()
        results, status_code = video_service.process_video(video_path, camera_id)
        return jsonify(results), status_code
    except Exception as e:
        return jsonify({'error': f'Video processing failed: {str(e)}'}), 500

