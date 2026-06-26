#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="$REPO_ROOT/logs"
mkdir -p "$LOG_DIR"

CRON_LINE="23 3 * * 0 $REPO_ROOT/scripts/backup.sh >> $LOG_DIR/weekly-backup.log 2>&1"
TMP_FILE="$(mktemp)"
trap 'rm -f "$TMP_FILE"' EXIT

crontab -l 2>/dev/null | grep -v -F "$REPO_ROOT/scripts/backup.sh" > "$TMP_FILE" || true
printf '%s\n' "$CRON_LINE" >> "$TMP_FILE"
crontab "$TMP_FILE"

printf 'Installed weekly cron: %s\n' "$CRON_LINE"
