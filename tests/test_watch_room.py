import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.data.seeder import seed_database
from app.services.watch_room_service import room_manager

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

def test_watch_party_room_workflow(test_db):
    # 1. Create room
    create_res = room_manager.create_room("Alice", ["netflix", "prime_video"], test_db)
    code = create_res["room_code"]
    assert len(code) == 6
    assert create_res["host_name"] == "Alice"

    # 2. Join room
    join_res = room_manager.join_room(code, "Bob", ["hotstar", "sonyliv"])
    assert join_res is not None
    assert "Bob" in join_res["participants"]

    # 3. Cast votes
    state1 = room_manager.get_room_state(code, test_db)
    first_title_id = state1["candidates"][0]["title"]["id"]

    vote1 = room_manager.cast_vote(code, "Alice", first_title_id, 1)
    assert vote1["total_score"] == 1

    vote2 = room_manager.cast_vote(code, "Bob", first_title_id, 1)
    assert vote2["total_score"] == 2

    # 4. Check winning title
    state2 = room_manager.get_room_state(code, test_db)
    assert state2["winning_title"]["id"] == first_title_id
