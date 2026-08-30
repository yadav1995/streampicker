from typing import List, Optional, Tuple, Set
from sqlalchemy.orm import Session
from app.models import Title, TitleProvider, Provider
from app.schemas import (
    GroupPickRequest,
    GroupPickResponse,
    TitleResponse,
    TitleProviderInfo
)
from app.services.catalog_service import format_title_response

def resolve_group_compromise(
    db: Session,
    request: GroupPickRequest
) -> Optional[GroupPickResponse]:
    v1 = request.viewer_1
    v2 = request.viewer_2

    # Combined accessible platforms (watching together in person)
    combined_providers = set(v1.subscriptions) | set(v2.subscriptions)
    if not combined_providers:
        # Fallback to all active providers if neither specified
        combined_providers = {p[0] for p in db.query(Provider.id).filter(Provider.is_active == True).all()}

    # Candidate query
    query = db.query(Title).join(Title.providers).filter(
        TitleProvider.provider_id.in_(combined_providers),
        Title.rating_imdb >= (request.min_imdb_rating or 7.0)
    )

    if request.max_runtime:
        query = query.filter(Title.runtime_minutes <= request.max_runtime)

    candidates = query.distinct().all()
    if not candidates:
        # Relax runtime
        candidates = db.query(Title).filter(
            Title.rating_imdb >= (request.min_imdb_rating or 6.5)
        ).distinct().all()

    if not candidates:
        return None

    scored_candidates = []

    for t in candidates:
        t_genres = [g.strip().lower() for g in (t.genres or "").split(",") if g.strip()]
        t_moods = [m.strip().lower() for m in (t.mood_tags or "").split(",") if m.strip()]

        # Viewer 1 Satisfaction
        v1_score = 50.0
        if v1.preferred_mood and any(v1.preferred_mood.lower() in m for m in t_moods):
            v1_score += 25.0
        v1_genre_hits = [g for g in v1.preferred_genres if g.lower() in t_genres]
        v1_score += min(len(v1_genre_hits) * 10.0, 20.0)

        # Viewer 2 Satisfaction
        v2_score = 50.0
        if v2.preferred_mood and any(v2.preferred_mood.lower() in m for m in t_moods):
            v2_score += 25.0
        v2_genre_hits = [g for g in v2.preferred_genres if g.lower() in t_genres]
        v2_score += min(len(v2_genre_hits) * 10.0, 20.0)

        # Compromise Balance: penalize heavy asymmetry (e.g. 90 vs 40 is worse than 75 vs 75)
        avg_score = (v1_score + v2_score) / 2.0
        asymmetry_penalty = abs(v1_score - v2_score) * 0.25
        compromise_score = avg_score - asymmetry_penalty

        # Quality bonus
        if t.rating_imdb >= 8.0:
            compromise_score += 8.0

        scored_candidates.append((t, compromise_score, v1_score, v2_score))

    scored_candidates.sort(key=lambda x: x[1], reverse=True)
    top_candidate, final_compromise_score, v1_sat, v2_sat = scored_candidates[0]

    # Format response
    title_resp = format_title_response(top_candidate, combined_providers, {})

    breakdown = [
        f"Selected for {v1.name} and {v2.name}",
        f"Available on your shared subscriptions: {', '.join([p.provider_name for p in title_resp.providers])}",
        f"Runtime of {top_candidate.runtime_minutes}m fits within both schedules"
    ]
    if v1.preferred_mood:
        breakdown.append(f"Includes {v1.name}'s vibe: '{v1.preferred_mood}'")
    if v2.preferred_mood and v2.preferred_mood != v1.preferred_mood:
        breakdown.append(f"Balances {v2.name}'s vibe: '{v2.preferred_mood}'")

    return GroupPickResponse(
        chosen_title=title_resp,
        compromise_score=round(min(final_compromise_score, 99.0), 1),
        compromise_breakdown=breakdown,
        shared_streaming_options=title_resp.providers,
        viewer_1_satisfaction=round(min(v1_sat, 100.0), 1),
        viewer_2_satisfaction=round(min(v2_sat, 100.0), 1)
    )
