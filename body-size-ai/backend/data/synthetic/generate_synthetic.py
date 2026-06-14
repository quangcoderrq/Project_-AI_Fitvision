"""
Synthetic Data Generator
Generates synthetic training data for body measurement prediction.
Extended version with 9 target measurements and 18 features.
"""

import os
import sys
import random
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple


# Anthropometric statistics (mean, std) based on population data
# Values in cm or kg

MALE_STATS = {
    'height': (172, 7),
    'weight': (72, 12),
    # Circumferences (targets)
    'chest': (96, 8),
    'waist': (82, 10),
    'hip': (98, 7),
    # Linear measurements
    'shoulder_width': (44, 3),
    'arm_length': (60, 4),
    'leg_length': (80, 5),
    'torso_length': (50, 3),
    # New measurements
    'back_length': (47, 3),
    'neck_circumference': (38, 2),
    'arm_circumference': (32, 3),
    'thigh_circumference': (55, 5),
    'inseam': (76, 4),
    'belly_width': (28, 4),
}

FEMALE_STATS = {
    'height': (160, 6),
    'weight': (58, 10),
    # Circumferences (targets)
    'chest': (88, 7),
    'waist': (70, 8),
    'hip': (96, 7),
    # Linear measurements
    'shoulder_width': (38, 2.5),
    'arm_length': (54, 3),
    'leg_length': (74, 4),
    'torso_length': (45, 2.5),
    # New measurements
    'back_length': (42, 2.5),
    'neck_circumference': (33, 1.5),
    'arm_circumference': (27, 2.5),
    'thigh_circumference': (53, 5),
    'inseam': (70, 3.5),
    'belly_width': (25, 3.5),
}


