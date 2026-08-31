import re
from typing import Dict, Any, Optional
from pydantic import BaseModel

class DeviceDeepLink(BaseModel):
    device_type: str  # 'ios', 'android', 'web', 'tv'
    resolved_uri: str
    fallback_web_url: str
    provider_id: str
    provider_name: str
    target_action: str  # 'launch_app' or 'open_browser'

PROVIDER_URI_TEMPLATES = {
    "netflix": {
        "ios": "nflx://title/{id}",
        "android": "nflx://title/{id}",
        "web": "https://www.netflix.com/title/{id}",
        "tv": "netflix://title/{id}"
    },
    "prime_video": {
        "ios": "primevideo://detail?asin={id}",
        "android": "primevideo://detail?asin={id}",
        "web": "https://www.primevideo.com/detail/{id}",
        "tv": "primevideo://detail?asin={id}"
    },
    "hotstar": {
        "ios": "hotstar://movies/{id}",
        "android": "hotstar://movies/{id}",
        "web": "https://www.hotstar.com/in/movies/{id}",
        "tv": "hotstar://movies/{id}"
    },
    "apple_tv": {
        "ios": "appletv://movie/{id}",
        "android": "appletv://movie/{id}",
        "web": "https://tv.apple.com/in/movie/{id}",
        "tv": "appletv://movie/{id}"
    },
    "sonyliv": {
        "ios": "sonyliv://content/movie/{id}",
        "android": "sonyliv://content/movie/{id}",
        "web": "https://www.sonyliv.com/movies/{id}",
        "tv": "sonyliv://content/movie/{id}"
    },
    "zee5": {
        "ios": "zee5://content/movie/{id}",
        "android": "zee5://content/movie/{id}",
        "web": "https://www.zee5.com/movies/{id}",
        "tv": "zee5://content/movie/{id}"
    }
}

def detect_device_from_user_agent(user_agent: Optional[str]) -> str:
    if not user_agent:
        return "web"
    ua = user_agent.lower()
    if "iphone" in ua or "ipad" in ua or "ipod" in ua:
        return "ios"
    elif "android" in ua:
        return "android"
    elif "smart-tv" in ua or "tizen" in ua or "webos" in ua or "appletv" in ua or "googletv" in ua:
        return "tv"
    return "web"

def resolve_provider_deep_link(
    provider_id: str,
    provider_name: str,
    web_url: str,
    existing_deep_link: Optional[str] = None,
    device: Optional[str] = None,
    user_agent: Optional[str] = None
) -> DeviceDeepLink:
    target_device = device.lower() if device and device in ["ios", "android", "web", "tv"] else detect_device_from_user_agent(user_agent)

    # If an existing deep link is already stored and device is mobile/tv
    if target_device in ["ios", "android", "tv"] and existing_deep_link:
        resolved_uri = existing_deep_link
        action = "launch_app"
    elif target_device == "web":
        resolved_uri = web_url or existing_deep_link
        action = "open_browser"
    else:
        # Generate from template if available
        templates = PROVIDER_URI_TEMPLATES.get(provider_id.lower(), {})
        template = templates.get(target_device) or templates.get("web") or web_url
        
        # Extract title id from web_url if possible
        extracted_id = web_url.rstrip("/").split("/")[-1] if web_url else "12345"
        resolved_uri = template.format(id=extracted_id) if "{id}" in template else template
        action = "launch_app" if target_device in ["ios", "android", "tv"] else "open_browser"

    return DeviceDeepLink(
        device_type=target_device,
        resolved_uri=resolved_uri,
        fallback_web_url=web_url,
        provider_id=provider_id,
        provider_name=provider_name,
        target_action=action
    )
