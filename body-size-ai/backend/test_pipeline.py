
import os
import sys
import cv2
import numpy as np

# Add local lib and src to path
project_root = os.getcwd()
sys.path.insert(0, os.path.join(project_root, 'lib'))
sys.path.insert(0, project_root)

from src.pose.pose_detector import PoseDetector
from src.features.extract_features import FeatureExtractor

def test_full_pipeline():
    image_path = "C:/Users/Hi/.gemini/antigravity/brain/c499f703-df1b-4e04-8f80-b04cc1417cbd/full_body_test_pose_1768407632353.png"
    if not os.path.exists(image_path):
        print(f"Error: Image not found at {image_path}")
        return

    print(f"Testing with image: {image_path}")
    
    detector = PoseDetector()
    extractor = FeatureExtractor()
    
    image = cv2.imread(image_path)
    if image is None:
        print("Error: Could not read image")
        return
        
    detection = detector.detect(image)
    if detection is None:
        print("Error: No pose detected")
        return
        
    is_valid, issues = detector.validate_pose(detection)
    print(f"Pose valid: {is_valid}, Issues: {issues}")
    
    keypoints = detector.get_body_keypoints(detection)
    print(f"Keypoints extracted: {list(keypoints.keys())}")
    
    try:
        features = extractor.extract(keypoints, 165, 55, 'female')
        print("Features extracted successfully!")
        print(f"Feature vector shape: {features.shape}")
    except Exception as e:
        print(f"Error during extraction: {e}")

if __name__ == "__main__":
    test_full_pipeline()
