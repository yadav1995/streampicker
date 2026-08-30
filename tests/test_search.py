import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.data.seeder import seed_database
from app.services.search_service import search_catalog

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

def test_search_by_keyword(test_db):
    titles, total = search_catalog(test_db, query_str="Nolan", user_id="test_user")
    assert total > 0
    assert any("Nolan" in t.director or "Oppenheimer" in t.title or "Inception" in t.title for t in titles)

def test_search_by_genre_and_provider(test_db):
    titles, total = search_catalog(
        test_db,
        genre="Sci-Fi",
        providers=["netflix"],
        user_id="test_user"
    )
    assert total > 0
    for t in titles:
        assert any("Sci-Fi" in g for g in t.genres)
        assert any(p.provider_id == "netflix" for p in t.providers)
