#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEST_ROOT="$(mktemp -d)"
OLD_PID=""
NEW_PID=""

cleanup() {
  for pid in "$OLD_PID" "$NEW_PID"; do
    if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
      kill "$pid" 2>/dev/null || true
    fi
  done
  rm -rf "$TEST_ROOT"
}
trap cleanup EXIT

mkdir -p "$TEST_ROOT/var" "$TEST_ROOT/logs"
cp "$PROJECT_ROOT/healthcheck.sh" "$TEST_ROOT/healthcheck.sh"
printf '%s\n' \
  '#!/usr/bin/env bash' \
  'set -euo pipefail' \
  'ROOT="$(cd "$(dirname "$0")" && pwd)"' \
  'printf "%s\\n" "$$" > "$ROOT/var/router.pid"' \
  'if [[ "${FAKE_STALLED:-}" == "1" ]]; then' \
  '  while true; do sleep 1; done' \
  'fi' \
  'while true; do' \
  '  date +%s > "$ROOT/var/router.heartbeat"' \
  '  sleep 1' \
  'done' \
  > "$TEST_ROOT/telegram_codex_bot.py"
chmod +x "$TEST_ROOT/healthcheck.sh" "$TEST_ROOT/telegram_codex_bot.py"

(cd "$TEST_ROOT" && exec env FAKE_STALLED=1 /bin/bash "$TEST_ROOT/telegram_codex_bot.py") &
OLD_PID="$!"
for _ in {1..50}; do
  [[ -s "$TEST_ROOT/var/router.pid" ]] && break
  sleep 0.02
done

PYTHON_BIN=/bin/bash HEALTHCHECK_HEARTBEAT_MAX_AGE_SECONDS=1 \
  "$TEST_ROOT/healthcheck.sh" --root "$TEST_ROOT"
NEW_PID="$(< "$TEST_ROOT/var/router.pid")"

[[ "$NEW_PID" != "$OLD_PID" ]]
! kill -0 "$OLD_PID" 2>/dev/null
[[ -s "$TEST_ROOT/var/router.heartbeat" ]]
