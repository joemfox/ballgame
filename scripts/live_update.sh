#!/usr/bin/env bash
DATE=$(date -d "yesterday 13:00" '+%Y-%m-%d')
cd /opt/ballgame
docker compose exec django python manage.py snapshot_roster $DATE
docker compose exec django python manage.py realtime_update $DATE overwrite --workers 1
