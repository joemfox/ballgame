"""
Queries against the ballgame Postgres database.
Connects via DATABASE_URL env var (postgres:// URL).

Near-sombrero detection reads the inning field that realtime_update populates
every ~5 minutes during in-progress games, so this bot doesn't need its own
MLB Stats API scraper.
"""
import os
from dataclasses import dataclass
from datetime import date

import psycopg2
import psycopg2.extras


def _conn():
    return psycopg2.connect(os.environ["DATABASE_URL"])


SOMBRERO_TIERS = {
    3: "near_sombrero",
    4: "golden_sombrero",
    5: "platinum_sombrero",
}
ULTIMATE_SOMBRERO_MIN = 6
ULTIMATE_SOMBRERO_TYPE = "ultimate_sombrero"


def sombrero_event_type(k: int) -> str:
    if k >= ULTIMATE_SOMBRERO_MIN:
        return ULTIMATE_SOMBRERO_TYPE
    return SOMBRERO_TIERS.get(k, "near_sombrero")


@dataclass
class SombreroGame:
    game_id: str       # MLB gamePk portion of BattingStatLine.id, e.g. "748531"
    player_id: str     # player mlbam_id as string
    statline_id: str   # BattingStatLine.id = f'{game_pk}-{player_mlbam_id}'
    player_name: str
    mlb_org: str
    k: int
    event_type: str
    inning: int | None          # current inning when statline was last written (None if unknown)
    inning_half: str | None     # 'top' or 'bottom'
    game_complete: bool | None  # True = final, False = in progress, None = unknown
    h: int | None
    ab: int | None


def _parse_statline_id(statline_id: str, player_mlbam_id: str) -> tuple[str, str]:
    """Extract (game_id, player_id) from a statline id like '748531-12345'."""
    parts = statline_id.rsplit("-", 1)
    game_id = parts[0] if len(parts) == 2 else statline_id
    return game_id, str(player_mlbam_id)


_FINAL_STATUSES = {"Final", "Game Over", "Completed Early"}
_SKIP_STATUSES   = {"Postponed", "Cancelled", "Suspended"}


def fetch_r_schedule(game_date: date) -> list:
    """Return regular-season schedule entries for the date from the MLB API."""
    import statsapi
    date_str = game_date.strftime("%m/%d/%Y")
    return [
        g for g in statsapi.schedule(start_date=date_str, end_date=date_str)
        if g.get("game_type") == "R"
    ]


def final_game_ids(r_schedule: list) -> set[str]:
    """Game IDs the schedule API reports as complete."""
    return {str(g["game_id"]) for g in r_schedule if g.get("status") in _FINAL_STATUSES}


def has_unstarted_games(game_date: date, r_schedule: list | None = None) -> bool:
    """True if the MLB schedule has regular-season games today that haven't produced any statlines yet."""
    if r_schedule is None:
        r_schedule = fetch_r_schedule(game_date)
    scheduled = {
        str(g["game_id"])
        for g in r_schedule
        if g.get("status") not in _SKIP_STATUSES
    }
    if not scheduled:
        return False
    sql = """
        SELECT DISTINCT split_part(id, '-', 1) AS game_pk
        FROM statsdb_battingstatline
        WHERE date = %(date)s AND game_type = 'R'
    """
    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, {"date": game_date})
            started = {row[0] for row in cur.fetchall()}
    return bool(scheduled - started)


def has_active_games(game_date: date, r_schedule: list | None = None) -> bool:
    """True if any regular-season games for the date are still in progress.

    Checks the DB first; if the DB shows active statlines, cross-checks with the
    MLB schedule API to guard against stale game_complete=False rows left by a
    failed realtime_update run.
    """
    sql = """
        SELECT 1 FROM statsdb_battingstatline
        WHERE date = %(date)s
          AND game_type = 'R'
          AND (game_complete = FALSE OR game_complete IS NULL)
        LIMIT 1
    """
    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, {"date": game_date})
            if cur.fetchone() is None:
                return False

    # DB shows active rows — verify against the schedule API so that stale
    # game_complete=False statlines (e.g. from a game that errored mid-update)
    # don't permanently block the postgame wrap-up.
    if r_schedule is None:
        r_schedule = fetch_r_schedule(game_date)
    if not r_schedule:
        return False
    return not all(g.get("status") in _FINAL_STATUSES for g in r_schedule)


def has_any_games(game_date: date) -> bool:
    """True if any regular-season statlines exist for the date."""
    sql = """
        SELECT 1 FROM statsdb_battingstatline
        WHERE date = %(date)s AND game_type = 'R'
        LIMIT 1
    """
    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, {"date": game_date})
            return cur.fetchone() is not None


