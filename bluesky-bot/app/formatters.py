"""
Turns DB rows into Bluesky post text.
"""
import random
from datetime import date

from db import SombreroGame, SombreroStandingsEntry

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
    if 11 <= (n % 100) <= 13:
        return f"{n}th"
    return f"{n}{['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]}"


def _inning_str(inning: int | None) -> str:
    if inning is None:
        return ""
    return f" in the {_ordinal(inning)} inning"


def format_near_sombrero(game: SombreroGame) -> str:
    org = f" ({game.mlb_org})" if game.mlb_org else ""
    return (
        f"👀 SOMBRERO WATCH 👀\n"
        f"{game.player_name}{org} is 0-3 with 3 strikeouts"
        f"{_inning_str(game.inning)}."
    )


def format_golden_sombrero(
    game: SombreroGame,
    season: int,
    season_count: int,
    player_season_count: int,
) -> str:
    emoji = random.choice(CELEBRATION_EMOJI)
    org = f" ({game.mlb_org})" if game.mlb_org else ""
    return (
        f"{emoji} GOLDEN SOMBRERO\n"
        f"{game.player_name}{org} has achieved the season's "
        f"{_ordinal(season_count)} golden sombrero "
        f"and his {_ordinal(player_season_count)} in {season}."
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
        f"{game.player_name}{org} has just struck out {game.k} times "
        f"without recording a single hit. "
        f"This is the {_ordinal(all_time_count)} time this has ever happened "
        f"in baseball history and the {_ordinal(player_season_count)} time "
        f"for {game.player_name} in {season}. "
        f"We may never see this again."
    )


TIER_LABEL = {
    "golden_sombrero":   "Golden Sombrero",
    "platinum_sombrero": "Platinum Sombrero",
    "ultimate_sombrero": "Ultimate Sombrero",
}

TIER_ORDER = ["ultimate_sombrero", "platinum_sombrero", "golden_sombrero"]


def format_daily_sombrero_list(games: list[SombreroGame], game_date) -> str:
    date_str = game_date.strftime("%B %-d")
    lines = [f"Today's sombreros ({date_str}):\n"]

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
