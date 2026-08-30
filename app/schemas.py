from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

# ==================== AUTH SCHEMAS ====================

class UserRegisterRequest(BaseModel):
    email: str = Field(..., description="User email address")
    password: str = Field(..., min_length=6, description="Password minimum 6 characters")
    full_name: str = Field(default="Viewer", min_length=1)

class UserLoginRequest(BaseModel):
    email: str
    password: str

class GoogleAuthRequest(BaseModel):
    id_token: str
    email: str
    full_name: str
    avatar_url: Optional[str] = None

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    avatar_url: Optional[str] = None
    is_active: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_seconds: int
    user: UserResponse

# ==================== CATALOG & PROVIDER SCHEMAS ====================

class ProviderBase(BaseModel):
    id: str
    name: str
    icon_url: Optional[str] = None
    brand_color: str = "#E50914"
    badge_bg: str = "rgba(229, 9, 20, 0.15)"
    monthly_price_inr: float = 199.0
    is_active: bool = True
    display_priority: int = 100

class ProviderResponse(ProviderBase):
    is_subscribed: bool = False
    model_config = ConfigDict(from_attributes=True)

class TitleProviderInfo(BaseModel):
    provider_id: str
    provider_name: str
    provider_icon: Optional[str] = None
    brand_color: str = "#E50914"
    access_type: str = "flatrate"  # flatrate, free, ads, rent, buy
    price: Optional[float] = None
    currency: str = "INR"
    web_url: str
    deep_link: str
    is_in_user_subscription: bool = False

class TitleResponse(BaseModel):
    id: str
    tmdb_id: Optional[str] = None
    imdb_id: Optional[str] = None
    title: str
    type: str  # movie, series
    runtime_minutes: int
    release_year: int
    genres: List[str]
    mood_tags: List[str]
    director: str
    cast_members: List[str]
    rating_imdb: float
    rating_tmdb: float
    rating_rotten_tomatoes: int
    overview: str
    poster_url: str
    backdrop_url: str
    trailer_url: Optional[str] = None
    providers: List[TitleProviderInfo] = []
    is_in_watchlist: bool = False
    watchlist_status: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class PickRequest(BaseModel):
    providers: Optional[List[str]] = Field(default=None, description="Active OTT provider IDs to filter by")
    mood: Optional[str] = Field(default=None, description="Target mood e.g. 'Mind-Bending', 'Adrenaline', 'Feel-Good'")
    genres: Optional[List[str]] = Field(default=None, description="Target genres")
    max_runtime: Optional[int] = Field(default=180, ge=30, le=300, description="Max runtime in minutes")
    min_imdb_rating: Optional[float] = Field(default=6.5, ge=0.0, le=10.0, description="Minimum IMDb rating")
    content_type: Optional[str] = Field(default=None, description="'movie', 'series', or null for all")
    exclude_title_ids: Optional[List[str]] = Field(default_factory=list, description="Titles to skip (e.g. already viewed/skipped)")

class PickResponse(BaseModel):
    title: TitleResponse
    match_score: float
    match_reasons: List[str]
    best_stream_option: Optional[TitleProviderInfo] = None
    available_alternatives: List[TitleResponse] = []
    is_cached: bool = False

class SubscriptionUpdateRequest(BaseModel):
    provider_ids: List[str]

class WatchlistCreateRequest(BaseModel):
    title_id: str
    status: str = "saved"  # saved, watching, watched

class WatchlistStatusUpdateRequest(BaseModel):
    status: str  # saved, watching, watched

class WatchlistItemResponse(BaseModel):
    id: str
    title_id: str
    status: str
    created_at: datetime
    title: TitleResponse

    model_config = ConfigDict(from_attributes=True)

class VibeSearchRequest(BaseModel):
    query: str = Field(..., description="Natural language vibe query e.g. 'mind bending sci-fi thriller under 100 mins'")
    providers: Optional[List[str]] = None
    min_imdb_rating: Optional[float] = 6.0

class ExtractedCriteria(BaseModel):
    detected_mood: Optional[str] = None
    detected_genres: List[str] = []
    detected_max_runtime: Optional[int] = None
    detected_director_or_actor: Optional[str] = None
    keywords: List[str] = []

