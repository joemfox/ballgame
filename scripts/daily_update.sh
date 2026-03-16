#!/usr/bin/env bash
DATE=$(date -d "yesterday 13:00" '+%Y-%m-%d')
cd /opt/ballgame
docker compose exec django python manage.py snapshot_roster $DATE
docker compose exec django python manage.py realtime_update $DATE overwrite --workers 1
docker compose exec django python manage.py aggregate_team_points $DATE
docker compose exec django python manage.py aggregate_points 2026
docker compose exec django python manage.py download_fg_rosters
docker compose exec django python manage.py update_status_from_fg_rosters
