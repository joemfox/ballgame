"""
Bluesky sombrero bot entry point.

Two modes:
  live      -- run every ~5 min during games; posts near-sombrero (3K, 0H) alerts
  postgame  -- run once after aggregate_points; posts golden/platinum/ultimate
               sombreros and the daily standings update

Usage:
  python main.py live
  python main.py postgame --date 2026-04-01
  python main.py postgame --date 2026-04-01 --dry-run
"""
import argparse
from datetime import date, datetime

import bluesky
import db
import formatters
import state


def run_live(client, game_date: date, season: int, dry_run: bool) -> None:
    print(f"Running live{' (dry run)' if dry_run else ''}")

    # Near-sombrero watch (in-progress games)
    for game in db.get_near_sombreros(game_date):
        if state.already_posted(season, "near_sombrero", game.game_id, game.player_id):
            continue
        text = formatters.format_near_sombrero(game)
        print(text)
        if not dry_run:
            bluesky.post(client, text)
            state.mark_posted(season, "near_sombrero", game.game_id, game.player_id)

    # Individual tier posts as games complete
    for game in db.get_sombreros(game_date):
        if state.already_posted(season, game.event_type, game.game_id, game.player_id):
            continue

        if game.event_type == "golden_sombrero":
            season_count  = db.get_season_sombrero_count(season, min_k=4)
            player_count  = db.get_player_season_sombrero_count(game.player_id, season, min_k=4)
            text = formatters.format_golden_sombrero(game, season, season_count, player_count)

        elif game.event_type == "platinum_sombrero":
            season_plat   = db.get_season_sombrero_count(season, min_k=5)
            season_total  = db.get_season_sombrero_count(season, min_k=4)
            player_count  = db.get_player_season_sombrero_count(game.player_id, season, min_k=4)
            text = formatters.format_platinum_sombrero(game, season, season_plat, season_total, player_count)

        elif game.event_type == "ultimate_sombrero":
            season_count  = db.get_season_sombrero_count(season, min_k=6)
            player_count  = db.get_player_season_sombrero_count(game.player_id, season, min_k=6)
            text = formatters.format_ultimate_sombrero(game, season, season_count, player_count)

        else:
            continue

        print(text)
        if not dry_run:
            bluesky.post(client, text)
            state.mark_posted(season, game.event_type, game.game_id, game.player_id)


def run_postgame(client, game_date: date, season: int, dry_run: bool) -> None:
    date_key = game_date.isoformat()
    sombreros = db.get_sombreros(game_date)

    # Post 1: daily sombrero list (one combined post)
    if not state.already_posted(season, "daily_list", date_key, "all"):
        text = formatters.format_daily_sombrero_list(sombreros, game_date)
        print(text)
        print()
        if not dry_run:
            bluesky.post(client, text)
            state.mark_posted(season, "daily_list", date_key, "all")

    # Post 2: season standings image (only if at least one sombrero has occurred this season)
    if not state.already_posted(season, "standings", date_key, "all"):
        entries = db.get_sombrero_standings(season)
        if entries:
            import images
            alt = images.standings_alt_text(entries, season, game_date)
            print(alt)
            if not dry_run:
                img_bytes = images.generate_standings_image(entries, season, game_date)
                bluesky.post_image(client, text="", image_bytes=img_bytes, alt_text=alt)
                state.mark_posted(season, "standings", date_key, "all")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["live", "postgame"])
    parser.add_argument("--date", default=date.today().isoformat(),
                        help="Date to process (YYYY-MM-DD), defaults to today")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print posts without sending to Bluesky or writing state")
    args = parser.parse_args()

    game_date = datetime.strptime(args.date, "%Y-%m-%d").date()
    season = game_date.year
    client = bluesky.login()

    if args.mode == "live":
        run_live(client, game_date, season, args.dry_run)
    elif args.mode == "postgame":
        run_postgame(client, game_date, season, args.dry_run)


if __name__ == "__main__":
    main()
