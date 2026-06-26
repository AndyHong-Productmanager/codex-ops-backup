#!/usr/bin/env bash
set -euo pipefail

ROOT="/home/ubuntuhong/dev/codex-telegram-bot"
ENV_FILE="$ROOT/.env"

if [ -f "$ENV_FILE" ]; then
  set -a
  source "$ENV_FILE"
  set +a
fi

: "${TG_CODEX_BOT_TOKEN:?TG_CODEX_BOT_TOKEN missing}"
: "${TG_CHAT_ID:?TG_CHAT_ID missing}"

if [ "$#" -gt 0 ]; then
  MSG="$*"
else
  MSG="$(cat)"
fi

if [ -z "$MSG" ]; then
  echo "empty message" >&2
  exit 1
fi

if [ "${#MSG}" -gt 3900 ]; then
  MSG="${MSG:0:3900}"
fi

curl -sS -o /tmp/codex_telegram_bot_notify.json -w "%{http_code}\n" \
  "https://api.telegram.org/bot${TG_CODEX_BOT_TOKEN}/sendMessage" \
  -d chat_id="${TG_CHAT_ID}" \
  --data-urlencode text="$MSG"
