# 🏀 Smart Pick Pro AI

A fully local NBA prop-betting analysis platform.  **All predictions,
simulations, and analysis run off historical data seeded into a local
SQLite database** — no live API calls at runtime.

The system is split into two parts:

| Component | Purpose |
|-----------|---------|
| **SmartPicksProAI** (backend) | ETL pipeline — creates the database, seeds 39 tables of NBA data from `nba_api`, and keeps it current with incremental updates. |
| **Smart Pick Pro AI** (frontend) | Streamlit dashboard — 16 pages for prop analysis, game reports, player simulation, entry building, live sweating, backtesting, and more.  Reads exclusively from the seeded database (plus live prop lines from PrizePicks / Underdog / DraftKings). |

---

## 🚀 Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Create the database schema

```bash
cd SmartPicksProAI/backend
python setup_db.py
```

Creates `smartpicks.db` with **39 tables**, **43 indexes**, and **5 AI-ready
views**.  Safe to run multiple times — uses `IF NOT EXISTS`.

### 3. Seed historical data (run once)

```bash
cd SmartPicksProAI/backend
python initial_pull.py
```

Pulls the full **2025-26 NBA regular season** from `nba_api` and populates
every table.  This takes 15-30 minutes due to API rate limits.  Once
complete the database is fully self-contained — the frontend never makes
live NBA API calls.

### 4. Run the app

**Terminal 1 — FastAPI backend (optional, for the SmartPicksProAI admin UI):**

```bash
cd SmartPicksProAI/backend
uvicorn api:app --reload --port 8000
```

**Terminal 2 — Streamlit frontend (the main app):**

```bash
cd SmartAI-NBA
streamlit run app.py
```

Opens at `http://localhost:8501`.  All predictions, simulations, and
analysis run against the local `smartpicks.db`.

---

## How It Works

```
┌─────────────────────────────────────────────────────────────┐
│                      nba_api  (source)                      │
└──────────────────────────┬──────────────────────────────────┘
                           │  one-time seed (initial_pull.py)
                           │  incremental   (data_updater.py)
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    smartpicks.db  (SQLite)                   │
│  39 tables · 43 indexes · 5 views · ~500 MB fully seeded   │
└──────────────────────────┬──────────────────────────────────┘
                           │  read-only via etl_data_service.py
                           ▼
┌─────────────────────────────────────────────────────────────┐
│               Smart Pick Pro AI  (Streamlit)                │
│  16 pages · 40+ engine modules · Quantum Matrix Simulation  │
│  Props from PrizePicks / Underdog / DraftKings              │
└─────────────────────────────────────────────────────────────┘
```

---

## Project Structure

```
NBA_API-ETL/
│
├── SmartPicksProAI/                  # ETL backend
│   ├── backend/
│   │   ├── setup_db.py               # Create 39-table schema + indexes + views
│   │   ├── initial_pull.py           # One-time historical data seed
│   │   ├── data_updater.py           # Incremental update module
│   │   └── api.py                    # FastAPI backend (35+ endpoints)
│   │
│   └── frontend/
│       ├── api_service.py            # HTTP client with caching
│       └── app.py                    # SmartPicksProAI admin dashboard
│
├── SmartAI-NBA/                      # Smart Pick Pro AI frontend
│   ├── app.py                        # Main Streamlit entry point
│   ├── pages/                        # 16 analysis pages
│   ├── engine/                       # 40+ prediction/simulation modules
│   ├── data/
│   │   ├── etl_data_service.py       # Bridge to smartpicks.db (40+ query functions)
│   │   ├── nba_data_service.py       # Central routing — all pages import from here
│   │   ├── platform_fetcher.py       # PrizePicks / Underdog prop fetching
│   │   └── sportsbook_service.py     # DraftKings Pick6 prop fetching
│   ├── agent/                        # Joseph M. Smith AI analyst persona
│   ├── tracking/                     # Bet tracking + model health
│   ├── tests/                        # 2,483 tests
│   └── ...
│
├── requirements.txt                  # Shared Python dependencies
└── README.md                         # This file
```

---

