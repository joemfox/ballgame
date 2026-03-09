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
| `download_fg_rosters` | — | Downloads FanGraphs depth-chart roster JSON to `data/rosters/{ABBR}_roster.json` |
| `download_fg_free_agents` | — | Downloads FanGraphs free agent list to `data/rosters/free_agents.json` |
| `download_mlb_depthcharts` | — | Scrapes MLB/MiLB rosters to `data/rosters/all_mlb_rosters.json` (slow) |
| `load_rosters` | — | Imports players from all downloaded roster data (FG depth charts, FG free agents, MLB depth charts) |
| `update_status_from_fg_rosters` | — | Updates player MLB status flags (`is_mlb`, `is_bullpen`, etc.) from downloaded FG rosters |

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
| `clear_data` | `[--yes]` | Deletes all application data (players, stats, teams, drafts). Preserves users. Prompts for confirmation unless `--yes` is passed. |

---

## Procedures

### Deploy

**First-time setup on the host:**
```bash
# 1. Firewall — allow only SSH, HTTP, HTTPS
ufw allow 22 && ufw allow 80 && ufw allow 443 && ufw enable

# 2. Configure secrets
cp .env.example .env
```

Edit `.env` — required values:
- `POSTGRES_PASSWORD` — strong random password
- `DJANGO_SECRET_KEY` — run this to generate one:
  ```bash
  python3 -c "import secrets; print(secrets.token_urlsafe(50))"
  ```
- `DOMAIN` — your server's public domain name (e.g. `ballgame.example.com`)
- `CSRF_TRUSTED_ORIGINS` — `https://` + your domain (e.g. `https://ballgame.example.com`)
- `DJANGO_ALLOWED_HOSTS` — your domain (e.g. `ballgame.example.com`)

```bash
# 3. Start services — Caddy will automatically obtain a TLS certificate
docker compose up -d --build
docker compose exec django python manage.py migrate
docker compose exec django python manage.py createsuperuser
```

Caddy handles HTTPS automatically via Let's Encrypt. Port 8000 (Django) and port 80/nginx (frontend) are no longer exposed to the internet — all traffic goes through Caddy on 443.

### Offseason setup (load prior-year stats)
In `settings.py`: `CURRENT_SEASON = 2026`, `CURRENT_SEASON_TYPE = "offseason"` → API serves 2025 stats.
```bash
docker compose exec django python manage.py download_fg_rosters
docker compose exec django python manage.py download_fg_free_agents
docker compose exec django python manage.py load_rosters
docker compose exec django python manage.py fetch_season_statlines 2025
```
`download_mlb_depthcharts` is optional (slow scrape) — run it if you want birthdates populated from MLB.com.
`fetch_season_statlines` is required because fantasy scores are computed game-by-game through the custom scoring pipeline and then aggregated.

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
docker compose exec django python manage.py download_fg_rosters
docker compose exec django python manage.py update_status_from_fg_rosters
```
`update_status_from_fg_rosters` refreshes player level badges (`mlevel`: MLB, AAA, AA, A+, A, R) from FanGraphs roster data. `download_fg_rosters` fetches fresh roster files first.

### Backfill a full season
```bash
docker compose exec django python manage.py fetch_season_statlines 2025
```
This calls `realtime_update` + `aggregate_team_points` for every day in the season, then `aggregate_points`. Takes a long time.

### Database backups

The script `scripts/backup.sh` handles daily and weekly backups via a single cron entry.

**Retention policy:**
- Daily backups (`daily_YYYY-MM-DD.sql.gz`) are taken every day and kept until the next weekly backup.
- On Sunday, the day's dump is promoted to a weekly backup (`weekly_YYYY-MM-DD.sql.gz`) and all daily backups are deleted.
- The 8 most recent weekly backups are kept (~2 months); older ones are pruned automatically.

**Setup (run once on the host):**
```bash
mkdir -p /opt/ballgame/backups
cp scripts/backup.sh /opt/ballgame/scripts/backup.sh
chmod +x /opt/ballgame/scripts/backup.sh
crontab -e
# Add:
# 0 2 * * * /opt/ballgame/scripts/backup.sh >> /opt/ballgame/backups/backup.log 2>&1
```

The script reads `POSTGRES_DB`, `POSTGRES_USER`, and `POSTGRES_PASSWORD` from the `.env` file in the project root. No other configuration is required.

**Restore from a backup:**
```bash
gunzip -c /opt/ballgame/backups/weekly_2025-03-02.sql.gz \
  | docker compose -f /opt/ballgame/docker-compose.yml exec -T postgres \
    psql -U ballgame ballgame
```

**Expected disk usage:** ~600 MB at steady state (6 daily × ~40 MB + 8 weekly × ~40 MB, compressed).

---

### Draft
1. Create user accounts for each participant (via `/admin/`). A `Team` is auto-created per user.
2. Optionally load and assign players first (`load_rosters`, `fill_rosters --clear`, or via admin).
3. Start the draft (admin or staff account required):
   ```
   POST /api/draft/start   {"order": ["AAA","BBB","CCC"], "rounds": 16}
   ```
   Omit `order` to auto-populate from all teams with users, sorted alphabetically.
4. Each team picks at `/draft` in the UI. Snake order is enforced server-side.
