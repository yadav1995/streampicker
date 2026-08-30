from typing import List, Optional, Tuple, Set
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, desc, asc
from app.models import Title, TitleProvider, Provider
from app.schemas import TitleResponse
from app.services.catalog_service import (
    format_title_response,
    get_user_active_subscriptions,
    get_user_watchlist_map
)

def search_catalog(
    db: Session,
    query_str: Optional[str] = None,
    providers: Optional[List[str]] = None,
    genre: Optional[str] = None,
    mood: Optional[str] = None,
    content_type: Optional[str] = None,
    min_rating: Optional[float] = None,
    max_runtime: Optional[int] = None,
    sort_by: str = "rating",  # 'rating', 'year', 'runtime', 'title'
    limit: int = 50,
    offset: int = 0,
    user_id: str = "default_user"
) -> Tuple[List[TitleResponse], int]:
    user_subs = get_user_active_subscriptions(db, user_id)
    watchlist_map = get_user_watchlist_map(db, user_id)

    query = db.query(Title)

    # 1. Text Search across Title, Cast, Director, Overview
    if query_str:
        search_pattern = f"%{query_str.strip()}%"
        query = query.filter(
            or_(
                Title.title.ilike(search_pattern),
                Title.cast_members.ilike(search_pattern),
                Title.director.ilike(search_pattern),
                Title.genres.ilike(search_pattern),
                Title.mood_tags.ilike(search_pattern),
                Title.overview.ilike(search_pattern)
            )
        )

    # 2. Provider Filter
    if providers and len(providers) > 0:
        query = query.join(Title.providers).filter(
            TitleProvider.provider_id.in_(providers)
        )

    # 3. Genre Filter
    if genre:
        query = query.filter(Title.genres.ilike(f"%{genre.strip()}%"))

    # 4. Mood Filter
    if mood:
        query = query.filter(Title.mood_tags.ilike(f"%{mood.strip()}%"))

    # 5. Content Type
    if content_type:
        query = query.filter(Title.type == content_type)

    # 6. Min Rating
    if min_rating is not None:
        query = query.filter(Title.rating_imdb >= min_rating)

    # 7. Max Runtime
    if max_runtime is not None:
        query = query.filter(Title.runtime_minutes <= max_runtime)

    # Sorting
    if sort_by == "rating":
        query = query.order_by(desc(Title.rating_imdb))
    elif sort_by == "year":
        query = query.order_by(desc(Title.release_year))
    elif sort_by == "runtime":
        query = query.order_by(asc(Title.runtime_minutes))
    elif sort_by == "title":
        query = query.order_by(asc(Title.title))
    else:
        query = query.order_by(desc(Title.rating_imdb))

    query = query.distinct()
    total_count = query.count()
    titles = query.offset(offset).limit(limit).all()

    formatted_titles = [
        format_title_response(t, user_subs, watchlist_map) for t in titles
    ]
    return formatted_titles, total_count
