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
import os
from datetime import date, datetime

import bluesky
import db
import formatters
import images
import state


SEASON = int(os.environ.get("SEASON", date.today().year))


def run_live(client, handle: str, game_date: date, season: int, dry_run: bool) -> None:
    print(f"Running live{' (dry run)' if dry_run else ''}")
    candidates = db.get_near_sombreros(game_date)
    if(len(candidates) == 0):
        print("No sombrero candidates")
    for game in candidates:
        if state.already_posted(client, handle, season, "near_sombrero", game.game_id, game.player_id):
            continue
        text = formatters.format_near_sombrero(game)
        print(text)
        if not dry_run:
            bluesky.post(client, text)
            state.mark_posted(client, handle, "near_sombrero", game.game_id, game.player_id)


def run_postgame(client, handle: str, game_date: date, season: int, dry_run: bool) -> None:
    date_key = game_date.isoformat()
    sombreros = db.get_completed_sombreros(game_date)

    # Post 1: daily sombrero list (one combined post)
    if not state.already_posted(client, handle, season, "daily_list", date_key, "all"):
        text = formatters.format_daily_sombrero_list(sombreros, game_date)
        print(text)
        print()
        if not dry_run:
            bluesky.post(client, text)
            state.mark_posted(client, handle, "daily_list", date_key, "all")

    # Post 2: season standings image (only if at least one sombrero has occurred this season)
    if not state.already_posted(client, handle, season, "standings", date_key, "all"):
        entries = db.get_sombrero_standings(season)
        if entries:
            alt = images.standings_alt_text(entries, season, game_date)
            print(alt)
            if not dry_run:
                img_bytes = images.generate_standings_image(entries, season, game_date)
                bluesky.post_image(client, text="", image_bytes=img_bytes, alt_text=alt)
                state.mark_posted(client, handle, "standings", date_key, "all")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["live", "postgame"])
    parser.add_argument("--date", default=date.today().isoformat(),
                        help="Date to process (YYYY-MM-DD), defaults to today")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print posts without sending to Bluesky or writing state")
    args = parser.parse_args()

    game_date = datetime.strptime(args.date, "%Y-%m-%d").date()
    handle = os.environ["BLUESKY_HANDLE"]

    client = bluesky.login()

    if args.mode == "live":
        run_live(client, handle, game_date, SEASON, args.dry_run)
    elif args.mode == "postgame":
        run_postgame(client, handle, game_date, SEASON, args.dry_run)


if __name__ == "__main__":
    main()
