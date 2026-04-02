# 🏀 Smart Pick Pro AI — Frontend

**NBA Prop Betting Analysis Engine — Powered by Local Historical Data**

This is the Streamlit frontend for Smart Pick Pro AI.  All NBA data is
read from the SmartPicksProAI SQLite database (`smartpicks.db`) — no live
NBA API calls are made at runtime.  The only live fetches are prop lines
from PrizePicks, Underdog Fantasy, and DraftKings Pick6.

---

## Prerequisites

Before running the frontend you must seed the database:

```bash
cd SmartPicksProAI/backend
python setup_db.py          # Create 39-table schema
python initial_pull.py      # Seed historical data (15-30 min)
```

See the [root README](../README.md) for full details.

---

## Running the App

```bash
pip install -r requirements.txt
streamlit run app.py
```

Opens at `http://localhost:8501`.

---

## How Data Flows

```
smartpicks.db  →  data/etl_data_service.py  →  data/nba_data_service.py  →  all pages
                  (40+ query functions)         (central routing module)
```

- **`etl_data_service.py`** connects to the SmartPicksProAI database read-only.
  It exposes 40+ functions covering all 39 tables and 5 AI views.
- **`nba_data_service.py`** is the single import point for every page and engine
  module.  It delegates all queries to `etl_data_service.py`.
- **Props** (PrizePicks, Underdog, DraftKings) are the only data fetched live,
  via `platform_fetcher.py` and `sportsbook_service.py`.

Database resolution order:
1. `SMARTPICKS_DB_PATH` environment variable
2. `../../SmartPicksProAI/backend/smartpicks.db` (relative to `data/`)
3. `db/etl_data.db` (legacy fallback)

---

## App Structure

```
SmartAI-NBA/
├── app.py                              # Main entry point — home dashboard
├── requirements.txt                    # Production dependencies (29 packages)
├── requirements-dev.txt                # Dev dependencies (pytest, httpx, etc.)
│
├── pages/
│   ├── 0_🏆_Live_Scores_&_Props.py    # Real-time NBA scores & stat leaders
│   ├── 1_📡_Live_Games.py             # Tonight's games + one-click setup
│   ├── 2_🔬_Prop_Scanner.py           # Enter/upload/fetch prop lines
│   ├── 3_⚡_Quantum_Analysis_Matrix.py # Main simulation engine
│   ├── 4_📋_Game_Report.py            # AI-powered SAFE Score™ game reports
│   ├── 5_💦_Live_Sweat.py             # Live AI Panic Room — in-game tracking
│   ├── 5b_🔮_Player_Simulator.py      # What-if player scenario simulator
│   ├── 6_🧬_Entry_Builder.py          # Build optimal DFS entries (parlays)
│   ├── 7_🎙️_The_Studio.py            # Joseph M. Smith AI analyst desk
│   ├── 8_🛡️_Risk_Shield.py           # Flagged picks to avoid
│   ├── 9_📡_Data_Feed.py              # Database status + refresh controls
│   ├── 10_🗺️_Correlation_Matrix.py   # Prop correlation analysis
│   ├── 11_📈_Bet_Tracker.py           # Bet tracking & model health
│   ├── 12_📊_Backtester.py            # Historical backtesting engine
│   ├── 13_⚙️_Settings.py             # Engine configuration
│   └── 14_💎_Subscription_Level.py    # Premium subscription (Stripe)
│
├── engine/                             # 40+ prediction/simulation modules
│   ├── simulation.py                   # Quantum Matrix Engine (Monte Carlo)
│   ├── projections.py                  # Player stat projections
│   ├── edge_detection.py              # Betting edge finder
│   ├── confidence.py                  # Confidence scoring + tier system
│   ├── entry_optimizer.py             # Optimal parlay construction
│   ├── game_prediction.py             # Game outcome prediction
│   ├── correlation.py                 # Prop correlation analysis
│   ├── backtester.py                  # Historical backtesting
│   ├── player_intelligence.py         # Player deep-dive intelligence
│   ├── joseph_brain.py                # Joseph M. Smith AI persona
│   └── ...                            # + 30 more modules
│
├── data/
│   ├── etl_data_service.py            # Bridge to smartpicks.db (40+ functions)
│   ├── nba_data_service.py            # Central routing — all pages import here
│   ├── platform_fetcher.py            # PrizePicks / Underdog prop fetching
│   ├── sportsbook_service.py          # DraftKings Pick6 prop fetching
│   ├── data_manager.py                # CSV data + session state helpers
│   ├── player_profile_service.py      # Player context & headshots
│   ├── roster_engine.py               # Active roster & injury engine
│   └── live_game_tracker.py           # Live game score tracker
│
├── agent/                              # AI analyst persona modules
│   ├── payload_builder.py             # Game state classifier
│   ├── live_persona.py                # Joseph's live commentary
│   └── response_parser.py             # Vibe response parsing
│
├── styles/                             # CSS themes
├── utils/                              # Shared UI components + helpers
├── tracking/                           # Bet tracking + SQLite wrapper
├── api/                                # FastAPI backend (optional)
├── config/                             # App configuration
├── scripts/                            # Utility scripts
│
├── tests/                              # 2,483 tests
│   ├── test_api/                       # API integration tests
│   ├── test_engine/                    # Engine module tests
│   └── ...
│
└── db/                                 # Auto-created on first run
    └── smartai_nba.db                  # Local bet tracking database
```

