"""
setup_db.py
-----------
Creates the smartpicks.db SQLite database and initialises all tables used by
the SmartPicksProAI data pipeline.

Run this script once before any other pipeline script:
    python setup_db.py

NOTE: The Player_Game_Logs table uses a composite PRIMARY KEY (player_id,
game_id) which replaces the old log_id autoincrement PK.  Because SQLite
does not support ALTER TABLE … ADD PRIMARY KEY, this composite PK only takes
effect on a fresh database.  Existing databases with the old log_id schema
must be re-initialised (delete smartpicks.db and re-run this script followed
by initial_pull.py).
"""

import logging
import sqlite3

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

DB_PATH = "smartpicks.db"

CREATE_PLAYERS = """
CREATE TABLE IF NOT EXISTS Players (
    player_id          INTEGER PRIMARY KEY,
    first_name         TEXT    NOT NULL,
    last_name          TEXT    NOT NULL,
    full_name          TEXT,
    team_id            INTEGER,
    team_abbreviation  TEXT,
    position           TEXT,
    is_active          INTEGER DEFAULT 1
);
"""

CREATE_TEAMS = """
CREATE TABLE IF NOT EXISTS Teams (
    team_id        INTEGER PRIMARY KEY,
    abbreviation   TEXT    NOT NULL,
    team_name      TEXT    NOT NULL,
    conference     TEXT,
    division       TEXT,
    pace           REAL,
    ortg           REAL,
    drtg           REAL
);
"""

CREATE_GAMES = """
CREATE TABLE IF NOT EXISTS Games (
    game_id        TEXT    PRIMARY KEY,
    game_date      TEXT    NOT NULL,
    season         TEXT,
    home_team_id   INTEGER,
    away_team_id   INTEGER,
    home_abbrev    TEXT,
    away_abbrev    TEXT,
    matchup        TEXT,
    home_score     INTEGER,
    away_score     INTEGER
);
"""

# NOTE: The composite PRIMARY KEY (player_id, game_id) only applies to fresh
# databases.  See module docstring for migration instructions.
CREATE_PLAYER_GAME_LOGS = """
CREATE TABLE IF NOT EXISTS Player_Game_Logs (
    player_id   INTEGER NOT NULL REFERENCES Players(player_id),
    game_id     TEXT    NOT NULL REFERENCES Games(game_id),
    wl          TEXT,
    min         TEXT,
    pts         INTEGER,
    reb         INTEGER,
    ast         INTEGER,
    stl         INTEGER,
    blk         INTEGER,
    tov         INTEGER,
    fgm         INTEGER,
    fga         INTEGER,
    fg_pct      REAL,
    fg3m        INTEGER,
    fg3a        INTEGER,
    fg3_pct     REAL,
    ftm         INTEGER,
    fta         INTEGER,
    ft_pct      REAL,
    oreb        INTEGER,
    dreb        INTEGER,
    pf          INTEGER,
    plus_minus  REAL,
    PRIMARY KEY (player_id, game_id)
);
"""

CREATE_TEAM_GAME_STATS = """
CREATE TABLE IF NOT EXISTS Team_Game_Stats (
    game_id          TEXT    NOT NULL REFERENCES Games(game_id),
    team_id          INTEGER NOT NULL REFERENCES Teams(team_id),
    opponent_team_id INTEGER,
    is_home          INTEGER,
    points_scored    INTEGER,
    points_allowed   INTEGER,
    pace_est         REAL,
    ortg_est         REAL,
    drtg_est         REAL,
    PRIMARY KEY (game_id, team_id)
);
"""

CREATE_DEFENSE_VS_POSITION = """
CREATE TABLE IF NOT EXISTS Defense_Vs_Position (
    team_abbreviation  TEXT    NOT NULL,
    season             TEXT    NOT NULL,
    pos                TEXT    NOT NULL,
    vs_pts_mult        REAL    DEFAULT 1.0,
    vs_reb_mult        REAL    DEFAULT 1.0,
    vs_ast_mult        REAL    DEFAULT 1.0,
    vs_stl_mult        REAL    DEFAULT 1.0,
    vs_blk_mult        REAL    DEFAULT 1.0,
    vs_3pm_mult        REAL    DEFAULT 1.0,
    PRIMARY KEY (team_abbreviation, season, pos)
);
"""