def get_near_sombreros(game_date: date) -> list[SombreroGame]:
    """
    Batters currently at exactly k=3 today (mid-game near-sombrero watch).
    Reads from live statlines that realtime_update writes every ~5 min.
    """
    sql = """
        SELECT
            b.id               AS statline_id,
            b.player_mlbam_id,
            p.name             AS player_name,
            p.mlb_org,
            b.k,
            b.h,
            b.ab,
            b.inning,
            b.inning_half,
            b.game_complete
        FROM statsdb_battingstatline b
        LEFT JOIN statsdb_player p ON p.mlbam_id = b.player_mlbam_id
        WHERE
            b.date = %(date)s
            AND b.k = 3
            AND b.game_type = 'R'
            AND (b.game_complete = FALSE OR b.game_complete IS NULL)
        ORDER BY p.name
    """
    with _conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(sql, {"date": game_date})
            rows = cur.fetchall()

    results = []
    for row in rows:
        game_id, player_id = _parse_statline_id(row["statline_id"], row["player_mlbam_id"])
        results.append(
            SombreroGame(
                game_id=game_id,
                player_id=player_id,
                statline_id=row["statline_id"],
                player_name=row["player_name"] or player_id,
                mlb_org=row["mlb_org"] or "",
                k=3,
                event_type="near_sombrero",
                inning=row["inning"],
                inning_half=row["inning_half"],
                game_complete=row["game_complete"],
                h=row["h"],
                ab=row["ab"],
            )
        )
    return results


def get_sombreros(game_date: date) -> list[SombreroGame]:
    """All golden/platinum/ultimate sombrero statlines (k>=4) for a given date, including in-progress games."""
    sql = """
        SELECT
            b.id               AS statline_id,
            b.player_mlbam_id,
            p.name             AS player_name,
            p.mlb_org,
            b.k,
            b.h,
            b.ab,
            b.inning,
            b.inning_half,
            b.game_complete
        FROM statsdb_battingstatline b
        LEFT JOIN statsdb_player p ON p.mlbam_id = b.player_mlbam_id
        WHERE
            b.date = %(date)s
            AND b.k >= 4
            AND b.game_type = 'R'
        ORDER BY b.k DESC, p.name
    """
    with _conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(sql, {"date": game_date})
            rows = cur.fetchall()

    results = []
    for row in rows:
        game_id, player_id = _parse_statline_id(row["statline_id"], row["player_mlbam_id"])
        results.append(
            SombreroGame(
                game_id=game_id,
                player_id=player_id,
                statline_id=row["statline_id"],
                player_name=row["player_name"] or player_id,
                mlb_org=row["mlb_org"] or "",
                k=row["k"],
                event_type=sombrero_event_type(row["k"]),
                inning=row["inning"],
                inning_half=row["inning_half"],
                game_complete=row["game_complete"],
                h=row["h"],
                ab=row["ab"],
            )
        )
    return results


def get_season_sombrero_count(season: int, min_k: int = 4) -> int:
    """Total regular-season games with k>=min_k."""
    sql = """
        SELECT COUNT(*) FROM statsdb_battingstatline
        WHERE k >= %(min_k)s
          AND EXTRACT(YEAR FROM date) = %(season)s
          AND game_type = 'R'
    """
    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, {"min_k": min_k, "season": season})
            return cur.fetchone()[0]


def get_player_season_sombrero_count(player_id: str, season: int, min_k: int = 4) -> int:
    """Player's regular-season games with k>=min_k."""
    sql = """
        SELECT COUNT(*) FROM statsdb_battingstatline
        WHERE player_mlbam_id = %(player_id)s
          AND k >= %(min_k)s
          AND EXTRACT(YEAR FROM date) = %(season)s
          AND game_type = 'R'
    """
    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, {"player_id": player_id, "min_k": min_k, "season": season})
            return cur.fetchone()[0]


@dataclass
class SombreroStandingsEntry:
    player_id: str
    player_name: str
    mlb_org: str
    sombrero_count: int  # golden+ (k>=4, h=0)


def get_sombrero_standings(season: int, top_n: int = 50) -> list[SombreroStandingsEntry]:
    """Season leaderboard for golden+ sombreros (k>=4), descending."""
    sql = """
        SELECT
            b.player_mlbam_id,
            p.name                              AS player_name,
            p.mlb_org,
            COUNT(*)                            AS sombrero_count,
            SUM(COALESCE(b.k, 0))               AS total_k,
            SUM(COALESCE(b.h, 0))               AS total_h,
            SUM(COALESCE(b.h, 0) + COALESCE(b.bb, 0)) AS total_tob,
            SUM(COALESCE(b.ab, 0) + COALESCE(b.bb, 0)) AS total_pa,
            MIN(b.last_name)                    AS last_name
        FROM statsdb_battingstatline b
        LEFT JOIN statsdb_player p ON p.mlbam_id = b.player_mlbam_id
        WHERE
            b.k >= 4
            AND EXTRACT(YEAR FROM b.date) = %(season)s
            AND b.game_type = 'R'
        GROUP BY b.player_mlbam_id, p.name, p.mlb_org
        ORDER BY
            sombrero_count DESC,
            total_k DESC,
            total_h ASC,
            total_tob ASC,
            total_pa ASC,
            last_name ASC
        LIMIT %(top_n)s
    """
    with _conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(sql, {"season": season, "top_n": top_n})
            rows = cur.fetchall()

    return [
        SombreroStandingsEntry(
            player_id=row["player_mlbam_id"],
            player_name=row["player_name"] or row["player_mlbam_id"],
            mlb_org=row["mlb_org"] or "",
            sombrero_count=row["sombrero_count"],
        )
        for row in rows
    ]