---

## Pages

### 🏠 Home (app.py)
Dashboard showing tonight's slate, status cards, and quick-start guide.

### 🏆 Page 0: Live Scores & Props
Real-time NBA scores and season stat leaders.

### 📡 Page 1: Live Games
Load tonight's matchups, fetch platform props with one click.

### 🔬 Page 2: Prop Scanner
Enter prop lines manually, upload CSV, or fetch live lines.

### ⚡ Page 3: Quantum Analysis Matrix
Main engine — simulate every prop.  Shows probability, edge, tier
(Platinum/Gold/Silver/Bronze), direction (OVER/UNDER), and forces.

### 📋 Page 4: Game Report
AI-powered game reports with SAFE Score™ analysis.

### 💦 Page 5: Live Sweat
Live AI Panic Room — track active bets during games with pace tracking
and Joseph M. Smith live commentary.

### 🔮 Page 5b: Player Simulator
What-if simulator — adjust minutes, pace, matchup factors.

### 🧬 Page 6: Entry Builder
Build optimal parlays with Expected Value optimization.

### 🎙️ Page 7: The Studio
Joseph M. Smith AI analyst desk — game breakdowns, scouting, bet building.

### 🛡️ Page 8: Risk Shield
Props to avoid with explanations (trap lines, low edge, sharp lines).

### 📡 Page 9: Data Feed
Database status and refresh controls.

### 🗺️ Page 10: Correlation Matrix
Prop correlation analysis for smarter parlays.

### 📈 Page 11: Bet Tracker
Track results, win rates by tier, model health monitoring.

### 📊 Page 12: Backtester
Validate the model against historical game logs.

### ⚙️ Page 13: Settings
Simulation depth, minimum edge, preset profiles, API keys.

### 💎 Page 14: Subscription
Premium subscription management (Stripe).

---

## Running Tests

```bash
pip install -r requirements-dev.txt
python -m pytest tests/ -v --tb=short
```

2,483 tests — ~5 minutes.

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `SMARTPICKS_DB_PATH` | Optional | Override path to smartpicks.db |
| `ODDS_API_KEY` | For DraftKings | The Odds API key |
| `STRIPE_SECRET_KEY` | For payments | Stripe secret key |
| `STRIPE_PUBLISHABLE_KEY` | For payments | Stripe publishable key |
| `STRIPE_PRICE_ID` | For payments | Stripe product price ID |
| `SMARTAI_PRODUCTION` | For production | Set to `"true"` for subscription gates |

---

## ⚠️ Disclaimer

This app is for **personal entertainment and analysis** only.
Always gamble responsibly.  Never bet more than you can afford to lose.

**Responsible Gambling:** Call **1-800-522-4700** or visit
[www.ncpgambling.org](https://www.ncpgambling.org).
