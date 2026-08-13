import os
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score, classification_report
from ml.data.dataset_generator import generate_behavioral_dataset

MODEL_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(MODEL_DIR, "attention_loss_model.joblib")

def train_and_save_model():
    """
    Trains RandomForest attention loss prediction model and serializes joblib artifact.
    """
    print("[ML Trainer] Generating training dataset...")
    X, y = generate_behavioral_dataset(num_samples=1500)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    print("[ML Trainer] Training RandomForestClassifier model...")
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=6,
        random_state=42,
        class_weight="balanced"
    )
    model.fit(X_train, y_train)

    # Evaluation
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    acc = accuracy_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_prob)

    print(f"[ML Trainer] Model trained successfully!")
    print(f" - Test Accuracy: {acc * 100:.2f}%")
    print(f" - ROC-AUC Score: {auc:.4f}")
    print("\nClassification Report:\n", classification_report(y_test, y_pred))

    # Feature Importance
    feature_importances = dict(zip(X.columns, model.feature_importances_))
    print("Feature Importances:")
    for feat, imp in sorted(feature_importances.items(), key=lambda x: x[1], reverse=True):
        print(f" - {feat}: {imp * 100:.2f}%")

    os.makedirs(MODEL_DIR, exist_ok=True)
    artifact = {
        "model": model,
        "feature_names": list(X.columns),
        "feature_importances": feature_importances,
        "accuracy": acc,
        "roc_auc": auc
    }
    joblib.dump(artifact, MODEL_PATH)
    print(f"[ML Trainer] Model artifact saved to: {MODEL_PATH}")
    return artifact

if __name__ == "__main__":
    train_and_save_model()
