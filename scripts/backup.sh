#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOME_DIR="${HOME:-/home/ubuntuhong}"
DEV_DIR="${DEV_DIR:-$HOME_DIR/dev}"
CODEX_HOME="${CODEX_HOME:-$HOME_DIR/.codex}"
BOT_DIR="${BOT_DIR:-$DEV_DIR/codex-telegram-bot}"
SNAPSHOT_DIR="$REPO_ROOT/snapshot"
CODEX_BIN="${CODEX_BIN:-/home/ubuntuhong/.npm-global/bin/codex}"

copy_file() {
  local source="$1"
  local base="$2"
  local target_root="$3"
  local rel="${source#"$base"/}"
  mkdir -p "$target_root/$(dirname "$rel")"
  cp -p "$source" "$target_root/$rel"
}

sanitize_config() {
  local source="$1"
  local target="$2"
  mkdir -p "$(dirname "$target")"
  sed -E \
    -e 's/(token[[:space:]]*=[[:space:]]*)".*"/\1"[REDACTED]"/Ig' \
    -e 's/(key[[:space:]]*=[[:space:]]*)".*"/\1"[REDACTED]"/Ig' \
    -e 's/(secret[[:space:]]*=[[:space:]]*)".*"/\1"[REDACTED]"/Ig' \
    -e 's/(password[[:space:]]*=[[:space:]]*)".*"/\1"[REDACTED]"/Ig' \
    "$source" > "$target"
}

write_env_example() {
  local target="$1"
  cat > "$target" <<'ENV'
TG_CODEX_BOT_TOKEN=
TG_CHAT_ID=
CODEX_BIN=/home/ubuntuhong/.npm-global/bin/codex
CODEX_WORK_DIR=/home/ubuntuhong/dev
CODEX_EXEC_TIMEOUT=600
ENV
}

write_manifest() {
  local target="$SNAPSHOT_DIR/MANIFEST.md"
  local timestamp
  timestamp="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

  {
    printf '# Codex Ops Snapshot\n\n'
    printf -- '- Generated: `%s`\n' "$timestamp"
    printf -- '- Host: `%s`\n' "$(hostname)"
    printf -- '- User: `%s`\n' "$(id -un)"
    printf -- '- Source dev dir: `%s`\n' "$DEV_DIR"
    printf -- '- Source Codex home: `%s`\n' "$CODEX_HOME"
    printf -- '- Telegram router: `%s`\n' "$BOT_DIR"
    if [ -x "$CODEX_BIN" ]; then
      printf -- '- Codex CLI: `%s`\n' "$("$CODEX_BIN" --version 2>/dev/null || true)"
    else
      printf -- '- Codex CLI: `not found at %s`\n' "$CODEX_BIN"
    fi
    printf '\n## Local Skills\n\n'
    find "$CODEX_HOME/skills" -name SKILL.md -print 2>/dev/null \
      | sed "s#^$CODEX_HOME/skills/##; s#/SKILL.md\$##" \
      | sort \
      | sed 's#^#- #'
    printf '\n## Plugin Skills\n\n'
    find "$CODEX_HOME/plugins/cache" -path '*/skills/*/SKILL.md' -print 2>/dev/null \
      | sed "s#^$CODEX_HOME/plugins/cache/##; s#/SKILL.md\$##" \
      | sort \
      | sed 's#^#- #'
    printf '\n## Telegram Router Files\n\n'
    find "$SNAPSHOT_DIR/telegram-bot" -maxdepth 2 -type f -print 2>/dev/null \
      | sed "s#^$SNAPSHOT_DIR/telegram-bot/##" \
      | sort \
      | sed 's#^#- #'
  } > "$target"
}

rm -rf "$SNAPSHOT_DIR"
mkdir -p "$SNAPSHOT_DIR/codex" "$SNAPSHOT_DIR/telegram-bot"

if [ -f "$CODEX_HOME/config.toml" ]; then
  sanitize_config "$CODEX_HOME/config.toml" "$SNAPSHOT_DIR/codex/config.toml"
fi

if [ -d "$CODEX_HOME/skills" ]; then
  mkdir -p "$SNAPSHOT_DIR/codex/skills"
  rsync -a --delete "$CODEX_HOME/skills/" "$SNAPSHOT_DIR/codex/skills/"
fi

if [ -d "$CODEX_HOME/agents" ]; then
  mkdir -p "$SNAPSHOT_DIR/codex/agents"
  rsync -a --delete "$CODEX_HOME/agents/" "$SNAPSHOT_DIR/codex/agents/"
fi

if [ -d "$CODEX_HOME/plugins/cache" ]; then
  mkdir -p "$SNAPSHOT_DIR/codex/plugins/cache"
  while IFS= read -r -d '' file; do
    copy_file "$file" "$CODEX_HOME/plugins/cache" "$SNAPSHOT_DIR/codex/plugins/cache"
  done < <(
    find "$CODEX_HOME/plugins/cache" -type f \( \
      -path '*/skills/*' -o \
      -path '*/components/*/skills/*' -o \
      -path '*/.agents/plugins/*' -o \
      -name '.mcp.json' -o \
      -name '.app.json' -o \
      -name 'plugin.lock.json' -o \
      -name 'lazycodex-install.json' -o \
      -name 'model-catalog.json' -o \
      -name 'package.json' \
    \) -print0
  )
fi

if [ -d "$BOT_DIR" ]; then
  rsync -a --delete \
    --exclude '.env' \
    --exclude 'logs' \
    --exclude 'var' \
    --exclude '__pycache__' \
    --exclude '*.pyc' \
    "$BOT_DIR/" "$SNAPSHOT_DIR/telegram-bot/"
  write_env_example "$SNAPSHOT_DIR/telegram-bot/.env.example"
fi

write_manifest

if git -C "$REPO_ROOT" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  git -C "$REPO_ROOT" add -A
  if ! git -C "$REPO_ROOT" diff --cached --quiet; then
    git -C "$REPO_ROOT" commit -m "Backup Codex ops snapshot $(date -u +%F)"
  fi
  if git -C "$REPO_ROOT" remote get-url origin >/dev/null 2>&1; then
    git -C "$REPO_ROOT" push
  fi
fi

printf 'Codex ops backup complete: %s\n' "$SNAPSHOT_DIR"
