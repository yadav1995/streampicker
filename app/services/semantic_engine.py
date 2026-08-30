import re
from typing import List, Optional, Tuple, Set, Dict
from sqlalchemy.orm import Session
from app.models import Title, TitleProvider, Provider
from app.schemas import (
    VibeSearchRequest,
    VibeSearchResponse,
    VibeSearchResultItem,
    ExtractedCriteria,
    TitleProviderInfo
)
from app.services.catalog_service import (
    format_title_response,
    get_user_active_subscriptions,
    get_user_watchlist_map
)

MOOD_KEYWORDS_MAP = {
    "mind-bending": ["mind-bending", "mind bending", "cerebral", "trippy", "psychological", "twist", "complex"],
    "adrenaline rush": ["adrenaline", "action", "thrill", "suspense", "fast paced", "explosive", "hype", "intense"],
    "feel-good & uplifting": ["feel good", "feel-good", "uplifting", "comfort", "wholesome", "heartwarming", "cozy", "happy"],
    "late-night mystery": ["mystery", "late night", "whodunit", "detective", "investigation", "puzzle", "crime"],
    "dark & gritty": ["dark", "gritty", "noir", "violent", "grim", "raw", "cynical"],
    "date night": ["date night", "romance", "romantic", "love", "couple", "chemistry"],
    "hilarious comedy": ["comedy", "funny", "hilarious", "laugh", "humor", "satire"],
    "epic scope": ["epic", "grand", "space", "historical", "monumental", "masterpiece"]
}

GENRE_MAP = {
    "sci-fi": ["sci-fi", "science fiction", "space", "alien", "futuristic", "time travel"],
    "drama": ["drama", "dramatic", "emotional", "serious"],
    "action": ["action", "fighting", "gun", "superhero"],
    "comedy": ["comedy", "humor", "comic"],
    "thriller": ["thriller", "suspense", "tension"],
    "mystery": ["mystery", "detective", "murder"],
    "crime": ["crime", "gangster", "mafia", "heist", "police"],
    "romance": ["romance", "romantic", "love"],
    "biography": ["biography", "biopic", "true story", "based on real"]
}

def parse_natural_language_query(query: str) -> ExtractedCriteria:
    q_lower = query.lower()
    criteria = ExtractedCriteria()

    # 1. Detect runtime patterns (e.g., "under 90 mins", "< 100 min", "less than 2 hours", "around 1 hour")
    runtime_match = re.search(r'(?:under|<|less than|within)\s*(\d+)\s*(?:m|min|mins|minutes)?', q_lower)
    if runtime_match:
        criteria.detected_max_runtime = int(runtime_match.group(1))
    else:
        hour_match = re.search(r'(?:under|<|less than|within)\s*(\d+(?:\.\d+)?)\s*(?:h|hr|hrs|hours)', q_lower)
        if hour_match:
            criteria.detected_max_runtime = int(float(hour_match.group(1)) * 60)

    # 2. Detect Mood
    for mood, keywords in MOOD_KEYWORDS_MAP.items():
        if any(kw in q_lower for kw in keywords):
            criteria.detected_mood = mood.title()
            break

    # 3. Detect Genres
    detected_genres = []
    for g, syns in GENRE_MAP.items():
        if any(syn in q_lower for syn in syns):
            detected_genres.append(g.title())
    criteria.detected_genres = detected_genres

    # 4. Detect Specific People (Directors / Actors)
    director_match = re.search(r'(?:by|directed by)\s+([a-zA-Z\s]+)', q_lower)
    if director_match:
        criteria.detected_director_or_actor = director_match.group(1).strip().title()

    # 5. Extract remaining meaningful tokens
    tokens = re.findall(r'\w+', q_lower)
    stop_words = {"a", "an", "the", "with", "and", "or", "for", "in", "on", "movie", "movies", "show", "shows", "film", "watch", "something"}
    criteria.keywords = [t for t in tokens if t not in stop_words and len(t) > 2]

    return criteria

def compute_vibe_score(title: Title, criteria: ExtractedCriteria, query_text: str) -> Tuple[float, List[str]]:
    score = 50.0
    reasons: List[str] = []
    
    t_genres = [g.strip().lower() for g in (title.genres or "").split(",") if g.strip()]
    t_moods = [m.strip().lower() for m in (title.mood_tags or "").split(",") if m.strip()]
    t_text = f"{title.title} {title.overview} {title.director} {title.cast_members} {title.genres} {title.mood_tags}".lower()

    # Mood match
    if criteria.detected_mood:
        detected_lower = criteria.detected_mood.lower()
        if any(detected_lower in m or m in detected_lower for m in t_moods):
            score += 20.0
            reasons.append(f"Matches desired '{criteria.detected_mood}' vibe")

    # Genre matches
    matched_genres = []
    for g in criteria.detected_genres:
        if g.lower() in t_genres:
            matched_genres.append(g)
    if matched_genres:
        score += min(len(matched_genres) * 10.0, 20.0)
        reasons.append(f"Matches genres: {', '.join(matched_genres)}")

    # Runtime fit
    if criteria.detected_max_runtime:
        if title.runtime_minutes <= criteria.detected_max_runtime:
            score += 15.0
            reasons.append(f"Fits runtime constraint ({title.runtime_minutes}m ≤ {criteria.detected_max_runtime}m)")
        else:
            score -= 30.0

    # Director / Actor mention
    if criteria.detected_director_or_actor:
        needle = criteria.detected_director_or_actor.lower()
        if needle in (title.director or "").lower() or needle in (title.cast_members or "").lower():
            score += 25.0
            reasons.append(f"Matches creator/cast: {criteria.detected_director_or_actor}")

    # Keyword overlap
    keyword_hits = [kw for kw in criteria.keywords if kw in t_text]
    if keyword_hits:
        score += min(len(keyword_hits) * 5.0, 15.0)

    # Base quality rating bonus
    if title.rating_imdb >= 8.0:
        score += 10.0
        reasons.append(f"High IMDb rating ({title.rating_imdb})")

    final_score = min(max(round(score, 1), 20.0), 99.0)
    return final_score, reasons

def search_by_vibe(
    db: Session,
    request: VibeSearchRequest,
    user_id: str = "default_user"
) -> VibeSearchResponse:
    criteria = parse_natural_language_query(request.query)
    user_subs = get_user_active_subscriptions(db, user_id)
    watchlist_map = get_user_watchlist_map(db, user_id)

    # Query candidate titles
    all_titles = db.query(Title).filter(
        Title.rating_imdb >= (request.min_imdb_rating or 6.0)
    ).all()

    results: List[VibeSearchResultItem] = []

    for t in all_titles:
        score, reasons = compute_vibe_score(t, criteria, request.query)
        if score >= 55.0:
            formatted_title = format_title_response(t, user_subs, watchlist_map)
            
            # Find best stream option
            best_stream = None
            for p in formatted_title.providers:
                if p.is_in_user_subscription:
                    best_stream = p
                    break
            if not best_stream and formatted_title.providers:
                best_stream = formatted_title.providers[0]

            explanation = " • ".join(reasons) if reasons else "Good thematic match for your search"
            
            results.append(
                VibeSearchResultItem(
                    title=formatted_title,
                    semantic_score=score,
                    match_explanation=explanation,
                    best_stream_option=best_stream
                )
            )

    # Sort by semantic score descending
    results.sort(key=lambda r: r.semantic_score, reverse=True)

    return VibeSearchResponse(
        query=request.query,
        extracted_criteria=criteria,
        results_count=len(results),
        results=results[:12]
    )
