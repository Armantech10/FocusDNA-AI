import os
import joblib
import pandas as pd
from typing import Dict, Any
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from ml.data.dataset_generator import generate_behavioral_dataset

MODEL_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(MODEL_DIR, "attention_loss_model.joblib")
REPORT_PATH = os.path.abspath(os.path.join(MODEL_DIR, "../reports/model_comparison_report.md"))

def run_model_comparison() -> Dict[str, Any]:
    """
    Trains Random Forest and Gradient Boosted Trees on identical train/test data.
    Compares Accuracy, Precision, Recall, F1-Score and selects winning model based on F1-Score.
    """
    print("[ML Comparator] Generating dataset for model comparison...")
    X, y = generate_behavioral_dataset(num_samples=1600, random_seed=42)

    # Identical train/test split for fair evaluation
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    models = {
        "Random Forest": RandomForestClassifier(
            n_estimators=100, max_depth=6, random_state=42, class_weight="balanced"
        ),
        "Gradient Boosted Trees (XGBoost Equivalent)": GradientBoostingClassifier(
            n_estimators=100, max_depth=5, random_state=42
        )
    }

    results = {}

    for name, model in models.items():
        print(f"[ML Comparator] Training {name}...")
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, zero_division=0)
        rec = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)

        feature_importances = dict(zip(X.columns, model.feature_importances_))

        results[name] = {
            "model": model,
            "accuracy": round(acc, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1_score": round(f1, 4),
            "feature_importances": feature_importances
        }

        print(f" -> {name} - Acc: {acc:.4f}, Prec: {prec:.4f}, Rec: {rec:.4f}, F1: {f1:.4f}")

    # Select winner based on F1-Score (handling rare distraction class)
    winner_name = max(results, key=lambda k: results[k]["f1_score"])
    winner_data = results[winner_name]

    print(f"\n🏆 Winning Model Selected: {winner_name} (F1-Score: {winner_data['f1_score']})")

    # Serialize winning model artifact
    os.makedirs(MODEL_DIR, exist_ok=True)
    artifact = {
        "model_name": winner_name,
        "model": winner_data["model"],
        "feature_names": list(X.columns),
        "feature_importances": winner_data["feature_importances"],
        "accuracy": winner_data["accuracy"],
        "precision": winner_data["precision"],
        "recall": winner_data["recall"],
        "f1_score": winner_data["f1_score"],
        "all_results": {k: {m: v[m] for m in ["accuracy", "precision", "recall", "f1_score"]} for k, v in results.items()}
    }
    joblib.dump(artifact, MODEL_PATH)

    # Generate Markdown Comparison Report
    generate_markdown_report(results, winner_name, REPORT_PATH)

    return artifact

def generate_markdown_report(results: Dict[str, Any], winner_name: str, report_path: str):
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    
    report_content = f"""# FocusDNA AI — Machine Learning Model Comparison Report

This report documents the empirical performance comparison between **Random Forest** and **Gradient Boosted Trees (XGBoost Equivalent)** trained on identical behavioral feature dataset splits.

---

## 1. Benchmark Comparison Table

| Classifier Model | Accuracy | Precision | Recall | F1-Score (Selection Metric) | Selection Status |
| :--- | :---: | :---: | :---: | :---: | :---: |
"""
    for name, m in results.items():
        status = "🏆 **Selected Production Model**" if name == winner_name else "Candidate Model"
        report_content += f"| **{name}** | {m['accuracy']*100:.2f}% | {m['precision']*100:.2f}% | {m['recall']*100:.2f}% | **{m['f1_score']:.4f}** | {status} |\n"

    report_content += f"""
---

## 2. Selection Rationale

- **Primary Selection Metric**: **F1-Score** was selected as the decision criterion because distraction and attention loss events represent imbalanced, critical behavioral states.
- **Winning Classifier**: **{winner_name}** achieved the highest F1-Score of **{results[winner_name]['f1_score']:.4f}**.
- **Model Output**: Serialized model artifact saved to `ml/models/attention_loss_model.joblib`.

---

## 3. Feature Importance Analysis ({winner_name})

"""
    winner_importances = results[winner_name]["feature_importances"]
    for feat, imp in sorted(winner_importances.items(), key=lambda x: x[1], reverse=True):
        report_content += f"- **`{feat}`**: {imp*100:.2f}%\n"

    with open(report_path, "w") as f:
        f.write(report_content)
    print(f"[ML Comparator] Markdown report generated at: {report_path}")

if __name__ == "__main__":
    run_model_comparison()
