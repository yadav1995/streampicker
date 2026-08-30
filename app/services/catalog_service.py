from typing import List, Set, Optional, Dict
from sqlalchemy.orm import Session
from app.models import Title, TitleProvider, Provider, UserSubscription, WatchlistItem
from app.schemas import TitleResponse, TitleProviderInfo

def split_comma_field(field_str: Optional[str]) -> List[str]:
    if not field_str:
        return []
    return [item.strip() for item in field_str.split(",") if item.strip()]

def get_user_active_subscriptions(db: Session, user_id: str = "default_user") -> Set[str]:
    subs = db.query(UserSubscription.provider_id).filter(
        UserSubscription.user_id == user_id,
        UserSubscription.is_active == True
    ).all()
    return {s[0] for s in subs}

def get_user_watchlist_map(db: Session, user_id: str = "default_user") -> Dict[str, str]:
    items = db.query(WatchlistItem.title_id, WatchlistItem.status).filter(
        WatchlistItem.user_id == user_id
    ).all()
    return {item[0]: item[1] for item in items}

def format_title_response(
    title: Title,
    user_subscriptions: Optional[Set[str]] = None,
    watchlist_map: Optional[Dict[str, str]] = None
) -> TitleResponse:
    if user_subscriptions is None:
        user_subscriptions = set()
    if watchlist_map is None:
        watchlist_map = {}

    providers_info: List[TitleProviderInfo] = []
    for tp in title.providers:
        prov = tp.provider
        if prov and prov.is_active:
            is_sub = prov.id in user_subscriptions and tp.access_type in ["flatrate", "free", "ads"]
            providers_info.append(
                TitleProviderInfo(
                    provider_id=prov.id,
                    provider_name=prov.name,
                    provider_icon=prov.icon_url,
                    brand_color=prov.brand_color,
                    access_type=tp.access_type,
                    price=tp.price,
                    currency=tp.currency,
                    web_url=tp.web_url,
                    deep_link=tp.deep_link,
                    is_in_user_subscription=is_sub
                )
            )

    # Sort providers so subscribed ones come first
    providers_info.sort(key=lambda p: (not p.is_in_user_subscription, p.access_type != "flatrate"))

    is_saved = title.id in watchlist_map
    wl_status = watchlist_map.get(title.id)

    return TitleResponse(
        id=title.id,
        tmdb_id=title.tmdb_id,
        imdb_id=title.imdb_id,
        title=title.title,
        type=title.type,
        runtime_minutes=title.runtime_minutes,
        release_year=title.release_year,
        genres=split_comma_field(title.genres),
        mood_tags=split_comma_field(title.mood_tags),
        director=title.director or "",
        cast_members=split_comma_field(title.cast_members),
        rating_imdb=title.rating_imdb,
        rating_tmdb=title.rating_tmdb,
        rating_rotten_tomatoes=title.rating_rotten_tomatoes,
        overview=title.overview or "",
        poster_url=title.poster_url or "",
        backdrop_url=title.backdrop_url or "",
        trailer_url=title.trailer_url or "",
        providers=providers_info,
        is_in_watchlist=is_saved,
        watchlist_status=wl_status
    )
