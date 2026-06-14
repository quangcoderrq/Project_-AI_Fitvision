"""
Regressors Module
ML models for body measurement prediction.
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
    Predicts: chest, waist, hip circumferences.
    """
    
    # Target measurement names (expanded from 3 to 9)
    TARGET_NAMES = [
        'chest', 'waist', 'hip',
        'shoulder_width_cm', 'back_length', 'inseam',
        'thigh_circumference', 'neck_circumference', 'arm_circumference'
    ]
    
    def __init__(self, model_type: str = 'random_forest'):
        """
        Initialize regressor.
        
        Args:
            model_type: Type of model ('random_forest', 'gradient_boosting', 'ridge')
        """
        self.model_type = model_type
        self.model = self._create_model(model_type)
        self.is_fitted = False
        self.feature_names: Optional[List[str]] = None
    
    def _create_model(self, model_type: str) -> MultiOutputRegressor:
        """Create the underlying model based on type."""
        if model_type == 'random_forest':
            base_model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1
            )
        elif model_type == 'gradient_boosting':
            base_model = GradientBoostingRegressor(
                n_estimators=100,
                max_depth=5,
                learning_rate=0.1,
                random_state=42
            )
        elif model_type == 'ridge':
            base_model = Ridge(alpha=1.0)
        else:
            raise ValueError(f"Unknown model type: {model_type}")
        
        return MultiOutputRegressor(base_model)
    
    def fit(self, X: np.ndarray, y: np.ndarray,
            feature_names: Optional[List[str]] = None) -> 'BodyMeasurementRegressor':
        """
        Train the model.
        
        Args:
            X: Feature matrix (n_samples, n_features)
            y: Target matrix (n_samples, 3) for chest, waist, hip
            feature_names: Optional list of feature names
            
        Returns:
            self
        """
        if y.shape[1] != len(self.TARGET_NAMES):
            raise ValueError(
                f"Expected {len(self.TARGET_NAMES)} targets, got {y.shape[1]}"
            )
        
        self.model.fit(X, y)
        self.is_fitted = True
        self.feature_names = feature_names
        
        return self
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Predict body measurements.
        
        Args:
            X: Feature matrix
            
        Returns:
            Predictions (n_samples, 3)
        """
        if not self.is_fitted:
            raise ValueError("Model not fitted. Call fit() first.")
        
        # Handle 1D input
        if len(X.shape) == 1:
            X = X.reshape(1, -1)
        
        return self.model.predict(X)
    
    def predict_dict(self, X: np.ndarray) -> Dict[str, float]:
        """
        Predict and return as dictionary.
        
        Args:
            X: Single feature vector
            
        Returns:
            Dictionary of measurements
        """
        predictions = self.predict(X)
        
        if len(predictions.shape) > 1:
            predictions = predictions[0]
        
        return {
            name: float(pred) 
            for name, pred in zip(self.TARGET_NAMES, predictions)
        }
    
    def predict_with_confidence(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Predict with confidence intervals (for RandomForest).
        
        Args:
            X: Feature matrix
            
        Returns:
            Tuple of (predictions, std_deviations)
        """
        if not self.is_fitted:
            raise ValueError("Model not fitted. Call fit() first.")
        
        if self.model_type != 'random_forest':
            predictions = self.predict(X)
            # Return zero std for non-RF models
            return predictions, np.zeros_like(predictions)
        
        # Handle 1D input
        if len(X.shape) == 1:
            X = X.reshape(1, -1)
        
        # Get predictions from all trees
        predictions_per_tree = np.array([
            [est.predict(X) for est in estimator.estimators_]
            for estimator in self.model.estimators_
        ])
        
        # Shape: (n_targets, n_trees, n_samples) -> (n_samples, n_targets)
        predictions = np.mean(predictions_per_tree, axis=1).T
        stds = np.std(predictions_per_tree, axis=1).T
        
        return predictions, stds
    
    def score(self, X: np.ndarray, y: np.ndarray) -> float:
        """
        Calculate R² score.
        
        Args:
            X: Feature matrix
            y: True values
            
        Returns:
            R² score
        """
        if not self.is_fitted:
            raise ValueError("Model not fitted. Call fit() first.")
        
        return self.model.score(X, y)
    
    def get_feature_importance(self) -> Optional[Dict[str, float]]:
        """
        Get feature importances (for tree-based models).
        
        Returns:
            Dictionary of feature name to importance
        """
        if not self.is_fitted:
            return None
        
        if self.model_type not in ['random_forest', 'gradient_boosting']:
            return None
        
        # Average importance across all target estimators
        importances = np.mean([
            est.feature_importances_ 
            for est in self.model.estimators_
        ], axis=0)
        
        if self.feature_names:
            return dict(zip(self.feature_names, importances))
        else:
            return {f'feature_{i}': imp for i, imp in enumerate(importances)}
    
    def save(self, filepath: str) -> None:
        """Save model to file."""
        if not self.is_fitted:
            raise ValueError("Cannot save unfitted model")
        
        data = {
            'model': self.model,
            'model_type': self.model_type,
            'feature_names': self.feature_names,
            'target_names': self.TARGET_NAMES
        }
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        joblib.dump(data, filepath)
    
    def load(self, filepath: str) -> 'BodyMeasurementRegressor':
        """Load model from file."""
        data = joblib.load(filepath)
        
        self.model = data['model']
        self.model_type = data['model_type']
        self.feature_names = data.get('feature_names')
        self.is_fitted = True
        
        return self
    
    @classmethod
    def from_file(cls, filepath: str) -> 'BodyMeasurementRegressor':
        """Load model from file (class method)."""
        instance = cls()
        return instance.load(filepath)
