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
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")


def today_et() -> date:
    return datetime.now(ET).date()

import bluesky
import db
import formatters
import state


def log(msg: str) -> None:
    print(f"[{datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')}] {msg}", flush=True)


def run_live(client, game_date: date, season: int, dry_run: bool) -> None:
    log(f"run_live date={game_date} season={season}{' DRY-RUN' if dry_run else ''}")

    # Near-sombrero watch (in-progress games)
    near = db.get_near_sombreros(game_date)
    log(f"near-sombreros found: {len(near)}")
    for game in near:
        if state.already_posted(season, "near_sombrero", game.game_id, game.player_id):
            log(f"  skip near_sombrero already posted: {game.player_name} game={game.game_id}")
            continue
        text = formatters.format_near_sombrero(game)
        log(f"  posting near_sombrero: {game.player_name} ({game.mlb_org}) k={game.k} inning={game.inning}")
        print(text)
        if not dry_run:
            bluesky.post(client, text)
            state.mark_posted(season, "near_sombrero", game.game_id, game.player_id)
            log(f"  posted and marked: near_sombrero {game.player_name}")

    # Individual tier posts as games complete
    sombreros = db.get_sombreros(game_date)
    log(f"sombrero games found: {len(sombreros)}")
    for game in sombreros:
        if state.already_posted(season, game.event_type, game.game_id, game.player_id):
            log(f"  skip {game.event_type} already posted: {game.player_name} game={game.game_id}")
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
            log(f"  unknown event_type={game.event_type!r} for {game.player_name}, skipping")
            continue

        log(f"  posting {game.event_type}: {game.player_name} ({game.mlb_org}) k={game.k} complete={game.game_complete}")
        print(text)
        if not dry_run:
            bluesky.post(client, text)
            state.mark_posted(season, game.event_type, game.game_id, game.player_id)
            log(f"  posted and marked: {game.event_type} {game.player_name}")

    any_games     = db.has_any_games(game_date)
    active_games  = db.has_active_games(game_date)
    unstarted     = db.has_unstarted_games(game_date)
    log(f"game state: any={any_games} active={active_games} unstarted={unstarted}")
    if any_games and not active_games and not unstarted:
        log("All games complete — running postgame wrap-up")
        run_postgame(client, game_date, season, dry_run)


def run_postgame(client, game_date: date, season: int, dry_run: bool) -> None:
    log(f"run_postgame date={game_date} season={season}{' DRY-RUN' if dry_run else ''}")
    date_key = game_date.isoformat()
    sombreros = db.get_sombreros(game_date)
    log(f"sombrero games for daily list: {len(sombreros)}")

    # Post 1: daily sombrero list (one combined post)
    if state.already_posted(season, "daily_list", date_key, "all"):
        log("skip daily_list: already posted")
    else:
        text = formatters.format_daily_sombrero_list(sombreros, game_date)
        log("posting daily_list")
        print(text)
        print()
        if not dry_run:
            bluesky.post(client, text)
            state.mark_posted(season, "daily_list", date_key, "all")
            log("posted and marked: daily_list")

    # Post 2: season standings image (only if at least one sombrero has occurred this season)
    if state.already_posted(season, "standings", date_key, "all"):
        log("skip standings: already posted")
    else:
        entries = db.get_sombrero_standings(season)
        log(f"standings entries: {len(entries)}")
        if entries:
            import images
            alt = images.standings_alt_text(entries, season, game_date)
            log("posting standings image")
            print(alt)
            if not dry_run:
                img_bytes = images.generate_standings_image(entries, season, game_date)
                bluesky.post_image(client, text="", image_bytes=img_bytes, alt_text=alt)
                state.mark_posted(season, "standings", date_key, "all")
                log("posted and marked: standings")
        else:
            log("no standings entries yet this season, skipping standings post")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["live", "postgame"])
    parser.add_argument("--date", default=today_et().isoformat(),
                        help="Date to process (YYYY-MM-DD), defaults to today")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print posts without sending to Bluesky or writing state")
    args = parser.parse_args()

    game_date = datetime.strptime(args.date, "%Y-%m-%d").date()
    season = game_date.year
    log(f"starting mode={args.mode} date={game_date} season={season}{' DRY-RUN' if args.dry_run else ''}")

    client = bluesky.login()
    log("bluesky login ok")

    if args.mode == "live":
        run_live(client, game_date, season, args.dry_run)
    elif args.mode == "postgame":
        run_postgame(client, game_date, season, args.dry_run)

    log("done")


if __name__ == "__main__":
    main()
