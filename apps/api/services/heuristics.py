from typing import List, Dict, Any
from core.categories import category_registry

class FeatureAggregator:
    @staticmethod
    def aggregate_features(user_id: str, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Aggregates recent behavioral events into feature vectors.
        """
        total_duration = sum(e.get("session_duration", 0) for e in events)
        app_switches = sum(e.get("app_switch_count", 0) for e in events)
        browser_switches = sum(e.get("browser_switch_count", 0) for e in events)
        total_switches = app_switches + browser_switches
        notification_count = sum(e.get("notification_count", 0) for e in events)
        idle_seconds = sum(e.get("idle_seconds", 0) for e in events)

        social_media_duration = 0
        entertainment_duration = 0
        productive_duration = 0
        communication_duration = 0

        for e in events:
            domain = e.get("website_domain")
            app = e.get("application_name")
            dur = e.get("session_duration", 30)

            domain_cat = category_registry.get_domain_category(user_id, domain) if domain else None
            app_cat = category_registry.get_app_category(user_id, app) if app else None

            active_cat = domain_cat or app_cat or "neutral"

            if active_cat == "social_media":
                social_media_duration += dur
            elif active_cat == "entertainment":
                entertainment_duration += dur
            elif active_cat == "productive":
                productive_duration += dur
            elif active_cat == "communication":
                communication_duration += dur

        return {
            "session_duration": total_duration,
            "app_switches": app_switches,
            "browser_switches": browser_switches,
            "total_switches": total_switches,
            "notification_count": notification_count,
            "idle_seconds": idle_seconds,
            "social_media_duration": social_media_duration,
            "entertainment_duration": entertainment_duration,
            "productive_duration": productive_duration,
            "communication_duration": communication_duration,
            "event_count": len(events)
        }

class BehavioralHeuristicScorer:
    """
    Transparent Rule-Based Behavioral Focus Scorer.
    Explicitly labeled as 'Heuristic Focus Score' (NOT AI prediction).
    """

    @staticmethod
    def evaluate_focus_score(user_id: str, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        features = FeatureAggregator.aggregate_features(user_id, events)
        
        if not events or features["event_count"] == 0:
            return {
                "score_value": 85.0,
                "evaluation_type": "heuristic",
                "is_distracted": False,
                "features": features,
                "explanation": "[Heuristic Focus Score] No recent activity events recorded. Baseline focus score."
            }

        base_score = 100.0
        switch_penalty = 0.0
        social_penalty = 0.0
        entertainment_penalty = 0.0
        idle_penalty = 0.0
        notification_penalty = 0.0
        productive_bonus = 0.0

        switches = features["total_switches"]
        social_sec = features["social_media_duration"]
        entertainment_sec = features["entertainment_duration"]
        idle_sec = features["idle_seconds"]
        notifs = features["notification_count"]
        prod_sec = features["productive_duration"]

        # 1. Context Switching Penalty (Switches in window)
        if switches >= 8:
            switch_penalty = min(35.0, (switches - 3) * 3.0)
        elif switches >= 4:
            switch_penalty = (switches - 3) * 2.0

        # 2. Social Media & Entertainment Time Penalties
        if social_sec > 0:
            social_penalty = min(35.0, (social_sec / 30.0) * 5.0)

        if entertainment_sec > 0:
            entertainment_penalty = min(30.0, (entertainment_sec / 30.0) * 4.0)

        # 3. Idle Time Penalty
        if idle_sec > 180:
            idle_penalty = min(25.0, (idle_sec - 180) / 20.0)

        # 4. Notification Overload Penalty
        if notifs > 3:
            notification_penalty = min(20.0, (notifs - 3) * 4.0)

        # 5. Productive Bonus
        if prod_sec > 60:
            productive_bonus = min(15.0, (prod_sec / 60.0) * 3.0)

        final_score = base_score - switch_penalty - social_penalty - entertainment_penalty - idle_penalty - notification_penalty + productive_bonus
        final_score = max(0.0, min(100.0, final_score))

        is_distracted = final_score < 60.0

        # Construct explainable human-readable rationale
        reasons = []
        if switch_penalty > 5:
            reasons.append(f"switched contexts {switches} times in the recent window")
        if social_penalty > 5:
            reasons.append(f"spent {social_sec}s on social media domains")
        if entertainment_penalty > 5:
            reasons.append(f"spent {entertainment_sec}s on entertainment domains")
        if idle_penalty > 5:
            reasons.append(f"had {idle_sec}s of extended idle duration")
        if notification_penalty > 5:
            reasons.append(f"received {notifs} notifications")

        if final_score < 80.0 and reasons:
            explanation = f"[Heuristic Focus Score] Your score decreased because you {', and '.join(reasons)}."
        elif productive_bonus > 5:
            explanation = f"[Heuristic Focus Score] High focus sustained! Spent {prod_sec}s actively working on productive developer tools."
        else:
            explanation = "[Heuristic Focus Score] Steady behavioral focus pattern observed."

        return {
            "score_value": round(final_score, 1),
            "evaluation_type": "heuristic",
            "is_distracted": is_distracted,
            "features": features,
            "breakdown": {
                "base_score": base_score,
                "switch_penalty": round(switch_penalty, 1),
                "social_penalty": round(social_penalty, 1),
                "entertainment_penalty": round(entertainment_penalty, 1),
                "idle_penalty": round(idle_penalty, 1),
                "notification_penalty": round(notification_penalty, 1),
                "productive_bonus": round(productive_bonus, 1)
            },
            "explanation": explanation
        }