CREATE_TEAM_ROSTER = """
CREATE TABLE IF NOT EXISTS Team_Roster (
    team_id              INTEGER NOT NULL REFERENCES Teams(team_id),
    player_id            INTEGER NOT NULL REFERENCES Players(player_id),
    effective_start_date TEXT,
    effective_end_date   TEXT,
    is_two_way           INTEGER DEFAULT 0,
    is_g_league          INTEGER DEFAULT 0,
    PRIMARY KEY (team_id, player_id, effective_start_date)
);
"""

CREATE_INJURY_STATUS = """
CREATE TABLE IF NOT EXISTS Injury_Status (
    player_id       INTEGER NOT NULL REFERENCES Players(player_id),
    team_id         INTEGER,
    report_date     TEXT    NOT NULL,
    status          TEXT    NOT NULL,
    reason          TEXT,
    source          TEXT,
    last_updated_ts TEXT,
    PRIMARY KEY (player_id, report_date)
);
"""

# ---------------------------------------------------------------------------
# New tables for previously-unhandled NBA API data
# ---------------------------------------------------------------------------

CREATE_STANDINGS = """
CREATE TABLE IF NOT EXISTS Standings (
    season_id              TEXT    NOT NULL,
    team_id                INTEGER NOT NULL REFERENCES Teams(team_id),
    conference             TEXT,
    conference_record      TEXT,
    playoff_rank           INTEGER,
    clinch_indicator       TEXT,
    division               TEXT,
    division_record        TEXT,
    division_rank          INTEGER,
    wins                   INTEGER,
    losses                 INTEGER,
    win_pct                REAL,
    league_rank            INTEGER,
    record                 TEXT,
    home                   TEXT,
    road                   TEXT,
    l10                    TEXT,
    last10_home            TEXT,
    last10_road            TEXT,
    ot                     TEXT,
    three_pts_or_less      TEXT,
    ten_pts_or_more        TEXT,
    long_home_streak       INTEGER,
    long_road_streak       INTEGER,
    long_win_streak        INTEGER,
    long_loss_streak       INTEGER,
    current_home_streak    INTEGER,
    current_road_streak    INTEGER,
    current_streak         INTEGER,
    str_current_streak     TEXT,
    conference_games_back  REAL,
    division_games_back    REAL,
    clinched_conf_title    INTEGER,
    clinched_div_title     INTEGER,
    clinched_playoff       INTEGER,
    eliminated_conf        INTEGER,
    eliminated_div         INTEGER,
    ahead_at_half          TEXT,
    behind_at_half         TEXT,
    tied_at_half           TEXT,
    ahead_at_third         TEXT,
    behind_at_third        TEXT,
    tied_at_third          TEXT,
    score_100pts           TEXT,
    opp_score_100pts       TEXT,
    opp_over_500           TEXT,
    lead_in_fg_pct         TEXT,
    lead_in_reb            TEXT,
    fewer_turnovers        TEXT,
    points_pg              REAL,
    opp_points_pg          REAL,
    diff_points_pg         REAL,
    vs_east                TEXT,
    vs_atlantic            TEXT,
    vs_central             TEXT,
    vs_southeast           TEXT,
    vs_west                TEXT,
    vs_northwest           TEXT,
    vs_pacific             TEXT,
    vs_southwest           TEXT,
    PRIMARY KEY (season_id, team_id)
);
"""

