"""
Regressors Module
ML models for body measurement prediction.

Supports:
- full body model: 9 targets
- shirt model: custom targets
- pants model: custom targets
"""

from typing import Dict, List, Optional, Tuple
import numpy as np
import os
import joblib

from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.multioutput import MultiOutputRegressor


class BodyMeasurementRegressor:
    """
    Multi-output regressor for predicting body measurements.
    """

    DEFAULT_TARGET_NAMES = [
        "chest",
        "waist",
        "hip",
        "shoulder_width_cm",
        "back_length",
        "inseam",
        "thigh_circumference",
        "neck_circumference",
        "arm_circumference",
    ]

    def __init__(
        self,
        model_type: str = "random_forest",
        target_names: Optional[List[str]] = None,
    ):
        self.model_type = model_type
        self.target_names = target_names or self.DEFAULT_TARGET_NAMES.copy()

        # Backward compatibility with old code
        self.TARGET_NAMES = self.target_names

        self.model = self._create_model(model_type)
        self.is_fitted = False
        self.feature_names: Optional[List[str]] = None

    def _create_model(self, model_type: str) -> MultiOutputRegressor:
        if model_type == "random_forest":
            base_model = RandomForestRegressor(
                n_estimators=200,
                max_depth=14,
                min_samples_split=4,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1,
            )

        elif model_type == "gradient_boosting":
            base_model = GradientBoostingRegressor(
                n_estimators=200,
                max_depth=5,
                learning_rate=0.05,
                random_state=42,
            )

        elif model_type == "ridge":
            base_model = Ridge(alpha=1.0)

        else:
            raise ValueError(f"Unknown model type: {model_type}")

        return MultiOutputRegressor(base_model)

    def fit(
        self,
        X: np.ndarray,
        y: np.ndarray,
        feature_names: Optional[List[str]] = None,
        target_names: Optional[List[str]] = None,
    ) -> "BodyMeasurementRegressor":

        if target_names is not None:
            self.target_names = target_names
            self.TARGET_NAMES = target_names

        if y.ndim != 2:
            raise ValueError("Target y must be 2D array")

        if y.shape[1] != len(self.target_names):
            raise ValueError(
                f"Expected {len(self.target_names)} targets "
                f"({self.target_names}), got {y.shape[1]}"
            )

        self.model.fit(X, y)
        self.is_fitted = True
        self.feature_names = feature_names

        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        if not self.is_fitted:
            raise ValueError("Model not fitted. Call fit() first.")

        if len(X.shape) == 1:
            X = X.reshape(1, -1)

        return self.model.predict(X)

    def predict_dict(self, X: np.ndarray) -> Dict[str, float]:
        predictions = self.predict(X)

        if len(predictions.shape) > 1:
            predictions = predictions[0]

        return {
            name: float(pred)
            for name, pred in zip(self.target_names, predictions)
        }

    def predict_with_confidence(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        if not self.is_fitted:
            raise ValueError("Model not fitted. Call fit() first.")

        if self.model_type != "random_forest":
            predictions = self.predict(X)
            return predictions, np.zeros_like(predictions)

        if len(X.shape) == 1:
            X = X.reshape(1, -1)

        all_target_predictions = []

        for target_estimator in self.model.estimators_:
            tree_predictions = np.array([
                tree.predict(X)
                for tree in target_estimator.estimators_
            ])

            all_target_predictions.append(tree_predictions)

        all_target_predictions = np.array(all_target_predictions)

        predictions = np.mean(all_target_predictions, axis=1).T
        stds = np.std(all_target_predictions, axis=1).T

        return predictions, stds

    def score(self, X: np.ndarray, y: np.ndarray) -> float:
        if not self.is_fitted:
            raise ValueError("Model not fitted. Call fit() first.")

        return float(self.model.score(X, y))

    def get_feature_importance(self) -> Dict[str, float]:
        if not self.is_fitted:
            return {}

        if self.model_type not in ["random_forest", "gradient_boosting"]:
            return {}

        if not self.feature_names:
            return {}

        importances = []

        for estimator in self.model.estimators_:
            if hasattr(estimator, "feature_importances_"):
                importances.append(estimator.feature_importances_)

        if not importances:
            return {}

        avg_importance = np.mean(importances, axis=0)

        return {
            name: float(importance)
            for name, importance in zip(self.feature_names, avg_importance)
        }

    def save(self, filepath: str) -> None:
        if not self.is_fitted:
            raise ValueError("Cannot save unfitted model")

        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        data = {
            "model_type": self.model_type,
            "model": self.model,
            "feature_names": self.feature_names,
            "target_names": self.target_names,
            "is_fitted": self.is_fitted,
        }

        joblib.dump(data, filepath)

    def load(self, filepath: str) -> "BodyMeasurementRegressor":
        data = joblib.load(filepath)

        self.model_type = data.get("model_type", "random_forest")
        self.model = data["model"]
        self.feature_names = data.get("feature_names")
        self.target_names = data.get(
            "target_names",
            self.DEFAULT_TARGET_NAMES.copy()
        )

        self.TARGET_NAMES = self.target_names
        self.is_fitted = data.get("is_fitted", True)

        return self

    @classmethod
    def from_file(cls, filepath: str) -> "BodyMeasurementRegressor":
        instance = cls()
        instance.load(filepath)
        return instance