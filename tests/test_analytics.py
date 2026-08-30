from app.services.analytics_service import AnalyticsTracker

def test_analytics_tracker_recording():
    tracker = AnalyticsTracker()
    tracker.record_pick_event(latency_ms=14.5, success=True)
    tracker.record_provider_click("netflix")
    
    summary = tracker.get_metrics_summary()
    assert summary["total_discovery_sessions"] > 0
    assert summary["discovery_success_rate_percent"] > 0
    assert summary["average_decision_latency_ms"] > 0
    assert summary["provider_ctr_distribution"]["netflix"] > 0
