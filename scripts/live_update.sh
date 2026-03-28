#!/usr/bin/env bash
set -euo pipefail

LOCKFILE=/tmp/live_update.lock
exec 9>"$LOCKFILE"
if ! flock -n 9; then
    echo "$(date): live_update already running, skipping"
    exit 0
fi

HOUR=$(date -u '+%H')
if [ "$HOUR" -lt 7 ]; then
    DATE=$(date -u -d "yesterday" '+%Y-%m-%d')
else
    DATE=$(date -u '+%Y-%m-%d')
fi

cd /opt/ballgame
docker compose exec -T django python manage.py realtime_update $DATE overwrite --workers 1
docker compose exec -T bluesky-bot python main.py live --date $DATE >> /var/log/sombrero-bot.log 2>&1
