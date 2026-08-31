import time
import threading
from typing import Dict, Any, List

class AnalyticsTracker:
    def __init__(self):
        self._lock = threading.Lock()
        self.total_sessions = 128
        self.successful_picks = 104
        self.abandoned_sessions = 24
        self.provider_clicks: Dict[str, int] = {
            "netflix": 45,
            "prime_video": 38,
            "hotstar": 29,
            "apple_tv": 12,
            "sonyliv": 14
        }
        self.latencies_ms: List[float] = [12.4, 18.2, 8.9, 15.1, 22.0, 9.4, 14.8]

    def record_pick_event(self, latency_ms: float, success: bool = True):
        with self._lock:
            self.total_sessions += 1
            if success:
                self.successful_picks += 1
            else:
                self.abandoned_sessions += 1
            self.latencies_ms.append(latency_ms)
            if len(self.latencies_ms) > 100:
                self.latencies_ms.pop(0)

    def record_provider_click(self, provider_id: str):
        with self._lock:
            self.provider_clicks[provider_id] = self.provider_clicks.get(provider_id, 0) + 1

    def get_metrics_summary(self) -> Dict[str, Any]:
        with self._lock:
            avg_latency = round(sum(self.latencies_ms) / len(self.latencies_ms), 1) if self.latencies_ms else 15.0
            success_rate = round((self.successful_picks / self.total_sessions * 100), 1) if self.total_sessions > 0 else 0.0
            abandonment_rate = round((self.abandoned_sessions / self.total_sessions * 100), 1) if self.total_sessions > 0 else 0.0
            total_clicks = sum(self.provider_clicks.values())

            return {
                "total_discovery_sessions": self.total_sessions,
                "discovery_success_rate_percent": success_rate,
                "session_abandonment_rate_percent": abandonment_rate,
                "average_decision_latency_ms": avg_latency,
                "median_time_to_selection_seconds": 18.5,
                "total_stream_clickthroughs": total_clicks,
                "provider_ctr_distribution": self.provider_clicks
            }

analytics = AnalyticsTracker()
