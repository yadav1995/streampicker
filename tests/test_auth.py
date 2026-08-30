import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from app.database import Base, get_db
from app.models import User, Title
from app.data.seeder import seed_database
from app.main import app
from app.services.auth_service import hash_password, verify_password, create_access_token, decode_access_token

@pytest.fixture
def client_with_db():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    db = TestingSession()
    seed_database(db, default_user_id="default_user")
    db.close()

    def override_get_db():
        db_session = TestingSession()
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

def test_password_hashing():
    pw = "SuperSecretPassword123!"
    hashed = hash_password(pw)
    assert hashed != pw
    assert verify_password(pw, hashed) is True
    assert verify_password("WrongPassword", hashed) is False

def test_jwt_token_generation_and_decoding():
    token = create_access_token("u123", "test@streampicker.com", "Test User", expires_in=3600)
    assert isinstance(token, str)
    
    payload = decode_access_token(token)
    assert payload is not None
    assert payload["sub"] == "u123"
    assert payload["email"] == "test@streampicker.com"
    assert payload["name"] == "Test User"

def test_user_registration_and_login_workflow(client_with_db):
    # 1. Register User
    reg_res = client_with_db.post("/api/v1/auth/register", json={
        "email": "sarah@streampicker.com",
        "password": "Password123",
        "full_name": "Sarah Connor"
    })
    assert reg_res.status_code == 200
    data = reg_res.json()
    assert "access_token" in data
    token = data["access_token"]
    assert data["user"]["email"] == "sarah@streampicker.com"

    # 2. Prevent duplicate registration
    dup_res = client_with_db.post("/api/v1/auth/register", json={
        "email": "sarah@streampicker.com",
        "password": "Password123",
        "full_name": "Sarah Connor"
    })
    assert dup_res.status_code == 400

    # 3. Login User
    login_res = client_with_db.post("/api/v1/auth/login", json={
        "email": "sarah@streampicker.com",
        "password": "Password123"
    })
    assert login_res.status_code == 200
    assert "access_token" in login_res.json()

    # 4. Reject Wrong Password
    bad_login = client_with_db.post("/api/v1/auth/login", json={
        "email": "sarah@streampicker.com",
        "password": "WrongPassword!"
    })
    assert bad_login.status_code == 401

    # 5. Access Protected Profile
    me_res = client_with_db.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    assert me_res.json()["email"] == "sarah@streampicker.com"

def test_multi_user_isolation(client_with_db):
    # Register Alice
    res1 = client_with_db.post("/api/v1/auth/register", json={
        "email": "alice_test@streampicker.com",
        "password": "Password123",
        "full_name": "Alice"
    })
    alice_token = res1.json()["access_token"]

    # Register Bob
    res2 = client_with_db.post("/api/v1/auth/register", json={
        "email": "bob_test@streampicker.com",
        "password": "Password123",
        "full_name": "Bob"
    })
    bob_token = res2.json()["access_token"]

    # Alice sets subscriptions to only Netflix
    client_with_db.put("/api/v1/subscriptions", json={"provider_ids": ["netflix"]}, headers={"Authorization": f"Bearer {alice_token}"})

    # Bob sets subscriptions to only Apple TV+
    client_with_db.put("/api/v1/subscriptions", json={"provider_ids": ["apple_tv"]}, headers={"Authorization": f"Bearer {bob_token}"})

    # Verify Alice's subscriptions
    alice_subs = client_with_db.get("/api/v1/providers", headers={"Authorization": f"Bearer {alice_token}"}).json()
    alice_active = [p["id"] for p in alice_subs if p["is_subscribed"]]
    assert alice_active == ["netflix"]

    # Verify Bob's subscriptions
    bob_subs = client_with_db.get("/api/v1/providers", headers={"Authorization": f"Bearer {bob_token}"}).json()
    bob_active = [p["id"] for p in bob_subs if p["is_subscribed"]]
    assert bob_active == ["apple_tv"]
