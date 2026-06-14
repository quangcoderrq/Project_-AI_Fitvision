"""
Test Pose Detection Module
"""

import sys
import os
import numpy as np
import pytest

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.pose.keypoints_utils import KeypointsUtils


class TestKeypointsUtils:
    """Tests for KeypointsUtils class."""
    
    def test_distance(self):
        """Test distance calculation."""
        point1 = [0, 0]
        point2 = [3, 4]
        
        result = KeypointsUtils.distance(point1, point2)
        
        assert result == 5.0
    
    def test_distance_same_point(self):
        """Test distance when points are the same."""
        point = [10, 20]
        
        result = KeypointsUtils.distance(point, point)
        
        assert result == 0.0
    
    def test_midpoint(self):
        """Test midpoint calculation."""
        point1 = [0, 0]
        point2 = [10, 10]
        
        result = KeypointsUtils.midpoint(point1, point2)
        
        assert result == [5.0, 5.0]
    
    def test_angle(self):
        """Test angle calculation."""
        # Right angle
        point1 = [0, 0]
        point2 = [0, 5]
        point3 = [5, 5]
        
        result = KeypointsUtils.angle(point1, point2, point3)
        
        assert abs(result - 90.0) < 0.01
    
    def test_calculate_all_distances(self):
        """Test all distances calculation."""
        keypoints = {
            'left_shoulder': [100, 100],
            'right_shoulder': [200, 100],
            'left_hip': [120, 250],
            'right_hip': [180, 250]
        }
        
        result = KeypointsUtils.calculate_all_distances(keypoints)
        
        assert 'shoulder_width' in result
        assert 'hip_width' in result
        assert result['shoulder_width'] == 100.0
        assert result['hip_width'] == 60.0
        
    def test_calculate_inseam_distances(self):
        """Test inseam distance calculation."""
        keypoints = {
            'left_hip': [100, 200],
            'left_ankle': [100, 400],
            'right_hip': [150, 200],
            'right_ankle': [150, 400]
        }
        
        result = KeypointsUtils.calculate_all_distances(keypoints)
        assert 'left_inseam' in result
        assert result['left_inseam'] == 200.0
        
    def test_estimate_body_widths(self):
        """Test body width estimations."""
        keypoints = {
            'left_shoulder': [100, 100],
            'right_shoulder': [140, 100],
            'left_hip': [110, 200],
            'right_hip': [130, 200],
            'left_ankle': [110, 300],
            'right_ankle': [130, 300],
            'nose': [120, 70]
        }
        # height roughly 300-70 = 230px
        widths = KeypointsUtils.estimate_body_widths(keypoints, 22.0, 'male')
        assert 'neck_circ_ratio' in widths
        assert 'belly_width_ratio' in widths
    
    def test_normalize_keypoints(self):
        """Test keypoint normalization."""
        keypoints = {
            'left_shoulder': [100, 200],
            'right_shoulder': [300, 200]
        }
        image_size = (400, 400)
        
        result = KeypointsUtils.normalize_keypoints(keypoints, image_size)
        
        assert result['left_shoulder'] == [0.25, 0.5]
        assert result['right_shoulder'] == [0.75, 0.5]
    
    def test_check_pose_symmetry_symmetric(self):
        """Test symmetry check with symmetric pose."""
        keypoints = {
            'left_shoulder': [100, 100],
            'right_shoulder': [200, 100],
            'left_hip': [110, 200],
            'right_hip': [190, 200]
        }
        
        is_symmetric, score = KeypointsUtils.check_pose_symmetry(keypoints)
        
        assert is_symmetric is True
        assert score < 0.1
    
    def test_check_pose_symmetry_asymmetric(self):
        """Test symmetry check with asymmetric pose."""
        keypoints = {
            'left_shoulder': [100, 100],
            'right_shoulder': [200, 150],  # Much lower
            'left_hip': [110, 200],
            'right_hip': [190, 250]  # Much lower
        }
        
        is_symmetric, score = KeypointsUtils.check_pose_symmetry(keypoints)
        
        assert is_symmetric is False
        assert score > 0.1


class TestPoseDetector:
    """Tests for PoseDetector class (requires MediaPipe)."""
    
    def test_import(self):
        """Test that pose detector can be imported."""
        try:
            from src.pose.pose_detector import PoseDetector, MEDIAPIPE_AVAILABLE
            assert True
        except ImportError:
            pytest.skip("MediaPipe not installed")
    
    def test_landmark_names(self):
        """Test landmark names are defined."""
        from src.pose.pose_detector import PoseDetector
        
        assert len(PoseDetector.LANDMARK_NAMES) == 33
        assert 'nose' in PoseDetector.LANDMARK_NAMES.values()
        assert 'left_shoulder' in PoseDetector.LANDMARK_NAMES.values()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
