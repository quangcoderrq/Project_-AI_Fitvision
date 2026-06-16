"""
Training Script
Trains the body measurement prediction model.

Supports:
- synthetic data
- optional real measurement data
- full body model
- shirt-focused model
- pants-focused model
- metrics export
"""

import os
import sys
import json
import argparse
from datetime import datetime

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.models.regressors import BodyMeasurementRegressor
from src.features.normalize import FeatureNormalizer


FEATURE_COLS = [
    'shoulder_width_ratio',
    'hip_width_ratio',
    'torso_length_ratio',
    'leg_length_ratio',
    'arm_length_ratio',
    'shoulder_hip_ratio',
    'torso_leg_ratio',
    'back_length_ratio',
    'belly_width_ratio',
    'neck_width_ratio',
    'upper_arm_ratio',
    'thigh_ratio',
    'inseam_ratio',
    'arm_span_ratio',
    'bmi',
    'height_cm',
    'weight_kg',
    'gender_male'
]

FULL_TARGET_COLS = [
    'chest',
    'waist',
    'hip',
    'shoulder_width_cm',
    'back_length',
    'inseam',
    'thigh_circumference',
    'neck_circumference',
    'arm_circumference'
]

SHIRT_TARGET_COLS = [
    'chest',
    'waist',
    'shoulder_width_cm',
    'back_length',
    'neck_circumference',
    'arm_circumference'
]

PANTS_TARGET_COLS = [
    'waist',
    'hip',
    'inseam',
    'thigh_circumference'
]


def get_target_cols(train_mode: str) -> list:
    if train_mode == "shirt":
        return SHIRT_TARGET_COLS
    if train_mode == "pants":
        return PANTS_TARGET_COLS
    return FULL_TARGET_COLS


def load_csv_data(data_path: str, target_cols: list) -> pd.DataFrame:
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Data file not found: {data_path}")

    df = pd.read_csv(data_path)

    missing_features = [c for c in FEATURE_COLS if c not in df.columns]
    if missing_features:
        raise ValueError(f"Missing feature columns: {missing_features}")

    missing_targets = [c for c in target_cols if c not in df.columns]
    if missing_targets:
        raise ValueError(f"Missing target columns: {missing_targets}")

    return df


def clean_training_data(df: pd.DataFrame, target_cols: list) -> pd.DataFrame:
    required_cols = FEATURE_COLS + target_cols

    df = df.copy()

    # Keep only required columns
    df = df[required_cols]

    # Convert all values to numeric
    for col in required_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Drop rows with missing values
    df = df.dropna()

    # Basic human range filters
    df = df[
        (df["height_cm"] >= 100) & (df["height_cm"] <= 250) &
        (df["weight_kg"] >= 30) & (df["weight_kg"] <= 300) &
        (df["bmi"] >= 10) & (df["bmi"] <= 60)
    ]

    # Measurement sanity filters
    measurement_ranges = {
        "chest": (50, 180),
        "waist": (45, 170),
        "hip": (50, 180),
        "shoulder_width_cm": (25, 80),
        "back_length": (25, 90),
        "inseam": (40, 120),
        "thigh_circumference": (25, 100),
        "neck_circumference": (20, 70),
        "arm_circumference": (15, 80),
    }

    for col, (min_v, max_v) in measurement_ranges.items():
        if col in df.columns:
            df = df[(df[col] >= min_v) & (df[col] <= max_v)]

    return df.reset_index(drop=True)


def load_training_data(
    synthetic_path: str,
    real_path: str | None,
    target_cols: list
) -> tuple:
    synthetic_df = load_csv_data(synthetic_path, target_cols)
    synthetic_df["data_source"] = "synthetic"

    frames = [synthetic_df]

    if real_path:
        if os.path.exists(real_path):
            real_df = load_csv_data(real_path, target_cols)
            real_df["data_source"] = "real"
            frames.append(real_df)
            print(f"Loaded real data: {len(real_df)} samples")
        else:
            print(f"Warning: real data file not found: {real_path}")

    df = pd.concat(frames, ignore_index=True)
    before = len(df)

    df = clean_training_data(df, target_cols)
    after = len(df)

    print(f"Data before cleaning: {before}")
    print(f"Data after cleaning:  {after}")

    X = df[FEATURE_COLS].values.astype(np.float32)
    y = df[target_cols].values.astype(np.float32)

    return X, y, FEATURE_COLS, target_cols, df


