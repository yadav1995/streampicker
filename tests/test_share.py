import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.data.seeder import seed_database
from app.services.share_service import (
    create_share_link,
    get_shared_content,
    export_watchlist_csv,
    export_watchlist_json
)
from app.services.watchlist_service import add_to_watchlist
from app.schemas import WatchlistCreateRequest
from app.models import Title

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

def test_create_and_get_share_link():
    res = create_share_link("pick", {"title_id": "123", "title": "Inception"}, ttl_seconds=60)
    assert "token" in res
    assert res["share_type"] == "pick"

    stored = get_shared_content(res["token"])
    assert stored is not None
    assert stored["payload"]["title"] == "Inception"

def test_export_watchlist(test_db):
    first_title = test_db.query(Title).first()
    assert first_title is not None
    add_to_watchlist(test_db, WatchlistCreateRequest(title_id=first_title.id, status="saved"), user_id="test_user")

    csv_data = export_watchlist_csv(test_db, user_id="test_user")
    assert "Title,Type,Release Year" in csv_data
    assert first_title.title in csv_data

    json_data = export_watchlist_json(test_db, user_id="test_user")
    assert len(json_data) >= 1
    assert json_data[0]["title"]["id"] == first_title.id
