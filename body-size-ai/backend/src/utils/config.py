"""
Configuration Module
Application configuration and paths.
"""

import os
from typing import Optional
from dataclasses import dataclass


@dataclass
class Config:
    """Application configuration."""
    
    # Project paths
    PROJECT_ROOT: str = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    
    # Data paths
    DATA_DIR: str = os.path.join(PROJECT_ROOT, 'data')
    RAW_DATA_DIR: str = os.path.join(DATA_DIR, 'raw')
    PROCESSED_DATA_DIR: str = os.path.join(DATA_DIR, 'processed')
    SYNTHETIC_DATA_DIR: str = os.path.join(DATA_DIR, 'synthetic')
    SIZE_CHART_DIR: str = os.path.join(DATA_DIR, 'size_chart')
    
    # Model paths
    MODELS_DIR: str = os.path.join(PROJECT_ROOT, 'models')
    MODEL_PATH: str = os.path.join(MODELS_DIR, 'body_measure.pkl')
    SCALER_PATH: str = os.path.join(MODELS_DIR, 'scaler.pkl')
    
    MODEL_SHIRT_PATH: str = os.path.join(MODELS_DIR, 'body_measure_shirt.pkl')
    SCALER_SHIRT_PATH: str = os.path.join(MODELS_DIR, 'scaler_shirt.pkl')

    MODEL_PANTS_PATH: str = os.path.join(MODELS_DIR, 'body_measure_pants.pkl')
    SCALER_PANTS_PATH: str = os.path.join(MODELS_DIR, 'scaler_pants.pkl')
    
    # Size chart path
    SIZE_CHART_PATH: str = os.path.join(SIZE_CHART_DIR, 'size_charts.json')
    
    # Synthetic data path
    SYNTHETIC_DATA_PATH: str = os.path.join(SYNTHETIC_DATA_DIR, 'synthetic_data.csv')
    
    # Image processing settings
    MIN_IMAGE_WIDTH: int = 640
    MIN_IMAGE_HEIGHT: int = 480
    TARGET_IMAGE_SIZE: tuple = (640, 480)
    
    # Pose detection settings
    MIN_DETECTION_CONFIDENCE: float = 0.5
    MIN_TRACKING_CONFIDENCE: float = 0.5
    
    # API settings
    API_HOST: str = '0.0.0.0'
    API_PORT: int = 8000
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # Default brand
    DEFAULT_BRAND: str = 'generic'
    
    @classmethod
    def ensure_directories(cls) -> None:
        """Create required directories if they don't exist."""
        directories = [
            cls.DATA_DIR,
            cls.RAW_DATA_DIR,
            cls.PROCESSED_DATA_DIR,
            cls.SYNTHETIC_DATA_DIR,
            cls.SIZE_CHART_DIR,
            cls.MODELS_DIR
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    @classmethod
    def get_model_path(cls, model_name: str = 'body_measure') -> str:
        """Get path for a specific model."""
        return os.path.join(cls.MODELS_DIR, f'{model_name}.pkl')
    
    @classmethod
    def is_model_available(cls) -> bool:
        """Check if trained model exists."""
        return os.path.exists(cls.MODEL_PATH) and os.path.exists(cls.SCALER_PATH)
    
    @classmethod
    def get_available_brands(cls) -> list:
        """Get list of available brands from size charts."""
        if os.path.exists(cls.SIZE_CHART_PATH):
            import json
            with open(cls.SIZE_CHART_PATH, 'r') as f:
                data = json.load(f)
            return list(data.keys())
        return ['generic']


# Create singleton instance
config = Config()
