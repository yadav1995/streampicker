# StreamPicker — High-Performance OTT Discovery & Constraint Solver Engine

StreamPicker is an intelligent OTT aggregation and recommendation engine engineered to eliminate streaming catalog fragmentation and choice paralysis across **Netflix, Amazon Prime Video, Disney+ Hotstar, JioCinema, Apple TV+, SonyLIV, and ZEE5**.

---

## 🌟 Core Feature Matrix

| Feature | Description |
| :--- | :--- |
| **🎯 Rapid Constraint Solver** | Solves intersection of user subscriptions, mood, runtime bounds ($\le 90\text{m}$, $\le 120\text{m}$), and IMDb rating in $< 30\text{ms}$. |
| **🔮 AI Semantic Vibe Search** | Natural language conversational search mapping human vibes (*"mind bending sci-fi thriller under 100 mins"*) to titles. |
| **👥 Watch Together / Couple Mode** | Merges 2 viewers' subscriptions and calculates a mutual compromise pick with satisfaction metrics. |
| **🍿 Collaborative Watch Party** | Multi-user live rooms with 6-character room codes (`STREAM-XXX`) and real-time voting. |
| **💰 Subscription ROI Optimizer** | Monthly spend tracker, catalog coverage %, and anti-waste warnings for redundant movie rentals. |
| **🔗 Universal Deep Linking** | Device-aware router for **iOS Universal Links**, **Android App Intents**, **Desktop Web**, and **Smart TV**. |
| **⚡ High-Speed Caching & Rate Limiting** | Dual-mode Redis + in-memory TTL caching tier with sliding-window token-bucket rate limiter. |
| **📑 Unified Watchlist & Export** | Centralized bookmarking with 1-click **CSV** and **JSON** exports. |
| **🧠 Vector Space Similarity** | Cosine similarity model generating **"More Like This"** recommendations. |
| **📊 Telemetry & Analytics Dashboard** | Real-time tracking of time-to-selection latency distribution, provider CTR, and cache hit efficiency. |

---

## 🚀 Quick Start (Local Development)

### 1. Requirements
- Python 3.10+ (SQLite is included out of the box)

### 2. Install & Run
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start StreamPicker
python run.py
```
Open **[http://localhost:8000](http://localhost:8000)** in your browser.

### 3. Run Automated Tests
```bash
python -m pytest tests/ -v
```

---

## 🐳 Production Deployment with Docker Compose

StreamPicker includes a production multi-container setup with **FastAPI**, **PostgreSQL 16**, and **Redis 7**.

### 1-Click Launch:
```bash
docker-compose up -d --build
```
This automatically boots:
- `streampicker_web`: FastAPI web app on port `8000`
- `streampicker_db`: PostgreSQL database on port `5432` with persistent storage
- `streampicker_redis`: Redis cache & rate limiter on port `6379` with health checks

Check container logs:
```bash
docker-compose logs -f web
```

---

## ☁️ Cloud Deployment Options

### Deploy to Render / Railway / Fly.io
1. Connect your GitHub repository.
2. Select **Dockerfile** as build type or use `docker-compose.yml`.
3. Set environment variables:
   - `DATABASE_URL`: Your PostgreSQL connection string.
   - `REDIS_URL`: Your Redis connection string.
   - `ENVIRONMENT`: `production`

---

## 🛠️ Tech Stack
- **Backend**: FastAPI, SQLAlchemy, Pydantic V2, Uvicorn, Gunicorn
- **Database**: PostgreSQL (Production) / SQLite (Local)
- **Cache & Rate Limiting**: Redis 7 / In-Memory TTL Cache
- **Frontend**: Zero-dependency SPA (HTML5, Tailwind CSS, Lucide Icons, Vanilla JS)
- **Testing**: Pytest, HTTPX
