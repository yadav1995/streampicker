from typing import List, Optional, Set
from sqlalchemy.orm import Session
from app.models import Provider, UserSubscription, Title, TitleProvider, WatchlistItem
from app.schemas import (
    SubscriptionROIResponse,
    RedundancyCheckResponse,
    ProviderResponse,
    TitleProviderInfo
)
from app.services.catalog_service import get_user_active_subscriptions

def calculate_subscription_roi(
    db: Session,
    user_id: str = "default_user"
) -> SubscriptionROIResponse:
    user_subs = get_user_active_subscriptions(db, user_id)
    all_providers = db.query(Provider).filter(Provider.is_active == True).all()

    active_provider_models = [p for p in all_providers if p.id in user_subs]
    total_monthly_spend = sum(p.monthly_price_inr for p in active_provider_models)

    # Total catalog count
    total_titles_count = db.query(Title).count()

    # Titles accessible for free/flatrate with active subscriptions
    if user_subs:
        accessible_titles_count = db.query(Title.id).join(Title.providers).filter(
            TitleProvider.provider_id.in_(user_subs),
            TitleProvider.access_type.in_(["flatrate", "free", "ads"])
        ).distinct().count()
    else:
        accessible_titles_count = 0

    coverage_pct = round((accessible_titles_count / total_titles_count * 100), 1) if total_titles_count > 0 else 0.0

    # Watched count in watchlist
    watched_count = db.query(WatchlistItem).filter(
        WatchlistItem.user_id == user_id,
        WatchlistItem.status == "watched"
    ).count()

    cost_per_watched = round(total_monthly_spend / max(watched_count, 1), 1)

    # Identify underutilized subscriptions
    underutilized = []
    for p in active_provider_models:
        titles_on_p = db.query(TitleProvider).filter(
            TitleProvider.provider_id == p.id,
            TitleProvider.access_type.in_(["flatrate", "free"])
        ).count()
        if titles_on_p < 2:
            underutilized.append(p.name)

    active_provider_responses = [
        ProviderResponse(
            id=p.id,
            name=p.name,
            icon_url=p.icon_url,
            brand_color=p.brand_color,
            badge_bg=p.badge_bg,
            monthly_price_inr=p.monthly_price_inr,
            is_active=p.is_active,
            display_priority=p.display_priority,
            is_subscribed=True
        )
        for p in active_provider_models
    ]

    return SubscriptionROIResponse(
        total_monthly_spend_inr=total_monthly_spend,
        active_subscriptions_count=len(user_subs),
        active_providers=active_provider_responses,
        accessible_catalog_count=accessible_titles_count,
        total_catalog_count=total_titles_count,
        catalog_coverage_percent=coverage_pct,
        estimated_cost_per_title_watched=cost_per_watched,
        underutilized_subscriptions=underutilized
    )

def check_title_redundancy(
    db: Session,
    title_id: str,
    user_id: str = "default_user"
) -> RedundancyCheckResponse:
    title = db.query(Title).filter(Title.id == title_id).first()
    if not title:
        return RedundancyCheckResponse(
            title_id=title_id,
            title_name="Unknown",
            is_redundant=False,
            redundancy_message="Title not found"
        )

    user_subs = get_user_active_subscriptions(db, user_id)

    # Check if there is a paid option (rent / buy)
    paid_tp = None
    free_providers = []

    for tp in title.providers:
        prov = tp.provider
        if not prov:
            continue
        if tp.access_type in ["rent", "buy"] and not paid_tp:
            paid_tp = TitleProviderInfo(
                provider_id=prov.id,
                provider_name=prov.name,
                provider_icon=prov.icon_url,
                brand_color=prov.brand_color,
                access_type=tp.access_type,
                price=tp.price,
                currency=tp.currency,
                web_url=tp.web_url,
                deep_link=tp.deep_link,
                is_in_user_subscription=False
            )
        elif tp.access_type in ["flatrate", "free", "ads"] and prov.id in user_subs:
            free_providers.append(prov.name)

    is_redundant = len(free_providers) > 0 and paid_tp is not None
    if is_redundant:
        msg = f"Save money! This title is available for FREE with your active {', '.join(free_providers)} subscription. Do not pay {paid_tp.currency} {paid_tp.price} to {paid_tp.access_type} on {paid_tp.provider_name}."
    elif free_providers:
        msg = f"Available to stream for free on your active {', '.join(free_providers)} subscription."
    elif paid_tp:
        msg = f"Available to {paid_tp.access_type} on {paid_tp.provider_name} for {paid_tp.currency} {paid_tp.price}."
    else:
        msg = "No streaming options currently verified."

    return RedundancyCheckResponse(
        title_id=title.id,
        title_name=title.title,
        is_redundant=is_redundant,
        redundancy_message=msg,
        free_available_on=free_providers,
        paid_option_found=paid_tp
    )
