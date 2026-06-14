"""
Feature Extractor Module
Extracts feature vectors from pose keypoints and user inputs.
"""

from typing import Dict, List, Optional, Tuple
import numpy as np

from ..pose.keypoints_utils import KeypointsUtils
from .pixel_converter import PixelConverter


class FeatureExtractor:
    """Extracts features for body measurement prediction."""
    
    # Feature names in order — expanded from 11 to 18
    FEATURE_NAMES = [
        'shoulder_width_ratio',
        'hip_width_ratio',
        'torso_length_ratio',
        'leg_length_ratio',
        'arm_length_ratio',
        'shoulder_hip_ratio',
        'torso_leg_ratio',
        # New features
        'back_length_ratio',
        'belly_width_ratio',
        'neck_width_ratio',
        'upper_arm_ratio',
        'thigh_ratio',
        'inseam_ratio',
        'arm_span_ratio',
        # Physical measurements
        'bmi',
        'height_cm',
        'weight_kg',
        'gender_male'  # 1 for male, 0 for female
    ]
    
    def __init__(self):
        self.keypoints_utils = KeypointsUtils()
        self.pixel_converter = PixelConverter()
    
    def extract(self, 
                keypoints: Dict[str, List[int]],
                height_cm: float,
                weight_kg: float,
                gender: str = 'male',
                image_type: str = 'full') -> np.ndarray:
        """
        Extract feature vector from keypoints and user inputs.
        
        Args:
            keypoints: Dictionary of pose keypoints
            height_cm: User's height in cm
            weight_kg: User's weight in kg
            gender: 'male' or 'female'
            image_type: 'full', 'upper', or 'lower'
            
        Returns:
            Feature vector as numpy array (18 features)
        """
        # Calculate pixel measurements
        proportions = self.keypoints_utils.estimate_body_proportions(keypoints)
        
        # Get body height in pixels for ratio calculation
        if image_type == 'full':
            body_height_px = self.keypoints_utils.estimate_body_height_pixels(keypoints)
        elif image_type == 'upper':
            # Estimate from torso length (typically ~30% of height)
            distances = self.keypoints_utils.calculate_all_distances(keypoints)
            torso_left = distances.get('torso_left', 0)
            torso_right = distances.get('torso_right', 0)
            torso = (torso_left + torso_right) / 2 if (torso_left > 0 and torso_right > 0) else max(torso_left, torso_right)
            body_height_px = torso / 0.30 if torso > 0 else 1000  # fallback
        elif image_type == 'lower':
            # Estimate from leg length (typically ~45% of height)
            distances = self.keypoints_utils.calculate_all_distances(keypoints)
            leg_left = distances.get('left_leg', 0)
            leg_right = distances.get('right_leg', 0)
            leg = (leg_left + leg_right) / 2 if (leg_left > 0 and leg_right > 0) else max(leg_left, leg_right)
            body_height_px = leg / 0.45 if leg > 0 else 1000  # fallback
        
        if body_height_px <= 0:
            body_height_px = 1000  # Prevent div by zero
        
        bmi = self._calculate_bmi(height_cm, weight_kg)
        
        # Get body width estimations
        body_widths = self.keypoints_utils.estimate_body_widths(
            keypoints, bmi, gender
        )
        
        # Calculate ratios relative to body height
        features = {}
        
        # === Original width ratios ===
        features['shoulder_width_ratio'] = (
            proportions.get('shoulder_width', 0) / body_height_px
        )
        features['hip_width_ratio'] = (
            proportions.get('hip_width', 0) / body_height_px
        )
        
        # === Original length ratios ===
        features['torso_length_ratio'] = (
            proportions.get('torso_length', 0) / body_height_px
        )
        features['leg_length_ratio'] = (
            proportions.get('leg_length', 0) / body_height_px
        )
        features['arm_length_ratio'] = (
            proportions.get('arm_length', 0) / body_height_px
        )
        
        # === Original body proportions ===
        features['shoulder_hip_ratio'] = proportions.get('shoulder_hip_ratio', 1.0)
        features['torso_leg_ratio'] = proportions.get('torso_leg_ratio', 0.5)
        
        # === NEW feature ratios ===
        features['back_length_ratio'] = (
            proportions.get('back_length', 0) / body_height_px
        )
        features['belly_width_ratio'] = body_widths.get('belly_width_ratio', 
            proportions.get('belly_width', 0) / body_height_px if proportions.get('belly_width', 0) > 0 else 0.15
        )
        features['neck_width_ratio'] = (
            proportions.get('neck_width', 0) / body_height_px
        )
        features['upper_arm_ratio'] = (
            proportions.get('upper_arm_length', 0) / body_height_px
        )
        features['thigh_ratio'] = (
            proportions.get('thigh_length', 0) / body_height_px
        )
        features['inseam_ratio'] = (
            proportions.get('inseam_length', 0) / body_height_px
        )
        features['arm_span_ratio'] = (
            proportions.get('arm_span', 0) / body_height_px
        )
        
        # === Physical measurements ===
        features['bmi'] = bmi
        features['height_cm'] = height_cm
        features['weight_kg'] = weight_kg
        features['gender_male'] = 1.0 if gender.lower() == 'male' else 0.0
        
        # Create feature vector in correct order
        feature_vector = np.array([
            features[name] for name in self.FEATURE_NAMES
        ], dtype=np.float32)
        
        return feature_vector
    
    def extract_with_real_measurements(self,
                                        keypoints: Dict[str, List[int]],
                                        height_cm: float,
                                        weight_kg: float,
                                        gender: str = 'male',
                                        image_type: str = 'full') -> Tuple[np.ndarray, Dict]:
        """
        Extract features and also return estimated real measurements.
        
        Args:
            keypoints: Dictionary of pose keypoints
            height_cm: User's height in cm
            weight_kg: User's weight in kg
            gender: 'male' or 'female'
            
        Returns:
            Tuple of (feature_vector, measurements_dict)
        """
        # Get feature vector
        feature_vector = self.extract(keypoints, height_cm, weight_kg, gender, image_type)
        
        # Calculate pixel to real conversion
        if image_type == 'full':
            body_height_px = self.keypoints_utils.estimate_body_height_pixels(keypoints)
        elif image_type == 'upper':
            distances = self.keypoints_utils.calculate_all_distances(keypoints)
            torso = (distances.get('torso_left', 0) + distances.get('torso_right', 0)) / 2
            body_height_px = torso / 0.30 if torso > 0 else 1000
        else:
            distances = self.keypoints_utils.calculate_all_distances(keypoints)
            leg = (distances.get('left_leg', 0) + distances.get('right_leg', 0)) / 2
            body_height_px = leg / 0.45 if leg > 0 else 1000
            
        self.pixel_converter.calibrate(height_cm, body_height_px)
        
        # Get pixel measurements
        proportions = self.keypoints_utils.estimate_body_proportions(keypoints)
        
        # Convert to real measurements
        real_measurements = {}
        
        # Original measurements
        if 'shoulder_width' in proportions:
            real_measurements['shoulder_width_cm'] = (
                self.pixel_converter.pixels_to_cm(proportions['shoulder_width'])
            )
        
        if 'hip_width' in proportions:
            real_measurements['hip_width_cm'] = (
                self.pixel_converter.pixels_to_cm(proportions['hip_width'])
            )
        
        if 'torso_length' in proportions:
            real_measurements['torso_length_cm'] = (
                self.pixel_converter.pixels_to_cm(proportions['torso_length'])
            )
        
        if 'leg_length' in proportions:
            real_measurements['leg_length_cm'] = (
                self.pixel_converter.pixels_to_cm(proportions['leg_length'])
            )
        
        if 'arm_length' in proportions:
            real_measurements['arm_length_cm'] = (
                self.pixel_converter.pixels_to_cm(proportions['arm_length'])
            )
        
        # NEW measurements
        if 'back_length' in proportions:
            real_measurements['back_length_cm'] = (
                self.pixel_converter.pixels_to_cm(proportions['back_length'])
            )
        
        if 'inseam_length' in proportions:
            real_measurements['inseam_cm'] = (
                self.pixel_converter.pixels_to_cm(proportions['inseam_length'])
            )
        
        if 'upper_arm_length' in proportions:
            real_measurements['upper_arm_cm'] = (
                self.pixel_converter.pixels_to_cm(proportions['upper_arm_length'])
            )
        
        if 'thigh_length' in proportions:
            real_measurements['thigh_length_cm'] = (
                self.pixel_converter.pixels_to_cm(proportions['thigh_length'])
            )
        
        if 'belly_width' in proportions:
            real_measurements['belly_width_cm'] = (
                self.pixel_converter.pixels_to_cm(proportions['belly_width'])
            )
        
        if 'neck_width' in proportions:
            real_measurements['neck_width_cm'] = (
                self.pixel_converter.pixels_to_cm(proportions['neck_width'])
            )
        
        if 'arm_span' in proportions:
            real_measurements['arm_span_cm'] = (
                self.pixel_converter.pixels_to_cm(proportions['arm_span'])
            )
        
        return feature_vector, real_measurements
    
    def _calculate_bmi(self, height_cm: float, weight_kg: float) -> float:
        """Calculate BMI from height and weight."""
        height_m = height_cm / 100
        if height_m > 0:
            return weight_kg / (height_m ** 2)
        return 0
    
    def get_feature_names(self) -> List[str]:
        """Get list of feature names."""
        return self.FEATURE_NAMES.copy()
        
    def detect_baggy_clothes(self, keypoints: Dict[str, List[int]], height_cm: float, weight_kg: float, gender: str, image_type: str = 'full') -> bool:
        """
        Heuristic to detect baggy clothes.
        Checks if estimated body width is significantly larger than what's typical for the person's BMI.
        """
        if image_type == 'lower':
            return False  # Hard to detect baggy pants without full contour, skip for now
            
        bmi = self._calculate_bmi(height_cm, weight_kg)
        proportions = self.keypoints_utils.estimate_body_proportions(keypoints)
        
        if image_type == 'full':
            body_height_px = self.keypoints_utils.estimate_body_height_pixels(keypoints)
        else:
            distances = self.keypoints_utils.calculate_all_distances(keypoints)
            torso = (distances.get('torso_left', 0) + distances.get('torso_right', 0)) / 2
            body_height_px = torso / 0.30 if torso > 0 else 1000
            
        if body_height_px <= 0: return False
        
        # Check belly width ratio (usually from body contour / image masks, but here we use proportion)
        # In a real app with masks, we'd compare mask width to skeletal width.
        # Since we only have keypoints here, we can estimate if the shoulder width or belly width is very large.
        belly_width_ratio = proportions.get('belly_width', 0) / body_height_px
        shoulder_width_ratio = proportions.get('shoulder_width', 0) / body_height_px
        
        # Baggy heuristic: If BMI is low/normal (e.g., < 25), but the estimated shoulder/belly width is very high
        if bmi < 24 and (shoulder_width_ratio > 0.28 or belly_width_ratio > 0.25):
            return True
            
        if bmi < 28 and (shoulder_width_ratio > 0.32 or belly_width_ratio > 0.30):
            return True
            
        return False
    
    def validate_inputs(self, 
                       height_cm: float, 
                       weight_kg: float,
                       gender: str) -> Tuple[bool, List[str]]:
        """
        Validate user inputs.
        
        Args:
            height_cm: Height in cm
            weight_kg: Weight in kg
            gender: Gender string
            
        Returns:
            Tuple of (is_valid, list of issues)
        """
        issues = []
        
        # Validate height (reasonable range: 100-250 cm)
        if height_cm < 100:
            issues.append(f"Height {height_cm}cm seems too low (min: 100cm)")
        elif height_cm > 250:
            issues.append(f"Height {height_cm}cm seems too high (max: 250cm)")
        
        # Validate weight (reasonable range: 30-300 kg)
        if weight_kg < 30:
            issues.append(f"Weight {weight_kg}kg seems too low (min: 30kg)")
        elif weight_kg > 300:
            issues.append(f"Weight {weight_kg}kg seems too high (max: 300kg)")
        
        # Validate gender
        if gender.lower() not in ['male', 'female']:
            issues.append(f"Gender must be 'male' or 'female', got: {gender}")
        
        # Validate BMI is reasonable (10-60)
        bmi = self._calculate_bmi(height_cm, weight_kg)
        if bmi < 10:
            issues.append(f"BMI {bmi:.1f} seems unrealistically low")
        elif bmi > 60:
            issues.append(f"BMI {bmi:.1f} seems unrealistically high")
        
        return len(issues) == 0, issues
