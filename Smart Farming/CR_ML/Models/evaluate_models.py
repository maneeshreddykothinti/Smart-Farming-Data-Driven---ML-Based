"""
Model Evaluation Script for Crop Recommendation
This script evaluates and compares all three models to determine the best performer.
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report
)
import joblib
import time
import os

# Change to Models directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Paths
DATA_PATH = '../datasets/crop_recommendation_processed.csv'

# Feature columns
FEATURE_COLUMNS = [
    'N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall',
    'soil_moisture', 'soil_type', 'sunlight_exposure', 'wind_speed',
    'co2_concentration', 'organic_matter', 'irrigation_frequency',
    'crop_density', 'pest_pressure', 'fertilizer_usage', 'growth_stage',
    'urban_area_proximity', 'water_source_type', 'frost_risk',
    'water_usage_efficiency'
]

def load_and_preprocess_data():
    """Load and preprocess the dataset."""
    print("Loading data...")
    df = pd.read_csv(DATA_PATH)

    # Encode the target variable
    label_encoder = LabelEncoder()
    df['label_encoded'] = label_encoder.fit_transform(df['label'])

    # Select features
    X = df[FEATURE_COLUMNS]
    y = df['label_encoded']

    # Split data (same split for all models for fair comparison)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    return X_train, X_test, y_train, y_test, label_encoder

def evaluate_model(model, X_test, y_test, model_name, label_encoder):
    """Evaluate a single model and return metrics."""
    print(f"\n{'='*60}")
    print(f"Evaluating {model_name}")
    print(f"{'='*60}")

    # Measure prediction time
    start_time = time.time()
    y_pred = model.predict(X_test)
    prediction_time = time.time() - start_time

    # Calculate metrics
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average='weighted')
    recall = recall_score(y_test, y_pred, average='weighted')
    f1 = f1_score(y_test, y_pred, average='weighted')

    # Print metrics
    print(f"Accuracy: {accuracy:.4f}")
    print(f"Precision (weighted): {precision:.4f}")
    print(f"Recall (weighted): {recall:.4f}")
    print(f"F1 Score (weighted): {f1:.4f}")
    print(f"Prediction Time: {prediction_time:.4f} seconds")

    # Confusion Matrix
    cm = confusion_matrix(y_test, y_pred)
    print(f"\nConfusion Matrix shape: {cm.shape}")

    return {
        'model_name': model_name,
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1_score': f1,
        'prediction_time': prediction_time,
        'confusion_matrix': cm
    }

def compare_models(metrics_list):
    """Compare all models and print summary."""
    print(f"\n{'='*60}")
    print("MODEL COMPARISON SUMMARY")
    print(f"{'='*60}\n")

    # Create comparison table
    comparison_df = pd.DataFrame([{
        'Model': m['model_name'],
        'Accuracy': m['accuracy'],
        'Precision': m['precision'],
        'Recall': m['recall'],
        'F1 Score': m['f1_score'],
        'Prediction Time (s)': m['prediction_time']
    } for m in metrics_list])

    print(comparison_df.to_string(index=False))

    # Find best model for each metric
    best_accuracy = max(metrics_list, key=lambda x: x['accuracy'])
    best_f1 = max(metrics_list, key=lambda x: x['f1_score'])
    fastest = min(metrics_list, key=lambda x: x['prediction_time'])

    print(f"\n{'='*60}")
    print("BEST MODEL FOR EACH METRIC")
    print(f"{'='*60}")
    print(f"Best Accuracy: {best_accuracy['model_name']} ({best_accuracy['accuracy']:.4f})")
    print(f"Best F1 Score: {best_f1['model_name']} ({best_f1['f1_score']:.4f})")
    print(f"Fastest Prediction: {fastest['model_name']} ({fastest['prediction_time']:.4f}s)")

    # Overall recommendation
    print(f"\n{'='*60}")
    print("OVERALL RECOMMENDATION")
    print(f"{'='*60}")

    # Calculate a composite score (accuracy weighted more heavily)
    for m in metrics_list:
        m['composite_score'] = (m['accuracy'] * 0.5 + m['f1_score'] * 0.3 +
                               (1 / (m['prediction_time'] + 0.01)) * 0.2)

    best_overall = max(metrics_list, key=lambda x: x['composite_score'])
    print(f"Recommended Model: {best_overall['model_name']}")
    print(f"Composite Score: {best_overall['composite_score']:.4f}")
    print(f"  - Accuracy: {best_overall['accuracy']:.4f}")
    print(f"  - F1 Score: {best_overall['f1_score']:.4f}")
    print(f"  - Prediction Time: {best_overall['prediction_time']:.4f}s")

    return comparison_df, best_overall

def save_report(comparison_df, best_model):
    """Save evaluation report to a text file."""
    report_path = 'model_evaluation_report.txt'

    with open(report_path, 'w') as f:
        f.write("="*60 + "\n")
        f.write("CROP RECOMMENDATION MODEL EVALUATION REPORT\n")
        f.write("="*60 + "\n\n")

        f.write("MODELS EVALUATED:\n")
        f.write("1. Random Forest Classifier\n")
        f.write("2. Decision Tree Classifier\n")
        f.write("3. Gradient Boosting Classifier\n\n")

        f.write("="*60 + "\n")
        f.write("PERFORMANCE METRICS\n")
        f.write("="*60 + "\n\n")
        f.write(comparison_df.to_string(index=False))
        f.write("\n\n")

        f.write("="*60 + "\n")
        f.write("RECOMMENDATION\n")
        f.write("="*60 + "\n\n")
        f.write(f"Best Model: {best_model['model_name']}\n")
        f.write(f"Accuracy: {best_model['accuracy']:.4f}\n")
        f.write(f"Precision: {best_model['precision']:.4f}\n")
        f.write(f"Recall: {best_model['recall']:.4f}\n")
        f.write(f"F1 Score: {best_model['f1_score']:.4f}\n")
        f.write(f"Prediction Time: {best_model['prediction_time']:.4f}s\n")
        f.write(f"Composite Score: {best_model['composite_score']:.4f}\n\n")

        f.write("="*60 + "\n")
        f.write("DETAILED ANALYSIS\n")
        f.write("="*60 + "\n\n")

        # Add analysis for each model
        f.write("Random Forest:\n")
        f.write("- Advantages: Ensemble method reduces overfitting, handles complex relationships\n")
        f.write("- Good for: Large datasets with many features\n")
        f.write("- Trade-offs: Slower prediction time due to multiple trees\n\n")

        f.write("Decision Tree:\n")
        f.write("- Advantages: Fast prediction, interpretable, simple to understand\n")
        f.write("- Good for: Quick recommendations, understanding feature importance\n")
        f.write("- Trade-offs: Prone to overfitting, less accurate on complex patterns\n\n")

        f.write("Gradient Boosting:\n")
        f.write("- Advantages: High accuracy, handles complex non-linear relationships\n")
        f.write("- Good for: Maximizing prediction accuracy\n")
        f.write("- Trade-offs: Longer training time, more complex to tune\n\n")

    print(f"\nEvaluation report saved to {report_path}")

def main():
    """Main evaluation pipeline."""
    print("Starting Model Evaluation...")

    # Load data
    X_train, X_test, y_train, y_test, label_encoder = load_and_preprocess_data()

    # Load models
    models = {}
    try:
        models['Random Forest'] = joblib.load('random_forest_model.pkl')
        models['Decision Tree'] = joblib.load('decision_tree_model.pkl')
        models['Gradient Boosting'] = joblib.load('gradient_boosting_model.pkl')
    except FileNotFoundError as e:
        print(f"Error: Model file not found. {e}")
        print("Please train the models first by running their respective scripts.")
        return

    # Evaluate all models
    metrics_list = []
    for model_name, model in models.items():
        metrics = evaluate_model(model, X_test, y_test, model_name, label_encoder)
        metrics_list.append(metrics)

    # Compare models
    comparison_df, best_model = compare_models(metrics_list)

    # Save report
    save_report(comparison_df, best_model)

    print("\nEvaluation completed successfully!")

if __name__ == "__main__":
    main()
