from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models import WatchlistItem, Title, TitleProvider
from app.services.catalog_service import get_user_active_subscriptions

def get_user_alerts(db: Session, user_id: str = "default_user") -> List[Dict[str, Any]]:
    user_subs = get_user_active_subscriptions(db, user_id)
    watchlist_items = db.query(WatchlistItem).filter(
        WatchlistItem.user_id == user_id,
        WatchlistItem.status.in_(["saved", "watching"])
    ).all()

    alerts = []
    for item in watchlist_items:
        t = item.title
        if not t:
            continue

        # Check for free subscription availability
        for tp in t.providers:
            prov = tp.provider
            if prov and prov.id in user_subs and tp.access_type in ["flatrate", "free"]:
                alerts.append({
                    "id": f"alert-free-{t.id}-{prov.id}",
                    "type": "availability",
                    "title_id": t.id,
                    "title_name": t.title,
                    "provider_name": prov.name,
                    "poster_url": t.poster_url,
                    "message": f"'{t.title}' is now included FREE in your active {prov.name} subscription!",
                    "action_url": tp.deep_link or tp.web_url,
                    "severity": "success"
                })

            # Check for rental price drop
            elif tp.access_type == "rent" and tp.price and tp.price < 120.0:
                alerts.append({
                    "id": f"alert-price-{t.id}-{tp.provider_id}",
                    "type": "price_drop",
                    "title_id": t.id,
                    "title_name": t.title,
                    "provider_name": prov.name if prov else "Store",
                    "poster_url": t.poster_url,
                    "message": f"Price drop! Rent '{t.title}' on {prov.name if prov else 'Store'} for only ₹{tp.price}.",
                    "action_url": tp.deep_link or tp.web_url,
                    "severity": "info"
                })

    return alerts
