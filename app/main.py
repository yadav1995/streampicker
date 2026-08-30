import os
import json
from contextlib import asynccontextmanager
from typing import List, Optional, Dict, Any
from pathlib import Path

from fastapi import FastAPI, Depends, HTTPException, Query, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse
from sqlalchemy.orm import Session

from app.config import settings
from app.database import engine, Base, get_db, SessionLocal
from app.models import Title, TitleProvider, UserFeedback, User
from app.data.seeder import seed_database
from app.schemas import (
    UserRegisterRequest,
    UserLoginRequest,
    GoogleAuthRequest,
    UserResponse,
    TokenResponse,
    ProviderResponse,
    TitleResponse,
    PickRequest,
    PickResponse,
    SubscriptionUpdateRequest,
    WatchlistCreateRequest,
    WatchlistItemResponse,
    VibeSearchRequest,
    VibeSearchResponse,
    GroupPickRequest,
    GroupPickResponse,
    SubscriptionROIResponse,
    RedundancyCheckResponse,
    FeedbackCreateRequest,
    FeedbackResponse,
    DeepLinkResolveResponse,
    CacheStatsResponse,
    ShareCreateRequest,
    ShareResponse,
    SimilarTitlesResponse,
    SimilarTitleItem,
    RoomCreateRequest,
    RoomCreateResponse,
    RoomJoinRequest,
    RoomVoteRequest,
    RoomStateResponse,
    AlertNotificationItem,
    AnalyticsMetricsResponse
)
from app.services import (
    discovery_engine,
    search_service,
    catalog_service,
    watchlist_service,
    semantic_engine,
    subscription_optimizer,
    group_watch_service,
    cache_service,
    deeplink_service,
    share_service,
    vector_search,
    ingestion_worker,
    watch_room_service,
    alert_service,
    analytics_service,
    auth_service,
    live_api_sync,
    tmdb_client,
    watchmode_client
)
from app.services.auth_service import get_current_user, get_current_user_optional
from app.services.rate_limiter import RateLimitMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_database(db, settings.DEFAULT_USER_ID)
    finally:
        db.close()
    yield

app = FastAPI(
    title="StreamPicker API",
    description="High-performance OTT Discovery, Multi-User Auth & Constraint Engine",
    version=settings.APP_VERSION,
    lifespan=lifespan
)

# Rate Limiting Middleware (180 requests/min, 60 burst)
app.add_middleware(RateLimitMiddleware, requests_per_minute=180, burst_limit=60)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Static Files
STATIC_DIR = Path(__file__).resolve().parent / "static"
if not STATIC_DIR.exists():
    STATIC_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/")
async def root():
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return {"message": "StreamPicker API is running."}

@app.get("/api/v1/health")
def health_check():
    return {"status": "healthy", "service": "streampicker", "version": settings.APP_VERSION}

# ==================== Authentication & Multi-Tenancy ====================

