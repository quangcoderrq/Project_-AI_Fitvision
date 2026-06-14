"""
Training Script
Trains the body measurement prediction model.
"""

import os
import sys
import argparse
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.models.regressors import BodyMeasurementRegressor
from src.features.normalize import FeatureNormalizer


def load_synthetic_data(data_path: str) -> tuple:
    """
    Load synthetic training data.
    
    Args:
        data_path: Path to CSV file
        
    Returns:
        Tuple of (X, y, feature_names)
    """
    df = pd.read_csv(data_path)
    
    # Feature columns (expanded: 18 features)
    feature_cols = [
        'shoulder_width_ratio', 'hip_width_ratio', 'torso_length_ratio',
        'leg_length_ratio', 'arm_length_ratio', 'shoulder_hip_ratio',
        'torso_leg_ratio',
        'back_length_ratio', 'belly_width_ratio', 'neck_width_ratio',
        'upper_arm_ratio', 'thigh_ratio', 'inseam_ratio', 'arm_span_ratio',
        'bmi', 'height_cm', 'weight_kg', 'gender_male'
    ]
    
    # Target columns (expanded: 9 targets)
    target_cols = [
        'chest', 'waist', 'hip',
        'shoulder_width_cm', 'back_length', 'inseam',
        'thigh_circumference', 'neck_circumference', 'arm_circumference'
    ]
    
    # Check columns exist
    missing_features = [c for c in feature_cols if c not in df.columns]
    if missing_features:
        raise ValueError(f"Missing feature columns: {missing_features}")
    
    missing_targets = [c for c in target_cols if c not in df.columns]
    if missing_targets:
        raise ValueError(f"Missing target columns: {missing_targets}")
    
    X = df[feature_cols].values
    y = df[target_cols].values
    
    return X, y, feature_cols


def train_model(X: np.ndarray, y: np.ndarray, 
                feature_names: list,
                model_type: str = 'random_forest',
                test_size: float = 0.2) -> tuple:
    """
    Train and evaluate model.
    
    Args:
        X: Feature matrix
        y: Target matrix
        feature_names: List of feature names
        model_type: Type of regressor
        test_size: Fraction for test set
        
    Returns:
        Tuple of (model, normalizer, metrics)
    """
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=42
    )
    
    print(f"Training samples: {len(X_train)}")
    print(f"Test samples: {len(X_test)}")
    
    # Normalize features
    normalizer = FeatureNormalizer()
    X_train_norm = normalizer.fit_transform(X_train, feature_names)
    X_test_norm = normalizer.transform(X_test)
    
    # Train model
    print(f"\nTraining {model_type} model...")
    model = BodyMeasurementRegressor(model_type=model_type)
    model.fit(X_train_norm, y_train, feature_names)
    
    # Evaluate
    train_score = model.score(X_train_norm, y_train)
    test_score = model.score(X_test_norm, y_test)
    
    print(f"\nModel Performance:")
    print(f"  Train R² score: {train_score:.4f}")
    print(f"  Test R² score: {test_score:.4f}")
    
    # Per-target evaluation
    y_pred = model.predict(X_test_norm)
    target_names = [
        'chest', 'waist', 'hip',
        'shoulder_width_cm', 'back_length', 'inseam',
        'thigh_circumference', 'neck_circumference', 'arm_circumference'
    ]
    for i, name in enumerate(target_names):
        if i < y_test.shape[1]:
            mae = np.mean(np.abs(y_test[:, i] - y_pred[:, i]))
            print(f"  {name:25} MAE: {mae:.2f} cm")
    
    # Feature importance
    importance = model.get_feature_importance()
    if importance:
        print("\nFeature Importance:")
        sorted_importance = sorted(importance.items(), 
                                   key=lambda x: x[1], reverse=True)
        for name, imp in sorted_importance[:5]:
            print(f"  {name}: {imp:.4f}")
    
    metrics = {
        'train_r2': train_score,
        'test_r2': test_score,
        'n_train': len(X_train),
        'n_test': len(X_test)
    }
    
    return model, normalizer, metrics


def main():
    parser = argparse.ArgumentParser(description='Train body measurement model')
    parser.add_argument(
        '--data', 
        type=str, 
        default='data/synthetic/synthetic_data.csv',
        help='Path to training data CSV'
    )
    parser.add_argument(
        '--model-type',
        type=str,
        default='random_forest',
        choices=['random_forest', 'gradient_boosting', 'ridge'],
        help='Type of model to train'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='models',
        help='Directory to save trained models'
    )
    
    args = parser.parse_args()
    
    # Get project root
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    data_path = os.path.join(project_root, args.data)
    output_dir = os.path.join(project_root, args.output_dir)
    
    # Check data exists
    if not os.path.exists(data_path):
        print(f"Error: Data file not found: {data_path}")
        print("Run 'python data/synthetic/generate_synthetic.py' first.")
        sys.exit(1)
    
    # Load data
    print(f"Loading data from {data_path}...")
    X, y, feature_names = load_synthetic_data(data_path)
    print(f"Loaded {len(X)} samples with {len(feature_names)} features")
    
    # Train model
    model, normalizer, metrics = train_model(
        X, y, feature_names, 
        model_type=args.model_type
    )
    
    # Save model and normalizer
    os.makedirs(output_dir, exist_ok=True)
    
    model_path = os.path.join(output_dir, 'body_measure.pkl')
    scaler_path = os.path.join(output_dir, 'scaler.pkl')
    
    model.save(model_path)
    normalizer.save(scaler_path)
    
    print(f"\nModel saved to: {model_path}")
    print(f"Scaler saved to: {scaler_path}")
    print("\nTraining complete!")


if __name__ == '__main__':
    main()
