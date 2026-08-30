import uuid
import logging
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models import Title, TitleProvider, Provider
from app.services.tmdb_client import tmdb_client
from app.services.cache_service import cache

logger = logging.getLogger(__name__)

def sync_live_trending_titles(db: Session, max_titles: int = 10) -> Dict[str, Any]:
    trending_raw = tmdb_client.get_trending("day")
    synced_count = 0
    created_count = 0
    updated_count = 0

    for item in trending_raw[:max_titles]:
        media_type = item.get("media_type") or "movie"
        if media_type not in ["movie", "tv", "series"]:
            media_type = "movie"
        
        type_str = "movie" if media_type == "movie" else "series"
        tmdb_id = item.get("id")

        # Fetch detailed record if live client is configured, otherwise use item
        details = tmdb_client.get_title_details(tmdb_id, "movie" if type_str == "movie" else "tv")
        transformed = tmdb_client.transform_tmdb_item(details or item, type_str)

        # Check if already in DB
        existing = db.query(Title).filter(
            (Title.tmdb_id == str(tmdb_id)) | (Title.title.ilike(transformed["title"]))
        ).first()

        if existing:
            # Update rating and overview
            existing.rating_tmdb = transformed["rating_tmdb"]
            existing.rating_imdb = max(existing.rating_imdb, transformed["rating_imdb"])
            existing.overview = transformed["overview"]
            target_title = existing
            updated_count += 1
        else:
            # Create new title
            new_title = Title(
                id=str(uuid.uuid4()),
                tmdb_id=str(tmdb_id),
                title=transformed["title"],
                type=transformed["type"],
                runtime_minutes=transformed["runtime_minutes"],
                release_year=transformed["release_year"],
                genres=",".join(transformed["genres"]),
                mood_tags=",".join(transformed["mood_tags"]),
                director=transformed["director"],
                cast_members=",".join(transformed["cast_members"]),
                rating_imdb=transformed["rating_imdb"],
                rating_tmdb=transformed["rating_tmdb"],
                rating_rotten_tomatoes=transformed["rating_rotten_tomatoes"],
                overview=transformed["overview"],
                poster_url=transformed["poster_url"],
                backdrop_url=transformed["backdrop_url"]
            )
            db.add(new_title)
            db.flush()
            target_title = new_title
            created_count += 1

        # Upsert TitleProviders
        for p_info in transformed["providers"]:
            prov = db.query(Provider).filter(Provider.id == p_info["provider_id"]).first()
            if not prov:
                continue

            existing_tp = db.query(TitleProvider).filter(
                TitleProvider.title_id == target_title.id,
                TitleProvider.provider_id == prov.id
            ).first()

            if not existing_tp:
                new_tp = TitleProvider(
                    id=str(uuid.uuid4()),
                    title_id=target_title.id,
                    provider_id=prov.id,
                    access_type=p_info["access_type"],
                    price=p_info["price"],
                    currency=p_info["currency"],
                    web_url=p_info["web_url"],
                    deep_link=p_info["deep_link"]
                )
                db.add(new_tp)

        synced_count += 1

    db.commit()

    # Invalidate cache
    cache.clear_prefix("pick:")
    cache.clear_prefix("roi:")

    return {
        "status": "success",
        "synced_count": synced_count,
        "created_count": created_count,
        "updated_count": updated_count,
        "is_live_mode": tmdb_client.is_configured(),
        "source": "The Movie Database (TMDB)" if tmdb_client.is_configured() else "TMDB Simulation Engine"
    }
