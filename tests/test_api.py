import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine, SessionLocal
from app.data.seeder import seed_database
from app.models import Title

@pytest.fixture(scope="module", autouse=True)
def setup_test_app():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    seed_database(db, default_user_id="default_user")
    db.close()
    yield

def test_health_endpoint():
    with TestClient(app) as client:
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

def test_list_providers_endpoint():
    with TestClient(app) as client:
        response = client.get("/api/v1/providers")
        assert response.status_code == 200
        providers = response.json()
        assert len(providers) >= 6

def test_pick_for_me_endpoint():
    with TestClient(app) as client:
        payload = {
            "mood": "Adrenaline Rush",
            "max_runtime": 150,
            "min_imdb_rating": 7.0
        }
        response = client.post("/api/v1/discovery/pick", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "title" in data
        assert "match_score" in data

def test_vibe_search_endpoint():
    with TestClient(app) as client:
        payload = {
            "query": "mind-bending sci-fi under 120 mins",
            "min_imdb_rating": 7.0
        }
        response = client.post("/api/v1/discovery/vibe-search", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "extracted_criteria" in data
        assert len(data["results"]) > 0

def test_group_pick_endpoint():
    with TestClient(app) as client:
        payload = {
            "viewer_1": {
                "name": "Alex",
                "subscriptions": ["netflix"],
                "preferred_mood": "Mind-Bending"
            },
            "viewer_2": {
                "name": "Sam",
                "subscriptions": ["prime_video"],
                "preferred_mood": "Feel-Good & Uplifting"
            },
            "max_runtime": 180
        }
        response = client.post("/api/v1/discovery/group-pick", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "chosen_title" in data
        assert "compromise_score" in data

def test_watchlist_workflow():
    with TestClient(app) as client:
        titles_resp = client.get("/api/v1/titles?q=Coherence")
        assert titles_resp.status_code == 200
        item = titles_resp.json()["items"][0]
        title_id = item["id"]

        # Add to watchlist
        add_resp = client.post("/api/v1/watchlist", json={"title_id": title_id, "status": "saved"})
        assert add_resp.status_code == 200

        # Verify
        wl_resp = client.get("/api/v1/watchlist")
        assert wl_resp.status_code == 200
        assert any(w["title_id"] == title_id for w in wl_resp.json())

        # Feedback test
        fb_resp = client.post("/api/v1/history/feedback", json={"title_id": title_id, "liked": True})
        assert fb_resp.status_code == 200

        # Remove
        del_resp = client.delete(f"/api/v1/watchlist/{title_id}")
        assert del_resp.status_code == 200
