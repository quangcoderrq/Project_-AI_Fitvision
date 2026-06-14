"""
Prediction Module
Handles body measurement prediction pipeline.
"""

from typing import Dict, Optional, Tuple
import os
import numpy as np

from .regressors import BodyMeasurementRegressor
from ..features.normalize import FeatureNormalizer
from ..features.extract_features import FeatureExtractor
from ..pose.pose_detector import PoseDetector
from ..pose.keypoints_utils import KeypointsUtils


class BodyPredictor:
    """
    Complete prediction pipeline for body measurements.
    Combines pose detection, feature extraction, and ML prediction.
    """
    
    def __init__(self, 
                 model_path: Optional[str] = None,
                 scaler_path: Optional[str] = None):
        """
        Initialize predictor.
        
        Args:
            model_path: Path to trained model file
            scaler_path: Path to fitted scaler file
        """
        self.pose_detector = None
        self.feature_extractor = FeatureExtractor()
        self.keypoints_utils = KeypointsUtils()
        
        self.model: Optional[BodyMeasurementRegressor] = None
        self.normalizer: Optional[FeatureNormalizer] = None
        
        # Load model and scaler if paths provided
        if model_path and os.path.exists(model_path):
            self.model = BodyMeasurementRegressor.from_file(model_path)
        
        if scaler_path and os.path.exists(scaler_path):
            self.normalizer = FeatureNormalizer()
            self.normalizer.load(scaler_path)
    
    def _init_pose_detector(self):
        """Lazily initialize pose detector."""
        if self.pose_detector is None:
            self.pose_detector = PoseDetector()
    
    def predict_from_image(self,
                           image: np.ndarray,
                           height_cm: float,
                           weight_kg: float,
                           gender: str = 'male',
                           image_type: str = 'full',
                           ignore_baggy_warning: bool = False) -> Dict:
        """
        Predict body measurements from image.
        
        Args:
            image: Input image (BGR format)
            height_cm: Height in cm
            weight_kg: Weight in kg
            gender: 'male' or 'female'
            image_type: 'full', 'upper', or 'lower'
            ignore_baggy_warning: Whether to ignore baggy clothes warning
            
        Returns:
            Dictionary with predictions and metadata
        """
        self._init_pose_detector()
        
        # Detect pose
        detection = self.pose_detector.detect(image)
        if detection is None:
            return {
                'success': False,
                'error': 'No pose detected in image',
                'measurements': None,
                'confidence': 0.0
            }
        
        # Validate pose
        is_valid, issues = self.pose_detector.validate_pose(detection, image_type=image_type)
        if not is_valid:
            return {
                'success': False,
                'error': f'Invalid pose: {", ".join(issues)}',
                'measurements': None,
                'confidence': 0.0
            }
        
        # Get keypoints
        keypoints = self.pose_detector.get_body_keypoints(detection)
        
        return self.predict_from_keypoints(
            keypoints, height_cm, weight_kg, gender, confidences=detection['confidences'], 
            image_type=image_type, ignore_baggy_warning=ignore_baggy_warning
        )
    
    def predict_from_keypoints(self,
                               keypoints: Dict,
                               height_cm: float,
                               weight_kg: float,
                               gender: str = 'male',
                               confidences: Optional[Dict] = None,
                               image_type: str = 'full',
                               ignore_baggy_warning: bool = False) -> Dict:
        """
        Predict body measurements from keypoints.
        
        Args:
            keypoints: Dictionary of body keypoints
            height_cm: Height in cm
            weight_kg: Weight in kg
            gender: 'male' or 'female'
            confidences: Optional keypoint confidences
            image_type: 'full', 'upper', or 'lower'
            ignore_baggy_warning: Whether to ignore baggy clothes warning
            
        Returns:
            Dictionary with predictions and metadata
        """
        # Check model is loaded
        if self.model is None or self.normalizer is None:
            return {
                'success': False,
                'error': 'Model not loaded. Provide model_path and scaler_path.',
                'measurements': None,
                'confidence': 0.0
            }
        
        # Validate inputs
        is_valid, issues = self.feature_extractor.validate_inputs(
            height_cm, weight_kg, gender
        )
        if not is_valid:
            return {
                'success': False,
                'error': f'Invalid inputs: {", ".join(issues)}',
                'measurements': None,
                'confidence': 0.0
            }
        
        try:
            # Check baggy clothes
            is_baggy = self.feature_extractor.detect_baggy_clothes(
                keypoints, height_cm, weight_kg, gender, image_type
            )
            
            if is_baggy and not ignore_baggy_warning:
                return {
                    'success': True,  # Technically success but needs confirmation
                    'require_user_confirmation': True,
                    'baggy_clothes_detected': True,
                    'warning_message': 'Hệ thống phát hiện bạn có thể đang mặc quần áo rộng. Điều này có thể làm sai lệch số đo thực tế. Bạn có muốn hệ thống tự động điều chỉnh và tiếp tục không?',
                    'measurements': None,
                    'confidence': 0.0
                }
                
            # Extract features
            features, real_measurements = self.feature_extractor.extract_with_real_measurements(
                keypoints, height_cm, weight_kg, gender, image_type
            )
            
            # Normalize features
            features_norm = self.normalizer.transform(features)
            
            # Predict
            predictions = self.model.predict_dict(features_norm)
            
            # Calculate confidence
            confidence = self._calculate_confidence(confidences, features)
            
            # Apply Baggy Correction Factor if confirmed
            if is_baggy and ignore_baggy_warning:
                # Reduce circumferences/widths by ~5%
                predictions['chest'] *= 0.95
                predictions['waist'] *= 0.95
                predictions['hip'] *= 0.95
                if 'shoulder_width_cm' in predictions:
                    predictions['shoulder_width_cm'] *= 0.97 # Shoulder is less affected
            
            return {
                'success': True,
                'error': None,
                'require_user_confirmation': False,
                'baggy_clothes_detected': is_baggy,
                'warning_message': None,
                'measurements': {
                    'chest': round(predictions['chest'], 1),
                    'waist': round(predictions['waist'], 1),
                    'hip': round(predictions['hip'], 1),
                    'shoulder_width_cm': round(predictions.get('shoulder_width_cm', 0), 1),
                    'back_length': round(predictions.get('back_length', 0), 1),
                    'inseam': round(predictions.get('inseam', 0), 1),
                    'thigh_circumference': round(predictions.get('thigh_circumference', 0), 1),
                    'neck_circumference': round(predictions.get('neck_circumference', 0), 1),
                    'arm_circumference': round(predictions.get('arm_circumference', 0), 1),
                },
                'estimated_proportions': real_measurements,
                'confidence': confidence,
                'gender': gender,
                'bmi': round(features[14], 1)  # BMI is at index 14 in expanded features
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'measurements': None,
                'confidence': 0.0
            }
    
    def _calculate_confidence(self, 
                             confidences: Optional[Dict],
                             features: np.ndarray) -> float:
        """
        Calculate overall prediction confidence.
        
        Args:
            confidences: Keypoint detection confidences
            features: Extracted features
            
        Returns:
            Confidence score (0-1)
        """
        scores = []
        
        # Pose detection confidence
        if confidences:
            key_points = [
                'left_shoulder', 'right_shoulder',
                'left_hip', 'right_hip'
            ]
            pose_scores = [
                confidences.get(p, 0) for p in key_points
                if p in confidences
            ]
            if pose_scores:
                scores.append(np.mean(pose_scores))
        
        # Feature quality (check for unreasonable values)
        # Shoulder/hip ratio should be 0.8-1.4
        shoulder_hip = features[5]  # Index 5 is shoulder_hip_ratio (unchanged)
        if 0.8 <= shoulder_hip <= 1.4:
            scores.append(0.9)
        else:
            scores.append(0.5)
        
        # BMI reasonability (15-40)
        bmi = features[14]  # Index 14 in expanded features
        if 15 <= bmi <= 40:
            scores.append(0.9)
        else:
            scores.append(0.6)
        
        if scores:
            return round(float(np.mean(scores)), 2)
        return 0.7  # Default confidence
    
    def load_models(self, model_path: str, scaler_path: str) -> None:
        """
        Load model and scaler.
        
        Args:
            model_path: Path to model file
            scaler_path: Path to scaler file
        """
        self.model = BodyMeasurementRegressor.from_file(model_path)
        self.normalizer = FeatureNormalizer()
        self.normalizer.load(scaler_path)
    
    def is_ready(self) -> bool:
        """Check if predictor is ready for predictions."""
        return self.model is not None and self.normalizer is not None
    
    def close(self):
        """Release resources."""
        if self.pose_detector:
            self.pose_detector.close()
            self.pose_detector = None
