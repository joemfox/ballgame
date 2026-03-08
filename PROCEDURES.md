# Ballgame — Management Commands & Procedures

All commands run inside the Django container:
```
docker compose exec django python manage.py <command>
```

---

## Management Commands

### Player / roster data

| Command | Args | What it does |
|---|---|---|
| `load_rosters` | — | Imports players from FanGraphs roster data into the Player table |
| `update_status_from_fg_rosters` | — | Updates player MLB status flags (`is_mlb`, `is_bullpen`, etc.) from FG rosters |
| `download_fg_stats` | — | Downloads FG season batting/pitching JSON to `data/<year>/` |
| `load_season_stats_from_fg` | — | Loads downloaded FG JSON into `SeasonBattingStatLine` / `SeasonPitchingStatLine` |

### In-season daily pipeline

| Command | Args | What it does |
|---|---|---|
| `snapshot_roster` | `[YYYY-MM-DD]` | Records current `team_assigned` for all owned players. Default: today. **Run first, before games.** |
| `realtime_update` | `YYYY-MM-DD` | Fetches game-level stats from MLB Stats API for a date, creates `BattingStatLine` / `PitchingStatLine` records attributed to the snapshotted fantasy team |
| `aggregate_team_points` | `YYYY-MM-DD` | Aggregates that day's statlines into `TeamBattingStatLine` / `TeamPitchingStatLine` (used for standings) |
| `aggregate_points` | `YEAR` | Re-aggregates all game statlines for the year into `SeasonBattingStatLine` / `SeasonPitchingStatLine` (player totals) |
| `fetch_season_statlines` | `YEAR` | Bulk backfill: runs `realtime_update` + `aggregate_team_points` for every day Apr 1 – Dec 31, then `aggregate_points`. Slow. |

### Season setup

| Command | Args | What it does |
|---|---|---|
| `init_season` | `[--year YEAR]` | Seeds zero-stat `SeasonBattingStatLine` / `SeasonPitchingStatLine` rows for every player. Run once when switching to inseason. Default year: `CURRENT_SEASON` |
| `fill_rosters` | `[--per-team N] [--clear] [--mlb-only]` | Randomly distributes unowned players across all teams. `--clear` wipes existing assignments first. `--mlb-only` restricts to MLB-rostered players. |

---

## Procedures

### Deploy
```bash
cp .env.example .env   # fill in secrets
docker compose up -d --build
docker compose exec django python manage.py migrate
docker compose exec django python manage.py createsuperuser
```

### Offseason setup (load prior-year stats)
In `settings.py`: `CURRENT_SEASON = 2026`, `CURRENT_SEASON_TYPE = "offseason"` → API serves 2025 stats.
```bash
docker compose exec django python manage.py load_rosters
docker compose exec django python manage.py fetch_season_statlines 2025
```
`fetch_season_statlines` is required (not `load_season_stats_from_fg`) because fantasy scores must be computed game-by-game through the custom scoring pipeline. `load_season_stats_from_fg` only loads raw stats and leaves all FAN_* fields blank.

### Switch to in-season
1. Set `CURRENT_SEASON_TYPE = "inseason"` in `settings.py` and rebuild.
2. Seed season records:
   ```bash
   docker compose exec django python manage.py init_season
   ```

### Daily cron (in-season)
Run each morning before the first game:
```bash
DATE=$(date +%Y-%m-%d)
docker compose exec django python manage.py snapshot_roster $DATE
docker compose exec django python manage.py realtime_update $DATE
docker compose exec django python manage.py aggregate_team_points $DATE
docker compose exec django python manage.py aggregate_points 2026
```

### Backfill a full season
```bash
docker compose exec django python manage.py fetch_season_statlines 2025
```
This calls `realtime_update` + `aggregate_team_points` for every day in the season, then `aggregate_points`. Takes a long time.

### Draft
1. Create user accounts for each participant (via `/admin/`). A `Team` is auto-created per user.
2. Optionally load and assign players first (`load_rosters`, `fill_rosters --clear`, or via admin).
3. Start the draft (admin or staff account required):
   ```
   POST /api/draft/start   {"order": ["AAA","BBB","CCC"], "rounds": 16}
   ```
   Omit `order` to auto-populate from all teams with users, sorted alphabetically.
4. Each team picks at `/draft` in the UI. Snake order is enforced server-side.
