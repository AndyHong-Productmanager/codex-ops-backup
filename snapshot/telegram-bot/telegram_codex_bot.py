#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# ///
# How to run:
# cd /home/ubuntuhong/dev/codex-telegram-bot
# nohup python3 telegram_codex_bot.py > logs/router.stdout.log 2>&1 &
from __future__ import annotations

import atexit
import fcntl
import glob
import json
import os
import pathlib
import queue
import re
import signal
import subprocess
import sys
import threading
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from typing import Final, TextIO, TypedDict, assert_never

from telegram_media import (
    MediaSettings,
    PreparedUpdate,
    TelegramMediaClient,
    prepare_telegram_update,
)


ROOT: Final = pathlib.Path(__file__).resolve().parent
ENV_FILE: Final = ROOT / ".env"
VAR_DIR: Final = ROOT / "var"
LOG_DIR: Final = ROOT / "logs"
OFFSET_FILE: Final = VAR_DIR / "telegram.offset"
SESSION_FILE: Final = VAR_DIR / "codex.session"
PID_FILE: Final = VAR_DIR / "router.pid"
HEARTBEAT_FILE: Final = VAR_DIR / "router.heartbeat"
INFLIGHT_FILE: Final = VAR_DIR / "inflight.json"
POLL_LOCK_FILE: Final = pathlib.Path(
    os.environ.get(
        "TG_CODEX_POLL_LOCK_FILE",
        f"/run/user/{os.getuid()}/codex-telegram-bot.poller.lock",
    )
)
LOG_FILE: Final = LOG_DIR / "router.log"


def load_env() -> None:
    if not ENV_FILE.exists():
        return
    for raw in ENV_FILE.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ[key.strip()] = value.strip().strip('"').strip("'")


load_env()


CODEX_BIN: Final = os.environ.get(
    "CODEX_BIN", "/home/ubuntuhong/.npm-global/bin/codex"
)
CODEX_MODEL: Final = os.environ.get("CODEX_MODEL", "gpt-5.6-terra")
CODEX_REASONING: Final = os.environ.get("CODEX_REASONING", "high")
WORK_DIR: Final = os.environ.get("CODEX_WORK_DIR", str(ROOT))
EXEC_TIMEOUT: Final = int(os.environ.get("CODEX_EXEC_TIMEOUT", "21600"))
CODEX_SESSIONS_DIR: Final = pathlib.Path(
    os.environ.get("CODEX_SESSIONS_DIR", "/home/ubuntuhong/.codex/sessions")
)

SECTION_RE: Final = re.compile(
    r"(?:^|\n)codex\n(?P<body>.*?)(?=\n(?:developer\n|system\n|hook:|tokens used|user\n|codex\n|$))",
    re.DOTALL,
)
SESSION_ID_RE: Final = re.compile(
    r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
)
RETURNED_SESSION_ID_RE: Final = re.compile(
    rf"(?im)^session id:\s*({SESSION_ID_RE.pattern})\s*$"
)
LOG_BEARER_TOKEN_RE: Final = re.compile(
    r"(?i)(\bauthorization\s*:\s*bearer\s+)([^\s]+)"
)
LOG_SECRET_ASSIGNMENT_RE: Final = re.compile(
    r"(?i)(\b(?:api[_-]?key|token|secret|password)\s*[=:]\s*)([^\s\"']+)"
)
LOG_OPENAI_KEY_RE: Final = re.compile(r"\bsk-[A-Za-z0-9_-]+")
LOG_TELEGRAM_TOKEN_RE: Final = re.compile(r"\b\d{6,}:[A-Za-z0-9_-]{20,}\b")
USER_ECHO_RE: Final = re.compile(
    r"(?:^|\n)user\n.*?(?=\n(?:codex\n|hook:|warning:|tokens used|--------\n|$))",
    re.DOTALL,
)
NOISE_PREFIXES: Final = (
    "hook:", "tokens used", "model:", "directory:", "workdir:",
    "provider:", "approval:", "sandbox:", "reasoning", "session id:",
    "OpenAI Codex", "--------", "user", "warning:",
    "Reading additional input",
)
TODO_NUMBERED_RE: Final = re.compile(r"^\s*(\d+)[.)]\s+(.+)$", re.MULTILINE)

