import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.data.seeder import seed_database
from app.models import Title
from app.services.watchlist_service import add_to_watchlist
from app.schemas import WatchlistCreateRequest
from app.services.alert_service import get_user_alerts

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

def test_get_user_alerts(test_db):
    # Add a title to watchlist that is free on default subscriptions (e.g. Inception on Netflix)
    inception = test_db.query(Title).filter(Title.title.ilike("%Inception%")).first()
    assert inception is not None
    add_to_watchlist(test_db, WatchlistCreateRequest(title_id=inception.id, status="saved"), user_id="test_user")

    alerts = get_user_alerts(test_db, user_id="test_user")
    assert len(alerts) >= 1
    assert any(a["title_id"] == inception.id for a in alerts)
    assert any("FREE" in a["message"] for a in alerts)