@app.post("/api/v1/auth/register", response_model=TokenResponse)
def register_user(req: UserRegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == req.email.lower()).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists."
        )

    new_user = User(
        email=req.email.lower(),
        hashed_password=auth_service.hash_password(req.password),
        full_name=req.full_name,
        is_active=True,
        is_verified=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Seed default subscriptions for new user (Netflix + Prime)
    watchlist_service.update_user_subscriptions(db, ["netflix", "prime_video"], user_id=new_user.id)

    token = auth_service.create_access_token(new_user.id, new_user.email, new_user.full_name)
    return TokenResponse(
        access_token=token,
        expires_in_seconds=auth_service.ACCESS_TOKEN_EXPIRE_SECONDS,
        user=UserResponse.model_validate(new_user)
    )

@app.post("/api/v1/auth/login", response_model=TokenResponse)
def login_user(req: UserLoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email.lower()).first()
    if not user or not user.hashed_password or not auth_service.verify_password(req.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )

    token = auth_service.create_access_token(user.id, user.email, user.full_name)
    return TokenResponse(
        access_token=token,
        expires_in_seconds=auth_service.ACCESS_TOKEN_EXPIRE_SECONDS,
        user=UserResponse.model_validate(user)
    )

@app.post("/api/v1/auth/google", response_model=TokenResponse)
def google_auth(req: GoogleAuthRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email.lower()).first()
    if not user:
        user = User(
            email=req.email.lower(),
            full_name=req.full_name,
            avatar_url=req.avatar_url,
            is_active=True,
            is_verified=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        watchlist_service.update_user_subscriptions(db, ["netflix", "prime_video", "hotstar"], user_id=user.id)

    token = auth_service.create_access_token(user.id, user.email, user.full_name)
    return TokenResponse(
        access_token=token,
        expires_in_seconds=auth_service.ACCESS_TOKEN_EXPIRE_SECONDS,
        user=UserResponse.model_validate(user)
    )

@app.get("/api/v1/auth/me", response_model=UserResponse)
def get_current_user_profile(user: User = Depends(get_current_user)):
    return UserResponse.model_validate(user)

# ==================== Providers & Subscriptions ====================

@app.get("/api/v1/providers", response_model=List[ProviderResponse])
def list_providers(
    user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    return watchlist_service.get_all_providers(db, user_id=user.id)

@app.put("/api/v1/subscriptions", response_model=List[str])
def update_subscriptions(
    req: SubscriptionUpdateRequest,
    user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    cache_service.cache.clear_prefix(f"pick:{user.id}")
    cache_service.cache.clear_prefix(f"roi:{user.id}")
    return watchlist_service.update_user_subscriptions(db, req.provider_ids, user_id=user.id)

@app.get("/api/v1/subscriptions/roi", response_model=SubscriptionROIResponse)
def get_subscription_roi(
    user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    cache_key = f"roi:{user.id}"
    cached = cache_service.cache.get(cache_key)
    if cached:
        return cached
    res = subscription_optimizer.calculate_subscription_roi(db, user_id=user.id)
    cache_service.cache.set(cache_key, res.model_dump(), ttl=120)
    return res

@app.get("/api/v1/subscriptions/redundancy-check/{title_id}", response_model=RedundancyCheckResponse)
def check_redundancy(
    title_id: str,
    user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    return subscription_optimizer.check_title_redundancy(db, title_id, user_id=user.id)

# ==================== Rapid Discovery & AI Vibe Search ====================

@app.post("/api/v1/discovery/pick", response_model=PickResponse)
def pick_title(
    req: PickRequest,
    user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    cache_key = None
    if not req.exclude_title_ids:
        cache_key = f"pick:{user.id}:{req.mood}:{req.max_runtime}:{req.min_imdb_rating}:{','.join(req.providers or [])}"
        cached = cache_service.cache.get(cache_key)
        if cached:
            cached["is_cached"] = True
            analytics_service.analytics.record_pick_event(latency_ms=4.2, success=True)
            return cached

    result = discovery_engine.pick_for_me(db, req, user_id=user.id)
    if not result:
        analytics_service.analytics.record_pick_event(latency_ms=18.0, success=False)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No titles matched your selected constraints. Try relaxing runtime or rating filters."
        )

    if cache_key:
        cache_service.cache.set(cache_key, result.model_dump(), ttl=60)

    analytics_service.analytics.record_pick_event(latency_ms=12.5, success=True)
    return result

@app.post("/api/v1/discovery/vibe-search", response_model=VibeSearchResponse)
def search_vibe(
    req: VibeSearchRequest,
    user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    return semantic_engine.search_by_vibe(db, req, user_id=user.id)

@app.post("/api/v1/discovery/group-pick", response_model=GroupPickResponse)
def group_pick(
    req: GroupPickRequest,
    db: Session = Depends(get_db)
):
    result = group_watch_service.resolve_group_compromise(db, req)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not find a mutual compromise title."
        )
    return result

# ==================== Universal Catalog & Search ====================

@app.get("/api/v1/titles", response_model=dict)
def search_titles(
    q: Optional[str] = Query(None, description="Search keyword"),
    providers: Optional[str] = Query(None, description="Comma-separated provider IDs"),
    genre: Optional[str] = Query(None, description="Genre name"),
    mood: Optional[str] = Query(None, description="Mood tag"),
    type: Optional[str] = Query(None, description="'movie' or 'series'"),
    min_rating: Optional[float] = Query(None, description="Min IMDb rating"),
    max_runtime: Optional[int] = Query(None, description="Max runtime minutes"),
    sort_by: str = Query("rating", description="Sort by rating, year, runtime, title"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    provider_list = [p.strip() for p in providers.split(",") if p.strip()] if providers else None
    titles, total = search_service.search_catalog(
        db=db,
        query_str=q,
        providers=provider_list,
        genre=genre,
        mood=mood,
        content_type=type,
        min_rating=min_rating,
        max_runtime=max_runtime,
        sort_by=sort_by,
        limit=limit,
        offset=offset,
        user_id=user.id
    )
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "items": titles
    }

@app.get("/api/v1/titles/{title_id}", response_model=TitleResponse)
def get_title(
    title_id: str,
    user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    title = db.query(Title).filter(Title.id == title_id).first()
    if not title:
        raise HTTPException(status_code=404, detail="Title not found")
    
    user_subs = catalog_service.get_user_active_subscriptions(db, user.id)
    wl_map = catalog_service.get_user_watchlist_map(db, user.id)
    return catalog_service.format_title_response(title, user_subs, wl_map)

@app.get("/api/v1/titles/{title_id}/similar", response_model=SimilarTitlesResponse)
def get_similar_titles(
    title_id: str,
    limit: int = Query(6, ge=1, le=20),
    user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    results = vector_search.find_similar_titles(db, title_id=title_id, limit=limit, user_id=user.id)
    items = [SimilarTitleItem(title=t, similarity_score=score) for t, score in results]
    return SimilarTitlesResponse(source_title_id=title_id, similar_titles=items)

# ==================== Universal Deep Link Router ====================

@app.get("/api/v1/deeplink/resolve", response_model=DeepLinkResolveResponse)
def resolve_deeplink(
    title_id: str,
    provider_id: str,
    device: Optional[str] = Query(None, description="'ios', 'android', 'web', 'tv'"),
    request: Request = None,
    db: Session = Depends(get_db)
):
    tp = db.query(TitleProvider).filter(
        TitleProvider.title_id == title_id,
        TitleProvider.provider_id == provider_id
    ).first()
    if not tp:
        raise HTTPException(status_code=404, detail="Title provider link not found")

    user_agent = request.headers.get("user-agent") if request else None
    resolved = deeplink_service.resolve_provider_deep_link(
        provider_id=tp.provider.id,
        provider_name=tp.provider.name,
        web_url=tp.web_url,
        existing_deep_link=tp.deep_link,
        device=device,
        user_agent=user_agent
    )

    analytics_service.analytics.record_provider_click(provider_id)

    return DeepLinkResolveResponse(
        title_id=title_id,
        provider_id=provider_id,
        provider_name=tp.provider.name,
        device_type=resolved.device_type,
        resolved_uri=resolved.resolved_uri,
        fallback_web_url=resolved.fallback_web_url,
        target_action=resolved.target_action
    )

# ==================== Watch Party Collaborative Rooms ====================

@app.post("/api/v1/rooms/create", response_model=RoomCreateResponse)
def create_room(
    req: RoomCreateRequest,
    db: Session = Depends(get_db)
):
    return watch_room_service.room_manager.create_room(
        host_name=req.host_name,
        host_subscriptions=req.subscriptions,
        db=db
    )

@app.post("/api/v1/rooms/{room_code}/join")
def join_room(
    room_code: str,
    req: RoomJoinRequest
):
    res = watch_room_service.room_manager.join_room(
        room_code=room_code,
        user_name=req.user_name,
        subscriptions=req.subscriptions
    )
    if not res:
        raise HTTPException(status_code=404, detail="Room not found")
    return res

@app.post("/api/v1/rooms/{room_code}/vote")
def cast_vote(
    room_code: str,
    req: RoomVoteRequest
):
    res = watch_room_service.room_manager.cast_vote(
        room_code=room_code,
        user_name=req.user_name,
        title_id=req.title_id,
        vote=req.vote
    )
    if not res:
        raise HTTPException(status_code=404, detail="Room not found")
    return res

@app.get("/api/v1/rooms/{room_code}", response_model=RoomStateResponse)
def get_room(
    room_code: str,
    db: Session = Depends(get_db)
):
    state = watch_room_service.room_manager.get_room_state(room_code, db)
    if not state:
        raise HTTPException(status_code=404, detail="Room not found")
    return state

# ==================== Unified Watchlist, Alerts & Export ====================

@app.get("/api/v1/watchlist", response_model=List[WatchlistItemResponse])
def get_watchlist(
    user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    return watchlist_service.get_user_watchlist(db, user_id=user.id)

@app.post("/api/v1/watchlist", response_model=WatchlistItemResponse)
def add_watchlist_item(
    req: WatchlistCreateRequest,
    user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    cache_service.cache.clear_prefix(f"roi:{user.id}")
    item = watchlist_service.add_to_watchlist(db, req, user_id=user.id)
    if not item:
        raise HTTPException(status_code=404, detail="Title not found")
    return item

@app.delete("/api/v1/watchlist/{title_id}")
def remove_watchlist_item(
    title_id: str,
    user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    cache_service.cache.clear_prefix(f"roi:{user.id}")
    success = watchlist_service.remove_from_watchlist(db, title_id, user_id=user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Watchlist item not found")
    return {"status": "success", "message": "Item removed from watchlist"}

@app.get("/api/v1/watchlist/export")
def export_watchlist(
    format: str = Query("json", description="'json' or 'csv'"),
    user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    if format.lower() == "csv":
        csv_data = share_service.export_watchlist_csv(db, user_id=user.id)
        return Response(
            content=csv_data,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=streampicker_watchlist.csv"}
        )
    else:
        json_data = share_service.export_watchlist_json(db, user_id=user.id)
        return JSONResponse(content=json_data)

@app.get("/api/v1/alerts/notifications", response_model=List[AlertNotificationItem])
def get_notifications(
    user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    return alert_service.get_user_alerts(db, user_id=user.id)

# ==================== Share Links ====================

@app.post("/api/v1/share/create", response_model=ShareResponse)
def create_share(req: ShareCreateRequest):
    return share_service.create_share_link(
        share_type=req.share_type,
        payload=req.payload,
        ttl_seconds=86400
    )

@app.get("/api/v1/share/{token}")
def get_shared(token: str):
    data = share_service.get_shared_content(token)
    if not data:
        raise HTTPException(status_code=404, detail="Share link expired or not found")
    return data

@app.get("/s/{token}")
def render_shared_page(token: str):
    data = share_service.get_shared_content(token)
    if not data:
        return PlainTextResponse("This StreamPicker shared link has expired.", status_code=404)
    return FileResponse(str(STATIC_DIR / "index.html"))

# ==================== Live TMDB & System APIs ====================

@app.post("/api/v1/system/sync-live-tmdb")
def sync_live_tmdb(
    max_titles: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    return live_api_sync.sync_live_trending_titles(db, max_titles=max_titles)

@app.get("/api/v1/system/api-status")
def get_api_status():
    return {
        "tmdb_configured": tmdb_client.tmdb_client.is_configured(),
        "tmdb_region": settings.TMDB_DEFAULT_REGION,
        "watchmode_configured": watchmode_client.watchmode_client.is_configured(),
        "redis_configured": bool(settings.REDIS_URL),
        "database_backend": "PostgreSQL" if "postgresql" in settings.DATABASE_URL else "SQLite"
    }

@app.post("/api/v1/system/sync-catalog")
def sync_catalog(db: Session = Depends(get_db)):
    return ingestion_worker.sync_catalog_deltas(db)

@app.get("/api/v1/system/cache-stats", response_model=CacheStatsResponse)
def get_cache_stats():
    return cache_service.cache.get_stats()

@app.get("/api/v1/system/analytics", response_model=AnalyticsMetricsResponse)
def get_analytics():
    return analytics_service.analytics.get_metrics_summary()

# ==================== Feedback Loop ====================

@app.post("/api/v1/history/feedback", response_model=FeedbackResponse)
def record_feedback(
    req: FeedbackCreateRequest,
    user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    feedback = UserFeedback(
        user_id=user.id,
        title_id=req.title_id,
        liked=req.liked,
        rating=req.rating,
        notes=req.notes
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return feedback