CREATE_SCHEDULE = """
CREATE TABLE IF NOT EXISTS Schedule (
    game_id              TEXT    PRIMARY KEY,
    season_year          TEXT,
    game_date            TEXT    NOT NULL,
    game_code            TEXT,
    game_status          INTEGER,
    game_status_text     TEXT,
    game_sequence        INTEGER,
    game_date_est        TEXT,
    game_time_est        TEXT,
    game_datetime_est    TEXT,
    game_date_utc        TEXT,
    game_time_utc        TEXT,
    game_datetime_utc    TEXT,
    day                  TEXT,
    month_num            INTEGER,
    week_number          INTEGER,
    week_name            TEXT,
    if_necessary         INTEGER,
    series_game_number   TEXT,
    game_label           TEXT,
    game_sub_label       TEXT,
    series_text          TEXT,
    arena_name           TEXT,
    arena_state          TEXT,
    arena_city           TEXT,
    postponed_status     TEXT,
    game_subtype         TEXT,
    is_neutral           INTEGER,
    home_team_id         INTEGER REFERENCES Teams(team_id),
    home_team_name       TEXT,
    home_team_city       TEXT,
    home_team_tricode    TEXT,
    home_team_wins       INTEGER,
    home_team_losses     INTEGER,
    home_team_score      INTEGER,
    home_team_seed       INTEGER,
    away_team_id         INTEGER REFERENCES Teams(team_id),
    away_team_name       TEXT,
    away_team_city       TEXT,
    away_team_tricode    TEXT,
    away_team_wins       INTEGER,
    away_team_losses     INTEGER,
    away_team_score      INTEGER,
    away_team_seed       INTEGER
);
"""

CREATE_PLAY_BY_PLAY = """
CREATE TABLE IF NOT EXISTS Play_By_Play (
    game_id        TEXT    NOT NULL REFERENCES Games(game_id),
    action_number  INTEGER NOT NULL,
    clock          TEXT,
    period         INTEGER,
    team_id        INTEGER REFERENCES Teams(team_id),
    team_tricode   TEXT,
    person_id      INTEGER REFERENCES Players(player_id),
    player_name    TEXT,
    player_name_i  TEXT,
    x_legacy       REAL,
    y_legacy       REAL,
    shot_distance  REAL,
    shot_result    TEXT,
    is_field_goal  INTEGER,
    score_home     TEXT,
    score_away     TEXT,
    points_total   INTEGER,
    location       TEXT,
    description    TEXT,
    action_type    TEXT,
    sub_type       TEXT,
    video_available INTEGER,
    action_id      INTEGER,
    PRIMARY KEY (game_id, action_number)
);
"""

CREATE_PLAYER_BIO = """
CREATE TABLE IF NOT EXISTS Player_Bio (
    player_id            INTEGER PRIMARY KEY REFERENCES Players(player_id),
    player_name          TEXT,
    team_id              INTEGER REFERENCES Teams(team_id),
    team_abbreviation    TEXT,
    age                  REAL,
    player_height        TEXT,
    player_height_inches REAL,
    player_weight        REAL,
    college              TEXT,
    country              TEXT,
    draft_year           TEXT,
    draft_round          TEXT,
    draft_number         TEXT,
    gp                   INTEGER,
    pts                  REAL,
    reb                  REAL,
    ast                  REAL,
    net_rating           REAL,
    oreb_pct             REAL,
    dreb_pct             REAL,
    usg_pct              REAL,
    ts_pct               REAL,
    ast_pct              REAL
);
"""

CREATE_SHOT_CHART = """
CREATE TABLE IF NOT EXISTS Shot_Chart (
    game_id            TEXT    NOT NULL REFERENCES Games(game_id),
    game_event_id      INTEGER NOT NULL,
    player_id          INTEGER NOT NULL REFERENCES Players(player_id),
    player_name        TEXT,
    team_id            INTEGER REFERENCES Teams(team_id),
    team_name          TEXT,
    period             INTEGER,
    minutes_remaining  INTEGER,
    seconds_remaining  INTEGER,
    event_type         TEXT,
    action_type        TEXT,
    shot_type          TEXT,
    shot_zone_basic    TEXT,
    shot_zone_area     TEXT,
    shot_zone_range    TEXT,
    shot_distance      INTEGER,
    loc_x              REAL,
    loc_y              REAL,
    shot_attempted_flag INTEGER,
    shot_made_flag     INTEGER,
    game_date          TEXT,
    htm                TEXT,
    vtm                TEXT,
    PRIMARY KEY (game_id, game_event_id, player_id)
);
"""

