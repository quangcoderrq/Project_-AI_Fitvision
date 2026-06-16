"""
Pose Detector Module
Uses MediaPipe to detect body pose keypoints.
"""

from typing import Dict, List, Optional, Tuple
import numpy as np
import cv2

import os
import sys

# Ensure local lib is in path if it exists
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
local_lib = os.path.join(project_root, 'lib')
if os.path.exists(local_lib) and local_lib not in sys.path:
    sys.path.insert(0, local_lib)

try:
    import mediapipe as mp
    from mediapipe.python.solutions import pose as mp_pose
    from mediapipe.python.solutions import drawing_utils as mp_drawing
    MEDIAPIPE_AVAILABLE = True
except Exception as e:
    MEDIAPIPE_AVAILABLE = False
    print(f"Warning: MediaPipe import failed: {e}")




class PoseDetector:
    """Detects human body pose using MediaPipe."""
    
    # MediaPipe pose landmark indices
    LANDMARK_NAMES = {
        0: 'nose',
        1: 'left_eye_inner',
        2: 'left_eye',
        3: 'left_eye_outer',
        4: 'right_eye_inner',
        5: 'right_eye',
        6: 'right_eye_outer',
        7: 'left_ear',
        8: 'right_ear',
        9: 'mouth_left',
        10: 'mouth_right',
        11: 'left_shoulder',
        12: 'right_shoulder',
        13: 'left_elbow',
        14: 'right_elbow',
        15: 'left_breast_center', # Not standard MP, but for reference
        16: 'right_breast_center',
        15: 'left_wrist',
        16: 'right_wrist',
        17: 'left_pinky',
        18: 'right_pinky',
        19: 'left_index',
        20: 'right_index',
        21: 'left_thumb',
        22: 'right_thumb',
        23: 'left_hip',
        24: 'right_hip',
        25: 'left_knee',
        26: 'right_knee',
        27: 'left_ankle',
        28: 'right_ankle',
        29: 'left_heel',
        30: 'right_heel',
        31: 'left_foot_index',
        32: 'right_foot_index'
    }
    
    # Key body points for measurement
    BODY_KEYPOINTS = [
        'nose',
        'left_shoulder', 'right_shoulder',
        'left_hip', 'right_hip',
        'left_knee', 'right_knee',
        'left_ankle', 'right_ankle',
        'left_elbow', 'right_elbow',
        'left_wrist', 'right_wrist'
    ]
    
    def __init__(self, 
                 static_image_mode: bool = True,
                 min_detection_confidence: float = 0.5,
                 min_tracking_confidence: float = 0.5):
        """
        Initialize pose detector.
        """
        if not MEDIAPIPE_AVAILABLE:
            raise ImportError("MediaPipe is required for pose detection")
        
        self.static_image_mode = static_image_mode
        self.min_detection_confidence = min_detection_confidence
        self.min_tracing_confidence = min_tracking_confidence
        
        # Use MediaPipe solutions
        self.mp_pose = mp_pose
        self.mp_drawing = mp_drawing
        
        self.pose = self.mp_pose.Pose(
            static_image_mode=static_image_mode,
            model_complexity=1,
            enable_segmentation=False,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )


    
    def detect(self, image: np.ndarray) -> Optional[Dict]:
        """
        Detect pose in an image.
        
        Args:
            image: Input image (BGR format from OpenCV)
            
        Returns:
            Dictionary with keypoints or None if no pose detected
        """
        # Convert BGR to RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Process image
        results = self.pose.process(image_rgb)
        
        if not results.pose_landmarks:
            return None
        
        # Get image dimensions
        height, width = image.shape[:2]
        
        # Extract keypoints
        keypoints = {}
        confidences = {}
        
        for idx, landmark in enumerate(results.pose_landmarks.landmark):
            name = self.LANDMARK_NAMES.get(idx, f'point_{idx}')
            
            # Convert normalized coordinates to pixel coordinates
            x = int(landmark.x * width)
            y = int(landmark.y * height)
            
            keypoints[name] = [x, y]
            confidences[name] = landmark.visibility
        
        return {
            'keypoints': keypoints,
            'confidences': confidences,
            'image_size': (width, height),
            'raw_landmarks': results.pose_landmarks
        }
    
    def detect_from_file(self, image_path: str) -> Optional[Dict]:
        """
        Detect pose from image file.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Dictionary with keypoints or None
        """
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Failed to load image: {image_path}")
        return self.detect(image)
    
    def get_body_keypoints(self, detection_result: Dict) -> Dict[str, List[int]]:
        """
        Extract only key body measurement points.
        
        Args:
            detection_result: Result from detect()
            
        Returns:
            Dictionary with body keypoints
        """
        if not detection_result:
            return {}
        
        keypoints = detection_result['keypoints']
        body_points = {}
        
        for name in self.BODY_KEYPOINTS:
            if name in keypoints:
                body_points[name] = keypoints[name]
        
        return body_points
    
    def validate_pose(self, detection_result: Dict, 
                      min_confidence: float = 0.5,
                      image_type: str = 'full') -> Tuple[bool, List[str]]:
        """
        Validate if pose is suitable for measurement.
        
        Args:
            detection_result: Result from detect()
            min_confidence: Minimum required confidence
            image_type: Type of image ('full', 'upper', 'lower')
            
        Returns:
            Tuple of (is_valid, list of issues)
        """
        issues = []
        
        if not detection_result:
            return False, ["No pose detected"]
        
        keypoints = detection_result['keypoints']
        confidences = detection_result['confidences']
        
        # Check required points exist based on image type
        if image_type == 'upper':
            required_points = [
                'nose',
                'left_shoulder', 'right_shoulder',
                'left_hip', 'right_hip'
            ]
        elif image_type == 'lower':
            required_points = [
                'left_hip', 'right_hip',
                'left_ankle', 'right_ankle'
            ]
        else:
            required_points = [
                'nose',
                'left_shoulder', 'right_shoulder',
                'left_hip', 'right_hip',
                'left_ankle', 'right_ankle'
            ]
        
        for point in required_points:
            if point not in keypoints:
                issues.append(f"Missing keypoint: {point}")
            elif confidences.get(point, 0) < min_confidence:
                issues.append(
                    f"Low confidence for {point}: "
                    f"{confidences.get(point, 0):.2f}"
                )
        
        # Check if person is roughly upright
        if all(p in keypoints for p in ['left_shoulder', 'left_hip']):
            shoulder_y = keypoints['left_shoulder'][1]
            hip_y = keypoints['left_hip'][1]
            if shoulder_y > hip_y:
                issues.append("Person appears to be upside down")
        
        # Check if full body is visible (only for full image)
        if image_type == 'full' and 'left_ankle' in keypoints and 'nose' in keypoints:
            ankle_y = keypoints['left_ankle'][1]
            nose_y = keypoints['nose'][1]
            body_height = abs(ankle_y - nose_y)
            image_height = detection_result['image_size'][1]
            
            if body_height < image_height * 0.5:
                issues.append("Body appears too small in frame")
        
        return len(issues) == 0, issues
    
    
    def calculate_pose_quality(
        self,
        detection_result: Dict,
        image_type: str = "full"
    ) -> float:
        if not detection_result:
            return 0.0

        keypoints = detection_result.get("keypoints", {})
        confidences = detection_result.get("confidences", {})
        image_size = detection_result.get("image_size", (0, 0))

        if not keypoints or not confidences:
            return 0.0

        if image_type == "upper":
            required_points = [
                "nose",
                "left_shoulder", "right_shoulder",
                "left_hip", "right_hip",
                "left_elbow", "right_elbow"
            ]
        elif image_type == "lower":
            required_points = [
                "left_hip", "right_hip",
                "left_knee", "right_knee",
                "left_ankle", "right_ankle"
            ]
        else:
            required_points = [
                "nose",
                "left_shoulder", "right_shoulder",
                "left_hip", "right_hip",
                "left_knee", "right_knee",
                "left_ankle", "right_ankle"
            ]

        visible_scores = [
            confidences.get(point, 0.0)
            for point in required_points
            if point in keypoints
        ]

        if not visible_scores:
            return 0.0

        visibility_score = sum(visible_scores) / len(required_points)
        symmetry_score = self._calculate_symmetry_score(keypoints, image_type)
        size_score = self._calculate_body_size_score(keypoints, image_size, image_type)
        vertical_score = self._calculate_vertical_alignment_score(keypoints)

        quality = (
            visibility_score * 0.45 +
            symmetry_score * 0.25 +
            size_score * 0.20 +
            vertical_score * 0.10
        )

        return round(float(max(0.0, min(quality, 1.0))), 2)

    def _calculate_symmetry_score(
        self,
        keypoints: Dict[str, List[int]],
        image_type: str = "full"
    ) -> float:
        pairs = []

        if image_type in ["full", "upper"]:
            pairs.extend([
                ("left_shoulder", "right_shoulder"),
                ("left_hip", "right_hip"),
            ])

        if image_type in ["full", "lower"]:
            pairs.extend([
                ("left_knee", "right_knee"),
                ("left_ankle", "right_ankle"),
            ])

        scores = []

        for left, right in pairs:
            if left in keypoints and right in keypoints:
                y1 = keypoints[left][1]
                y2 = keypoints[right][1]

                avg_y = max((abs(y1) + abs(y2)) / 2, 1)
                diff_ratio = abs(y1 - y2) / avg_y

                score = max(0.0, 1.0 - diff_ratio * 8)
                scores.append(score)

        if not scores:
            return 0.5

        return float(sum(scores) / len(scores))

    def _calculate_body_size_score(
        self,
        keypoints: Dict[str, List[int]],
        image_size: Tuple[int, int],
        image_type: str = "full"
    ) -> float:
        width, height = image_size

        if width <= 0 or height <= 0:
            return 0.0

        xs = [p[0] for p in keypoints.values()]
        ys = [p[1] for p in keypoints.values()]

        if not xs or not ys:
            return 0.0

        body_w = max(xs) - min(xs)
        body_h = max(ys) - min(ys)

        h_ratio = body_h / height
        w_ratio = body_w / width

        if image_type == "full":
            h_score = min(h_ratio / 0.65, 1.0)
            w_score = min(w_ratio / 0.25, 1.0)
        elif image_type == "upper":
            h_score = min(h_ratio / 0.45, 1.0)
            w_score = min(w_ratio / 0.30, 1.0)
        else:
            h_score = min(h_ratio / 0.45, 1.0)
            w_score = min(w_ratio / 0.22, 1.0)

        return float(h_score * 0.7 + w_score * 0.3)

    def _calculate_vertical_alignment_score(
        self,
        keypoints: Dict[str, List[int]]
    ) -> float:
        if not all(p in keypoints for p in [
            "left_shoulder", "right_shoulder", "left_hip", "right_hip"
        ]):
            return 0.7

        shoulder_mid = [
            (keypoints["left_shoulder"][0] + keypoints["right_shoulder"][0]) / 2,
            (keypoints["left_shoulder"][1] + keypoints["right_shoulder"][1]) / 2,
        ]

        hip_mid = [
            (keypoints["left_hip"][0] + keypoints["right_hip"][0]) / 2,
            (keypoints["left_hip"][1] + keypoints["right_hip"][1]) / 2,
        ]

        dx = abs(shoulder_mid[0] - hip_mid[0])
        dy = max(abs(hip_mid[1] - shoulder_mid[1]), 1)

        tilt_ratio = dx / dy

        return float(max(0.0, 1.0 - tilt_ratio * 2.5))

    def draw_pose(self, image: np.ndarray, 
                  detection_result: Dict,
                  draw_landmarks: bool = True,
                  draw_connections: bool = True) -> np.ndarray:
        """
        Draw pose on image.
        
        Args:
            image: Input image
            detection_result: Result from detect()
            draw_landmarks: Whether to draw landmark points
            draw_connections: Whether to draw connections
            
        Returns:
            Image with pose drawn
        """
        if not detection_result or 'raw_landmarks' not in detection_result:
            return image
        
        output_image = image.copy()
        
        self.mp_drawing.draw_landmarks(
            output_image,
            detection_result['raw_landmarks'],
            self.mp_pose.POSE_CONNECTIONS if draw_connections else None,
            self.mp_drawing.DrawingSpec(
                color=(0, 255, 0), thickness=2, circle_radius=3
            ) if draw_landmarks else None,
            self.mp_drawing.DrawingSpec(
                color=(255, 0, 0), thickness=2
            ) if draw_connections else None
        )
        
        return output_image
    
    def close(self):
        """Release resources."""
        if hasattr(self, 'pose'):
            self.pose.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
