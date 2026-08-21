"""
FocusDNA AI — Data Quality Pipeline (Phase 3)
Validates telemetry events and session metadata before dataset construction.
"""

from typing import Dict, Any, List, Tuple
import pandas as pd
import numpy as np

class DataQualityValidator:
    @staticmethod
    def validate_session_telemetry(
        telemetry_events: List[Dict[str, Any]],
        session_meta: Dict[str, Any] = None
    ) -> Tuple[bool, List[str]]:
        """
        Validates raw telemetry events and session metadata.
        Returns (is_valid, list_of_quality_issues).
        """
        issues = []

        if not telemetry_events and not session_meta:
            return False, ["No telemetry events or session metadata provided."]

        planned = float((session_meta or {}).get("planned_duration_minutes", 25))
        actual = float((session_meta or {}).get("actual_duration_minutes", 0))

        if planned < 1 or planned > 300:
            issues.append(f"Invalid planned duration: {planned}m")

        if actual < 0 or actual > 300:
            issues.append(f"Invalid actual duration: {actual}m")

        # Check telemetry event sanity
        seen_event_ids = set()
        for idx, event in enumerate(telemetry_events):
            eid = event.get("id")
            if eid:
                if eid in seen_event_ids:
                    issues.append(f"Duplicate telemetry event ID detected: {eid}")
                seen_event_ids.add(eid)

            dur = float(event.get("session_duration", 0))
            if dur < 0 or dur > 86400:
                issues.append(f"Event #{idx}: Impossible session duration {dur}s")

            idle = float(event.get("idle_seconds", 0))
            if idle < 0 or idle > 86400:
                issues.append(f"Event #{idx}: Negative or extreme idle seconds {idle}s")

            switches = int(event.get("browser_switch_count", 0)) + int(event.get("app_switch_count", 0))
            if switches < 0 or switches > 5000:
                issues.append(f"Event #{idx}: Out-of-bounds switch count {switches}")

        is_valid = len(issues) == 0
        return is_valid, issues

    @staticmethod
    def generate_quality_report(sessions_dataset: pd.DataFrame) -> Dict[str, Any]:
        """
        Produces summary dataset quality audit report.
        """
        total_rows = len(sessions_dataset)
        if total_rows == 0:
            return {
                "total_rows": 0,
                "passed": False,
                "missing_values_count": 0,
                "duplicate_session_ids": 0,
                "summary": "Empty dataset."
            }

        missing_count = int(sessions_dataset.isnull().sum().sum())
        dup_sessions = int(sessions_dataset.duplicated(subset=["focus_session_id"]).sum()) if "focus_session_id" in sessions_dataset.columns else 0

        return {
            "total_rows": total_rows,
            "passed": missing_count == 0 and dup_sessions == 0,
            "missing_values_count": missing_count,
            "duplicate_session_ids": dup_sessions,
            "columns": list(sessions_dataset.columns),
            "summary": f"Dataset contains {total_rows} sessions. Missing values: {missing_count}, Duplicate session IDs: {dup_sessions}."
        }