PROGRESS_MIN_INTERVAL: Final = 20
CHUNK_SIZE: Final = 3900
CHUNK_SLEEP: Final = 0.4

CONTEXT_FULL_MARKERS: Final = (
    "ran out of room in the model's context window",
    "context length exceeded",
    "maximum context length",
)

# OPERATING_RULES is loaded from the backup copy to preserve original em-dashes
# that the linter forbids in generated files.
_RULES_FILE: Final = ROOT / "operating_rules.txt"

_OPERATING_RULES_FALLBACK: Final = (
    "[Rules -- follow every turn, do not include in answer]\n"
    "- Your final answer goes to stdout and is relayed to Andy's Telegram.\n"
    "- For tasks >30s, send progress via:\n"
    "    bash /home/ubuntuhong/dev/codex-telegram-bot/notify-codex.sh "
    '"status: <short report>"\n'
    "- Answer in Korean, essentials only. Wrap paths in `backtick`.\n"
    "- Do not create/edit orchestra/, docs/rag/, docs/obsidian/ files.\n"
    "- Never output placeholder text as-is.\n"
    "\n[Context budget]\n"
    "- Do not embed screenshots/images in conversation.\n"
    "- Save images to /tmp or workdir; answer with path only.\n"
    "- Do not create scripts that output base64 images.\n"
    "- Redirect long output to file; use head/tail/grep.\n"
    "- Summarize intermediate findings; do not re-check known facts.\n"
    "\n[Andy message]\n"
)


def _load_operating_rules() -> str:
    if _RULES_FILE.exists():
        return _RULES_FILE.read_text(encoding="utf-8")
    return _OPERATING_RULES_FALLBACK


OPERATING_RULES: Final = _load_operating_rules()


class TelegramResult(TypedDict, total=False):
    ok: bool
    result: list[dict[str, object]]


@dataclass(frozen=True, slots=True)
class Config:
    bot_token: str
    chat_id: str


@dataclass(frozen=True, slots=True)
class CommandResult:
    returncode: int
    stdout: str
    stderr: str


@dataclass
class TodoItem:
    text: str
    status: str = "pending"


@dataclass
class ProgressState:
    start_time: float = field(default_factory=time.time)
    todos: list[TodoItem] = field(default_factory=list)
    latest_activity: str = ""
    queue_depth: int = 0
    progress_msg_id: int | None = None
    _last_content_key: str = ""
    _last_sent_time: float = 0.0

    def format_message(self) -> str:
        elapsed = time.time() - self.start_time
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)
        lines = [f"⏳ 작업 중 ({minutes}분 {seconds}초 경과)"]
        if self.todos:
            done_count = sum(1 for t in self.todos if t.status == "done")
            lines.append(f"진행: {done_count}/{len(self.todos)} 완료")
            for t in self.todos:
                icon = {"done": "✅", "in_progress": "\U0001f535", "pending": "⬜"}.get(t.status, "⬜")
                label = {"done": "완료", "in_progress": "진행중", "pending": "대기"}.get(t.status, "대기")
                lines.append(f"{icon} {t.text} ({label})")
        if self.latest_activity:
            lines.append(f"최근: {self.latest_activity}")
        lines.append(f"대기열: {self.queue_depth}건 \xb7 제한 {EXEC_TIMEOUT // 60}분")
        lines.append("중지: /cancel")
        return "\n".join(lines)

    def content_key(self) -> str:
        parts = []
        if self.todos:
            parts.append("|".join(t.status for t in self.todos))
        parts.append(self.latest_activity)
        return "\n".join(parts)


_codex_lock = threading.Lock()
_current_process: subprocess.Popen[str] | None = None
_current_process_lock = threading.Lock()
_cancel_event = threading.Event()
_message_queue: list[str] = []
_queue_lock = threading.Lock()
_pid_lock_handle: TextIO | None = None


def log(message: str) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    line = time.strftime("[%Y-%m-%dT%H:%M:%S%z] ") + message
    with LOG_FILE.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")
    print(line, flush=True)


