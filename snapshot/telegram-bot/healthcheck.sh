#!/usr/bin/env bash
set -u -o pipefail

DEFAULT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$DEFAULT_ROOT"
DRY_RUN=false

usage() {
  printf 'Usage: %s [--dry-run] [--root PATH]\n' "${0##*/}"
}

while (($# > 0)); do
  case "$1" in
    --dry-run)
      DRY_RUN=true
      ;;
    --root)
      shift
      if (($# == 0)); then
        usage >&2
        exit 2
      fi
      ROOT_DIR="$(cd "$1" && pwd)"
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      usage >&2
      exit 2
      ;;
  esac
  shift
done

readonly PID_FILE="$ROOT_DIR/var/router.pid"
readonly LOCK_FILE="$ROOT_DIR/var/healthcheck.lock"
readonly LOG_FILE="$ROOT_DIR/logs/healthcheck.log"
readonly STATUS_FILE="$ROOT_DIR/var/healthcheck.status"
readonly ROUTER_SCRIPT="$ROOT_DIR/telegram_codex_bot.py"
readonly HEARTBEAT_FILE="$ROOT_DIR/var/router.heartbeat"
readonly PYTHON_BIN="${PYTHON_BIN:-/usr/bin/python3}"
readonly HEARTBEAT_MAX_AGE_SECONDS="${HEALTHCHECK_HEARTBEAT_MAX_AGE_SECONDS:-180}"

log() {
  local message="$1"
  local line
  line="$(date '+[%Y-%m-%dT%H:%M:%S%z]') $message"
  printf '%s\n' "$line" | tee -a "$LOG_FILE"
}

log_state_change() {
  local state="$1"
  local message="$2"
  local previous_state=""

  if [[ -f "$STATUS_FILE" ]]; then
    previous_state="$(< "$STATUS_FILE")"
  fi
  if [[ "$state" == "$previous_state" ]]; then
    return
  fi
  printf '%s\n' "$state" > "$STATUS_FILE"
  log "$message"
}

router_pid() {
  local pid
  [[ -f "$PID_FILE" ]] || return 1
  pid="$(tr -d '[:space:]' < "$PID_FILE")"
  [[ "$pid" =~ ^[1-9][0-9]*$ ]] || return 1
  printf '%s\n' "$pid"
}

router_is_owned() {
  local pid="$1"
  local command_line
  local working_directory

  kill -0 "$pid" 2>/dev/null || return 1
  command_line="$(tr '\0' ' ' < "/proc/$pid/cmdline" 2>/dev/null)" || return 1
  working_directory="$(readlink -f "/proc/$pid/cwd" 2>/dev/null)" || return 1
  [[ "$working_directory" == "$ROOT_DIR" ]] || return 1
  [[ "$command_line" == *"telegram_codex_bot.py"* ]]
}

router_heartbeat_is_fresh() {
  local modified_at
  local now

  [[ -f "$HEARTBEAT_FILE" ]] || return 1
  modified_at="$(stat -c '%Y' "$HEARTBEAT_FILE" 2>/dev/null)" || return 1
  now="$(date +%s)"
  (( modified_at <= now && now - modified_at <= HEARTBEAT_MAX_AGE_SECONDS ))
}

router_is_healthy() {
  local pid="$1"

  router_is_owned "$pid" || return 1
  if ! router_heartbeat_is_fresh; then
    log "router heartbeat missing or stale pid=$pid"
    return 1
  fi
}

stop_router() {
  local attempt
  local pid="$1"

  if [[ "$DRY_RUN" == true ]]; then
    log "dry run: router stop required pid=$pid"
    return 0
  fi

  log "router unhealthy; stopping pid=$pid"
  kill -TERM "$pid" 2>/dev/null || return 1
  for attempt in {1..10}; do
    if ! kill -0 "$pid" 2>/dev/null; then
      return 0
    fi
    sleep 1
  done

  log "router did not stop after 10 seconds; sending SIGKILL pid=$pid"
  kill -KILL "$pid" 2>/dev/null || return 1
  for attempt in {1..5}; do
    if ! kill -0 "$pid" 2>/dev/null; then
      return 0
    fi
    sleep 1
  done

  log "recovery failed: router process remained after SIGKILL pid=$pid"
  return 1
}

start_router() {
  local attempt
  local pid

  if [[ ! -x "$PYTHON_BIN" ]]; then
    log "recovery failed: Python executable missing: $PYTHON_BIN"
    return 1
  fi
  if [[ ! -f "$ROUTER_SCRIPT" ]]; then
    log "recovery failed: router script missing: $ROUTER_SCRIPT"
    return 1
  fi
  if [[ "$DRY_RUN" == true ]]; then
    log "dry run: router restart required"
    return 0
  fi

  if pid="$(router_pid)" && router_is_owned "$pid"; then
    stop_router "$pid" || return 1
  fi

  log "router unhealthy; starting replacement"
  (
    cd "$ROOT_DIR" || exit 1
    nohup "$PYTHON_BIN" "$ROUTER_SCRIPT" >> "$ROOT_DIR/logs/router.stdout.log" 2>&1 &
  )

  for attempt in {1..10}; do
    sleep 1
    if pid="$(router_pid)" && router_is_healthy "$pid"; then
      log_state_change "healthy:$pid" "router recovered pid=$pid"
      return 0
    fi
  done

  log "recovery failed: replacement did not become healthy within 10 seconds"
  return 1
}

main() {
  local pid

  mkdir -p "$ROOT_DIR/var" "$ROOT_DIR/logs"
  if ! [[ "$HEARTBEAT_MAX_AGE_SECONDS" =~ ^[1-9][0-9]*$ ]]; then
    log "healthcheck configuration error: HEALTHCHECK_HEARTBEAT_MAX_AGE_SECONDS must be a positive integer"
    return 2
  fi
  exec 9>"$LOCK_FILE"
  if ! flock -n 9; then
    log "healthcheck skipped: another check is running"
    return 0
  fi

  if pid="$(router_pid)" && router_is_healthy "$pid"; then
    log_state_change "healthy:$pid" "router healthy pid=$pid"
    return 0
  fi

  start_router
}

main
