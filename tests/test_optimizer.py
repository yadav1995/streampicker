import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.data.seeder import seed_database
from app.models import Title
from app.services.subscription_optimizer import calculate_subscription_roi, check_title_redundancy

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

def test_check_title_redundancy(test_db):
    # Oppenheimer is available for flatrate on Hotstar and for rent on Prime Video
    oppenheimer = test_db.query(Title).filter(Title.title.ilike("%Oppenheimer%")).first()
    assert oppenheimer is not None

    redundancy = check_title_redundancy(test_db, oppenheimer.id, user_id="test_user")
    # test_user has hotstar in default subscriptions
    assert redundancy.is_redundant is True
    assert "Save money" in redundancy.redundancy_message
