"""
Turns DB rows into Bluesky post text.
"""
import random
from datetime import date

from db import SombreroGame, SombreroStandingsEntry

TEAM_HASHTAGS = {
    # FanGraphs / ROSTER_TEAM_IDS abbreviations (what load_rosters stores in mlb_org)
    "ARI": "#Dbacks",
    "ATL": "#BravesCountry",
    "BAL": "#Birdland",
    "BOS": "#DirtyWater",
    "CHC": "#BeHereForIt",
    "CHW": "#WhiteSox",
    "CIN": "#ATOBTTR",
    "CLE": "#GuardsBall",
    "COL": "#Rockies",
    "DET": "#RepDetroit",
    "HOU": "#ChaseTheFight",
    "KCR": "#FountainsUp",
    "LAA": "#RepTheHalo",
    "LAD": "#Dodgers",
    "MIA": "#FightinFish",
    "MIL": "#ThisIsMyCrew",
    "MIN": "#MNTwins",
    "NYM": "#LGM",
    "NYY": "#RepBX",
    "OAK": "#Athletics",
    "PHI": "#RingTheBell",
    "PIT": "#LetsGoBucs",
    "SDP": "#ForTheFaithful",
    "SEA": "#TridentsUp",
    "SFG": "#SFGiants",
    "STL": "#STLCards",
    "TBR": "#RaysUp",
    "TEX": "#AllForTX",
    "TOR": "#BlueJays50",
    "WAS": "#Natitude",
    "WSN": "#Natitude",
    # Alternate abbreviations (MLB_URL_TO_ORG_NAME and user-provided list)
    "ATH": "#Athletics",
    "AZ":  "#Dbacks",
    "CWS": "#WhiteSox",
    "KC":  "#FountainsUp",
    "SD":  "#ForTheFaithful",
    "SF":  "#SFGiants",
    "TB":  "#RaysUp",
    "WSH": "#Natitude",
}


def _hashtag(mlb_org: str | None) -> str:
    tag = TEAM_HASHTAGS.get(mlb_org or "")
    return f" {tag}" if tag else ""


CELEBRATION_EMOJI = [
    "🎉", "🥳", "🎊", "🎺", "🪗", "🎸", "🎷", "🏆", "🎖️", "🥂",
    "🍾", "🎆", "🎇", "✨", "🌟", "💫", "🎠", "🎡", "🎢", "🪅",
]

ULTIMATE_OPENERS = [
    "🚨🚨🚨 ULTIMATE SOMBRERO 🚨🚨🚨",
    "🌋💥🌋 THE RAREST OF FEATS 🌋💥🌋",
    "⚡⚡⚡ HISTORY HAS BEEN MADE ⚡⚡⚡",
]

# Documented 6+ K, 0 H games before our tracking began
HISTORICAL_ULTIMATE_SOMBREROS = 8


def _ordinal(n: int) -> str:
    if n < 10:
        return ['','first','second','third','fourth','fifth','sixth','seventh','eighth','ninth'][n]
    if 11 <= (n % 100) <= 13:
        return f"{n}th"
    return f"{n}{['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]}"


def _inning_str(inning: int | None) -> str:
    if inning is None:
        return ""
    return f" in the {_ordinal(inning)} inning"


def format_near_sombrero(game: SombreroGame) -> str:
    org = f" ({game.mlb_org})" if game.mlb_org else ""
    line = f"{game.h}-{game.ab}" if game.h is not None and game.ab is not None else "0-3"
    return (
        f"👀 SOMBRERO WATCH 👀\n"
        f"{game.player_name}{org} is {line} with 3 strikeouts"
        f"{_inning_str(game.inning)}."
        f"{_hashtag(game.mlb_org)}"
    )


def format_golden_sombrero(
    game: SombreroGame,
    season: int,
    season_count: int,
    player_season_count: int,
) -> str:
    VERBS = ["logged", "achieved", "secured", "notched", "garnered", "registered", "recorded", "chalked up", "earned", "claimed", "bagged", "posted", "put up"]
    emoji = random.choice(CELEBRATION_EMOJI)
    org = f" ({game.mlb_org})" if game.mlb_org else ""
    return (
        f"{emoji} GOLDEN SOMBRERO\n"
        f"{game.player_name}{org} has {random.choice(VERBS)} the season's "
        f"{_ordinal(season_count)} golden sombrero "
        f"and his {_ordinal(player_season_count)} in {season}."
        f"\n{_hashtag(game.mlb_org)}"
    )


def format_platinum_sombrero(
    game: SombreroGame,
    season: int,
    season_platinum_count: int,
    season_total_count: int,
    player_season_count: int,
) -> str:
    emojis = " ".join(random.sample(CELEBRATION_EMOJI, 3))
    org = f" ({game.mlb_org})" if game.mlb_org else ""
    return (
        f"{emojis} PLATINUM SOMBRERO\n"
        f"{game.player_name}{org} has achieved the season's "
        f"{_ordinal(season_platinum_count)} platinum sombrero. "
        f"It's the {_ordinal(season_total_count)} sombrero of the season "
        f"and his {_ordinal(player_season_count)} in {season}."
        f"\n{_hashtag(game.mlb_org)}"
    )


def format_ultimate_sombrero(
    game: SombreroGame,
    season: int,
    season_count: int,
    player_season_count: int,
) -> str:
    all_time_count = HISTORICAL_ULTIMATE_SOMBREROS + season_count
    org = f" ({game.mlb_org})" if game.mlb_org else ""
    opener = random.choice(ULTIMATE_OPENERS)
    return (
        f"{opener}\n"
        f"{game.player_name}{org} has just struck out {game.k} times!"
        f"This is the {_ordinal(all_time_count)} time this has ever happened "
        f"in baseball history and the {_ordinal(player_season_count)} time "
        f"for {game.player_name} in {season}. "
        f"We may never see this again."
        f"\n{_hashtag(game.mlb_org)}"
    )


TIER_LABEL = {
    "golden_sombrero":   "Golden Sombrero",
    "platinum_sombrero": "Platinum Sombrero",
    "ultimate_sombrero": "Ultimate Sombrero",
}

TIER_ORDER = ["ultimate_sombrero", "platinum_sombrero", "golden_sombrero"]


def format_daily_sombrero_list(games: list[SombreroGame], game_date) -> str:
    date_str = game_date.strftime("%B %-d")
    lines = [f"Today's sombreros ({date_str}):"]

    sorted_games = sorted(games, key=lambda g: TIER_ORDER.index(g.event_type))

    current_tier = None
    for game in sorted_games:
        if game.event_type != current_tier:
            current_tier = game.event_type
            lines.append(f"\n{TIER_LABEL[current_tier]}")
        org = f" ({game.mlb_org})" if game.mlb_org else ""
        lines.append(f"{game.player_name}{org} — {game.k} K")

    if not sorted_games:
        lines.append("None. :(")

    return "\n".join(lines)
