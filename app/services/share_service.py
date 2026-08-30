import uuid
import json
import csv
import io
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from app.models import Title, WatchlistItem
from app.services.cache_service import cache
from app.services.catalog_service import format_title_response, get_user_active_subscriptions

def create_share_link(
    share_type: str,  # 'pick', 'couple', 'watchlist'
    payload: Dict[str, Any],
    ttl_seconds: int = 86400  # 24 hours default
) -> Dict[str, Any]:
    token = str(uuid.uuid4())[:8]  # Short 8-char token
    cache_key = f"share:{token}"
    
    data_to_store = {
        "token": token,
        "type": share_type,
        "payload": payload
    }
    cache.set(cache_key, data_to_store, ttl=ttl_seconds)

    return {
        "token": token,
        "share_url": f"/s/{token}",
        "share_type": share_type,
        "expires_in_seconds": ttl_seconds
    }

def get_shared_content(token: str) -> Optional[Dict[str, Any]]:
    cache_key = f"share:{token}"
    return cache.get(cache_key)

def export_watchlist_csv(db: Session, user_id: str = "default_user") -> str:
    items = db.query(WatchlistItem).filter(WatchlistItem.user_id == user_id).all()
    user_subs = get_user_active_subscriptions(db, user_id)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Title", "Type", "Release Year", "Runtime (Mins)", "IMDb Rating", "Genres", "Available Platforms", "Saved Status"
    ])

    for item in items:
        if item.title:
            t = item.title
            prov_names = ", ".join([tp.provider.name for tp in t.providers if tp.provider])
            writer.writerow([
                t.title,
                t.type,
                t.release_year,
                t.runtime_minutes,
                t.rating_imdb,
                t.genres,
                prov_names,
                item.status
            ])

    return output.getvalue()

def export_watchlist_json(db: Session, user_id: str = "default_user") -> List[Dict[str, Any]]:
    items = db.query(WatchlistItem).filter(WatchlistItem.user_id == user_id).all()
    user_subs = get_user_active_subscriptions(db, user_id)

    results = []
    for item in items:
        if item.title:
            t_resp = format_title_response(item.title, user_subs, {item.title.id: item.status})
            results.append({
                "id": item.id,
                "status": item.status,
                "created_at": str(item.created_at),
                "title": t_resp.model_dump()
            })
    return results