class VibeSearchResultItem(BaseModel):
    title: TitleResponse
    semantic_score: float
    match_explanation: str
    best_stream_option: Optional[TitleProviderInfo] = None

class VibeSearchResponse(BaseModel):
    query: str
    extracted_criteria: ExtractedCriteria
    results_count: int
    results: List[VibeSearchResultItem]

class ViewerPreference(BaseModel):
    name: str = "Viewer"
    subscriptions: List[str] = []
    preferred_mood: Optional[str] = None
    preferred_genres: List[str] = []

class GroupPickRequest(BaseModel):
    viewer_1: ViewerPreference
    viewer_2: ViewerPreference
    max_runtime: Optional[int] = 150
    min_imdb_rating: Optional[float] = 7.0

class GroupPickResponse(BaseModel):
    chosen_title: TitleResponse
    compromise_score: float
    compromise_breakdown: List[str]
    shared_streaming_options: List[TitleProviderInfo]
    viewer_1_satisfaction: float
    viewer_2_satisfaction: float

class SubscriptionROIResponse(BaseModel):
    total_monthly_spend_inr: float
    active_subscriptions_count: int
    active_providers: List[ProviderResponse]
    accessible_catalog_count: int
    total_catalog_count: int
    catalog_coverage_percent: float
    estimated_cost_per_title_watched: float
    underutilized_subscriptions: List[str]

class RedundancyCheckResponse(BaseModel):
    title_id: str
    title_name: str
    is_redundant: bool
    redundancy_message: str
    free_available_on: List[str] = []
    paid_option_found: Optional[TitleProviderInfo] = None

class FeedbackCreateRequest(BaseModel):
    title_id: str
    liked: Optional[bool] = None
    rating: Optional[float] = None
    notes: Optional[str] = None

class FeedbackResponse(BaseModel):
    id: str
    title_id: str
    liked: Optional[bool]
    rating: Optional[float]
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class DeepLinkResolveResponse(BaseModel):
    title_id: str
    provider_id: str
    provider_name: str
    device_type: str
    resolved_uri: str
    fallback_web_url: str
    target_action: str

class CacheStatsResponse(BaseModel):
    active_entries: int
    is_redis_enabled: bool = False
    hits: int
    misses: int
    total_requests: int
    hit_ratio_percent: float
    evictions: int

class ShareCreateRequest(BaseModel):
    share_type: str = Field("pick", description="'pick', 'couple', or 'watchlist'")
    payload: Dict[str, Any]

class ShareResponse(BaseModel):
    token: str
    share_url: str
    share_type: str
    expires_in_seconds: int

class SimilarTitleItem(BaseModel):
    title: TitleResponse
    similarity_score: float

class SimilarTitlesResponse(BaseModel):
    source_title_id: str
    similar_titles: List[SimilarTitleItem]

class RoomCreateRequest(BaseModel):
    host_name: str = "Host"
    subscriptions: List[str] = []

class RoomCreateResponse(BaseModel):
    room_code: str
    host_name: str
    participants_count: int
    candidate_titles_count: int

class RoomJoinRequest(BaseModel):
    user_name: str
    subscriptions: List[str] = []

class RoomVoteRequest(BaseModel):
    user_name: str
    title_id: str
    vote: int = 1

class RoomStateResponse(BaseModel):
    room_code: str
    host_name: str
    participants: List[str]
    combined_subscriptions: List[str]
    candidates: List[Dict[str, Any]]
    winning_title: Optional[Dict[str, Any]] = None

class AlertNotificationItem(BaseModel):
    id: str
    type: str
    title_id: str
    title_name: str
    provider_name: str
    poster_url: str
    message: str
    action_url: str
    severity: str

class AnalyticsMetricsResponse(BaseModel):
    total_discovery_sessions: int
    discovery_success_rate_percent: float
    session_abandonment_rate_percent: float
    average_decision_latency_ms: float
    median_time_to_selection_seconds: float
    total_stream_clickthroughs: int
    provider_ctr_distribution: Dict[str, int]
