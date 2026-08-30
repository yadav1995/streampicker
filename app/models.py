import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    Boolean,
    Text,
    DateTime,
    ForeignKey,
    Index,
    Table
)
from sqlalchemy.orm import relationship
from app.database import Base

def generate_uuid():
    return str(uuid.uuid4())

def utc_now():
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=True)
    full_name = Column(String(255), nullable=False, default="Viewer")
    avatar_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    # Relationships
    subscriptions = relationship("UserSubscription", back_populates="user", cascade="all, delete-orphan")
    watchlist_items = relationship("WatchlistItem", back_populates="user", cascade="all, delete-orphan")
    feedbacks = relationship("UserFeedback", back_populates="user", cascade="all, delete-orphan")

class Provider(Base):
    __tablename__ = "providers"

    id = Column(String(50), primary_key=True)  # netflix, prime_video, hotstar, etc.
    name = Column(String(100), nullable=False)
    icon_url = Column(String(500), nullable=True)
    brand_color = Column(String(20), default="#E50914")
    badge_bg = Column(String(30), default="rgba(229, 9, 20, 0.15)")
    monthly_price_inr = Column(Float, default=199.0)
    is_active = Column(Boolean, default=True)
    display_priority = Column(Integer, default=100)
    created_at = Column(DateTime, default=utc_now)

    # Relationships
    titles = relationship("TitleProvider", back_populates="provider")
    user_subscriptions = relationship("UserSubscription", back_populates="provider")

class Title(Base):
    __tablename__ = "titles"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    tmdb_id = Column(String(50), unique=True, index=True, nullable=True)
    imdb_id = Column(String(50), unique=True, index=True, nullable=True)
    title = Column(String(255), nullable=False, index=True)
    original_title = Column(String(255), nullable=True)
    type = Column(String(20), nullable=False, default="movie")  # movie, series
    runtime_minutes = Column(Integer, default=90)
    release_year = Column(Integer, nullable=False)
    genres = Column(String(255), default="Drama")  # comma-separated
    mood_tags = Column(String(255), default="Feel-Good")  # comma-separated
    director = Column(String(255), nullable=True)
    cast_members = Column(Text, nullable=True)  # comma-separated
    rating_imdb = Column(Float, default=7.0)
    rating_tmdb = Column(Float, default=7.0)
    rating_rotten_tomatoes = Column(Integer, default=75)
    overview = Column(Text, nullable=True)
    poster_url = Column(String(500), nullable=True)
    backdrop_url = Column(String(500), nullable=True)
    trailer_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    # Relationships
    providers = relationship("TitleProvider", back_populates="title", cascade="all, delete-orphan")
    watchlist_entries = relationship("WatchlistItem", back_populates="title", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_title_runtime_rating", "type", "runtime_minutes", "rating_imdb"),
    )

class TitleProvider(Base):
    __tablename__ = "title_providers"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title_id = Column(String(36), ForeignKey("titles.id", ondelete="CASCADE"), nullable=False)
    provider_id = Column(String(50), ForeignKey("providers.id", ondelete="CASCADE"), nullable=False)
    access_type = Column(String(20), default="flatrate")  # flatrate, free, ads, rent, buy
    price = Column(Float, nullable=True)  # INR rental/purchase price if applicable
    currency = Column(String(10), default="INR")
    web_url = Column(String(500), nullable=False)
    deep_link = Column(String(500), nullable=False)
    available_from = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=utc_now)

    # Relationships
    title = relationship("Title", back_populates="providers")
    provider = relationship("Provider", back_populates="titles")

    __table_args__ = (
        Index("idx_title_provider", "title_id", "provider_id"),
    )

class UserSubscription(Base):
    __tablename__ = "user_subscriptions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), default="default_user", index=True)
    provider_id = Column(String(50), ForeignKey("providers.id", ondelete="CASCADE"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utc_now)

    # Relationships
    user = relationship("User", back_populates="subscriptions")
    provider = relationship("Provider", back_populates="user_subscriptions")

    __table_args__ = (
        Index("idx_user_subscription", "user_id", "provider_id"),
    )

class WatchlistItem(Base):
    __tablename__ = "watchlist_items"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), default="default_user", index=True)
    title_id = Column(String(36), ForeignKey("titles.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(20), default="saved")  # saved, watching, watched, dropped
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    # Relationships
    user = relationship("User", back_populates="watchlist_items")
    title = relationship("Title", back_populates="watchlist_entries")

    __table_args__ = (
        Index("idx_user_watchlist", "user_id", "title_id"),
    )

class UserFeedback(Base):
    __tablename__ = "user_feedback"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), default="default_user", index=True)
    title_id = Column(String(36), ForeignKey("titles.id", ondelete="CASCADE"), nullable=False)
    liked = Column(Boolean, nullable=True)  # True = thumbs up, False = thumbs down
    rating = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)

    user = relationship("User", back_populates="feedbacks")
