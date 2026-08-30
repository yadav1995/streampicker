import math
import re
from typing import List, Dict, Tuple, Optional, Set
from collections import Counter
from sqlalchemy.orm import Session
from app.models import Title, TitleProvider
from app.schemas import TitleResponse
from app.services.catalog_service import format_title_response, get_user_active_subscriptions

# Lightweight in-memory semantic vector space model
def extract_feature_vector(title: Title) -> Counter:
    features = []
    # Weighted features
    genres = [g.strip().lower() for g in (title.genres or "").split(",") if g.strip()]
    moods = [m.strip().lower() for m in (title.mood_tags or "").split(",") if m.strip()]
    director = (title.director or "").strip().lower()
    cast = [c.strip().lower() for c in (title.cast_members or "").split(",") if c.strip()]
    
    # Text tokens from overview
    tokens = re.findall(r'\w+', (title.overview or "").lower())
    stop_words = {"the", "a", "an", "and", "or", "in", "on", "of", "to", "with", "for", "is", "by", "as", "at"}
    words = [w for w in tokens if w not in stop_words and len(w) > 3]

    # Assign weights
    for g in genres:
        features.extend([f"genre:{g}"] * 4)
    for m in moods:
        features.extend([f"mood:{m}"] * 5)
    if director:
        features.extend([f"dir:{director}"] * 6)
    for c in cast:
        features.extend([f"cast:{c}"] * 3)
    for w in words:
        features.append(f"word:{w}")

    return Counter(features)

def cosine_similarity(vec1: Counter, vec2: Counter) -> float:
    intersection = set(vec1.keys()) & set(vec2.keys())
    numerator = sum(vec1[x] * vec2[x] for x in intersection)

    sum1 = sum(vec1[x] ** 2 for x in vec1.keys())
    sum2 = sum(vec2[x] ** 2 for x in vec2.keys())
    denominator = math.sqrt(sum1) * math.sqrt(sum2)

    if not denominator:
        return 0.0
    return float(numerator) / denominator

def find_similar_titles(
    db: Session,
    title_id: str,
    limit: int = 6,
    user_id: str = "default_user"
) -> List[Tuple[TitleResponse, float]]:
    target_title = db.query(Title).filter(Title.id == title_id).first()
    if not target_title:
        return []

    target_vec = extract_feature_vector(target_title)
    all_titles = db.query(Title).filter(Title.id != title_id).all()
    user_subs = get_user_active_subscriptions(db, user_id)

    scored: List[Tuple[Title, float]] = []
    for other in all_titles:
        other_vec = extract_feature_vector(other)
        sim = cosine_similarity(target_vec, other_vec)
        if sim > 0.05:
            # Bonus if available on user's active flatrate subscription
            available_subs = {tp.provider_id for tp in other.providers if tp.access_type in ["flatrate", "free"]}
            if available_subs & user_subs:
                sim += 0.05
            scored.append((other, round(sim * 100, 1)))

    scored.sort(key=lambda x: x[1], reverse=True)
    top_candidates = scored[:limit]

    results = []
    for t, score in top_candidates:
        formatted = format_title_response(t, user_subs, {})
        results.append((formatted, score))

    return results

def hybrid_semantic_search(
    db: Session,
    query_text: str,
    min_rating: float = 6.0,
    limit: int = 10,
    user_id: str = "default_user"
) -> List[Tuple[TitleResponse, float]]:
    # Build query vector from raw input
    tokens = re.findall(r'\w+', query_text.lower())
    query_vec = Counter([f"word:{t}" for t in tokens if len(t) > 2])
    
    # Also add potential genre and mood matches
    for t in tokens:
        query_vec[f"genre:{t}"] = 3
        query_vec[f"mood:{t}"] = 4
        query_vec[f"dir:{t}"] = 5

    all_titles = db.query(Title).filter(Title.rating_imdb >= min_rating).all()
    user_subs = get_user_active_subscriptions(db, user_id)

    scored = []
    for t in all_titles:
        t_vec = extract_feature_vector(t)
        sim = cosine_similarity(query_vec, t_vec)
        # Add IMDb rating prior
        combined_score = (sim * 70.0) + (t.rating_imdb * 3.0)
        scored.append((t, round(min(combined_score, 99.0), 1)))

    scored.sort(key=lambda x: x[1], reverse=True)
    
    return [
        (format_title_response(t, user_subs, {}), score)
        for t, score in scored[:limit]
    ]