def generate_correlated_values(stats: Dict, n_samples: int) -> Dict[str, np.ndarray]:
    """
    Generate anthropometric values with realistic correlations.
    
    Args:
        stats: Dictionary of (mean, std) for each measurement
        n_samples: Number of samples to generate
        
    Returns:
        Dictionary of measurement arrays
    """
    # Generate base height and weight (primary variables)
    height = np.random.normal(stats['height'][0], stats['height'][1], n_samples)
    
    # BMI follows a distribution, use it to derive weight
    bmi = np.random.normal(23.5, 4, n_samples)
    bmi = np.clip(bmi, 16, 40)
    weight = bmi * (height / 100) ** 2
    
    # Height factor for scaling other measurements
    height_factor = height / stats['height'][0]
    
    # Weight factor for circumferences
    weight_factor = np.sqrt(weight / stats['weight'][0])
    
    # Generate correlated measurements
    data = {
        'height_cm': height,
        'weight_kg': weight,
        'bmi': bmi
    }
    
    # Circumferences are influenced by both height and weight
    noise_factor = 0.15  # Random variation
    
    # === Circumference targets ===
    
    # Chest
    base_chest = stats['chest'][0] * height_factor * 0.3 + stats['chest'][0] * weight_factor * 0.7
    chest_noise = np.random.normal(0, stats['chest'][1] * noise_factor, n_samples)
    data['chest'] = base_chest + chest_noise
    
    # Waist (more influenced by weight)
    base_waist = stats['waist'][0] * height_factor * 0.2 + stats['waist'][0] * weight_factor * 0.8
    waist_noise = np.random.normal(0, stats['waist'][1] * noise_factor, n_samples)
    data['waist'] = base_waist + waist_noise
    
    # Hip
    base_hip = stats['hip'][0] * height_factor * 0.3 + stats['hip'][0] * weight_factor * 0.7
    hip_noise = np.random.normal(0, stats['hip'][1] * noise_factor, n_samples)
    data['hip'] = base_hip + hip_noise
    
    # Neck circumference (correlated with chest and weight)
    base_neck = stats['neck_circumference'][0] * height_factor * 0.3 + stats['neck_circumference'][0] * weight_factor * 0.7
    neck_noise = np.random.normal(0, stats['neck_circumference'][1] * noise_factor, n_samples)
    data['neck_circumference'] = base_neck + neck_noise
    
    # Arm circumference (correlated with chest and weight)
    base_arm_circ = stats['arm_circumference'][0] * height_factor * 0.2 + stats['arm_circumference'][0] * weight_factor * 0.8
    arm_circ_noise = np.random.normal(0, stats['arm_circumference'][1] * noise_factor, n_samples)
    data['arm_circumference'] = base_arm_circ + arm_circ_noise
    
    # Thigh circumference (correlated with hip and weight)
    base_thigh_circ = stats['thigh_circumference'][0] * height_factor * 0.25 + stats['thigh_circumference'][0] * weight_factor * 0.75
    thigh_circ_noise = np.random.normal(0, stats['thigh_circumference'][1] * noise_factor, n_samples)
    data['thigh_circumference'] = base_thigh_circ + thigh_circ_noise
    
    # === Linear measurements (more influenced by height) ===
    
    data['shoulder_width'] = (
        stats['shoulder_width'][0] * height_factor * 0.8 +
        stats['shoulder_width'][0] * weight_factor * 0.2 +
        np.random.normal(0, stats['shoulder_width'][1] * noise_factor, n_samples)
    )
    
    data['arm_length'] = (
        stats['arm_length'][0] * height_factor +
        np.random.normal(0, stats['arm_length'][1] * noise_factor, n_samples)
    )
    
    data['leg_length'] = (
        stats['leg_length'][0] * height_factor +
        np.random.normal(0, stats['leg_length'][1] * noise_factor, n_samples)
    )
    
    data['torso_length'] = (
        stats['torso_length'][0] * height_factor +
        np.random.normal(0, stats['torso_length'][1] * noise_factor, n_samples)
    )
    
    # Back length (shoulder to hip, ~95% of torso_length)
    data['back_length'] = (
        stats['back_length'][0] * height_factor +
        np.random.normal(0, stats['back_length'][1] * noise_factor, n_samples)
    )
    
    # Inseam (inner leg length, slightly shorter than leg_length)
    data['inseam'] = (
        stats['inseam'][0] * height_factor +
        np.random.normal(0, stats['inseam'][1] * noise_factor, n_samples)
    )
    
    # Belly width (correlated with waist)
    base_belly = stats['belly_width'][0] * height_factor * 0.2 + stats['belly_width'][0] * weight_factor * 0.8
    belly_noise = np.random.normal(0, stats['belly_width'][1] * noise_factor, n_samples)
    data['belly_width'] = base_belly + belly_noise
    
    return data


