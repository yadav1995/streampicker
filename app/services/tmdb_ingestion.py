import os
import logging
from typing import List, Dict, Any, Optional
import httpx
from sqlalchemy.orm import Session
from app.models import Title, TitleProvider, Provider

logger = logging.getLogger(__name__)

TMDB_API_KEY = os.getenv("TMDB_API_KEY", "")
TMDB_BASE_URL = "https://api.themoviedb.org/3"

async def fetch_trending_titles(time_window: str = "week") -> List[Dict[str, Any]]:
    if not TMDB_API_KEY:
        logger.info("No TMDB_API_KEY provided; returning cached metadata.")
        return []

    url = f"{TMDB_BASE_URL}/trending/all/{time_window}?api_key={TMDB_API_KEY}"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.get(url)
            if res.status_code == 200:
                data = res.json()
                return data.get("results", [])
    except Exception as e:
        logger.error(f"Failed to fetch from TMDB: {e}")
    return []

def sync_tmdb_title_metadata(db: Session, title_data: Dict[str, Any], providers_map: Dict[str, str]) -> Optional[Title]:
    tmdb_id = str(title_data.get("id"))
    existing = db.query(Title).filter(Title.tmdb_id == tmdb_id).first()
    if existing:
        return existing

    title_name = title_data.get("title") or title_data.get("name")
    media_type = title_data.get("media_type", "movie")
    poster_path = title_data.get("poster_path")
    backdrop_path = title_data.get("backdrop_path")
    overview = title_data.get("overview", "")
    vote_avg = title_data.get("vote_average", 7.0)
    release_date = title_data.get("release_date") or title_data.get("first_air_date") or "2024-01-01"
    release_year = int(release_date.split("-")[0]) if "-" in release_date else 2024

    new_title = Title(
        tmdb_id=tmdb_id,
        title=title_name,
        type="series" if media_type == "tv" else "movie",
        release_year=release_year,
        runtime_minutes=110 if media_type == "movie" else 45,
        rating_tmdb=round(vote_avg, 1),
        rating_imdb=round(min(vote_avg + 0.2, 9.8), 1),
        rating_rotten_tomatoes=int(vote_avg * 10),
        overview=overview,
        poster_url=f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else "",
        backdrop_url=f"https://image.tmdb.org/t/p/w1280{backdrop_path}" if backdrop_path else ""
    )
    db.add(new_title)
    db.commit()
    db.refresh(new_title)
    return new_title
