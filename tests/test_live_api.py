import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.data.seeder import seed_database
from app.services.tmdb_client import tmdb_client
from app.services.live_api_sync import sync_live_trending_titles

@pytest.fixture
def test_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine)
    db = TestingSession()
    seed_database(db, default_user_id="default_user")
    try:
        yield db
    finally:
        db.close()

def test_tmdb_client_fallback_trending():
    trending = tmdb_client.get_trending("day")
    assert len(trending) > 0
    first = trending[0]
    assert "title" in first or "name" in first

def test_live_api_sync_workflow(test_db):
    res = sync_live_trending_titles(test_db, max_titles=2)
    assert res["status"] == "success"
    assert res["synced_count"] >= 1