def load_config() -> Config:
    load_env()
    token = os.environ.get("TG_CODEX_BOT_TOKEN")
    chat_id = os.environ.get("TG_CHAT_ID")
    if not token or not chat_id:
        raise RuntimeError("TG_CODEX_BOT_TOKEN/TG_CHAT_ID missing")
    return Config(bot_token=token, chat_id=chat_id)


def api(config: Config, method: str, params: dict[str, int | str] | None) -> TelegramResult:
    url = f"https://api.telegram.org/bot{config.bot_token}/{method}"
    data = urllib.parse.urlencode(params).encode() if params is not None else None
    request = urllib.request.Request(url, data=data)
    with urllib.request.urlopen(request, timeout=70) as response:
        payload = json.load(response)
    if not isinstance(payload, dict):
        raise RuntimeError("Telegram returned non-object payload")
    return payload


def read_int(path: pathlib.Path) -> int | None:
    try:
        return int(path.read_text(encoding="utf-8").strip())
    except (FileNotFoundError, ValueError):
        return None


def write_text(path: pathlib.Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")


def write_heartbeat() -> None:
    write_text(HEARTBEAT_FILE, str(time.time_ns()))


def read_session_id() -> str | None:
    try:
        value = SESSION_FILE.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        return None
    return value or None


def returned_session_id(output: str) -> str | None:
    match = RETURNED_SESSION_ID_RE.search(output)
    return match.group(1) if match else None


def session_files_snapshot() -> set[pathlib.Path]:
    pattern = str(CODEX_SESSIONS_DIR / "**" / "rollout-*.jsonl")
    return {pathlib.Path(path) for path in glob.glob(pattern, recursive=True)}


def session_file_metadata(path: pathlib.Path) -> tuple[str, pathlib.Path] | None:
    try:
        with path.open(encoding="utf-8") as handle:
            record = json.loads(handle.readline())
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(record, dict) or record.get("type") != "session_meta":
        return None
    payload = record.get("payload")
    if not isinstance(payload, dict):
        return None
    session_id = payload.get("session_id")
    cwd = payload.get("cwd")
    if not isinstance(session_id, str) or not SESSION_ID_RE.fullmatch(session_id):
        return None
    if not isinstance(cwd, str):
        return None
    return session_id, pathlib.Path(cwd).resolve()


def select_new_session(before: set[pathlib.Path]) -> tuple[str | None, int]:
    expected_cwd = pathlib.Path(WORK_DIR).resolve()
    candidates: list[tuple[pathlib.Path, str]] = []
    for path in session_files_snapshot() - before:
        metadata = session_file_metadata(path)
        if metadata is None:
            continue
        session_id, cwd = metadata
        if cwd == expected_cwd:
            candidates.append((path, session_id))
    candidates.sort(key=lambda candidate: candidate[0].stat().st_mtime_ns, reverse=True)
    if not candidates:
        return None, 0
    return candidates[0][1], len(candidates)


def redact_log_text(text: str) -> str:
    redacted = LOG_BEARER_TOKEN_RE.sub(r"\1[REDACTED]", text)
    redacted = LOG_SECRET_ASSIGNMENT_RE.sub(r"\1[REDACTED]", redacted)
    redacted = LOG_OPENAI_KEY_RE.sub("[REDACTED]", redacted)
    return LOG_TELEGRAM_TOKEN_RE.sub("[REDACTED]", redacted)


def extract_codex_response(stdout: str) -> str:
    matches = list(SECTION_RE.finditer(stdout))
    if matches:
        return matches[-1].group("body").strip()
    scrubbed = USER_ECHO_RE.sub("\n", stdout)
    cleaned: list[str] = []
    for line in scrubbed.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if any(stripped.startswith(prefix) for prefix in NOISE_PREFIXES):
            continue
        cleaned.append(line)
    return "\n".join(cleaned).strip() or "(empty response)"


# ---- Inflight marker ----

def write_inflight(text: str) -> None:
    data = {"text": text[:200], "started": time.time(), "pid": os.getpid()}
    write_text(INFLIGHT_FILE, json.dumps(data, ensure_ascii=False))


def clear_inflight() -> None:
    INFLIGHT_FILE.unlink(missing_ok=True)


def check_inflight_on_boot(config: Config) -> None:
    if not INFLIGHT_FILE.exists():
        return
    try:
        data = json.loads(INFLIGHT_FILE.read_text(encoding="utf-8"))
        started = data.get("started", 0)
        text_preview = data.get("text", "")[:100]
        elapsed = time.time() - started
    except (json.JSONDecodeError, OSError):
        INFLIGHT_FILE.unlink(missing_ok=True)
        return
    INFLIGHT_FILE.unlink(missing_ok=True)
    minutes = int(elapsed / 60)
    log(f"boot: stale inflight marker found, age={minutes}m")
    try:
        send_chunked(
            config,
            "⚠️ 봇이 재시작되었습니다. "
            "이전 작업이 중단되었을 수 있습니다.\n"
            f"중단된 요청 (약 {minutes}분 전): {text_preview}\n"
            "필요하면 같은 메시지를 다시 보내주세요.",
        )
    except Exception:
        pass


# ---- Telegram messaging ----

def send_chunked(config: Config, text: str) -> None:
    if not text:
        return
    if len(text) <= CHUNK_SIZE:
        api(config, "sendMessage", {"chat_id": config.chat_id, "text": text})
        return
    chunks: list[str] = []
    remaining = text
    while remaining:
        if len(remaining) <= CHUNK_SIZE:
            chunks.append(remaining)
            break
        cut = remaining[:CHUNK_SIZE].rfind("\n")
        if cut < CHUNK_SIZE // 2:
            cut = CHUNK_SIZE
        chunks.append(remaining[:cut])
        remaining = remaining[cut:].lstrip("\n")
    total = len(chunks)
    for i, chunk in enumerate(chunks):
        label = f"({i + 1}/{total}) " if total > 1 else ""
        api(config, "sendMessage", {"chat_id": config.chat_id, "text": label + chunk})
        if i < total - 1:
            time.sleep(CHUNK_SLEEP)


def notify(config: Config, text: str) -> None:
    send_chunked(config, text)


def edit_or_send(
    config: Config, message_id: int | None, text: str,
) -> int | None:
    truncated = text[:4096]
    if message_id is not None:
        try:
            api(config, "editMessageText", {
                "chat_id": config.chat_id,
                "message_id": message_id,
                "text": truncated,
            })
            return message_id
        except urllib.error.HTTPError as exc:
            if exc.code == 400:
                return message_id
        except Exception:
            pass
    try:
        result = api(config, "sendMessage", {
            "chat_id": config.chat_id, "text": truncated,
        })
        msg = result.get("result")
        if isinstance(msg, dict):
            mid = msg.get("message_id")
            if isinstance(mid, int):
                return mid
    except Exception:
        pass
    return message_id


def maybe_send_progress(config: Config, state: ProgressState) -> None:
    now = time.time()
    content_key = state.content_key()
    if content_key == state._last_content_key:
        return
    if now - state._last_sent_time < PROGRESS_MIN_INTERVAL:
        return
    text = state.format_message()
    state.progress_msg_id = edit_or_send(config, state.progress_msg_id, text)
    state._last_content_key = content_key
    state._last_sent_time = now
    log(f"progress update sent: activity={state.latest_activity!r} msg_id={state.progress_msg_id}")


# ---- Todo parsing ----

def parse_todos(text: str) -> list[TodoItem]:
    matches = TODO_NUMBERED_RE.findall(text)
    if len(matches) < 2:
        return []
    items: list[TodoItem] = []
    for _, desc in matches:
        desc = desc.strip().rstrip(".")
        if len(desc) > 80:
            desc = desc[:77] + "..."
        items.append(TodoItem(text=desc))
    return items


def advance_todo(state: ProgressState) -> None:
    for i, t in enumerate(state.todos):
        if t.status == "in_progress":
            t.status = "done"
            if i + 1 < len(state.todos):
                state.todos[i + 1].status = "in_progress"
            return


# ---- Process management ----

def _terminate_process_group(
    process: subprocess.Popen[str], grace: float = 5.0,
) -> None:
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    try:
        process.wait(timeout=grace)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            pass


def _stdout_reader(pipe: TextIO, q: queue.Queue[str | None]) -> None:
    try:
        for line in pipe:
            q.put(line)
    except Exception:
        pass
    finally:
        q.put(None)


# ---- Codex execution ----

def _context_full(output: str) -> bool:
    lowered = output.lower()
    return any(marker.lower() in lowered for marker in CONTEXT_FULL_MARKERS)


def _run_codex_once(
    text: str,
    *,
    allow_resume: bool,
    config: Config,
    queue_depth: int = 0,
) -> tuple[int, str, str | None, str, str]:
    """Run one codex exec with JSONL streaming.

    Returns (rc, raw_output, new_session_id, mode, response_text).
    """
    session_id = read_session_id() if allow_resume else None
    wrapped = OPERATING_RULES + text
    base = [
        CODEX_BIN, "exec", "--json",
        "--skip-git-repo-check", "--cd", WORK_DIR,
        "--model", CODEX_MODEL,
        "-c", f'model_reasoning_effort="{CODEX_REASONING}"',
    ]
    if session_id:
        cmd = [*base, "resume", session_id, wrapped]
        mode = f"resume({session_id[:8]}...)"
    else:
        cmd = [*base, wrapped]
        mode = "new"

    before = session_files_snapshot()
    log(f"codex exec start {mode} chars={len(text)}")
    write_inflight(text)

    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=WORK_DIR,
            start_new_session=True,
        )
    except FileNotFoundError:
        clear_inflight()
        log(f"codex binary missing: {CODEX_BIN}")
        return (127, "codex binary missing", None, mode, "codex binary missing")

    with _current_process_lock:
        global _current_process
        _current_process = process

    progress = ProgressState(queue_depth=queue_depth)
    new_session: str | None = None
    agent_messages: list[str] = []
    raw_lines: list[str] = []
    plan_parsed = False
    agent_msg_count = 0

    progress.latest_activity = "시작 중..."
    progress.progress_msg_id = edit_or_send(config, None, progress.format_message())
    progress._last_sent_time = time.time()
    progress._last_content_key = progress.content_key()

    stdout_q: queue.Queue[str | None] = queue.Queue()
    reader = threading.Thread(
        target=_stdout_reader, args=(process.stdout, stdout_q), daemon=True,
    )
    reader.start()

    deadline = time.time() + EXEC_TIMEOUT
    timed_out = False
    cancelled = False

    try:
        while True:
            try:
                line = stdout_q.get(timeout=1.0)
            except queue.Empty:
                if time.time() > deadline:
                    timed_out = True
                    _terminate_process_group(process, grace=3.0)
                    break
                if _cancel_event.is_set():
                    cancelled = True
                    _terminate_process_group(process, grace=3.0)
                    break
                continue

            if line is None:
                break

            raw_lines.append(line)
            stripped = line.strip()
            if not stripped:
                continue

            try:
                event = json.loads(stripped)
            except json.JSONDecodeError:
                continue

            etype = event.get("type", "")

            if etype == "thread.started":
                sid = event.get("thread_id")
                if isinstance(sid, str) and SESSION_ID_RE.fullmatch(sid):
                    new_session = sid

            elif etype == "item.completed":
                item = event.get("item", {})
                itype = item.get("type", "")

                if itype == "agent_message":
                    msg_text = item.get("text", "")
                    agent_messages.append(msg_text)
                    agent_msg_count += 1

                    if not plan_parsed:
                        parsed = parse_todos(msg_text)
                        if parsed:
                            progress.todos = parsed
                            progress.todos[0].status = "in_progress"
                            plan_parsed = True
                    elif progress.todos and agent_msg_count > 1:
                        advance_todo(progress)

                    short = msg_text.replace("\n", " ").strip()[:50]
                    if short:
                        progress.latest_activity = short
                    maybe_send_progress(config, progress)

                elif itype == "file_change":
                    changes = item.get("changes", [])
                    if changes:
                        path = changes[0].get("path", "")
                        progress.latest_activity = (
                            f"파일 수정: {os.path.basename(path)}"
                        )
                    maybe_send_progress(config, progress)

                elif itype == "command_execution":
                    cmd_str = item.get("command", "")
                    short_cmd = cmd_str.split("\n")[0][:50]
                    ec = item.get("exit_code")
                    if ec == 0:
                        progress.latest_activity = (
                            f"명령 완료: {short_cmd}"
                        )
                    elif ec is not None:
                        progress.latest_activity = (
                            f"명령 실패(rc={ec}): {short_cmd}"
                        )
                    maybe_send_progress(config, progress)

            elif etype == "item.started":
                item = event.get("item", {})
                itype = item.get("type", "")

                if itype == "file_change":
                    changes = item.get("changes", [])
                    if changes:
                        path = changes[0].get("path", "")
                        progress.latest_activity = (
                            f"파일 수정 중: {os.path.basename(path)}"
                        )
                    maybe_send_progress(config, progress)

                elif itype == "command_execution":
                    cmd_str = item.get("command", "")
                    short_cmd = cmd_str.split("\n")[0][:50]
                    progress.latest_activity = (
                        f"명령 실행 중: {short_cmd}"
                    )
                    maybe_send_progress(config, progress)

        reader.join(timeout=5)
        stderr_output = ""
        if process.stderr:
            try:
                stderr_output = process.stderr.read()
            except Exception:
                pass
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            _terminate_process_group(process, grace=3.0)

    finally:
        with _current_process_lock:
            _current_process = None
        clear_inflight()

    rc = process.returncode if process.returncode is not None else -1
    raw_output = "".join(raw_lines) + (
        "\n" + stderr_output if stderr_output else ""
    )

    if new_session is None:
        new_session, candidate_count = select_new_session(before)
        if candidate_count > 1:
            log(
                f"codex session candidates count={candidate_count}; "
                "selecting newest"
            )
    if new_session:
        write_text(SESSION_FILE, new_session)

    if cancelled:
        response = "사용자 요청으로 중지되었습니다."
        if agent_messages:
            response += (
                "\n\n[중단 시점까지의 결과]\n"
                + agent_messages[-1]
            )
        elapsed = time.time() - progress.start_time
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)
        edit_or_send(
            config, progress.progress_msg_id,
            f"\U0001f6d1 작업 중지 ({minutes}분 {seconds}초)",
        )
        log(f"codex exec cancelled reply_chars={len(response)}")
        return (rc, raw_output, new_session, mode, response)

    if timed_out:
        response = (
            f"Codex 실행이 제한 시간"
            f"({EXEC_TIMEOUT // 60}분)을 넘겼습니다."
        )
        if agent_messages:
            response += (
                "\n\n[타임아웃 시점까지의 결과]\n"
                + agent_messages[-1]
            )
        elapsed = time.time() - progress.start_time
        minutes = int(elapsed // 60)
        edit_or_send(
            config, progress.progress_msg_id,
            f"⏰ 시간 초과 ({minutes}분)",
        )
        log(f"codex exec timeout reply_chars={len(response)}")
        return (rc, raw_output, new_session, mode, response)

    if agent_messages:
        response = agent_messages[-1]
    else:
        response = extract_codex_response(raw_output)

    elapsed = time.time() - progress.start_time
    minutes = int(elapsed // 60)
    seconds = int(elapsed % 60)
    final_parts = [
        f"✅ 작업 완료 ({minutes}분 {seconds}초)"
    ]
    if progress.todos:
        n = len(progress.todos)
        final_parts.append(f"진행: {n}/{n} 완료")
        for t in progress.todos:
            final_parts.append(f"✅ {t.text} (완료)")
    edit_or_send(config, progress.progress_msg_id, "\n".join(final_parts))

    if rc != 0:
        stderr_tail = redact_log_text(stderr_output[-2000:])
        stdout_tail = redact_log_text(raw_output[-500:])
        log(
            f"codex exec failed rc={rc} stderr_tail={stderr_tail!r} "
            f"stdout_tail={stdout_tail!r}"
        )
    log(
        f"codex exec done rc={rc} reply_chars={len(response)} "
        f"next_session={new_session[:8] if new_session else 'none'}"
    )
    return (rc, raw_output, new_session, mode, response)


def run_codex(text: str, config: Config, queue_depth: int = 0) -> str:
    rc, output, new_session, mode, response = _run_codex_once(
        text, allow_resume=True, config=config, queue_depth=queue_depth,
    )

    if _cancel_event.is_set():
        return response

    if read_session_id() and rc != 0 and "No session" in output:
        SESSION_FILE.unlink(missing_ok=True)
        log("resume failed; session cleared")
        return (
            "이전 Codex 세션을 찾지 못해 "
            "초기화했습니다. "
            "같은 메시지를 다시 보내주세요."
        )

    if _context_full(output):
        SESSION_FILE.unlink(missing_ok=True)
        log(f"context full on {mode}; session cleared, retrying as new")
        rc, output, new_session, mode, response = _run_codex_once(
            text, allow_resume=False, config=config, queue_depth=queue_depth,
        )
        if _context_full(output):
            SESSION_FILE.unlink(missing_ok=True)
            log("context full even on fresh session")
            return (
                "Codex 컨텍스트가 가득 찼습니다. "
                "세션을 초기화했지만 "
                "재시도도 실패했습니다. "
                "메시지를 짧게 나눠 다시 "
                "보내주세요."
            )

    if rc != 0 and not _context_full(output):
        if response in ("(empty response)", "") or not response:
            response = (
                f"Codex 실행 실패 (rc={rc}). "
                "세션이 손상됐거나 CLI 오류. "
                "`/new` 로 세션을 초기화한 뒤 "
                "다시 시도해 주세요.\n\n"
                "[표준출력\xb7표준오류 "
                "합본 마지막 조각]\n"
                + redact_log_text(output[-600:])
            )

    if (
        (response in ("(empty response)", "") or not response)
        and _context_full(output)
    ):
        SESSION_FILE.unlink(missing_ok=True)
        response = (
            "Codex 세션 컨텍스트가 가득 차 "
            "응답이 비었습니다. "
            "세션을 초기화했습니다. "
            "같은 메시지를 다시 보내주세요."
        )

    return response


# ---- Control commands ----

def handle_control(config: Config, text: str) -> bool:
    """Handle control commands WITHOUT holding _codex_lock."""
    cmd = text.strip()

    if cmd in ("/new", "/reset", "/clear", "새 세션"):
        SESSION_FILE.unlink(missing_ok=True)
        notify(
            config,
            "Codex 세션 초기화 완료. "
            "다음 메시지부터 새 "
            "대화로 시작합니다.",
        )
        return True

    if cmd in ("/session", "/status"):
        sid = read_session_id() or "(없음)"
        with _current_process_lock:
            busy = _current_process is not None
        with _queue_lock:
            qlen = len(_message_queue)
        status = "작업 중" if busy else "대기 중"
        parts = [f"상태: {status}", f"세션: `{sid}`"]
        if qlen > 0:
            parts.append(f"대기열: {qlen}건")
        parts.append(
            f"타임아웃: {EXEC_TIMEOUT // 60}분"
        )
        notify(config, "\n".join(parts))
        return True

    if cmd == "/cancel":
        with _current_process_lock:
            proc = _current_process
        if proc is None:
            notify(
                config,
                "현재 실행 중인 "
                "작업이 없습니다.",
            )
        else:
            _cancel_event.set()
            notify(
                config,
                "취소 요청을 보냈습니다. "
                "잠시 후 부분 "
                "결과를 전달합니다.",
            )
        return True

    return False


# ---- Message handling ----

def handle_message(config: Config, text: str) -> None:
    if handle_control(config, text):
        return

    acquired = _codex_lock.acquire(blocking=False)
    if not acquired:
        with _queue_lock:
            _message_queue.append(text)
            pos = len(_message_queue)
        notify(
            config,
            f"작업 중입니다. "
            f"대기열 {pos}번째로 "
            "등록되었습니다.",
        )
        return

    try:
        _cancel_event.clear()
        with _queue_lock:
            qdepth = len(_message_queue)
        reply = run_codex(text, config, queue_depth=qdepth)
        send_chunked(config, reply)

        while True:
            with _queue_lock:
                if not _message_queue:
                    break
                queued_text = _message_queue.pop(0)
                qdepth = len(_message_queue)
            _cancel_event.clear()
            reply = run_codex(queued_text, config, queue_depth=qdepth)
            send_chunked(config, reply)
    finally:
        _codex_lock.release()


def route_update(config: Config, update: dict[str, object]) -> None:
    message = update.get("message") or update.get("edited_message")
    if not isinstance(message, dict):
        return
    chat = message.get("chat")
    if not isinstance(chat, dict):
        return
    if str(chat.get("id", "")) != config.chat_id:
        return
    text = message.get("text")
    if not isinstance(text, str):
        return
    log(f"route chars={len(text)}")
    threading.Thread(
        target=handle_message, args=(config, text), daemon=True,
    ).start()


# ---- Singleton lock ----

def acquire_singleton_lock() -> None:
    """Ensure only one getUpdates poller runs for this bot."""
    global _pid_lock_handle
    VAR_DIR.mkdir(parents=True, exist_ok=True)
    handle = POLL_LOCK_FILE.open("a+", encoding="utf-8")
    try:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        handle.seek(0)
        other = handle.read().strip() or "?"
        handle.close()
        raise RuntimeError(
            f"another codex-telegram-bot instance holds {POLL_LOCK_FILE} "
            f"(pid={other}). Stop the duplicate before starting."
        ) from None
    handle.seek(0)
    handle.truncate()
    handle.write(str(os.getpid()))
    handle.flush()
    write_text(PID_FILE, str(os.getpid()))
    _pid_lock_handle = handle

    def _release() -> None:
        global _pid_lock_handle
        if _pid_lock_handle is None:
            return
        try:
            fcntl.flock(_pid_lock_handle.fileno(), fcntl.LOCK_UN)
            _pid_lock_handle.close()
        except OSError:
            pass
        _pid_lock_handle = None

    atexit.register(_release)


# ---- Main ----

def main() -> int:
    config = load_config()
    if not pathlib.Path(CODEX_BIN).exists():
        raise RuntimeError(f"codex binary missing: {CODEX_BIN}")
    acquire_singleton_lock()
    write_heartbeat()
    check_inflight_on_boot(config)
    offset = read_int(OFFSET_FILE)
    log(
        f"standalone router started cwd={WORK_DIR} pid={os.getpid()} "
        f"timeout={EXEC_TIMEOUT}s"
    )
    while True:
        try:
            params: dict[str, int | str] = {"timeout": 55, "limit": 20}
            if offset is not None:
                params["offset"] = offset
            response = api(config, "getUpdates", params)
            match response.get("ok"):
                case True:
                    pass
                case False | None:
                    log(f"telegram not ok: {response!r}")
                    time.sleep(5)
                    continue
                case unreachable:
                    assert_never(unreachable)
            for update in response.get("result", []):
                if not isinstance(update, dict):
                    continue
                update_id = update.get("update_id")
                if isinstance(update_id, int):
                    offset = update_id + 1
                    write_text(OFFSET_FILE, str(offset))
                route_update(config, update)
        except KeyboardInterrupt:
            log("router stopped")
            return 0
        except urllib.error.HTTPError as error:
            if error.code == 409:
                log(
                    "error: HTTPError: HTTP Error 409: Conflict "
                    "(duplicate getUpdates)"
                )
                time.sleep(15)
            else:
                log(
                    f"error: HTTPError: HTTP Error {error.code}: "
                    f"{error.reason}"
                )
                time.sleep(5)
        except (
            OSError, RuntimeError, json.JSONDecodeError, TimeoutError,
        ) as error:
            log(f"error: {type(error).__name__}: {error}")
            time.sleep(5)
        finally:
            write_heartbeat()


if __name__ == "__main__":
    raise SystemExit(main())