def train_model(
    X: np.ndarray,
    y: np.ndarray,
    feature_names: list,
    target_names: list,
    model_type: str = "random_forest",
    test_size: float = 0.2
) -> tuple:
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=42
    )

    print(f"Training samples: {len(X_train)}")
    print(f"Test samples:     {len(X_test)}")

    normalizer = FeatureNormalizer()
    X_train_norm = normalizer.fit_transform(X_train, feature_names)
    X_test_norm = normalizer.transform(X_test)

    print(f"\nTraining model: {model_type}")

    model = BodyMeasurementRegressor(
        model_type=model_type,
        target_names=target_names
    )
    # Important:
    # Your current BodyMeasurementRegressor expects its own TARGET_NAMES.
    # So for now full mode is safest.
    # Shirt/pants mode needs regressor.py update in Step 2.
    # if len(target_names) != len(model.TARGET_NAMES):
    #     raise ValueError(
    #         f"Current regressor expects {len(model.TARGET_NAMES)} targets, "
    #         f"but train mode has {len(target_names)} targets. "
    #         f"Use --train-mode full for now, or update regressors.py in Step 2."
    #     )

    model.fit(X_train_norm, y_train, feature_names)

    train_r2 = model.score(X_train_norm, y_train)
    test_r2 = model.score(X_test_norm, y_test)

    y_pred = model.predict(X_test_norm)

    per_target_mae = {}
    for i, name in enumerate(target_names):
        mae = float(np.mean(np.abs(y_test[:, i] - y_pred[:, i])))
        per_target_mae[name] = round(mae, 3)

    avg_mae = float(np.mean(list(per_target_mae.values())))

    print("\nModel Performance")
    print(f"Train R²: {train_r2:.4f}")
    print(f"Test R²:  {test_r2:.4f}")
    print(f"Avg MAE:  {avg_mae:.2f} cm")

    print("\nPer-target MAE")
    for name, mae in per_target_mae.items():
        print(f"  {name:25} {mae:.2f} cm")

    importance = model.get_feature_importance()
    top_features = []

    if importance:
        sorted_importance = sorted(
            importance.items(),
            key=lambda x: x[1],
            reverse=True
        )

        print("\nTop Feature Importance")
        for name, imp in sorted_importance[:10]:
            print(f"  {name:25} {imp:.4f}")
            top_features.append({
                "feature": name,
                "importance": float(imp)
            })

    metrics = {
        "created_at": datetime.utcnow().isoformat(),
        "model_type": model_type,
        "n_train": int(len(X_train)),
        "n_test": int(len(X_test)),
        "train_r2": float(train_r2),
        "test_r2": float(test_r2),
        "avg_mae_cm": round(avg_mae, 3),
        "per_target_mae_cm": per_target_mae,
        "feature_names": feature_names,
        "target_names": target_names,
        "top_features": top_features
    }

    return model, normalizer, metrics


def save_metrics(metrics: dict, output_path: str) -> None:
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)

def augment_training_data(
    X: np.ndarray,
    y: np.ndarray,
    feature_names: list,
    copies: int = 2,
    height_noise: float = 2.0,
    weight_noise: float = 3.0,
    target_noise: float = 0.6
) -> tuple:
    """
    Add controlled noise to height/weight/BMI so model does not overfit
    only on physical inputs.

    This improves real-world robustness.
    """

    X_list = [X]
    y_list = [y]

    height_idx = feature_names.index("height_cm")
    weight_idx = feature_names.index("weight_kg")
    bmi_idx = feature_names.index("bmi")

    for _ in range(copies):
        X_aug = X.copy()
        y_aug = y.copy()

        height_delta = np.random.normal(0, height_noise, size=len(X_aug))
        weight_delta = np.random.normal(0, weight_noise, size=len(X_aug))

        X_aug[:, height_idx] += height_delta
        X_aug[:, weight_idx] += weight_delta

        height_m = X_aug[:, height_idx] / 100.0
        X_aug[:, bmi_idx] = X_aug[:, weight_idx] / (height_m ** 2)

        y_aug += np.random.normal(0, target_noise, size=y_aug.shape)

        X_list.append(X_aug)
        y_list.append(y_aug)

    return np.vstack(X_list), np.vstack(y_list)


