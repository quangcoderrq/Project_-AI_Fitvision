"""
Prediction Module
Handles body measurement prediction pipeline.

Supports:
- full model
- shirt model
- pants model
"""

from typing import Dict, Optional
import os
from unittest import result
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

    def __init__(
        self,
        model_path: Optional[str] = None,
        scaler_path: Optional[str] = None,
        shirt_model_path: Optional[str] = None,
        shirt_scaler_path: Optional[str] = None,
        pants_model_path: Optional[str] = None,
        pants_scaler_path: Optional[str] = None,
    ):
        self.pose_detector = None
        self.feature_extractor = FeatureExtractor()
        self.keypoints_utils = KeypointsUtils()

        self.model: Optional[BodyMeasurementRegressor] = None
        self.normalizer: Optional[FeatureNormalizer] = None

        self.shirt_model: Optional[BodyMeasurementRegressor] = None
        self.shirt_normalizer: Optional[FeatureNormalizer] = None

        self.pants_model: Optional[BodyMeasurementRegressor] = None
        self.pants_normalizer: Optional[FeatureNormalizer] = None

        if model_path and os.path.exists(model_path):
            self.model = BodyMeasurementRegressor.from_file(model_path)

        if scaler_path and os.path.exists(scaler_path):
            self.normalizer = FeatureNormalizer()
            self.normalizer.load(scaler_path)

        if shirt_model_path and os.path.exists(shirt_model_path):
            self.shirt_model = BodyMeasurementRegressor.from_file(shirt_model_path)

        if shirt_scaler_path and os.path.exists(shirt_scaler_path):
            self.shirt_normalizer = FeatureNormalizer()
            self.shirt_normalizer.load(shirt_scaler_path)

        if pants_model_path and os.path.exists(pants_model_path):
            self.pants_model = BodyMeasurementRegressor.from_file(pants_model_path)

        if pants_scaler_path and os.path.exists(pants_scaler_path):
            self.pants_normalizer = FeatureNormalizer()
            self.pants_normalizer.load(pants_scaler_path)

    def _init_pose_detector(self):
        if self.pose_detector is None:
            self.pose_detector = PoseDetector()

    def is_ready(self) -> bool:
        return self.model is not None and self.normalizer is not None

    def is_shirt_ready(self) -> bool:
        return self.shirt_model is not None and self.shirt_normalizer is not None

    def is_pants_ready(self) -> bool:
        return self.pants_model is not None and self.pants_normalizer is not None

    def close(self):
        if self.pose_detector and hasattr(self.pose_detector, "close"):
            self.pose_detector.close()

    def _select_model(self, image_type: str):
        """
        Select model by image type.

        image_type:
        - full  -> full model
        - upper -> shirt model if available, else full
        - lower -> pants model if available, else full
        """

        if image_type == "upper" and self.is_shirt_ready():
            return self.shirt_model, self.shirt_normalizer, "shirt"

        if image_type == "lower" and self.is_pants_ready():
            return self.pants_model, self.pants_normalizer, "pants"

        return self.model, self.normalizer, "full"

    def predict_from_image(
        self,
        image: np.ndarray,
        height_cm: float,
        weight_kg: float,
        gender: str = "male",
        image_type: str = "full",
        ignore_baggy_warning: bool = False,
    ) -> Dict:

        self._init_pose_detector()

        detection = self.pose_detector.detect(image)

        if detection is None:
            return {
                "success": False,
                "error": "No pose detected in image",
                "measurements": None,
                "confidence": 0.0,
                "pose_quality": 0.0,
            }

        is_valid, issues = self.pose_detector.validate_pose(
            detection,
            image_type=image_type,
        )

        if not is_valid:
            return {
                "success": False,
                "error": f'Invalid pose: {", ".join(issues)}',
                "measurements": None,
                "confidence": 0.0,
                "pose_quality": 0.0,
            }

        pose_quality = self.pose_detector.calculate_pose_quality(
            detection,
            image_type=image_type
        )

        if pose_quality < 0.62:
            return {
                "success": False,
                "error": (
                    "Ảnh chưa đủ tốt để đo chính xác. "
                    "Vui lòng chụp rõ hơn, đứng thẳng, đủ sáng, "
                    "không nghiêng người và đảm bảo cơ thể chiếm phần lớn khung hình."
                ),
                "measurements": None,
                "confidence": pose_quality,
                "pose_quality": pose_quality,
            }

        keypoints = self.pose_detector.get_body_keypoints(detection)

        result = self.predict_from_keypoints(
            keypoints=keypoints,
            height_cm=height_cm,
            weight_kg=weight_kg,
            gender=gender,
            confidences=detection.get("confidences"),
            image_type=image_type,
            ignore_baggy_warning=ignore_baggy_warning,
        )

        if isinstance(result, dict):
            result["pose_quality"] = pose_quality

        return result

    def predict_from_keypoints(
        self,
        keypoints: Dict,
        height_cm: float,
        weight_kg: float,
        gender: str = "male",
        confidences: Optional[Dict] = None,
        image_type: str = "full",
        ignore_baggy_warning: bool = False,
    ) -> Dict:

        selected_model, selected_normalizer, model_used = self._select_model(image_type)

        if selected_model is None or selected_normalizer is None:
            return {
                "success": False,
                "error": f"Model not loaded for image_type={image_type}",
                "measurements": None,
                "confidence": 0.0,
            }

        is_valid, issues = self.feature_extractor.validate_inputs(
            height_cm,
            weight_kg,
            gender,
        )

        if not is_valid:
            return {
                "success": False,
                "error": f'Invalid inputs: {", ".join(issues)}',
                "measurements": None,
                "confidence": 0.0,
            }

        try:
            is_baggy = self.feature_extractor.detect_baggy_clothes(
                keypoints,
                height_cm,
                weight_kg,
                gender,
                image_type,
            )

            if is_baggy and not ignore_baggy_warning:
                return {
                    "success": True,
                    "require_user_confirmation": True,
                    "baggy_clothes_detected": True,
                    "warning_message": "Hệ thống phát hiện bạn có thể đang mặc quần áo rộng. Điều này có thể làm sai lệch số đo thực tế. Bạn có muốn hệ thống tự động điều chỉnh và tiếp tục không?",
                    "measurements": None,
                    "confidence": 0.0,
                    "model_used": model_used,
                }

            features, real_measurements = self.feature_extractor.extract_with_real_measurements(
                keypoints,
                height_cm,
                weight_kg,
                gender,
                image_type,
            )

            features_norm = selected_normalizer.transform(features)

            predictions = selected_model.predict_dict(features_norm)

            confidence = self._calculate_confidence(confidences, features)

            if is_baggy and ignore_baggy_warning:
                for key in ["chest", "waist", "hip"]:
                    if key in predictions:
                        predictions[key] *= 0.95

                if "shoulder_width_cm" in predictions:
                    predictions["shoulder_width_cm"] *= 0.97

            measurements = self._build_complete_measurements(
                predictions=predictions,
                real_measurements=real_measurements,
                image_type=image_type,
            )

            return {
                "success": True,
                "error": None,
                "require_user_confirmation": False,
                "baggy_clothes_detected": is_baggy,
                "warning_message": None,
                "measurements": measurements,
                "confidence": confidence,
                "bmi": self.feature_extractor._calculate_bmi(height_cm, weight_kg),
                "model_used": model_used,
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Prediction failed: {str(e)}",
                "measurements": None,
                "confidence": 0.0,
                "model_used": model_used,
            }

    def _build_complete_measurements(
        self,
        predictions: Dict[str, float],
        real_measurements: Dict,
        image_type: str,
    ) -> Dict[str, float]:

        defaults = {
            "chest": 0.0,
            "waist": 0.0,
            "hip": 0.0,
            "shoulder_width_cm": 0.0,
            "back_length": 0.0,
            "inseam": 0.0,
            "thigh_circumference": 0.0,
            "neck_circumference": 0.0,
            "arm_circumference": 0.0,
        }

        for key in defaults.keys():
            if key in predictions:
                defaults[key] = round(float(predictions[key]), 1)

        # Fill useful geometric fallback if model did not predict that target
        fallback_map = {
            "shoulder_width_cm": "shoulder_width_cm",
            "back_length": "back_length_cm",
            "inseam": "inseam_cm",
        }

        for target_key, real_key in fallback_map.items():
            if defaults[target_key] == 0.0 and real_key in real_measurements:
                defaults[target_key] = round(float(real_measurements[real_key]), 1)

        return defaults

    def _calculate_confidence(
        self,
        confidences: Optional[Dict],
        features: Optional[np.ndarray],
    ) -> float:

        base_confidence = 0.8

        if confidences:
            key_values = list(confidences.values())
            if key_values:
                avg_pose_conf = sum(key_values) / len(key_values)
                base_confidence = 0.5 + avg_pose_conf * 0.4

        if features is not None:
            try:
                if np.any(np.isnan(features)) or np.any(np.isinf(features)):
                    base_confidence *= 0.7
            except Exception:
                pass

        return round(float(min(max(base_confidence, 0.0), 0.98)), 2)