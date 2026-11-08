"""
Gradient Boosting Model for Crop Recommendation
This model predicts suitable crops based on soil and environmental attributes.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os

# Paths
DATA_PATH = '../datasets/crop_recommendation_processed.csv'
MODEL_PATH = 'gradient_boosting_model.pkl'
LABEL_ENCODER_PATH = 'label_encoder_gb.pkl'

# Feature columns (excluding label and non-predictive columns)
FEATURE_COLUMNS = [
    'N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall',
    'soil_moisture', 'soil_type', 'sunlight_exposure', 'wind_speed',
    'co2_concentration', 'organic_matter', 'irrigation_frequency',
    'crop_density', 'pest_pressure', 'fertilizer_usage', 'growth_stage',
    'urban_area_proximity', 'water_source_type', 'frost_risk',
    'water_usage_efficiency'
]

# Default values for missing features (median-based)
DEFAULT_VALUES = {}

def load_data():
    """Load and preprocess the dataset."""
    df = pd.read_csv(DATA_PATH)
    return df

def preprocess_data(df):
    """Preprocess data including handling missing values and encoding."""
    # Create a copy to avoid modifying original
    df_processed = df.copy()

    # Encode the target variable (label)
    label_encoder = LabelEncoder()
    df_processed['label_encoded'] = label_encoder.fit_transform(df_processed['label'])

    # Select features
    X = df_processed[FEATURE_COLUMNS]
    y = df_processed['label_encoded']

    # Calculate and store default values (median) for each feature
    global DEFAULT_VALUES
    for col in FEATURE_COLUMNS:
        DEFAULT_VALUES[col] = X[col].median()

    return X, y, label_encoder

def train_model(X, y, label_encoder):
    """Train Gradient Boosting classifier."""
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Initialize Gradient Boosting
    gb_model = GradientBoostingClassifier(
        n_estimators=100,
        learning_rate=0.1,
        max_depth=5,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42
    )

    # Train
    gb_model.fit(X_train, y_train)

    # Evaluate
    y_pred = gb_model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    print(f"Gradient Boosting Training Accuracy: {accuracy:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=label_encoder.classes_))

    return gb_model, X_test, y_test

def save_model(model, label_encoder):
    """Save the trained model and label encoder."""
    joblib.dump(model, MODEL_PATH)
    joblib.dump(label_encoder, LABEL_ENCODER_PATH)
    print(f"Model saved to {MODEL_PATH}")
    print(f"Label encoder saved to {LABEL_ENCODER_PATH}")

def predict_with_missing_features(input_dict, model, label_encoder):
    """
    Predict crop recommendation even with missing features.
    Missing features are replaced with median values.
    """
    # Create feature array with default values
    features = []
    for col in FEATURE_COLUMNS:
        if col in input_dict and input_dict[col] is not None:
            features.append(input_dict[col])
        else:
            # Use median value for missing features
            features.append(DEFAULT_VALUES[col])

    # Reshape for prediction
    features_array = np.array(features).reshape(1, -1)

    # Predict
    prediction = model.predict(features_array)
    probabilities = model.predict_proba(features_array)

    # Decode label
    predicted_crop = label_encoder.inverse_transform(prediction)[0]

    # Get top 3 crops with probabilities
    crop_names = label_encoder.classes_
    prob_dict = dict(zip(crop_names, probabilities[0]))
    top_crops = sorted(prob_dict.items(), key=lambda x: x[1], reverse=True)[:3]

    return predicted_crop, top_crops

def main():
    """Main training pipeline."""
    print("Loading data...")
    df = load_data()

    print("Preprocessing data...")
    X, y, label_encoder = preprocess_data(df)

    print("Training Gradient Boosting model...")
    model, X_test, y_test = train_model(X, y, label_encoder)

    print("Saving model...")
    save_model(model, label_encoder)

    print("\nModel training completed successfully!")
    print(f"Number of features used: {len(FEATURE_COLUMNS)}")
    print(f"Number of crop classes: {len(label_encoder.classes_)}")

    # Save default values for later use
    joblib.dump(DEFAULT_VALUES, 'default_values_gb.pkl')
    print("Default values saved for handling missing features")

if __name__ == "__main__":
    main()