CREATE_PLAYER_TRACKING = """
CREATE TABLE IF NOT EXISTS Player_Tracking_Stats (
    game_id                       TEXT    NOT NULL REFERENCES Games(game_id),
    person_id                     INTEGER NOT NULL REFERENCES Players(player_id),
    team_id                       INTEGER REFERENCES Teams(team_id),
    team_tricode                  TEXT,
    first_name                    TEXT,
    family_name                   TEXT,
    position                      TEXT,
    comment                       TEXT,
    jersey_num                    TEXT,
    minutes                       TEXT,
    speed                         REAL,
    distance                      REAL,
    rebound_chances_offensive     REAL,
    rebound_chances_defensive     REAL,
    rebound_chances_total         REAL,
    touches                       REAL,
    secondary_assists             REAL,
    free_throw_assists            REAL,
    passes                        REAL,
    assists                       REAL,
    contested_fg_made             REAL,
    contested_fg_attempted        REAL,
    contested_fg_pct              REAL,
    uncontested_fg_made           REAL,
    uncontested_fg_attempted      REAL,
    uncontested_fg_pct            REAL,
    fg_pct                        REAL,
    defended_at_rim_fg_made       REAL,
    defended_at_rim_fg_attempted  REAL,
    defended_at_rim_fg_pct        REAL,
    PRIMARY KEY (game_id, person_id)
);
"""

# New columns added to Players for existing databases.
_PLAYERS_ALTER = [
    "ALTER TABLE Players ADD COLUMN full_name TEXT",
    "ALTER TABLE Players ADD COLUMN team_abbreviation TEXT",
    "ALTER TABLE Players ADD COLUMN position TEXT",
    "ALTER TABLE Players ADD COLUMN is_active INTEGER DEFAULT 1",
]

# New columns added to Games for existing databases.
_GAMES_ALTER = [
    "ALTER TABLE Games ADD COLUMN season TEXT",
    "ALTER TABLE Games ADD COLUMN home_team_id INTEGER",
    "ALTER TABLE Games ADD COLUMN away_team_id INTEGER",
    "ALTER TABLE Games ADD COLUMN home_abbrev TEXT",
    "ALTER TABLE Games ADD COLUMN away_abbrev TEXT",
    "ALTER TABLE Games ADD COLUMN home_score INTEGER",
    "ALTER TABLE Games ADD COLUMN away_score INTEGER",
]

# New stat columns added to Player_Game_Logs for existing databases.
_LOGS_ALTER = [
    "ALTER TABLE Player_Game_Logs ADD COLUMN wl TEXT",
    "ALTER TABLE Player_Game_Logs ADD COLUMN fgm INTEGER",
    "ALTER TABLE Player_Game_Logs ADD COLUMN fga INTEGER",
    "ALTER TABLE Player_Game_Logs ADD COLUMN fg_pct REAL",
    "ALTER TABLE Player_Game_Logs ADD COLUMN fg3m INTEGER",
    "ALTER TABLE Player_Game_Logs ADD COLUMN fg3a INTEGER",
    "ALTER TABLE Player_Game_Logs ADD COLUMN fg3_pct REAL",
    "ALTER TABLE Player_Game_Logs ADD COLUMN ftm INTEGER",
    "ALTER TABLE Player_Game_Logs ADD COLUMN fta INTEGER",
    "ALTER TABLE Player_Game_Logs ADD COLUMN ft_pct REAL",
    "ALTER TABLE Player_Game_Logs ADD COLUMN oreb INTEGER",
    "ALTER TABLE Player_Game_Logs ADD COLUMN dreb INTEGER",
    "ALTER TABLE Player_Game_Logs ADD COLUMN pf INTEGER",
    "ALTER TABLE Player_Game_Logs ADD COLUMN plus_minus REAL",
]


