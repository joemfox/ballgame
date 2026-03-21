#!/usr/bin/env bash
# Run this each morning (e.g., 7am cron) to schedule the roster snapshot
# before the day's first game.
#
# Cron example (7am daily):
#   0 7 * * * /opt/ballgame/scripts/schedule_daily_snapshot.sh >> /var/log/ballgame/snapshot_schedule.log 2>&1

DATE=$(date '+%Y-%m-%d')
cd /opt/ballgame

LOCK_TIME=$(docker compose exec -T django python manage.py schedule_snapshot "$DATE" 2>/dev/null)

if [ -z "$LOCK_TIME" ]; then
    echo "$(date): No games found for $DATE, skipping snapshot scheduling"
    exit 0
fi

# Convert UTC ISO string to local time for `at`
AT_TIME=$(date -d "$LOCK_TIME" '+%H:%M %Y-%m-%d')

echo "docker compose exec django python manage.py snapshot_roster $DATE" | at "$AT_TIME"
echo "$(date): Scheduled snapshot_roster for $DATE at $AT_TIME (local) / $LOCK_TIME (UTC)"
