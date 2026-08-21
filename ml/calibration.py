"""
FocusDNA AI — Probability Calibration Engine (Phase 9)
Evaluates and fits Platt Scaling (Sigmoidal calibration) on validation dataset.
"""

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss

class ProbabilityCalibrator:
    def __init__(self):
        self.calibrator = None
        self.is_fitted = False
        self.brier_score_raw = 0.0
        self.brier_score_calibrated = 0.0

    def fit(self, raw_probs: np.ndarray, y_true: np.ndarray):
        """
        Fits Platt Scaling calibrator using logit transform of raw probabilities.
        """
        raw_probs = np.clip(raw_probs, 1e-6, 1.0 - 1e-6)
        logits = np.log(raw_probs / (1.0 - raw_probs)).reshape(-1, 1)

        self.calibrator = LogisticRegression(C=1.0, solver="lbfgs")
        self.calibrator.fit(logits, y_true)
        self.is_fitted = True

        cal_probs = self.predict_proba(raw_probs)
        self.brier_score_raw = float(brier_score_loss(y_true, raw_probs))
        self.brier_score_calibrated = float(brier_score_loss(y_true, cal_probs))

    def predict_proba(self, raw_probs: np.ndarray) -> np.ndarray:
        """
        Calibrates raw probabilities.
        """
        if not self.is_fitted or self.calibrator is None:
            return np.clip(raw_probs, 0.0, 1.0)

        raw_probs = np.clip(raw_probs, 1e-6, 1.0 - 1e-6)
        logits = np.log(raw_probs / (1.0 - raw_probs)).reshape(-1, 1)
        return self.calibrator.predict_proba(logits)[:, 1]
