"""
Feature Normalizer Module
Normalizes features for ML model input.
"""

from typing import Optional, List
import numpy as np
import os
import joblib


class FeatureNormalizer:
    """Normalizes features using StandardScaler-like approach."""
    
    def __init__(self):
        self.mean: Optional[np.ndarray] = None
        self.std: Optional[np.ndarray] = None
        self.feature_names: Optional[List[str]] = None
        self.is_fitted = False
    
    def fit(self, features: np.ndarray, 
            feature_names: Optional[List[str]] = None) -> 'FeatureNormalizer':
        """
        Fit normalizer to training data.
        
        Args:
            features: 2D array of features (samples x features)
            feature_names: Optional list of feature names
            
        Returns:
            self
        """
        if len(features.shape) != 2:
            raise ValueError("Features must be 2D array")
        
        self.mean = np.mean(features, axis=0)
        self.std = np.std(features, axis=0)
        
        # Avoid division by zero
        self.std[self.std == 0] = 1.0
        
        self.feature_names = feature_names
        self.is_fitted = True
        
        return self
    
    def transform(self, features: np.ndarray) -> np.ndarray:
        """
        Transform features using fitted parameters.
        
        Args:
            features: Features to transform (1D or 2D)
            
        Returns:
            Normalized features
        """
        if not self.is_fitted:
            raise ValueError("Normalizer not fitted. Call fit() first.")
        
        # Handle 1D input
        if len(features.shape) == 1:
            features = features.reshape(1, -1)
        
        normalized = (features - self.mean) / self.std
        return normalized
    
    def fit_transform(self, features: np.ndarray,
                      feature_names: Optional[List[str]] = None) -> np.ndarray:
        """
        Fit and transform in one step.
        
        Args:
            features: 2D array of features
            feature_names: Optional feature names
            
        Returns:
            Normalized features
        """
        self.fit(features, feature_names)
        return self.transform(features)
    
    def inverse_transform(self, normalized: np.ndarray) -> np.ndarray:
        """
        Convert normalized features back to original scale.
        
        Args:
            normalized: Normalized features
            
        Returns:
            Original scale features
        """
        if not self.is_fitted:
            raise ValueError("Normalizer not fitted. Call fit() first.")
        
        # Handle 1D input
        if len(normalized.shape) == 1:
            normalized = normalized.reshape(1, -1)
        
        return normalized * self.std + self.mean
    
    def save(self, filepath: str) -> None:
        """
        Save normalizer to file.
        
        Args:
            filepath: Path to save file
        """
        if not self.is_fitted:
            raise ValueError("Cannot save unfitted normalizer")
        
        data = {
            'mean': self.mean,
            'std': self.std,
            'feature_names': self.feature_names
        }
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        joblib.dump(data, filepath)
    
    def load(self, filepath: str) -> 'FeatureNormalizer':
        """
        Load normalizer from file.
        
        Args:
            filepath: Path to saved file
            
        Returns:
            self
        """
        data = joblib.load(filepath)
        
        self.mean = data['mean']
        self.std = data['std']
        self.feature_names = data.get('feature_names')
        self.is_fitted = True
        
        return self
    
    def get_stats(self) -> dict:
        """Get normalization statistics."""
        if not self.is_fitted:
            return {}
        
        stats = {
            'n_features': len(self.mean),
            'fitted': True
        }
        
        if self.feature_names:
            stats['features'] = {}
            for i, name in enumerate(self.feature_names):
                stats['features'][name] = {
                    'mean': float(self.mean[i]),
                    'std': float(self.std[i])
                }
        
        return stats