def create_tables(db_path: str = DB_PATH) -> None:
    """Create all SmartPicksProAI tables in *db_path*.

    Uses IF NOT EXISTS clauses so it is safe to call multiple times without
    overwriting existing data.  For existing databases that pre-date this
    schema version, ALTER TABLE … ADD COLUMN IF NOT EXISTS statements add the
    new columns to Players, Games, and Player_Game_Logs automatically.

    Args:
        db_path: Path to the SQLite database file.  Created automatically if
                 it does not already exist.
    """
    logger.info("Connecting to database: %s", db_path)
    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()

        logger.info("Creating table: Players")
        cursor.execute(CREATE_PLAYERS)
        logger.info("Creating table: Teams")
        cursor.execute(CREATE_TEAMS)
        logger.info("Creating table: Games")
        cursor.execute(CREATE_GAMES)
        logger.info("Creating table: Player_Game_Logs")
        cursor.execute(CREATE_PLAYER_GAME_LOGS)
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_pgl_player_date "
            "ON Player_Game_Logs (player_id, game_id)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_pgl_game "
            "ON Player_Game_Logs (game_id)"
        )
        logger.info("Creating table: Team_Game_Stats")
        cursor.execute(CREATE_TEAM_GAME_STATS)
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_tgs_team "
            "ON Team_Game_Stats (team_id)"
        )
        logger.info("Creating table: Defense_Vs_Position")
        cursor.execute(CREATE_DEFENSE_VS_POSITION)
        logger.info("Creating table: Team_Roster")
        cursor.execute(CREATE_TEAM_ROSTER)
        logger.info("Creating table: Injury_Status")
        cursor.execute(CREATE_INJURY_STATUS)

        # --- New tables for previously-unhandled NBA API data ---
        logger.info("Creating table: Standings")
        cursor.execute(CREATE_STANDINGS)
        logger.info("Creating table: Schedule")
        cursor.execute(CREATE_SCHEDULE)
        logger.info("Creating table: Play_By_Play")
        cursor.execute(CREATE_PLAY_BY_PLAY)
        logger.info("Creating table: Player_Bio")
        cursor.execute(CREATE_PLAYER_BIO)
        logger.info("Creating table: Shot_Chart")
        cursor.execute(CREATE_SHOT_CHART)
        logger.info("Creating table: Player_Tracking_Stats")
        cursor.execute(CREATE_PLAYER_TRACKING)

        # Performance indexes for frequently-used queries.
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_games_date "
            "ON Games (game_date)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_players_fullname "
            "ON Players (full_name)"
        )

        # Indexes for new tables.
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_standings_conf "
            "ON Standings (conference)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_schedule_date "
            "ON Schedule (game_date)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_schedule_home "
            "ON Schedule (home_team_id)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_schedule_away "
            "ON Schedule (away_team_id)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_pbp_game "
            "ON Play_By_Play (game_id)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_pbp_person "
            "ON Play_By_Play (person_id)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_shotchart_player "
            "ON Shot_Chart (player_id)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_shotchart_game "
            "ON Shot_Chart (game_id)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_tracking_game "
            "ON Player_Tracking_Stats (game_id)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_tracking_person "
            "ON Player_Tracking_Stats (person_id)"
        )

        # Migrate existing databases by adding new columns where absent.
        for stmt in _PLAYERS_ALTER + _GAMES_ALTER + _LOGS_ALTER:
            try:
                cursor.execute(stmt)
            except sqlite3.OperationalError:
                # Column already exists — safe to ignore.
                pass

        conn.commit()
        logger.info("All tables created (or already exist) successfully.")
    finally:
        conn.close()
        logger.info("Database connection closed.")


if __name__ == "__main__":
    create_tables()