## Database Schema (39 Tables)

### Core Tables (8)

| Table | Description |
|-------|-------------|
| **Players** | All NBA players — id, name, team, position, active status |
| **Teams** | 30 teams — abbreviation, conference, division, pace/ortg/drtg |
| **Games** | Every game — date, season, matchup, home/away scores |
| **Player_Game_Logs** | Per-player per-game stat lines (23 stat columns) |
| **Team_Game_Stats** | Per-team per-game stats — pace/ortg/drtg estimates |
| **Defense_Vs_Position** | Team defense multipliers by position (PG/SG/SF/PF/C) |
| **Team_Roster** | Current roster assignments with two-way/G-League flags |
| **Injury_Status** | Injury reports — status, reason, source |

### Per-Game Box Score Tables (7)

| Table | nba_api Endpoint |
|-------|------------------|
| **Box_Score_Advanced** | BoxScoreAdvancedV3 |
| **Box_Score_Scoring** | BoxScoreScoringV3 |
| **Box_Score_Misc** | (derived) |
| **Box_Score_Hustle** | (derived) |
| **Box_Score_Four_Factors** | (derived) |
| **Box_Score_Usage** | BoxScoreUsageV3 |
| **Box_Score_Matchups** | BoxScoreMatchupsV3 |

### Season-Level Dashboard Tables (8)

| Table | nba_api Endpoint |
|-------|------------------|
| **League_Dash_Player_Stats** | LeagueDashPlayerStats |
| **League_Dash_Team_Stats** | LeagueDashTeamStats |
| **Player_Estimated_Metrics** | PlayerEstimatedMetrics |
| **Team_Estimated_Metrics** | TeamEstimatedMetrics |
| **Player_Clutch_Stats** | LeagueDashPlayerClutch |
| **Team_Clutch_Stats** | LeagueDashTeamClutch |
| **Player_Hustle_Stats** | LeagueHustleStatsPlayer |
| **Team_Hustle_Stats** | LeagueHustleStatsTeam |

### API-Sourced Data Tables (6)

| Table | nba_api Endpoint |
|-------|------------------|
| **Standings** | LeagueStandingsV3 |
| **Schedule** | ScheduleLeagueV2 |
| **Play_By_Play** | PlayByPlayV3 |
| **Player_Bio** | LeagueDashPlayerBioStats |
| **Shot_Chart** | ShotChartDetail |
| **Player_Tracking_Stats** | BoxScorePlayerTrackV3 |

### Context & Historical Tables (10)

| Table | Description |
|-------|-------------|
| **League_Leaders** | Season stat leaders |
| **Common_Player_Info** | Detailed player bios |
| **Player_Career_Stats** | Career totals per season |
| **Team_Details** | Arena, owner, coach |
| **Game_Rotation** | Sub-in/sub-out data per game |
| **Draft_History** | Historical draft picks |
| **Synergy_Play_Types** | Play-type breakdowns |
| **League_Lineups** | Lineup combinations + stats |
| **Win_Probability_PBP** | Win probability by play |
| **Player_Awards** | (reserved) |

### AI-Ready Views (5)

| View | Description |
|------|-------------|
| `v_player_game_full` | Player logs joined with game context |
| `v_player_season_profile` | Season averages + bio + advanced metrics |
| `v_team_season_profile` | Team ratings + standings |
| `v_upcoming_matchups` | Schedule joined with team profiles |
| `v_defense_matchup_context` | DvP multipliers with team context |

---

## Data Seed — What `initial_pull.py` Populates

1. **Season game logs** — every player and team game log for 2025-26
2. **Teams** — all 30 teams with conference/division from `nba_api` static data
3. **Players** — every active player, with position from roster data
4. **Games** — every game with home/away scores back-filled from team stats
5. **Team pace/ortg/drtg** — season-level ratings computed from Team_Game_Stats
6. **Rosters** — full rosters via `CommonTeamRoster` (rate-limited: 1 req/team)
7. **Defense vs Position** — multipliers by 5-position model (PG/SG/SF/PF/C)
8. **Season dashboards** — clutch, hustle, bio, estimated metrics, league dash, leaders, standings (11 tables, one API call each)
9. **Per-player data** — career stats, shot chart detail (rate-limited: 1 req/player)
10. **Per-game box scores** — advanced, scoring, usage, tracking, matchups for every game