def main():
    parser = argparse.ArgumentParser(
        description="Train body measurement prediction model"
    )

    parser.add_argument(
        "--synthetic-data",
        type=str,
        default="data/synthetic/synthetic_data.csv",
        help="Path to synthetic training CSV"
    )

    parser.add_argument(
        "--real-data",
        type=str,
        default=None,
        help="Optional path to real measurement CSV"
    )

    parser.add_argument(
        "--model-type",
        type=str,
        default="random_forest",
        choices=["random_forest", "gradient_boosting", "ridge"],
        help="Type of model to train"
    )

    parser.add_argument(
        "--train-mode",
        type=str,
        default="full",
        choices=["full", "shirt", "pants"],
        help="Train full body, shirt-focused, or pants-focused model"
    )

    parser.add_argument(
        "--output-dir",
        type=str,
        default="models",
        help="Directory to save trained model files"
    )

    parser.add_argument(
        "--test-size",
        type=float,
        default=0.2,
        help="Test split ratio"
    )

    args = parser.parse_args()

    project_root = os.path.dirname(
        os.path.dirname(os.path.dirname(__file__))
    )

    synthetic_path = os.path.join(project_root, args.synthetic_data)

    real_path = None
    if args.real_data:
        real_path = os.path.join(project_root, args.real_data)

    output_dir = os.path.join(project_root, args.output_dir)
    os.makedirs(output_dir, exist_ok=True)

    target_cols = get_target_cols(args.train_mode)

    print("======================================")
    print("FitVision AI Training")
    print("======================================")
    print(f"Train mode:     {args.train_mode}")
    print(f"Model type:     {args.model_type}")
    print(f"Synthetic data: {synthetic_path}")
    print(f"Real data:      {real_path}")
    print(f"Output dir:     {output_dir}")
    print("======================================")

    X, y, feature_names, target_names, df = load_training_data(
        synthetic_path=synthetic_path,
        real_path=real_path,
        target_cols=target_cols
    )

    print(f"\nLoaded samples: {len(X)}")
    print(f"Features:       {len(feature_names)}")
    print(f"Targets:        {len(target_names)}")
    
    X, y = augment_training_data(
    X,
    y,
    feature_names,
    copies=3,
    height_noise=2.0,
    weight_noise=3.0,
    target_noise=0.5
    )

    print(f"After augmentation samples: {len(X)}")
    model, normalizer, metrics = train_model(
        X=X,
        y=y,
        feature_names=feature_names,
        target_names=target_names,
        model_type=args.model_type,
        test_size=args.test_size
    )

    if args.train_mode == "full":
        model_name = "body_measure.pkl"
        scaler_name = "scaler.pkl"
        metrics_name = "metrics_full.json"
    else:
        model_name = f"body_measure_{args.train_mode}.pkl"
        scaler_name = f"scaler_{args.train_mode}.pkl"
        metrics_name = f"metrics_{args.train_mode}.json"

    model_path = os.path.join(output_dir, model_name)
    scaler_path = os.path.join(output_dir, scaler_name)
    metrics_path = os.path.join(output_dir, metrics_name)

    model.save(model_path)
    normalizer.save(scaler_path)
    save_metrics(metrics, metrics_path)

    print("\nSaved files")
    print(f"Model:   {model_path}")
    print(f"Scaler:  {scaler_path}")
    print(f"Metrics: {metrics_path}")
    print("\nTraining complete!")


if __name__ == "__main__":
    main()