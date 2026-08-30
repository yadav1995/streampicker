# Product Problem Statement: OTT Catalog Fragmentation & Decision Fatigue

## 1. Executive Summary & Context
The digital streaming ecosystem is heavily fragmented. The average consumer actively manages between 3 to 6 Over-The-Top (OTT) streaming subscriptions (e.g., Netflix, Amazon Prime Video, Disney+ Hotstar, JioCinema, Apple TV+, SonyLIV). While access to high-quality content is at an all-time peak, the discovery experience has significantly degraded due to walled-garden catalog architectures, platform-exclusive licensing, and internal recommendation algorithms designed to maximize in-app dwell time rather than user satisfaction.

---

## 2. Core Problem Definition
Consumers experience chronic **"choice paralysis"** and **"catalog hopping fatigue,"** spending an average of **15 to 25 minutes per session** simply deciding what to watch. This decision latency degrades leisure time and leads to high bounce/session abandonment rates.

This overarching problem stems from three primary friction vectors:

### A. Catalog & Availability Silos
There is no unified, friction-free layer to immediately verify title availability. If a user wants to watch a specific film or series, they must execute a repetitive, manual search loop:
$$\text{Open App A} \longrightarrow \text{Search} \longrightarrow \text{Unavailable} \longrightarrow \text{Open App B} \longrightarrow \text{Search} \longrightarrow \text{Behind Paywall (Rent/Buy)}$$
This fragmented architecture hides whether a title is included in a user's active subscription, available via ad-supported tiers, or locked behind transactional video on demand (TVOD).

### B. High Cognitive Load in Open-Ended Discovery
When users do not have a specific title in mind, platform-native homepages present endless carousels optimized for self-promotion rather than relevance. Cross-referencing:
- Active subscriptions owned
- Specific genre / mood constraints
- Aggregated quality benchmarks (IMDb, Rotten Tomatoes, TMDB)
- Available watch time / runtime constraints

requires excessive cognitive overhead, often resulting in decision fatigue and abandoned viewing sessions.

### C. Underutilized Subscriptions & Redundant Purchases
Users struggle to track the consolidated catalog value of their active subscriptions. This leads to underutilizing paid services or accidentally purchasing/renting content on one platform (e.g., Apple TV / Prime Video Store) when it is already accessible for free on another active subscription (e.g., JioCinema / Hotstar).

---

## 3. Target User Persona & Friction Points

### User Persona: The Multi-Platform Streamer
- **Demographics:** Working professionals, digital natives, and binge-watchers (Ages 18–40) with 3+ active streaming subscriptions.
- **Behavior:** High screen time, values limited leisure hours, frequently watches content during evening wind-downs and weekends.

### Key Pain Points:
- **High Time-to-Play Latency:** Spends more time looking for content than actually watching it.
- **Fragmented Watchlists:** Inability to maintain a single list of bookmarked movies across disjointed apps.
- **Discovery Distrust:** Platform-specific recommendations feel algorithmic and biased toward proprietary originals rather than genuine match quality.

---

## 4. Product Objective & Success Metrics

### The Solution Objective
Build a lightweight, cross-platform discovery engine (**StreamPicker**) that aggregates multi-platform streaming availability into a single view and replaces infinite catalog scrolling with an instant, constraint-based selection mechanism.

### Key Success Metrics (MVP Goals):
- **Time-to-Selection:** Reduce the median time from app open to title selection to **$< 30\text{ seconds}$**.
- **Discovery Success Rate:** $\ge 75\%$ of "Pick For Me" sessions result in a user saving to watchlist, clicking a provider deep-link, or marking as "Watching".
- **Session Abandonment Rate:** Reduce discovery drop-off/app exit without a pick to **$< 10\%$**.
