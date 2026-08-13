import os
import json
import time
import hashlib
import urllib.request
import urllib.error
from typing import Dict, Any, Optional

class GeminiRecommendationService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY", "")
        self.cache: Dict[str, Dict[str, Any]] = {} # Hash -> {response, timestamp}
        self.cache_ttl_seconds = 900 # 15 minutes TTL
        self.user_request_timestamps: Dict[str, list] = {} # user_id -> list of float timestamps
        self.rate_limit_max_per_min = 10

    def generate_recommendation(
        self,
        user_id: str,
        stats: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generates structured AI recommendations from aggregated telemetry stats.
        Includes rate limiting, caching, and graceful fallback handling.
        """
        # 1. Check Rate Limiting
        now = time.time()
        user_timestamps = [t for t in self.user_request_timestamps.get(user_id, []) if now - t < 60.0]
        if len(user_timestamps) >= self.rate_limit_max_per_min:
            return {
                "error": "Rate limit exceeded",
                "message": "Too many recommendation requests. Please try again in a minute.",
                "status_code": 429
            }
        user_timestamps.append(now)
        self.user_request_timestamps[user_id] = user_timestamps

        # 2. Check Cache
        stats_hash = hashlib.md5(f"{user_id}:{json.dumps(stats, sort_keys=True)}".encode()).hexdigest()
        cached = self.cache.get(stats_hash)
        if cached and (now - cached["timestamp"] < self.cache_ttl_seconds):
            res = dict(cached["data"])
            res["cached"] = True
            return res

        # 3. If API Key is present, attempt Gemini REST call
        if self.api_key:
            try:
                ai_response = self._call_gemini_api(stats)
                if ai_response:
                    ai_response["cached"] = False
                    ai_response["source"] = "gemini_ai"
                    self.cache[stats_hash] = {"data": ai_response, "timestamp": now}
                    return ai_response
            except Exception as e:
                print(f"[Gemini Service Warning] API call failed: {e}. Executing heuristic fallback.")

        # 4. Graceful Fallback
        fallback_res = self._build_heuristic_fallback(stats)
        fallback_res["cached"] = False
        fallback_res["source"] = "heuristic_fallback"
        self.cache[stats_hash] = {"data": fallback_res, "timestamp": now}
        return fallback_res

    def _call_gemini_api(self, stats: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.api_key}"
        
        prompt = f"""You are FocusDNA AI, an expert behavioral attention coach.
Analyze the following structured user focus statistics and generate a concise response in JSON format.

STRUCTURED USER STATISTICS:
- Average focus session duration: {stats.get('average_focus_session', 35)} minutes
- Common distraction period: {stats.get('common_distraction_period', '2:00 PM - 4:00 PM')}
- Average context switches per window: {stats.get('average_switches', 3.5)}
- Top distraction trigger category: {stats.get('top_trigger', 'Social Media')}
- Recent behavioral anomaly detected: {stats.get('recent_anomaly', False)}
- Focus trend: {stats.get('focus_trend', 'stable')}

REQUIRED JSON OUTPUT FORMAT:
{{
  "explanation": "Short 1-2 sentence explanation of the pattern.",
  "recommendation": "Personalized action suggestion.",
  "suggested_intervention": "Concrete time-boxed intervention."
}}

Example:
"Your focus tends to drop after about 40 minutes. Try a 5-minute break before starting another session."
Only output valid JSON."""

        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": 0.3,
                "response_mime_type": "application/json"
            }
        }

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )

        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status == 200:
                res_body = json.loads(response.read().decode('utf-8'))
                text_content = res_body['candidates'][0]['content']['parts'][0]['text']
                parsed = json.loads(text_content)
                return {
                    "explanation": parsed.get("explanation", ""),
                    "recommendation": parsed.get("recommendation", ""),
                    "suggested_intervention": parsed.get("suggested_intervention", "")
                }
        return None

    def _build_heuristic_fallback(self, stats: Dict[str, Any]) -> Dict[str, Any]:
        avg_mins = int(stats.get("average_focus_session", 35))
        dist_period = stats.get("common_distraction_period", "2:00 PM – 4:00 PM")
        trigger = stats.get("top_trigger", "Social Media")

        explanation = f"Your focus tends to decline after about {avg_mins} minutes of continuous session work, particularly around {dist_period}."
        recommendation = f"Schedule a structured 5-minute break before the {avg_mins}-minute mark to prevent fatigue."
        suggested_intervention = f"Your focus tends to drop after about {avg_mins} minutes. Try a 5-minute break before starting another session, and block {trigger} domains during peak focus hours."

        return {
            "explanation": explanation,
            "recommendation": recommendation,
            "suggested_intervention": suggested_intervention
        }

gemini_service = GeminiRecommendationService()
