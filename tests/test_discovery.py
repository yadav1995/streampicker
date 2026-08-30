import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models import Provider, Title, TitleProvider, UserSubscription
from app.data.seeder import seed_database
from app.schemas import PickRequest
from app.services.discovery_engine import pick_for_me

@pytest.fixture
def test_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine)
    db = TestingSession()
    seed_database(db, default_user_id="test_user")
    try:
        yield db
    finally:
        db.close()

def test_pick_for_me_with_mood_constraint(test_db):
    req = PickRequest(
        mood="Mind-Bending",
        max_runtime=160,
        min_imdb_rating=7.5,
        providers=["netflix", "prime_video"]
    )
    result = pick_for_me(test_db, req, user_id="test_user")
    assert result is not None
    assert result.match_score >= 60.0
    assert result.title.runtime_minutes <= 160
    assert result.title.rating_imdb >= 7.5
    assert len(result.match_reasons) > 0

def test_pick_for_me_strict_runtime_filter(test_db):
    req = PickRequest(
        max_runtime=90,  # e.g. Coherence (89m)
        min_imdb_rating=7.0
    )
    result = pick_for_me(test_db, req, user_id="test_user")
    assert result is not None
    assert result.title.runtime_minutes <= 90

def test_pick_for_me_exclude_history(test_db):
    req1 = PickRequest(mood="Mind-Bending", max_runtime=180)
    result1 = pick_for_me(test_db, req1, user_id="test_user")
    assert result1 is not None

    # Exclude the first title
    req2 = PickRequest(mood="Mind-Bending", max_runtime=180, exclude_title_ids=[result1.title.id])
    result2 = pick_for_me(test_db, req2, user_id="test_user")
    assert result2 is not None
    assert result2.title.id != result1.title.id
