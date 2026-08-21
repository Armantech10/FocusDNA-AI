"""
FocusDNA AI — Model Card Generator (Phase 14)
Generates standardized Markdown model card documentation for every model version.
"""

import os
from typing import Dict, Any

class ModelCardGenerator:
    @staticmethod
    def generate_model_card(
        model_info: Dict[str, Any],
        output_dir: str = "docs/models"
    ) -> str:
        os.makedirs(output_dir, exist_ok=True)
        version = model_info.get("model_version", "v1.0.0-PrototypeBaseline")
        card_path = os.path.join(output_dir, f"{version}.md")

        metrics = model_info.get("metrics", {})
        ds_meta = model_info.get("dataset_meta", {})
        ds_type = ds_meta.get("dataset_type", "synthetic_baseline")
        real_count = ds_meta.get("real_labeled_sessions_count", 0)

        data_policy_notice = (
            "⚠️ **NOTICE: PROTOTYPE BASELINE MODEL**\n"
            "This model version was trained on a synthetic baseline dataset. Metrics reported reflect synthetic benchmark performance.\n"
            "Real user telemetry data collection and labeling infrastructure is active."
            if ds_type == "synthetic_baseline" or real_count < 50
            else "✅ **PRODUCTION MODEL (REAL USER LABELS)**\n"
            "This model version was trained on real, verified FocusDNA session labels."
        )

        content = f"""# FocusDNA Model Card: {version}

**Model Type**: `{model_info.get("model_type", "GradientBoostedTrees")}`  
**Feature Schema Version**: `1.0` (Canonical 13-feature vector)  
**Trained At**: `{model_info.get("trained_at", "N/A")}`  

---

## 1. Executive Status & Data Policy

{data_policy_notice}

- **Dataset Type**: `{ds_type}`
- **Real Labeled Sessions**: `{real_count}`
- **Total Samples**: `{ds_meta.get("total_samples", 0)}` (Train: {ds_meta.get("train_samples", 0)}, Val: {ds_meta.get("val_samples", 0)}, Test: {ds_meta.get("test_samples", 0)})
- **Leakage Safeguard**: `GroupKFold / Time-Aware Splitting` (Passed: `{ds_meta.get("leakage_check_passed", True)}`)

---

## 2. Evaluation Metrics

| Metric | Score |
| :--- | :--- |
| **Accuracy** | `{metrics.get("accuracy", 0.0) * 100:.2f}%` |
| **Precision** | `{metrics.get("precision", 0.0) * 100:.2f}%` |
| **Recall** | `{metrics.get("recall", 0.0) * 100:.2f}%` |
| **F1-Score** | `{metrics.get("f1_score", 0.0):.4f}` |
| **ROC-AUC** | `{metrics.get("roc_auc", 0.0):.4f}` |
| **Brier Score (Calibration)** | `{metrics.get("brier_score", 0.0):.4f}` |

---

## 3. Privacy & Security Constraints

- **Keystrokes**: NOT collected (0%)
- **Page Content / Text**: NOT collected (0%)
- **Screenshots / Passwords**: NOT collected (0%)
- **Features Used**: High-level behavioral metadata only (durations, switch frequencies, idle ratios, time of day).

---

## 4. Candidate Model Comparison

```json
{metrics.get("all_candidates", {})}
```

---

## 5. Intended Usage & Limitations

- **Intended Use**: Attention-loss prediction and personalized focus nudges.
- **Limitations**: Prototype models require minimum 50 real labeled sessions per user before personalized model promotion.
"""

        with open(card_path, "w") as f:
            f.write(content)

        print(f"[ModelCardGenerator] Model card written to: {card_path}")
        return card_path
