import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.data.seeder import seed_database
from app.schemas import GroupPickRequest, ViewerPreference
from app.services.group_watch_service import resolve_group_compromise

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

def test_resolve_group_compromise(test_db):
    req = GroupPickRequest(
        viewer_1=ViewerPreference(
            name="Alice",
            subscriptions=["netflix"],
            preferred_mood="Mind-Bending",
            preferred_genres=["Sci-Fi"]
        ),
        viewer_2=ViewerPreference(
            name="Bob",
            subscriptions=["prime_video"],
            preferred_mood="Adrenaline Rush",
            preferred_genres=["Action"]
        ),
        max_runtime=160,
        min_imdb_rating=7.5
    )
    res = resolve_group_compromise(test_db, req)
    assert res is not None
    assert res.compromise_score >= 50.0
    assert res.viewer_1_satisfaction > 0
    assert res.viewer_2_satisfaction > 0
    assert len(res.compromise_breakdown) > 0
