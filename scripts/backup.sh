#!/usr/bin/env bash
# Daily/weekly PostgreSQL backup script for ballgame.
#
# Retention policy:
#   - Daily backups are taken every day and kept until the next weekly backup.
#   - On WEEKLY_DAY (default: Sunday), the daily backup is promoted to a weekly
#     backup and all remaining daily backups are deleted.
#   - The most recent WEEKLY_KEEP weekly backups are retained; older ones are pruned.
#
# Cron (run daily at 2am):
#   0 2 * * * /opt/ballgame/scripts/backup.sh >> /opt/ballgame/backups/backup.log 2>&1
#
# Configuration via environment variables or a .env file:
#   COMPOSE_DIR   - directory containing docker-compose.yml (default: script's parent dir)
#   BACKUP_DIR    - where backups are stored (default: $COMPOSE_DIR/backups)
#   WEEKLY_DAY    - day of week for weekly backup, 1=Mon … 7=Sun (default: 7)
#   WEEKLY_KEEP   - number of weekly backups to retain (default: 8)
#   POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD - db credentials

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE_DIR="${COMPOSE_DIR:-$(dirname "$SCRIPT_DIR")}"
BACKUP_DIR="${BACKUP_DIR:-$COMPOSE_DIR/backups}"
WEEKLY_DAY="${WEEKLY_DAY:-7}"
WEEKLY_KEEP="${WEEKLY_KEEP:-8}"
ENV_FILE="$COMPOSE_DIR/.env"

# Load .env if present (skip comment lines and blank lines)
if [[ -f "$ENV_FILE" ]]; then
    while IFS='=' read -r key value; do
        [[ "$key" =~ ^#.*$ || -z "$key" ]] && continue
        key="${key%%[[:space:]]*}"
        value="${value#\"}" value="${value%\"}"  # strip optional quotes
        value="${value#\'}" value="${value%\'}"
        export "$key=$value"
    done < <(grep -v '^[[:space:]]*#' "$ENV_FILE" | grep -v '^[[:space:]]*$')
fi

DB="${POSTGRES_DB:-ballgame}"
USER="${POSTGRES_USER:-ballgame}"
PASS="${POSTGRES_PASSWORD:-changeme}"

DATE="$(date +%Y-%m-%d)"
DOW="$(date +%u)"   # 1=Mon … 7=Sun
DAILY_FILE="$BACKUP_DIR/daily_${DATE}.sql.gz"
WEEKLY_FILE="$BACKUP_DIR/weekly_${DATE}.sql.gz"

mkdir -p "$BACKUP_DIR"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting backup for $DATE (dow=$DOW)"

# Dump the database
PGPASSWORD="$PASS" docker compose -f "$COMPOSE_DIR/docker-compose.yml" \
    exec -T postgres \
    pg_dump -U "$USER" "$DB" \
    | gzip > "$DAILY_FILE"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Dump written to $DAILY_FILE ($(du -sh "$DAILY_FILE" | cut -f1))"

if [[ "$DOW" -eq "$WEEKLY_DAY" ]]; then
    # Promote today's daily to a weekly backup
    mv "$DAILY_FILE" "$WEEKLY_FILE"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Promoted to weekly backup: $WEEKLY_FILE"

    # Delete all remaining daily backups (this week's and any strays)
    find "$BACKUP_DIR" -maxdepth 1 -name 'daily_*.sql.gz' -delete
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Deleted daily backups"

    # Prune old weekly backups, keep the most recent WEEKLY_KEEP
    mapfile -t old_weeklies < <(ls -t "$BACKUP_DIR"/weekly_*.sql.gz 2>/dev/null | tail -n +$((WEEKLY_KEEP + 1)))
    if [[ ${#old_weeklies[@]} -gt 0 ]]; then
        rm -f "${old_weeklies[@]}"
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Pruned ${#old_weeklies[@]} old weekly backup(s)"
    fi
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Done"
