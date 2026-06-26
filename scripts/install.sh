#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOME_DIR="${HOME:-/home/ubuntuhong}"
DEV_DIR="${DEV_DIR:-$HOME_DIR/dev}"
CODEX_HOME="${CODEX_HOME:-$HOME_DIR/.codex}"
BOT_TARGET="${BOT_TARGET:-$DEV_DIR/codex-telegram-bot}"
BACKUP_SUFFIX="$(date -u +%Y%m%dT%H%M%SZ)"

mkdir -p "$CODEX_HOME" "$DEV_DIR"

if [ -d "$CODEX_HOME/skills" ]; then
  cp -a "$CODEX_HOME/skills" "$CODEX_HOME/skills.before-codex-ops-$BACKUP_SUFFIX"
fi
if [ -d "$CODEX_HOME/plugins/cache" ]; then
  mkdir -p "$CODEX_HOME/plugins"
  cp -a "$CODEX_HOME/plugins/cache" "$CODEX_HOME/plugins/cache.before-codex-ops-$BACKUP_SUFFIX"
fi
if [ -d "$BOT_TARGET" ]; then
  cp -a "$BOT_TARGET" "$BOT_TARGET.before-codex-ops-$BACKUP_SUFFIX"
fi

if [ -d "$REPO_ROOT/snapshot/codex/skills" ]; then
  mkdir -p "$CODEX_HOME/skills"
  rsync -a "$REPO_ROOT/snapshot/codex/skills/" "$CODEX_HOME/skills/"
fi

if [ -d "$REPO_ROOT/snapshot/codex/agents" ]; then
  mkdir -p "$CODEX_HOME/agents"
  rsync -a "$REPO_ROOT/snapshot/codex/agents/" "$CODEX_HOME/agents/"
fi

if [ -d "$REPO_ROOT/snapshot/codex/plugins/cache" ]; then
  mkdir -p "$CODEX_HOME/plugins/cache"
  rsync -a "$REPO_ROOT/snapshot/codex/plugins/cache/" "$CODEX_HOME/plugins/cache/"
fi

if [ -f "$REPO_ROOT/snapshot/codex/config.toml" ]; then
  if [ -f "$CODEX_HOME/config.toml" ]; then
    cp -p "$REPO_ROOT/snapshot/codex/config.toml" "$CODEX_HOME/config.toml.codex-ops-example"
  else
    cp -p "$REPO_ROOT/snapshot/codex/config.toml" "$CODEX_HOME/config.toml"
  fi
fi

mkdir -p "$BOT_TARGET"
rsync -a \
  --exclude '.env' \
  --exclude 'logs' \
  --exclude 'var' \
  "$REPO_ROOT/snapshot/telegram-bot/" "$BOT_TARGET/"
mkdir -p "$BOT_TARGET/logs" "$BOT_TARGET/var"
chmod +x "$BOT_TARGET/telegram_codex_bot.py" "$BOT_TARGET/notify-codex.sh" 2>/dev/null || true

for file in "$BOT_TARGET/telegram_codex_bot.py" "$BOT_TARGET/notify-codex.sh" "$BOT_TARGET/README.md" "$BOT_TARGET/.env.example"; do
  if [ -f "$file" ]; then
    sed -i \
      -e "s#/home/ubuntuhong/dev#$DEV_DIR#g" \
      -e "s#/home/ubuntuhong/.codex#$CODEX_HOME#g" \
      -e "s#/home/ubuntuhong/.npm-global#$HOME_DIR/.npm-global#g" \
      "$file"
  fi
done

if [ ! -f "$BOT_TARGET/.env" ] && [ -f "$BOT_TARGET/.env.example" ]; then
  cp -p "$BOT_TARGET/.env.example" "$BOT_TARGET/.env"
  chmod 600 "$BOT_TARGET/.env"
fi

printf 'Install complete.\n'
printf 'Codex home: %s\n' "$CODEX_HOME"
printf 'Telegram bot: %s\n' "$BOT_TARGET"
printf 'Fill Telegram values in %s/.env before starting the router.\n' "$BOT_TARGET"
