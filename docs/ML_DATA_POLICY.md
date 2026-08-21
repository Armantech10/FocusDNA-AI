# FocusDNA AI — Machine Learning Privacy & Data Policy

**Document Version**: 2.0  
**Effective Date**: August 20, 2026  

---

## 1. Zero-Keystroke & Privacy Guarantee

FocusDNA AI operates strictly as a **privacy-first behavioral metadata analyzer**.

### Prohibited Data Collection (0% Collection)
- ❌ **Keystrokes**: NEVER logged, typed, captured, or transmitted.
- ❌ **Page Contents & Text**: NEVER parsed or trained on.
- ❌ **LLM Messages & Prompts**: NEVER recorded or inspected.
- ❌ **Screenshots & Images**: NEVER taken or captured.
- ❌ **Passwords, Forms & Passwords**: NEVER touched.
- ❌ **Clipboard Content**: NEVER accessed.

---

## 2. Permitted Behavioral Metadata

ML models operate exclusively on high-level digital interaction metrics:
- Domain hostname (e.g., `github.com`, `twitter.com`)
- Tab context switch frequency (`switches/5m`)
- Duration spent per domain category (`social`, `entertainment`, `productive`)
- System idle duration (seconds)
- Hour of day & day of week

---

## 3. Real User Labeling Policy

- Ground truth target labels (`binary_target`) are derived **exclusively from explicit human feedback** (5-level post-session focus rating: *Very focused* $\dots$ *Very distracted*).
- **Rule-Based Scores are NOT Ground Truth**: Heuristic focus scores are rules, not ML training ground truth.
- **Domain Categories are NOT Ground Truth**: Opening YouTube or Twitter is not automatically labeled as distraction unless confirmed by user rating.

---

## 4. Controlled Promotion Policy

- Training pipeline generates versioned candidates (`v1.1.0`).
- Models must pass validation gates ($F1 \ge baseline\_f1$).
- **No Automatic Production Replacement**: Promoting a candidate to production requires explicit CLI execution:
  ```bash
  python -m ml.promote --promote v1.1.0
  ```
