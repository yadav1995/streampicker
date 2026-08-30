import httpx
import logging
from typing import Dict, Any, List, Optional
from app.config import settings

logger = logging.getLogger(__name__)

TMDB_PROVIDER_MAP = {
    8: ("netflix", "Netflix", "#E50914"),
    119: ("prime_video", "Amazon Prime Video", "#00A8E1"),
    122: ("hotstar", "Disney+ Hotstar", "#00143E"),
    220: ("jiocinema", "JioCinema", "#E5007D"),
    350: ("apple_tv", "Apple TV+", "#000000"),
    237: ("sonyliv", "SonyLIV", "#2D2D2D"),
    232: ("zee5", "ZEE5", "#8E24AA")
}

GENRE_MOOD_MAP = {
    "Science Fiction": "Mind-Bending",
    "Action": "Adrenaline Rush",
    "Comedy": "Hilarious Comedy",
    "Drama": "Feel-Good & Uplifting",
    "Thriller": "Dark & Gritty",
    "Mystery": "Late-Night Mystery",
    "Romance": "Date Night",
    "Animation": "Feel-Good & Uplifting",
    "Crime": "Dark & Gritty"
}

class TMDBClient:
    def __init__(self, api_key: Optional[str] = None, read_token: Optional[str] = None):
        self.api_key = api_key or settings.TMDB_API_KEY
        self.read_token = read_token or settings.TMDB_READ_ACCESS_TOKEN
        self.base_url = "https://api.themoviedb.org/3"
        self.image_base_url = "https://image.tmdb.org/t/p/original"
        self.region = settings.TMDB_DEFAULT_REGION

    def is_configured(self) -> bool:
        return bool(self.api_key or self.read_token)

    def _get_headers(self) -> Dict[str, str]:
        headers = {"Accept": "application/json"}
        if self.read_token:
            headers["Authorization"] = f"Bearer {self.read_token}"
        return headers

    def _get_params(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        p = params.copy() if params else {}
        if self.api_key and not self.read_token:
            p["api_key"] = self.api_key
        return p

    def get_trending(self, time_window: str = "day") -> List[Dict[str, Any]]:
        if not self.is_configured():
            # Return demo trending titles if key not configured
            return self._get_mock_trending()

        url = f"{self.base_url}/trending/all/{time_window}"
        try:
            with httpx.Client(timeout=10.0) as client:
                res = client.get(url, headers=self._get_headers(), params=self._get_params())
                if res.status_code == 200:
                    return res.json().get("results", [])
                logger.error(f"TMDB API error: {res.status_code} - {res.text}")
                return []
        except Exception as e:
            logger.error(f"TMDB API exception: {e}")
            return []

    def get_title_details(self, tmdb_id: int, media_type: str = "movie") -> Optional[Dict[str, Any]]:
        if not self.is_configured():
            return None

        url = f"{self.base_url}/{media_type}/{tmdb_id}"
        params = self._get_params({"append_to_response": "watch/providers,credits,videos"})
        try:
            with httpx.Client(timeout=10.0) as client:
                res = client.get(url, headers=self._get_headers(), params=params)
                if res.status_code == 200:
                    return res.json()
                return None
        except Exception as e:
            logger.error(f"TMDB get_title_details failed: {e}")
            return None

    def transform_tmdb_item(self, data: Dict[str, Any], media_type: str = "movie") -> Dict[str, Any]:
        title_name = data.get("title") or data.get("name") or "Untitled"
        release_date = data.get("release_date") or data.get("first_air_date") or "2024-01-01"
        release_year = int(release_date.split("-")[0]) if release_date else 2024
        
        runtime = data.get("runtime") or (data.get("episode_run_time", [45])[0] if data.get("episode_run_time") else 110)
        
        genres_list = [g.get("name") for g in data.get("genres", []) if g.get("name")]
        if not genres_list and "genre_ids" in data:
            genres_list = ["Drama", "Action"]

        # Derive mood tags
        moods = [GENRE_MOOD_MAP[g] for g in genres_list if g in GENRE_MOOD_MAP]
        if not moods:
            moods = ["Feel-Good & Uplifting"]

        # Credits
        credits = data.get("credits", {})
        director = "Director"
        for crew in credits.get("crew", []):
            if crew.get("job") == "Director":
                director = crew.get("name")
                break
        
        cast = [c.get("name") for c in credits.get("cast", [])[:4] if c.get("name")]

        # Ratings
        tmdb_vote = data.get("vote_average", 7.5)
        imdb_est = round(float(tmdb_vote), 1)

        # Watch Providers
        providers = []
        wp_data = data.get("watch/providers", {}).get("results", {}).get(self.region, {})
        
        flatrate = wp_data.get("flatrate", [])
        for p in flatrate:
            pid = p.get("provider_id")
            if pid in TMDB_PROVIDER_MAP:
                slug, name, color = TMDB_PROVIDER_MAP[pid]
                providers.append({
                    "provider_id": slug,
                    "access_type": "flatrate",
                    "price": None,
                    "currency": "INR",
                    "web_url": f"https://www.{slug.replace('_', '')}.com",
                    "deep_link": f"{slug}://title/{data.get('id')}"
                })

        rent = wp_data.get("rent", [])
        for p in rent:
            pid = p.get("provider_id")
            if pid in TMDB_PROVIDER_MAP:
                slug, name, color = TMDB_PROVIDER_MAP[pid]
                providers.append({
                    "provider_id": slug,
                    "access_type": "rent",
                    "price": 120.0,
                    "currency": "INR",
                    "web_url": f"https://www.{slug.replace('_', '')}.com",
                    "deep_link": f"{slug}://title/{data.get('id')}"
                })

        # Default fallback provider if empty
        if not providers:
            providers.append({
                "provider_id": "netflix",
                "access_type": "flatrate",
                "price": None,
                "currency": "INR",
                "web_url": f"https://www.netflix.com/title/{data.get('id')}",
                "deep_link": f"nflx://title/{data.get('id')}"
            })

        poster_path = data.get("poster_path")
        backdrop_path = data.get("backdrop_path")
        
        poster_url = f"{self.image_base_url}{poster_path}" if poster_path else "https://images.unsplash.com/photo-1536440136628-849c177e76a1?w=800&q=80"
        backdrop_url = f"{self.image_base_url}{backdrop_path}" if backdrop_path else "https://images.unsplash.com/photo-1518173946687-a4c8a383392e?w=1200&q=80"

        return {
            "tmdb_id": str(data.get("id")),
            "title": title_name,
            "type": media_type,
            "runtime_minutes": runtime,
            "release_year": release_year,
            "genres": genres_list,
            "mood_tags": moods,
            "director": director,
            "cast_members": cast,
            "rating_imdb": imdb_est,
            "rating_tmdb": round(float(tmdb_vote), 1),
            "rating_rotten_tomatoes": int(tmdb_vote * 10),
            "overview": data.get("overview") or "No overview available.",
            "poster_url": poster_url,
            "backdrop_url": backdrop_url,
            "providers": providers
        }

    def _get_mock_trending(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": 99901,
                "title": "Dune: Part Two",
                "media_type": "movie",
                "release_date": "2024-03-01",
                "runtime": 166,
                "genres": [{"name": "Science Fiction"}, {"name": "Action"}],
                "vote_average": 8.6,
                "overview": "Paul Atreides unites with Chani and the Fremen while seeking revenge against the conspirators who destroyed his family.",
                "poster_path": "/1pdfLvkbY9ohJlCjQH2CZjjYVvJ.jpg",
                "backdrop_path": "/xOMo8BRK7PfcJv9JCnx7s520b2.jpg"
            },
            {
                "id": 99902,
                "title": "Fallout",
                "media_type": "series",
                "first_air_date": "2024-04-10",
                "episode_run_time": [55],
                "genres": [{"name": "Action"}, {"name": "Science Fiction"}],
                "vote_average": 8.4,
                "overview": "In a future, post-apocalyptic Los Angeles brought about by nuclear decimation, citizens must live in underground bunkers to protect themselves.",
                "poster_path": "/AnsikBEWF6ikv9cQzD5r5xRerxS.jpg",
                "backdrop_path": "/mo2BffL2D9bY9ohJlCjQH2CZjj.jpg"
            }
        ]

tmdb_client = TMDBClient()
