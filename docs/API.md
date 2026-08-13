# FocusDNA AI — REST API Documentation Specification

This document details the backend REST endpoints provided by the FastAPI server (`http://localhost:8000`).

---

## 1. System Health & Infrastructure

### `GET /health`
- **Purpose**: System health check for Docker container orchestrators and load balancers.
- **Authentication**: None.
- **Response Example**:
  ```json
  {
    "status": "ok"
  }
  ```

---

## 2. Telemetry & Event Ingestion

### `POST /api/events`
- **Purpose**: Ingests 5-minute activity telemetry events from Chrome Extension or Desktop Agent.
- **Authentication**: Bearer JWT Token required.
- **Request Example**:
  ```json
  {
    "application_name": "Visual Studio Code",
    "website_domain": "github.com",
    "session_duration": 300,
    "app_switch_count": 2,
    "browser_switch_count": 1,
    "idle_seconds": 15,
    "device_type": "desktop_mac"
  }
  ```
- **Response Example (HTTP 201)**:
  ```json
  {
    "status": "recorded",
    "event_id": "evt_104",
    "score": 88
  }
  ```

---

## 3. Focus Session Engine

### `POST /api/sessions`
- **Purpose**: Creates a new focus session timer.
- **Authentication**: Bearer JWT Token required.
- **Request Example**:
  ```json
  {
    "session_name": "Core Feature Development",
    "planned_duration_minutes": 25
  }
  ```
- **Response Example (HTTP 201)**:
  ```json
  {
    "id": "sess_89a1b2",
    "session_name": "Core Feature Development",
    "planned_duration_minutes": 25,
    "actual_duration_minutes": 0,
    "status": "active",
    "distraction_count": 0,
    "app_switch_count": 0,
    "started_at": "2026-08-13T15:00:00Z"
  }
  ```

---

## 4. Machine Learning & Predictions

### `POST /api/ml/predict`
- **Purpose**: Evaluates behavioral feature vectors to predict attention loss probability using serialized Gradient Boosted Trees.
- **Authentication**: Bearer JWT Token required.
- **Request Example**:
  ```json
  {
    "app_switches": 6,
    "idle_seconds": 45,
    "distraction_ratio": 0.45,
    "average_session_duration": 40.0
  }
  ```
- **Response Example (HTTP 200)**:
  ```json
  {
    "prediction": "distracted",
    "probability": 0.82,
    "model_version": "1.0.0-gbt",
    "explanation_features": [
      { "feature": "distraction_ratio", "value": 0.45 },
      { "feature": "app_switches", "value": 6 }
    ]
  }
  ```

---

## 5. Personal FocusDNA Profile

### `GET /api/profile/focusdna`
- **Purpose**: Calculates personalized behavioral metrics from actual historical telemetry.
- **Authentication**: Bearer JWT Token required.
- **Response Example (HTTP 200)**:
  ```json
  {
    "has_data": true,
    "typical_focus_session_mins": 42.0,
    "best_focus_period": "9:00 AM – 11:00 AM",
    "average_context_switches": 3.2,
    "common_distraction_trigger": "Social Media",
    "focus_consistency_pct": 74.0,
    "total_sessions_analyzed": 14
  }
  ```

---

## 6. AI Recommendation Engine

### `POST /api/ai/recommendation`
- **Purpose**: Generates personalized AI focus interventions using Google Gemini REST API.
- **Authentication**: Bearer JWT Token required.
- **Request Example**:
  ```json
  {
    "average_focus_session": 40.0,
    "common_distraction_period": "2:00 PM – 4:00 PM",
    "average_switches": 3.5,
    "top_trigger": "Social Media",
    "recent_anomaly": false,
    "focus_trend": "improving"
  }
  ```
- **Response Example (HTTP 200)**:
  ```json
  {
    "explanation": "Your focus tends to drop after about 40 minutes of continuous session work, particularly around 2:00 PM – 4:00 PM.",
    "recommendation": "Schedule a structured 5-minute break before the 40-minute mark to prevent fatigue.",
    "suggested_intervention": "Your focus tends to drop after about 40 minutes. Try a 5-minute break before starting another session.",
    "cached": false,
    "source": "gemini_ai"
  }
  ```

---

## 7. User Feedback Loop

### `POST /api/feedback`
- **Purpose**: Ingests user feedback on predictions (`helpful`, `not_helpful`, `was_actually_focused`, `was_distracted`, `dont_remind_again`).
- **Authentication**: Bearer JWT Token required.
- **Request Example**:
  ```json
  {
    "prediction_id": "pred_rec_01",
    "feedback_type": "helpful"
  }
  ```
- **Response Example (HTTP 201)**:
  ```json
  {
    "status": "recorded",
    "feedback": {
      "id": "fb_1",
      "prediction_id": "pred_rec_01",
      "user_id": "user_100",
      "feedback_type": "helpful",
      "timestamp": "2026-08-13T15:20:00Z"
    },
    "message": "Feedback recorded successfully. Production models will be updated in controlled offline retraining pipeline."
  }
  ```

---

## 8. User Privacy Data Rights

### `GET /api/privacy/export`
- **Purpose**: Downloads full `JSON` dump of user profile, privacy settings, focus sessions, and activity events.
- **Authentication**: Bearer JWT Token required.
- **Response**: File download `focusdna_user_export.json`.

### `POST /api/privacy/purge`
- **Purpose**: Permanently deletes all focus sessions and activity events owned by the user.
- **Authentication**: Bearer JWT Token required.
- **Response Example (HTTP 200)**:
  ```json
  {
    "status": "data_purged",
    "user_id": "user_100",
    "message": "Successfully deleted all activity events and sessions."
  }
  ```
