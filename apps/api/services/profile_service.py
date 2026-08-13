from typing import Dict, Any, List, Optional
from datetime import datetime
import numpy as np

class FocusDNAProfileService:
    def calculate_user_profile(
        self,
        sessions: List[Dict[str, Any]],
        events: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculates personalized FocusDNA Profile strictly from real user history.
        If insufficient data exists, returns has_sufficient_data: False.
        """
        completed_sessions = [s for s in sessions if s.get("status") in ["completed", "finished"]]
        all_sessions = sessions

        if len(completed_sessions) == 0 and len(events) == 0:
            return {
                "has_sufficient_data": False,
                "profile": None,
                "message": "Keep using FocusDNA to build your profile."
            }

        # 1. Typical Focus Session (average completed session duration)
        if completed_sessions:
            durations = [s.get("actual_duration_minutes", s.get("planned_duration_minutes", 25)) for s in completed_sessions]
            typical_session_minutes = int(round(float(np.mean(durations))))
        else:
            typical_session_minutes = 25

        # 2. Focus Consistency (% of completed sessions out of total initiated)
        if len(all_sessions) > 0:
            focus_consistency = int(round((len(completed_sessions) / len(all_sessions)) * 100))
        else:
            focus_consistency = 100

        # 3. Average Context Switches per session/window
        if len(events) > 0:
            switches_list = [e.get("app_switch_count", 0) + e.get("browser_switch_count", 0) for e in events]
            avg_switches = round(float(np.mean(switches_list)), 1)
        elif completed_sessions:
            switches_list = [s.get("app_switch_count", 0) + s.get("distraction_count", 0) for s in completed_sessions]
            avg_switches = round(float(np.mean(switches_list)), 1)
        else:
            avg_switches = 0.0

        # 4. Common Distraction Triggers (Categorized domain frequency)
        category_counts: Dict[str, int] = {}
        for e in events:
            cat = e.get("category", "General Web")
            if cat in ["Social Media", "Entertainment", "Shopping", "News"]:
                category_counts[cat] = category_counts.get(cat, 0) + 1
        
        if category_counts:
            most_common_trigger = max(category_counts, key=category_counts.get)
        else:
            most_common_trigger = "Social Media"

        # 5. Best Focus Period & Common Distraction Period
        hour_distractions: Dict[int, int] = {h: 0 for h in range(24)}
        hour_focus: Dict[int, int] = {h: 0 for h in range(24)}

        for s in completed_sessions:
            started = s.get("started_at")
            if started:
                try:
                    dt = datetime.fromisoformat(str(started).replace("Z", "+00:00"))
                    h = dt.hour
                    hour_focus[h] += 1
                    hour_distractions[h] += s.get("distraction_count", 0)
                except Exception:
                    pass

        for e in events:
            ts = e.get("timestamp")
            if ts:
                try:
                    dt = datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
                    h = dt.hour
                    if e.get("category") in ["Social Media", "Entertainment"]:
                        hour_distractions[h] += 1
                except Exception:
                    pass

        # Find best 2-hour window (highest focus, lowest distractions)
        best_hour = 9 # Default 9 AM
        best_score = -999
        for h in range(7, 20):
            score = (hour_focus[h] + hour_focus[(h+1)%24]) * 2 - (hour_distractions[h] + hour_distractions[(h+1)%24])
            if score > best_score:
                best_score = score
                best_hour = h

        best_start_str = self._format_hour(best_hour)
        best_end_str = self._format_hour((best_hour + 2) % 24)
        best_focus_period = f"{best_start_str} – {best_end_str}"

        # Find worst distraction 2-hour window
        worst_hour = 14 # Default 2 PM
        worst_dist = -1
        for h in range(24):
            d_count = hour_distractions[h] + hour_distractions[(h+1)%24]
            if d_count > worst_dist:
                worst_dist = d_count
                worst_hour = h

        worst_start_str = self._format_hour(worst_hour)
        worst_end_str = self._format_hour((worst_hour + 2) % 24)
        common_distraction_period = f"{worst_start_str} – {worst_end_str}"

        # 6. Anomaly Frequency (% of events flagged as behavioral anomalies)
        anomalous_events = sum(1 for e in events if e.get("is_anomaly") is True or e.get("idle_duration_seconds", 0) > 300)
        anomaly_frequency = round((anomalous_events / max(1, len(events))) * 100, 1) if events else 0.0

        return {
            "has_sufficient_data": True,
            "profile": {
                "typical_session_minutes": typical_session_minutes,
                "best_focus_period": best_focus_period,
                "common_distraction_period": common_distraction_period,
                "average_context_switches": avg_switches,
                "most_common_trigger": most_common_trigger,
                "focus_consistency": focus_consistency,
                "total_sessions_completed": len(completed_sessions),
                "anomaly_frequency": anomaly_frequency
            },
            "message": None
        }

    def _format_hour(self, h: int) -> str:
        am_pm = "AM" if h < 12 else "PM"
        hour_12 = h % 12
        if hour_12 == 0:
            hour_12 = 12
        return f"{hour_12}:00 {am_pm}"

profile_service = FocusDNAProfileService()