def create_feature_vector(data: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
    """
    Create feature vectors from generated measurements.
    
    Args:
        data: Dictionary of measurement arrays
        
    Returns:
        Dictionary with feature columns
    """
    n_samples = len(data['height_cm'])
    
    features = {
        'height_cm': data['height_cm'],
        'weight_kg': data['weight_kg'],
        'bmi': data['bmi'],
        
        # === Original ratios (as if extracted from pose) ===
        'shoulder_width_ratio': data['shoulder_width'] / data['height_cm'],
        'hip_width_ratio': (data['hip'] / 3.14) / data['height_cm'],  # Approximate width from circumference
        'torso_length_ratio': data['torso_length'] / data['height_cm'],
        'leg_length_ratio': data['leg_length'] / data['height_cm'],
        'arm_length_ratio': data['arm_length'] / data['height_cm'],
        'shoulder_hip_ratio': data['shoulder_width'] / (data['hip'] / 3.14),
        'torso_leg_ratio': data['torso_length'] / data['leg_length'],
        
        # === NEW feature ratios ===
        'back_length_ratio': data['back_length'] / data['height_cm'],
        'belly_width_ratio': data['belly_width'] / data['height_cm'],
        'neck_width_ratio': (data['neck_circumference'] / 3.14) / data['height_cm'],  # Width from circumference
        'upper_arm_ratio': (data['arm_length'] * 0.55) / data['height_cm'],  # Upper arm ≈ 55% of full arm
        'thigh_ratio': (data['leg_length'] * 0.55) / data['height_cm'],  # Thigh ≈ 55% of full leg
        'inseam_ratio': data['inseam'] / data['height_cm'],
        'arm_span_ratio': (data['shoulder_width'] + data['arm_length'] * 2) / data['height_cm'],
        
        # === Targets (9 measurements) ===
        'chest': data['chest'],
        'waist': data['waist'],
        'hip': data['hip'],
        'shoulder_width_cm': data['shoulder_width'],
        'back_length': data['back_length'],
        'inseam': data['inseam'],
        'thigh_circumference': data['thigh_circumference'],
        'neck_circumference': data['neck_circumference'],
        'arm_circumference': data['arm_circumference'],
    }
    
    return features


def generate_dataset(n_male: int = 500, n_female: int = 500) -> pd.DataFrame:
    """
    Generate complete synthetic dataset.
    
    Args:
        n_male: Number of male samples
        n_female: Number of female samples
        
    Returns:
        DataFrame with all features and targets
    """
    # Generate male samples
    print(f"Generating {n_male} male samples...")
    male_data = generate_correlated_values(MALE_STATS, n_male)
    male_features = create_feature_vector(male_data)
    male_features['gender_male'] = np.ones(n_male)
    
    # Generate female samples
    print(f"Generating {n_female} female samples...")
    female_data = generate_correlated_values(FEMALE_STATS, n_female)
    female_features = create_feature_vector(female_data)
    female_features['gender_male'] = np.zeros(n_female)
    
    # Combine into DataFrames
    male_df = pd.DataFrame(male_features)
    female_df = pd.DataFrame(female_features)
    
    # Concatenate
    df = pd.concat([male_df, female_df], ignore_index=True)
    
    # Shuffle
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    # Round values
    round_cols = [
        'height_cm', 'weight_kg', 
        'chest', 'waist', 'hip',
        'shoulder_width_cm', 'back_length', 'inseam',
        'thigh_circumference', 'neck_circumference', 'arm_circumference'
    ]
    for col in round_cols:
        df[col] = df[col].round(1)
    
    ratio_cols = [
        'shoulder_width_ratio', 'hip_width_ratio', 'torso_length_ratio',
        'leg_length_ratio', 'arm_length_ratio', 'shoulder_hip_ratio',
        'torso_leg_ratio', 'bmi',
        'back_length_ratio', 'belly_width_ratio', 'neck_width_ratio',
        'upper_arm_ratio', 'thigh_ratio', 'inseam_ratio', 'arm_span_ratio'
    ]
    for col in ratio_cols:
        df[col] = df[col].round(4)
    
    return df


def main():
    # Output path
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    output_dir = os.path.join(project_root, 'data', 'synthetic')
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, 'synthetic_data.csv')
    
    # Generate dataset
    print("Generating synthetic dataset (extended version)...")
    df = generate_dataset(n_male=600, n_female=600)
    
    # Save
    df.to_csv(output_path, index=False)
    print(f"\nDataset saved to: {output_path}")
    print(f"Total samples: {len(df)}")
    print(f"Columns ({len(df.columns)}): {list(df.columns)}")
    
    # Print summary statistics
    print("\nSummary Statistics:")
    print("-" * 60)
    
    target_cols = ['height_cm', 'weight_kg', 'chest', 'waist', 'hip',
                   'shoulder_width_cm', 'back_length', 'inseam',
                   'thigh_circumference', 'neck_circumference', 'arm_circumference']
    
    for col in target_cols:
        print(f"{col:25} mean: {df[col].mean():6.1f}, std: {df[col].std():5.1f}")
    
    print("\nGender distribution:")
    print(f"  Male: {(df['gender_male'] == 1).sum()}")
    print(f"  Female: {(df['gender_male'] == 0).sum()}")
    
    print("\nDone!")


if __name__ == '__main__':
    main()
