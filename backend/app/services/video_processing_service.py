"""
Video processing service for handling video uploads and frame extraction.
Processes video files for analysis instead of live CCTV feeds.
"""
import cv2
import os
import json
from typing import Dict, List, Optional, Generator
from datetime import datetime
from app.config import Config
from app.services.face_detection_service import FaceDetectionService
from app.services.mask_detection_service import MaskDetectionService
from app.services.activity_detection_service import ActivityDetectionService
from app.repositories.activity_repository import ActivityRepository
from app.services.alert_service import AlertService


class VideoProcessingService:
    """Service for video processing and analysis."""
    
    def __init__(self):
        """Initialize video processing service."""
        self.face_detection = FaceDetectionService()
        self.mask_detection = MaskDetectionService()
        self.activity_detection = ActivityDetectionService()
        self.upload_folder = Config.UPLOAD_FOLDER
        
        # Create upload folder if it doesn't exist
        os.makedirs(self.upload_folder, exist_ok=True)
    
    def validate_video_file(self, filename: str) -> bool:
        """Validate video file extension."""
        from app.utils.validators import validate_video_file
        return validate_video_file(filename)
    
    def save_video(self, file, filename: str) -> str:
        """
        Save uploaded video file.
        
        Args:
            file: File object
            filename: Original filename
            
        Returns:
            Path to saved file
        """
        # Generate unique filename
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        safe_filename = f"{timestamp}_{filename}"
        filepath = os.path.join(self.upload_folder, safe_filename)
        
        file.save(filepath)
        return filepath
    
    def extract_frames(self, video_path: str, frame_interval: int = 30) -> Generator:
        """
        Extract frames from video at specified intervals.
        
        Args:
            video_path: Path to video file
            frame_interval: Extract every Nth frame
            
        Yields:
            Frame number and frame array
        """
        cap = cv2.VideoCapture(video_path)
        frame_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_count % frame_interval == 0:
                yield frame_count, frame
            
            frame_count += 1
        
        cap.release()
    
    def process_video(self, video_path: str, camera_id: int) -> Dict:
        """
        Process video file for analysis.
        
        Args:
            video_path: Path to video file
            camera_id: Associated camera ID
            
        Returns:
            Processing results summary
        """
        results = {
            'frames_processed': 0,
            'faces_detected': 0,
            'spoofed_faces': 0,
            'mask_violations': 0,
            'suspicious_activities': 0,
            'alerts_created': 0,
            'processing_time': 0
        }
        
        start_time = datetime.utcnow()
        previous_frame = None
        
        try:
            for frame_num, frame in self.extract_frames(video_path, frame_interval=30):
                # Face detection
                face_results = self.face_detection.process_frame(frame)
                results['faces_detected'] += face_results['faces_detected']
                
                # Check for spoofed faces
                for face in face_results['faces']:
                    if face['is_spoofed']:
                        results['spoofed_faces'] += 1
                        # Create alert for spoofed face
                        AlertService.create_alert(
                            camera_id=camera_id,
                            alert_type='face_spoof',
                            message=f'Spoofed face detected at frame {frame_num}',
                            severity='high',
                            metadata={'frame': frame_num, 'confidence': face['spoof_confidence']}
                        )
                        results['alerts_created'] += 1
                
                # Mask detection
                mask_results = self.mask_detection.process_frame(frame)
                if mask_results['compliance_rate'] < 1.0:
                    mask_violations = sum(1 for m in mask_results['mask_compliance'] if not m['has_mask'])
                    results['mask_violations'] += mask_violations
                    
                    if mask_violations > 0:
                        # Create alert for mask violation
                        AlertService.create_alert(
                            camera_id=camera_id,
                            alert_type='mask_violation',
                            message=f'{mask_violations} mask violation(s) detected at frame {frame_num}',
                            severity='medium',
                            metadata={'frame': frame_num, 'violations': mask_violations}
                        )
                        results['alerts_created'] += 1
                
                # Activity detection
                activity_results = self.activity_detection.analyze_frame(frame, previous_frame)
                if activity_results['suspicious_activity']['is_suspicious']:
                    results['suspicious_activities'] += 1
                    # Create alert for suspicious activity
                    AlertService.create_alert(
                        camera_id=camera_id,
                        alert_type='suspicious_activity',
                        message=f"Suspicious activity detected: {activity_results['suspicious_activity']['activity_type']}",
                        severity='high',
                        metadata={
                            'frame': frame_num,
                            'activity_type': activity_results['suspicious_activity']['activity_type'],
                            'confidence': activity_results['suspicious_activity']['confidence']
                        }
                    )
                    results['alerts_created'] += 1
                    
                    # Log activity
                    ActivityRepository.create(
                        camera_id=camera_id,
                        activity_type=activity_results['suspicious_activity']['activity_type'],
                        description=activity_results['suspicious_activity'].get('details', {}).get('reason', 'Suspicious activity detected'),
                        confidence_score=activity_results['suspicious_activity']['confidence'],
                        metadata=json.dumps(activity_results['suspicious_activity'].get('details', {}))
                    )
                
                previous_frame = frame.copy()
                results['frames_processed'] += 1
        
        except Exception as e:
            return {'error': f'Video processing failed: {str(e)}'}, 500
        
        end_time = datetime.utcnow()
        results['processing_time'] = (end_time - start_time).total_seconds()
        
        return results, 200

