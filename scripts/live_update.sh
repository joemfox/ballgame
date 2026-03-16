#!/usr/bin/env bash
HOUR=$(date -u '+%H')
if [ "$HOUR" -lt 5 ]; then
    DATE=$(date -u -d "yesterday" '+%Y-%m-%d')
else
    DATE=$(date -u '+%Y-%m-%d')
fi
cd /opt/ballgame
docker compose exec django python manage.py realtime_update $DATE overwrite --workers 1