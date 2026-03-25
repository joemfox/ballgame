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


def _parse_statline_id(statline_id: str, player_mlbam_id: str) -> tuple[str, str]:
    """Extract (game_id, player_id) from a statline id like '748531-12345'."""
    parts = statline_id.rsplit("-", 1)
    game_id = parts[0] if len(parts) == 2 else statline_id
    return game_id, str(player_mlbam_id)


def get_near_sombreros(game_date: date) -> list[SombreroGame]:
    """
    Batters currently at exactly k=3, h=0 today (mid-game near-sombrero watch).
    Reads from live statlines that realtime_update writes every ~5 min.
    """
    sql = """
        SELECT
            b.id               AS statline_id,
            b.player_mlbam_id,
            p.name             AS player_name,
            p.mlb_org,
            b.k,
            b.inning,
            b.inning_half,
            b.game_complete
        FROM statsdb_battingstatline b
        LEFT JOIN statsdb_player p ON p.mlbam_id = b.player_mlbam_id
        WHERE
            b.date = %(date)s
            AND b.h = 0
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
            )
        )
    return results


def get_completed_sombreros(game_date: date) -> list[SombreroGame]:
    """Golden/platinum/ultimate sombrero games (k>=4, h=0) for a given date."""
    sql = """
        SELECT
            b.id               AS statline_id,
            b.player_mlbam_id,
            p.name             AS player_name,
            p.mlb_org,
            b.k,
            b.inning,
            b.inning_half,
            b.game_complete
        FROM statsdb_battingstatline b
        LEFT JOIN statsdb_player p ON p.mlbam_id = b.player_mlbam_id
        WHERE
            b.date = %(date)s
            AND b.h = 0
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
            )
        )
    return results


def get_season_sombrero_count(season: int, min_k: int = 4) -> int:
    """Total regular-season games with h=0 and k>=min_k."""
    sql = """
        SELECT COUNT(*) FROM statsdb_battingstatline
        WHERE h = 0 AND k >= %(min_k)s
          AND EXTRACT(YEAR FROM date) = %(season)s
          AND game_type = 'R'
    """
    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, {"min_k": min_k, "season": season})
            return cur.fetchone()[0]


def get_player_season_sombrero_count(player_id: str, season: int, min_k: int = 4) -> int:
    """Player's regular-season games with h=0 and k>=min_k."""
    sql = """
        SELECT COUNT(*) FROM statsdb_battingstatline
        WHERE player_mlbam_id = %(player_id)s
          AND h = 0 AND k >= %(min_k)s
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


def get_sombrero_standings(season: int, top_n: int = 10) -> list[SombreroStandingsEntry]:
    """Season leaderboard for golden+ sombreros, descending."""
    sql = """
        SELECT
            b.player_mlbam_id,
            p.name      AS player_name,
            p.mlb_org,
            COUNT(*)    AS sombrero_count
        FROM statsdb_battingstatline b
        LEFT JOIN statsdb_player p ON p.mlbam_id = b.player_mlbam_id
        WHERE
            b.sombrero = TRUE
            AND EXTRACT(YEAR FROM b.date) = %(season)s
            AND b.game_type = 'R'
        GROUP BY b.player_mlbam_id, p.name, p.mlb_org
        ORDER BY sombrero_count DESC, p.name
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
