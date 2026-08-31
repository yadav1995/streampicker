import httpx
import logging
from typing import Dict, Any, List, Optional
from app.config import settings

logger = logging.getLogger(__name__)

WATCHMODE_SOURCE_MAP = {
    "netflix": "netflix",
    "amazon_prime": "prime_video",
    "disney_plus": "hotstar",
    "apple_tv_plus": "apple_tv",
    "sonyliv": "sonyliv",
    "zee5": "zee5"
}

class WatchmodeClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.WATCHMODE_API_KEY
        self.base_url = "https://api.watchmode.com/v1"

    def is_configured(self) -> bool:
        return bool(self.api_key)

    def get_title_sources(self, watchmode_title_id: int) -> List[Dict[str, Any]]:
        if not self.is_configured():
            return []

        url = f"{self.base_url}/title/{watchmode_title_id}/sources/"
        params = {"apiKey": self.api_key, "regions": "IN"}
        try:
            with httpx.Client(timeout=10.0) as client:
                res = client.get(url, params=params)
                if res.status_code == 200:
                    return res.json()
                return []
        except Exception as e:
            logger.error(f"Watchmode API error: {e}")
            return []

watchmode_client = WatchmodeClient()
