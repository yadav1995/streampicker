import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.data.seeder import seed_database
from app.schemas import VibeSearchRequest
from app.services.semantic_engine import parse_natural_language_query, search_by_vibe

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

def test_natural_language_query_parser():
    criteria = parse_natural_language_query("mind-bending sci-fi thriller under 100 mins directed by Christopher Nolan")
    assert criteria.detected_mood == "Mind-Bending"
    assert "Sci-Fi" in criteria.detected_genres
    assert "Thriller" in criteria.detected_genres
    assert criteria.detected_max_runtime == 100
    assert "Christopher Nolan" in (criteria.detected_director_or_actor or "")

def test_search_by_vibe_execution(test_db):
    req = VibeSearchRequest(
        query="mind bending sci-fi thriller under 150 minutes",
        min_imdb_rating=7.0
    )
    res = search_by_vibe(test_db, req, user_id="test_user")
    assert res.results_count > 0
    assert len(res.results) > 0
    top_result = res.results[0]
    assert top_result.semantic_score >= 60.0
    assert len(top_result.match_explanation) > 0
