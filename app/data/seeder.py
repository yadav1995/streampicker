import uuid
from sqlalchemy.orm import Session
from app.models import Provider, Title, TitleProvider, UserSubscription, WatchlistItem, User
from app.data.seed_data import PROVIDERS, TITLES, INITIAL_SUBSCRIPTIONS

def to_comma_str(val, default=""):
    if isinstance(val, list):
        return ",".join(val)
    elif isinstance(val, str):
        return val
    return default

def seed_database(db: Session, default_user_id: str = "default_user"):
    # 0. Ensure default user exists
    user = db.query(User).filter(User.id == default_user_id).first()
    if not user:
        user = User(
            id=default_user_id,
            email="demo@streampicker.com",
            full_name="Demo Streamer",
            is_active=True,
            is_verified=True
        )
        db.add(user)
        db.commit()

    # 1. Seed Providers
    if db.query(Provider).count() == 0:
        for p in PROVIDERS:
            prov = Provider(
                id=p["id"],
                name=p["name"],
                icon_url=p.get("icon_url"),
                brand_color=p.get("brand_color", "#E50914"),
                badge_bg=p.get("badge_bg", "rgba(229, 9, 20, 0.15)"),
                monthly_price_inr=p.get("monthly_price_inr", 199.0),
                display_priority=p.get("display_priority", 100)
            )
            db.add(prov)
        db.commit()

    # 2. Seed Titles & TitleProviders
    if db.query(Title).count() == 0:
        for t_data in TITLES:
            t = Title(
                id=t_data.get("id") or str(uuid.uuid4()),
                tmdb_id=t_data.get("tmdb_id"),
                imdb_id=t_data.get("imdb_id"),
                title=t_data["title"],
                type=t_data.get("type", "movie"),
                runtime_minutes=t_data.get("runtime_minutes", 90),
                release_year=t_data.get("release_year", 2020),
                genres=to_comma_str(t_data.get("genres"), "Drama"),
                mood_tags=to_comma_str(t_data.get("mood_tags"), "Feel-Good"),
                director=t_data.get("director"),
                cast_members=to_comma_str(t_data.get("cast_members"), ""),
                rating_imdb=t_data.get("rating_imdb", 7.0),
                rating_tmdb=t_data.get("rating_tmdb", 7.0),
                rating_rotten_tomatoes=t_data.get("rating_rotten_tomatoes", 75),
                overview=t_data.get("overview"),
                poster_url=t_data.get("poster_url"),
                backdrop_url=t_data.get("backdrop_url")
            )
            db.add(t)
            db.flush()

            for p_info in t_data.get("providers", []):
                tp = TitleProvider(
                    id=str(uuid.uuid4()),
                    title_id=t.id,
                    provider_id=p_info["provider_id"],
                    access_type=p_info.get("access_type", "flatrate"),
                    price=p_info.get("price"),
                    currency=p_info.get("currency", "INR"),
                    web_url=p_info.get("web_url"),
                    deep_link=p_info.get("deep_link")
                )
                db.add(tp)
        db.commit()

    # 3. Seed Initial User Subscriptions
    if db.query(UserSubscription).filter(UserSubscription.user_id == default_user_id).count() == 0:
        for prov_id in INITIAL_SUBSCRIPTIONS:
            sub = UserSubscription(
                id=str(uuid.uuid4()),
                user_id=default_user_id,
                provider_id=prov_id,
                is_active=True
            )
            db.add(sub)
        db.commit()
