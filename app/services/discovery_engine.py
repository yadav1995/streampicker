import random
from typing import List, Optional, Tuple, Set, Dict
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from app.models import Title, TitleProvider, Provider, UserSubscription
from app.schemas import PickRequest, PickResponse, TitleResponse, TitleProviderInfo
from app.services.catalog_service import (
    format_title_response,
    get_user_active_subscriptions,
    get_user_watchlist_map
)

def evaluate_title_match(
    title: Title,
    user_subs: Set[str],
    requested_providers: Set[str],
    target_mood: Optional[str],
    target_genres: List[str],
    max_runtime: int,
    min_rating: float
) -> Tuple[float, List[str], Optional[TitleProviderInfo]]:
    score = 60.0
    reasons: List[str] = []

    # 1. Check Provider Availability
    available_providers = []
    subscribed_stream_options = []
    for tp in title.providers:
        prov = tp.provider
        if prov and prov.is_active:
            is_subscribed = prov.id in user_subs and tp.access_type in ["flatrate", "free", "ads"]
            info = TitleProviderInfo(
                provider_id=prov.id,
                provider_name=prov.name,
                provider_icon=prov.icon_url,
                brand_color=prov.brand_color,
                access_type=tp.access_type,
                price=tp.price,
                currency=tp.currency,
                web_url=tp.web_url,
                deep_link=tp.deep_link,
                is_in_user_subscription=is_subscribed
            )
            available_providers.append(info)
            if is_subscribed:
                subscribed_stream_options.append(info)

    best_stream: Optional[TitleProviderInfo] = None
    if subscribed_stream_options:
        best_stream = subscribed_stream_options[0]
        score += 15.0
        reasons.append(f"Ready to stream immediately on {best_stream.provider_name}")
    elif available_providers:
        best_stream = available_providers[0]
        reasons.append(f"Available on {best_stream.provider_name} ({best_stream.access_type})")

    # 2. Mood Match
    title_moods = [m.strip().lower() for m in (title.mood_tags or "").split(",") if m.strip()]
    if target_mood:
        target_lower = target_mood.strip().lower()
        if any(target_lower in m or m in target_lower for m in title_moods):
            score += 15.0
            reasons.append(f"Perfect fit for '{target_mood}' mood")

    # 3. Genre Match
    title_genres = [g.strip().lower() for g in (title.genres or "").split(",") if g.strip()]
    matched_genres = [g for g in target_genres if g.lower() in title_genres]
    if matched_genres:
        score += min(len(matched_genres) * 5.0, 10.0)
        reasons.append(f"Matches your genres: {', '.join(matched_genres)}")

    # 4. Runtime Fit
    if title.runtime_minutes <= max_runtime:
        diff = max_runtime - title.runtime_minutes
        score += 5.0
        reasons.append(f"Perfect {title.runtime_minutes}m runtime (under your {max_runtime}m limit)")
    else:
        score -= 20.0

    # 5. Rating Bonus
    if title.rating_imdb >= 8.0:
        score += 10.0
        reasons.append(f"Critically acclaimed ({title.rating_imdb}/10 IMDb, {title.rating_rotten_tomatoes}% RT)")
    elif title.rating_imdb >= min_rating:
        score += 5.0

    # Cap score
    score = min(max(round(score, 1), 50.0), 99.0)
    return score, reasons, best_stream

def pick_for_me(
    db: Session,
    request: PickRequest,
    user_id: str = "default_user"
) -> Optional[PickResponse]:
    # 1. Resolve active subscriptions
    user_subs = get_user_active_subscriptions(db, user_id)
    watchlist_map = get_user_watchlist_map(db, user_id)

    # If requested_providers specified, use intersection or request
    active_providers_filter = set(request.providers) if request.providers else user_subs
    if not active_providers_filter:
        # Fallback to all active providers if user has none selected
        all_provs = db.query(Provider.id).filter(Provider.is_active == True).all()
        active_providers_filter = {p[0] for p in all_provs}

    # 2. Build Query
    query = db.query(Title).join(Title.providers).filter(
        TitleProvider.provider_id.in_(active_providers_filter)
    )

    if request.content_type:
        query = query.filter(Title.type == request.content_type)

    if request.max_runtime:
        query = query.filter(Title.runtime_minutes <= request.max_runtime)

    if request.min_imdb_rating:
        query = query.filter(Title.rating_imdb >= request.min_imdb_rating)

    if request.exclude_title_ids:
        query = query.filter(~Title.id.in_(request.exclude_title_ids))

    candidate_titles = query.distinct().all()

    # If no strict candidates found, relax runtime or provider constraints slightly
    if not candidate_titles:
        query_relaxed = db.query(Title).filter(
            Title.rating_imdb >= (request.min_imdb_rating - 0.5 if request.min_imdb_rating else 6.0)
        )
        if request.exclude_title_ids:
            query_relaxed = query_relaxed.filter(~Title.id.in_(request.exclude_title_ids))
        candidate_titles = query_relaxed.distinct().all()

    if not candidate_titles:
        return None

    # 3. Score & Rank Candidates
    target_genres = request.genres or []
    scored_candidates = []

    for title in candidate_titles:
        score, reasons, best_stream = evaluate_title_match(
            title=title,
            user_subs=user_subs,
            requested_providers=active_providers_filter,
            target_mood=request.mood,
            target_genres=target_genres,
            max_runtime=request.max_runtime or 180,
            min_rating=request.min_imdb_rating or 6.5
        )
        scored_candidates.append((title, score, reasons, best_stream))

    # Sort descending by score, with slight randomized tie-breaker for roulette excitement
    scored_candidates.sort(key=lambda x: (x[1] + random.uniform(0, 4.0)), reverse=True)

    top_pick = scored_candidates[0]
    top_title, top_score, top_reasons, top_stream = top_pick

    # Format alternatives (top 3 next best)
    alternatives: List[TitleResponse] = []
    for cand in scored_candidates[1:4]:
        alternatives.append(format_title_response(cand[0], user_subs, watchlist_map))

    top_title_resp = format_title_response(top_title, user_subs, watchlist_map)

    return PickResponse(
        title=top_title_resp,
        match_score=top_score,
        match_reasons=top_reasons,
        best_stream_option=top_stream or (top_title_resp.providers[0] if top_title_resp.providers else None),
        available_alternatives=alternatives
    )