---

## Incremental Updates

After the initial seed, keep the database current:

```bash
cd SmartPicksProAI/backend
python -c "from data_updater import run_update; run_update()"
```

Or via the API:

```bash
curl -X POST http://localhost:8000/api/admin/refresh-data
```

The updater:
- Fetches only new game logs since the last stored date
- Upserts Players, Games, Player_Game_Logs, Team_Game_Stats
- Refreshes all season-level dashboards (11 tables)
- Fetches advanced box scores for new games
- Syncs today's schedule for the games/today endpoint

---

## FastAPI Endpoints (35+)

### Core Data
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/players/{id}/last5` | Last 5 game logs + averages |
| GET | `/api/players/search?q=name` | Case-insensitive player search |
| GET | `/api/games/today` | Today's NBA matchups (DB-driven) |
| GET | `/api/games/recent` | Recent completed games |
| GET | `/api/teams` | All 30 teams + pace/ortg/drtg |
| GET | `/api/teams/{id}/roster` | Team roster |
| GET | `/api/teams/{id}/stats?last_n=10` | Recent team game stats |
| GET | `/api/defense-vs-position/{abbrev}` | DvP multipliers |
| POST | `/api/admin/refresh-data` | Trigger incremental update |

### Player Deep-Dive
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/players/{id}/bio` | Player bio (height, weight, college) |
| GET | `/api/players/{id}/career` | Career stats by season |
| GET | `/api/players/{id}/advanced` | Advanced box score stats |
| GET | `/api/players/{id}/shot-chart` | Shot chart data |
| GET | `/api/players/{id}/tracking` | Player tracking stats |
| GET | `/api/players/{id}/clutch` | Clutch-time stats |
| GET | `/api/players/{id}/hustle` | Hustle stats |
| GET | `/api/players/{id}/scoring` | Scoring breakdown |
| GET | `/api/players/{id}/usage` | Usage rates |
| GET | `/api/players/{id}/matchups` | Defensive matchup data |

### Team Deep-Dive
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/teams/{id}/details` | Arena, owner, coach |
| GET | `/api/teams/{id}/clutch` | Team clutch stats |
| GET | `/api/teams/{id}/hustle` | Team hustle stats |
| GET | `/api/teams/{id}/estimated-metrics` | Estimated metrics |
| GET | `/api/teams/{id}/synergy` | Play-type breakdown |

### League & Game Context
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/standings` | Current NBA standings |
| GET | `/api/league-leaders` | Season stat leaders |
| GET | `/api/league-dash/players` | League-wide player dashboard |
| GET | `/api/league-dash/teams` | League-wide team dashboard |
| GET | `/api/schedule` | Full season schedule |
| GET | `/api/lineups` | Lineup stats |
| GET | `/api/draft-history` | Draft history |
| GET | `/api/games/{id}/play-by-play` | Play-by-play |
| GET | `/api/games/{id}/win-probability` | Win probability |
| GET | `/api/games/{id}/rotation` | Rotation data |
| GET | `/api/games/{id}/box-score` | Full box score |

---

## Frontend Pages (16)

