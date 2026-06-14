"""
Keypoints Utilities Module
Helper functions for working with pose keypoints.
"""

from typing import Dict, List, Tuple, Optional
import numpy as np
import math


class KeypointsUtils:
    """Utility class for keypoint operations."""
    
    # Pairs for distance calculations
    MEASUREMENT_PAIRS = {
        'shoulder_width': ('left_shoulder', 'right_shoulder'),
        'hip_width': ('left_hip', 'right_hip'),
        'left_arm': ('left_shoulder', 'left_wrist'),
        'right_arm': ('right_shoulder', 'right_wrist'),
        'left_leg': ('left_hip', 'left_ankle'),
        'right_leg': ('right_hip', 'right_ankle'),
        'torso_left': ('left_shoulder', 'left_hip'),
        'torso_right': ('right_shoulder', 'right_hip'),
        'left_upper_arm': ('left_shoulder', 'left_elbow'),
        'right_upper_arm': ('right_shoulder', 'right_elbow'),
        'left_forearm': ('left_elbow', 'left_wrist'),
        'right_forearm': ('right_elbow', 'right_wrist'),
        'left_thigh': ('left_hip', 'left_knee'),
        'right_thigh': ('right_hip', 'right_knee'),
        'left_calf': ('left_knee', 'left_ankle'),
        'right_calf': ('right_knee', 'right_ankle'),
        # New measurement pairs for expanded body analysis
        'left_inseam': ('left_hip', 'left_ankle'),
        'right_inseam': ('right_hip', 'right_ankle'),
    }
    
    @staticmethod
    def distance(point1: List[int], point2: List[int]) -> float:
        """
        Calculate Euclidean distance between two points.
        
        Args:
            point1: [x, y] coordinates
            point2: [x, y] coordinates
            
        Returns:
            Distance in pixels
        """
        return math.sqrt(
            (point2[0] - point1[0]) ** 2 + 
            (point2[1] - point1[1]) ** 2
        )
    
    @staticmethod
    def midpoint(point1: List[int], point2: List[int]) -> List[float]:
        """
        Calculate midpoint between two points.
        
        Args:
            point1: [x, y] coordinates
            point2: [x, y] coordinates
            
        Returns:
            Midpoint [x, y]
        """
        return [
            (point1[0] + point2[0]) / 2,
            (point1[1] + point2[1]) / 2
        ]
    
    @staticmethod
    def angle(point1: List[int], point2: List[int], 
              point3: List[int]) -> float:
        """
        Calculate angle at point2 formed by point1-point2-point3.
        
        Args:
            point1: First point
            point2: Vertex point
            point3: Third point
            
        Returns:
            Angle in degrees
        """
        v1 = np.array([point1[0] - point2[0], point1[1] - point2[1]])
        v2 = np.array([point3[0] - point2[0], point3[1] - point2[1]])
        
        cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
        cos_angle = np.clip(cos_angle, -1.0, 1.0)
        
        return math.degrees(math.acos(cos_angle))
    
    @classmethod
    def calculate_all_distances(cls, 
                                keypoints: Dict[str, List[int]]) -> Dict[str, float]:
        """
        Calculate all measurement distances from keypoints.
        
        Args:
            keypoints: Dictionary of keypoint name to [x, y]
            
        Returns:
            Dictionary of measurement name to distance
        """
        distances = {}
        
        for name, (point1_name, point2_name) in cls.MEASUREMENT_PAIRS.items():
            if point1_name in keypoints and point2_name in keypoints:
                distances[name] = cls.distance(
                    keypoints[point1_name],
                    keypoints[point2_name]
                )
        
        return distances
    
    @classmethod
    def estimate_body_height_pixels(cls, 
                                    keypoints: Dict[str, List[int]]) -> float:
        """
        Estimate body height in pixels from keypoints.
        
        Args:
            keypoints: Dictionary of keypoints
            
        Returns:
            Estimated height in pixels
        """
        # Try to get height from head to ankle
        top_point = None
        bottom_point = None
        
        # Find top point (head)
        for name in ['nose', 'left_eye', 'right_eye']:
            if name in keypoints:
                if top_point is None or keypoints[name][1] < top_point[1]:
                    top_point = keypoints[name]
        
        # Find bottom point (feet)
        for name in ['left_ankle', 'right_ankle', 'left_heel', 'right_heel']:
            if name in keypoints:
                if bottom_point is None or keypoints[name][1] > bottom_point[1]:
                    bottom_point = keypoints[name]
        
        if top_point and bottom_point:
            # Add ~10% for head above nose and feet below ankle
            raw_height = abs(bottom_point[1] - top_point[1])
            return raw_height * 1.1
        
        return 0
    
    @classmethod
    def get_center_point(cls, keypoints: Dict[str, List[int]]) -> List[float]:
        """
        Get center point of the body.
        
        Args:
            keypoints: Dictionary of keypoints
            
        Returns:
            Center point [x, y]
        """
        # Use hip center as body center
        if 'left_hip' in keypoints and 'right_hip' in keypoints:
            return cls.midpoint(keypoints['left_hip'], keypoints['right_hip'])
        
        # Fallback: average all points
        if keypoints:
            x_coords = [p[0] for p in keypoints.values()]
            y_coords = [p[1] for p in keypoints.values()]
            return [sum(x_coords) / len(x_coords), sum(y_coords) / len(y_coords)]
        
        return [0, 0]
    
    @classmethod
    def normalize_keypoints(cls, 
                           keypoints: Dict[str, List[int]],
                           image_size: Tuple[int, int]) -> Dict[str, List[float]]:
        """
        Normalize keypoints to 0-1 range.
        
        Args:
            keypoints: Dictionary of keypoints
            image_size: (width, height) of image
            
        Returns:
            Normalized keypoints
        """
        width, height = image_size
        normalized = {}
        
        for name, point in keypoints.items():
            normalized[name] = [
                point[0] / width,
                point[1] / height
            ]
        
        return normalized
    
    @classmethod
    def check_pose_symmetry(cls, 
                           keypoints: Dict[str, List[int]],
                           threshold: float = 0.1) -> Tuple[bool, float]:
        """
        Check if pose is roughly symmetric (standing straight).
        
        Args:
            keypoints: Dictionary of keypoints
            threshold: Maximum allowed asymmetry ratio
            
        Returns:
            Tuple of (is_symmetric, asymmetry_score)
        """
        pairs = [
            ('left_shoulder', 'right_shoulder'),
            ('left_hip', 'right_hip'),
            ('left_knee', 'right_knee'),
            ('left_ankle', 'right_ankle')
        ]
        
        asymmetry_scores = []
        
        for left_name, right_name in pairs:
            if left_name in keypoints and right_name in keypoints:
                left_y = keypoints[left_name][1]
                right_y = keypoints[right_name][1]
                
                # Calculate relative difference
                avg_y = (left_y + right_y) / 2
                if avg_y > 0:
                    diff = abs(left_y - right_y) / avg_y
                    asymmetry_scores.append(diff)
        
        if asymmetry_scores:
            avg_asymmetry = sum(asymmetry_scores) / len(asymmetry_scores)
            return avg_asymmetry < threshold, avg_asymmetry
        
        return True, 0.0
    
    @classmethod
    def estimate_body_proportions(cls, 
                                  keypoints: Dict[str, List[int]]) -> Dict[str, float]:
        """
        Estimate body proportions from keypoints.
        
        Args:
            keypoints: Dictionary of keypoints
            
        Returns:
            Dictionary of body proportions
        """
        distances = cls.calculate_all_distances(keypoints)
        proportions = {}
        
        # Calculate average values for symmetrical measurements
        if 'left_arm' in distances and 'right_arm' in distances:
            proportions['arm_length'] = (distances['left_arm'] + 
                                         distances['right_arm']) / 2
        
        if 'left_leg' in distances and 'right_leg' in distances:
            proportions['leg_length'] = (distances['left_leg'] + 
                                         distances['right_leg']) / 2
        
        if 'torso_left' in distances and 'torso_right' in distances:
            proportions['torso_length'] = (distances['torso_left'] + 
                                           distances['torso_right']) / 2
        
        if 'shoulder_width' in distances:
            proportions['shoulder_width'] = distances['shoulder_width']
        
        if 'hip_width' in distances:
            proportions['hip_width'] = distances['hip_width']
        
        # === NEW: Extended proportions ===
        
        # Back length (vertical distance from shoulder midpoint to hip midpoint)
        if all(p in keypoints for p in ['left_shoulder', 'right_shoulder', 'left_hip', 'right_hip']):
            shoulder_mid = cls.midpoint(keypoints['left_shoulder'], keypoints['right_shoulder'])
            hip_mid = cls.midpoint(keypoints['left_hip'], keypoints['right_hip'])
            proportions['back_length'] = abs(hip_mid[1] - shoulder_mid[1])
        
        # Neck width (estimated from nose to shoulder midpoint horizontal span)
        if 'nose' in keypoints and 'left_shoulder' in keypoints and 'right_shoulder' in keypoints:
            shoulder_mid = cls.midpoint(keypoints['left_shoulder'], keypoints['right_shoulder'])
            # Neck width ~ 40% of shoulder-to-nose horizontal distance
            neck_span = abs(keypoints['left_shoulder'][0] - keypoints['right_shoulder'][0]) * 0.28
            proportions['neck_width'] = neck_span
        
        # Belly width (estimated at midpoint between chest and hip)
        if all(p in keypoints for p in ['left_shoulder', 'right_shoulder', 'left_hip', 'right_hip']):
            # Belly is roughly between torso and hip
            left_belly_x = (keypoints['left_shoulder'][0] * 0.4 + keypoints['left_hip'][0] * 0.6)
            right_belly_x = (keypoints['right_shoulder'][0] * 0.4 + keypoints['right_hip'][0] * 0.6)
            proportions['belly_width'] = abs(right_belly_x - left_belly_x)
        
        # Inseam (hip midpoint to ankle, vertical-dominant)
        if 'left_inseam' in distances and 'right_inseam' in distances:
            proportions['inseam_length'] = (distances['left_inseam'] + 
                                            distances['right_inseam']) / 2
        elif 'left_leg' in distances and 'right_leg' in distances:
            # Fallback: inseam ≈ 90% of outer leg length
            proportions['inseam_length'] = proportions.get('leg_length', 0) * 0.90
        
        # Upper arm length
        if 'left_upper_arm' in distances and 'right_upper_arm' in distances:
            proportions['upper_arm_length'] = (distances['left_upper_arm'] + 
                                                distances['right_upper_arm']) / 2
        
        # Forearm length
        if 'left_forearm' in distances and 'right_forearm' in distances:
            proportions['forearm_length'] = (distances['left_forearm'] + 
                                             distances['right_forearm']) / 2
        
        # Thigh length
        if 'left_thigh' in distances and 'right_thigh' in distances:
            proportions['thigh_length'] = (distances['left_thigh'] + 
                                           distances['right_thigh']) / 2
        
        # Calf length
        if 'left_calf' in distances and 'right_calf' in distances:
            proportions['calf_length'] = (distances['left_calf'] + 
                                          distances['right_calf']) / 2
        
        # Arm span (full length from wrist to wrist)
        if 'left_wrist' in keypoints and 'right_wrist' in keypoints:
            proportions['arm_span'] = cls.distance(
                keypoints['left_wrist'], keypoints['right_wrist']
            )
        
        # === Ratios ===
        
        # Shoulder to hip ratio
        if 'shoulder_width' in proportions and 'hip_width' in proportions:
            if proportions['hip_width'] > 0:
                proportions['shoulder_hip_ratio'] = (
                    proportions['shoulder_width'] / proportions['hip_width']
                )
        
        # Torso to leg ratio
        if 'torso_length' in proportions and 'leg_length' in proportions:
            if proportions['leg_length'] > 0:
                proportions['torso_leg_ratio'] = (
                    proportions['torso_length'] / proportions['leg_length']
                )
        
        return proportions
    
    @classmethod
    def estimate_body_widths(cls,
                             keypoints: Dict[str, List[int]],
                             bmi: float,
                             gender: str = 'male') -> Dict[str, float]:
        """
        Estimate body circumferences/widths from 2D pose + BMI.
        
        Uses skeletal proportions from keypoints combined with BMI to 
        estimate circumferential measurements that can't be directly 
        measured from a single 2D image.
        
        Args:
            keypoints: Dictionary of keypoints
            bmi: Body Mass Index
            gender: 'male' or 'female'
            
        Returns:
            Dictionary of estimated body widths/circumferences ratios
        """
        proportions = cls.estimate_body_proportions(keypoints)
        body_height = cls.estimate_body_height_pixels(keypoints)
        
        if body_height == 0:
            return {}
        
        widths = {}
        
        # BMI factor: higher BMI → larger circumferences
        # Normalized around BMI 22 as baseline
        bmi_factor = (bmi / 22.0) ** 0.6
        
        # Gender factor for circumference estimation
        is_male = gender.lower() == 'male'
        
        # Neck circumference ratio (relative to body height)
        neck_w = proportions.get('neck_width', 0)
        if neck_w > 0:
            # Neck circumference ≈ neck_width * π * adjustment
            widths['neck_circ_ratio'] = (neck_w / body_height) * bmi_factor
        
        # Arm circumference ratio
        upper_arm = proportions.get('upper_arm_length', 0)
        if upper_arm > 0:
            # Arm thickness relative to arm length and BMI
            arm_thickness_factor = 0.22 if is_male else 0.19
            widths['arm_circ_ratio'] = (upper_arm / body_height) * arm_thickness_factor * bmi_factor
        
        # Thigh circumference ratio
        thigh_len = proportions.get('thigh_length', 0)
        if thigh_len > 0:
            thigh_factor = 0.38 if is_male else 0.40
            widths['thigh_circ_ratio'] = (thigh_len / body_height) * thigh_factor * bmi_factor
        
        # Belly width ratio (indicator of belly size)
        belly_w = proportions.get('belly_width', 0)
        if belly_w > 0:
            widths['belly_width_ratio'] = (belly_w / body_height) * bmi_factor
        
        return widths
