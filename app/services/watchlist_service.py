from typing import List, Optional
from sqlalchemy.orm import Session
from app.models import Provider, UserSubscription, WatchlistItem, Title
from app.schemas import (
    ProviderResponse,
    WatchlistItemResponse,
    WatchlistCreateRequest
)
from app.services.catalog_service import (
    format_title_response,
    get_user_active_subscriptions,
    get_user_watchlist_map
)

def get_all_providers(db: Session, user_id: str = "default_user") -> List[ProviderResponse]:
    providers = db.query(Provider).filter(Provider.is_active == True).order_by(Provider.display_priority).all()
    user_subs = get_user_active_subscriptions(db, user_id)

    response = []
    for p in providers:
        response.append(
            ProviderResponse(
                id=p.id,
                name=p.name,
                icon_url=p.icon_url,
                brand_color=p.brand_color,
                badge_bg=p.badge_bg,
                monthly_price_inr=p.monthly_price_inr or 199.0,
                is_active=p.is_active,
                display_priority=p.display_priority,
                is_subscribed=(p.id in user_subs)
            )
        )
    return response

def update_user_subscriptions(db: Session, provider_ids: List[str], user_id: str = "default_user") -> List[str]:
    # Delete existing user subscriptions
    db.query(UserSubscription).filter(UserSubscription.user_id == user_id).delete()
    
    for pid in provider_ids:
        # Validate provider exists
        prov = db.query(Provider).filter(Provider.id == pid).first()
        if prov:
            sub = UserSubscription(user_id=user_id, provider_id=pid, is_active=True)
            db.add(sub)
    db.commit()
    return provider_ids

def add_to_watchlist(db: Session, req: WatchlistCreateRequest, user_id: str = "default_user") -> Optional[WatchlistItemResponse]:
    title = db.query(Title).filter(Title.id == req.title_id).first()
    if not title:
        return None

    existing = db.query(WatchlistItem).filter(
        WatchlistItem.user_id == user_id,
        WatchlistItem.title_id == req.title_id
    ).first()

    if existing:
        existing.status = req.status
        db.commit()
        db.refresh(existing)
        item = existing
    else:
        item = WatchlistItem(
            user_id=user_id,
            title_id=req.title_id,
            status=req.status
        )
        db.add(item)
        db.commit()
        db.refresh(item)

    user_subs = get_user_active_subscriptions(db, user_id)
    watchlist_map = {req.title_id: item.status}
    title_resp = format_title_response(title, user_subs, watchlist_map)

    return WatchlistItemResponse(
        id=item.id,
        title_id=item.title_id,
        status=item.status,
        created_at=item.created_at,
        title=title_resp
    )

def remove_from_watchlist(db: Session, title_id: str, user_id: str = "default_user") -> bool:
    deleted = db.query(WatchlistItem).filter(
        WatchlistItem.user_id == user_id,
        WatchlistItem.title_id == title_id
    ).delete()
    db.commit()
    return deleted > 0

def get_user_watchlist(db: Session, user_id: str = "default_user") -> List[WatchlistItemResponse]:
    items = db.query(WatchlistItem).filter(
        WatchlistItem.user_id == user_id
    ).order_by(WatchlistItem.created_at.desc()).all()

    user_subs = get_user_active_subscriptions(db, user_id)
    watchlist_map = {item.title_id: item.status for item in items}

    results = []
    for item in items:
        if item.title:
            title_resp = format_title_response(item.title, user_subs, watchlist_map)
            results.append(
                WatchlistItemResponse(
                    id=item.id,
                    title_id=item.title_id,
                    status=item.status,
                    created_at=item.created_at,
                    title=title_resp
                )
            )
    return results