| Page | Description |
|------|-------------|
| 🏠 **Home** | Dashboard — tonight's slate, status cards, quick-start guide |
| 🏆 **Live Scores & Props** | Real-time NBA scores and season stat leaders |
| 📡 **Live Games** | Tonight's matchups + one-click setup + live prop fetch |
| 🔬 **Prop Scanner** | Enter/upload/fetch prop lines (manual, CSV, or live) |
| ⚡ **Quantum Analysis Matrix** | Main engine — simulate every prop, get probabilities, tiers, and edges |
| 📋 **Game Report** | AI-powered SAFE Score™ game reports with confidence bars |
| 💦 **Live Sweat** | Live AI Panic Room — real-time bet tracking during games |
| 🔮 **Player Simulator** | What-if scenario simulator — adjust minutes, pace, matchup |
| 🧬 **Entry Builder** | Build optimal DFS parlays with EV optimization |
| 🎙️ **The Studio** | Joseph M. Smith AI analyst desk — game breakdowns, scouting, bet building |
| 🛡️ **Risk Shield** | Flagged props to avoid (trap lines, low edge, sharp lines) |
| 📡 **Data Feed** | Database status and refresh controls |
| 🗺️ **Correlation Matrix** | Prop correlation analysis for smarter parlays |
| 📈 **Bet Tracker** | Track results, win rates by tier, model health |
| 📊 **Backtester** | Validate the model against historical game logs |
| ⚙️ **Settings** | Simulation depth, minimum edge, preset profiles |
| 💎 **Subscription** | Premium subscription management (Stripe) |

---

## Engine Modules

The `engine/` directory contains 40+ modules powering all analysis:

| Module | Purpose |
|--------|---------|
| `simulation.py` | Quantum Matrix Engine — Monte Carlo prop simulation |
| `projections.py` | Player stat projections from historical data |
| `edge_detection.py` | Find betting edges (Goblin/Demon/Gold tier system) |
| `confidence.py` | Confidence scoring + tier assignment |
| `entry_optimizer.py` | Optimal parlay construction |
| `game_prediction.py` | Game outcome prediction |
| `game_script.py` | Game script modeling |
| `correlation.py` | Prop correlation analysis |
| `backtester.py` | Historical backtesting engine |
| `player_intelligence.py` | Player deep-dive intelligence |
| `matchup_history.py` | Head-to-head matchup analysis |
| `impact_metrics.py` | Player impact quantification |
| `lineup_analysis.py` | Lineup combination analysis |
| `rotation_tracker.py` | Minutes/rotation modeling |
| `live_math.py` | Live game pacing calculations |
| `joseph_brain.py` | Joseph M. Smith AI persona engine |
| `arbitrage_matcher.py` | Cross-book EV scanner |
| `clv_tracker.py` | Closing line value tracking |
| `bankroll.py` | Bankroll allocation optimizer |
| `calibration.py` | Model calibration tools |

---

## Data Sources

| Data | Source | When |
|------|--------|------|
| **All NBA stats** | `nba_api` → `smartpicks.db` | Seeded once via `initial_pull.py`, updated via `data_updater.py` |
| **PrizePicks props** | Live fetch via `platform_fetcher.py` | At runtime (page 1 or page 9) |
| **Underdog Fantasy props** | Live fetch via `platform_fetcher.py` | At runtime |
| **DraftKings Pick6 props** | Live fetch via `sportsbook_service.py` | At runtime |

All NBA data is local.  The only live fetches at runtime are prop lines from
sportsbook platforms.

---

## Running Tests

```bash
cd SmartAI-NBA
pip install -r requirements-dev.txt
python -m pytest tests/ -v --tb=short
```

2,483 tests covering data service integration, engine modules, API endpoints,
and page rendering.

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `SMARTPICKS_DB_PATH` | Optional | Override path to `smartpicks.db` |
| `ODDS_API_KEY` | For DraftKings | The Odds API key |
| `STRIPE_SECRET_KEY` | For payments | Stripe secret key |
| `STRIPE_PUBLISHABLE_KEY` | For payments | Stripe publishable key |
| `STRIPE_PRICE_ID` | For payments | Stripe product price ID |
| `STRIPE_WEBHOOK_SECRET` | Recommended | Stripe webhook signing secret |
| `SMARTAI_PRODUCTION` | For production | Set to `"true"` to enforce subscription gates |
| `APP_URL` | For Stripe | Deployed app URL |

---

## ⚠️ Disclaimer

This app is for **personal entertainment and analysis** only.
Always gamble responsibly.  Past model performance does not guarantee future results.
Never bet more than you can afford to lose.

**Responsible Gambling:** If you or someone you know has a gambling problem, call
the National Council on Problem Gambling helpline at **1-800-522-4700** or visit
[www.ncpgambling.org](https://www.ncpgambling.org).