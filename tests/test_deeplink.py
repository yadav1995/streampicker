from app.services.deeplink_service import (
    resolve_provider_deep_link,
    detect_device_from_user_agent
)

def test_detect_device_from_user_agent():
    assert detect_device_from_user_agent("Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)") == "ios"
    assert detect_device_from_user_agent("Mozilla/5.0 (Linux; Android 14; Pixel 8)") == "android"
    assert detect_device_from_user_agent("Mozilla/5.0 (Windows NT 10.0; Win64; x64)") == "web"
    assert detect_device_from_user_agent("Mozilla/5.0 (SMART-TV; Linux; Tizen 6.0)") == "tv"

def test_resolve_provider_deep_link():
    res_ios = resolve_provider_deep_link(
        provider_id="netflix",
        provider_name="Netflix",
        web_url="https://www.netflix.com/title/70131314",
        device="ios"
    )
    assert res_ios.device_type == "ios"
    assert "nflx://" in res_ios.resolved_uri or "netflix.com" in res_ios.fallback_web_url
    assert res_ios.target_action == "launch_app"

    res_web = resolve_provider_deep_link(
        provider_id="prime_video",
        provider_name="Amazon Prime Video",
        web_url="https://www.primevideo.com/detail/0I7C58O4",
        device="web"
    )
    assert res_web.device_type == "web"
    assert res_web.target_action == "open_browser"
