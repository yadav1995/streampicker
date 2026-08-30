import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.data.seeder import seed_database
from app.models import Title
from app.services.vector_search import find_similar_titles, hybrid_semantic_search

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

def test_find_similar_titles(test_db):
    inception = test_db.query(Title).filter(Title.title.ilike("%Inception%")).first()
    assert inception is not None

    similar = find_similar_titles(test_db, title_id=inception.id, limit=4, user_id="test_user")
    assert len(similar) > 0
    # Other Nolan or Sci-Fi / Mind-Bending movies like Interstellar / Oppenheimer should score high
    top_titles = [t.title for t, score in similar]
    assert any("Interstellar" in t or "Oppenheimer" in t or "Matrix" in t or "Coherence" in t for t in top_titles)

def test_hybrid_semantic_search(test_db):
    results = hybrid_semantic_search(test_db, query_text="space adventure emotional", limit=5)
    assert len(results) > 0
    top_title = results[0][0].title
    assert "Interstellar" in top_title or "Mandalorian" in top_title or "Dune" in top_title
