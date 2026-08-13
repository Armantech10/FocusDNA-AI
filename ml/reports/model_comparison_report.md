# FocusDNA AI — Machine Learning Model Comparison Report

This report documents the empirical performance comparison between **Random Forest** and **Gradient Boosted Trees (XGBoost Equivalent)** trained on identical behavioral feature dataset splits.

---

## 1. Benchmark Comparison Table

| Classifier Model | Accuracy | Precision | Recall | F1-Score (Selection Metric) | Selection Status |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Random Forest** | 96.25% | 98.47% | 96.99% | **0.9773** | Candidate Model |
| **Gradient Boosted Trees (XGBoost Equivalent)** | 96.25% | 97.04% | 98.50% | **0.9776** | 🏆 **Selected Production Model** |

---

## 2. Selection Rationale

- **Primary Selection Metric**: **F1-Score** was selected as the decision criterion because distraction and attention loss events represent imbalanced, critical behavioral states.
- **Winning Classifier**: **Gradient Boosted Trees (XGBoost Equivalent)** achieved the highest F1-Score of **0.9776**.
- **Model Output**: Serialized model artifact saved to `ml/models/attention_loss_model.joblib`.

---

## 3. Feature Importance Analysis (Gradient Boosted Trees (XGBoost Equivalent))

- **`session_elapsed_minutes`**: 33.12%
- **`switch_frequency_5m`**: 23.64%
- **`social_media_ratio`**: 22.72%
- **`entertainment_ratio`**: 13.28%
- **`idle_ratio`**: 6.12%
- **`time_of_day_hour`**: 1.12%
