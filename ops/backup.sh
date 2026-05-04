#!/usr/bin/env bash
# Daily Postgres dump with 7-day rotation.
# Run via cron on the host:
#   0 3 * * *  /opt/vyklik/ops/backup.sh >> /var/log/vyklik-backup.log 2>&1

set -euo pipefail

REPO_DIR="${REPO_DIR:-/opt/vyklik}"
BACKUP_DIR="${BACKUP_DIR:-/var/backups/vyklik}"
KEEP_DAYS="${KEEP_DAYS:-7}"
COMPOSE_PROJECT="${COMPOSE_PROJECT:-vyklik}"

mkdir -p "$BACKUP_DIR"
ts="$(date -u +%Y%m%d_%H%M%S)"
out="$BACKUP_DIR/vyklik_${ts}.sql.gz"

cd "$REPO_DIR"
docker compose -p "$COMPOSE_PROJECT" exec -T postgres \
  sh -c 'pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB"' \
  | gzip > "$out"

echo "wrote $out ($(du -h "$out" | cut -f1))"

find "$BACKUP_DIR" -name 'vyklik_*.sql.gz' -mtime +"$KEEP_DAYS" -print -delete
