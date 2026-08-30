import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.data.seeder import seed_database
from app.services.ingestion_worker import sync_catalog_deltas

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

def test_sync_catalog_deltas(test_db):
    result = sync_catalog_deltas(test_db)
    assert result["status"] == "success"
    assert result["synced_titles_count"] > 0
    assert result["cache_invalidated"] is True
