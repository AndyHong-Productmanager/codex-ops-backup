#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# ///
# ─── How to run ───
# cd /home/ubuntuhong/dev/codex-telegram-bot
# nohup python3 telegram_codex_bot.py > logs/router.stdout.log 2>&1 &
from __future__ import annotations

import atexit
import fcntl
import glob
import json
import os
import pathlib
import re
import signal
import subprocess
import sys
import threading
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass
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
EXEC_TIMEOUT: Final = int(os.environ.get("CODEX_EXEC_TIMEOUT", "1800"))
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
# codex exec가 응답 섹션 없이 죽었을 때 stdout 청소용
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

_codex_lock = threading.Lock()
_pid_lock_handle: TextIO | None = None

# 실제 codex 컨텍스트 초과 에러 문구만 넣는다.
# "context window" 같은 일반 문구는 금지 — 스킬 지침/문서 인용에 그 단어가
# 등장하기만 하면 오탐으로 세션을 날린다. (2026-08-07, 2026-08-13 실발생)
CONTEXT_FULL_MARKERS: Final = (
    "ran out of room in the model's context window",
    "context length exceeded",
    "maximum context length",
)

OPERATING_RULES: Final = """\
[운영 규칙 — 매 턴 반드시 준수, 답에는 포함하지 말 것]
- 너의 최종 답변은 stdout으로 나가 자동으로 Andy의 Telegram(@Lazycodex_bot)에 전달된다.
- 작업이 30초 이상 걸리거나 Andy가 "N분마다 보고" 같은 주기 보고를 요청하면,
  중간 진행 상황을 다음 bash 명령으로 직접 보내라:
    bash /home/ubuntuhong/dev/codex-telegram-bot/notify-codex.sh "현황: <짧은 한 줄 보고>"
- 최종 답은 한국어, 핵심만. 코드/파일 경로는 `backtick`으로 감싸라.
- `orchestra/`, `docs/rag/`, `docs/obsidian/` 파일을 만들거나 수정하지 말 것.
- 절대 placeholder 텍스트를 그대로 출력하지 말 것.

[컨텍스트 절약 — 한 턴에 세션이 가득 차는 사고 방지]
- 스크린샷·이미지를 대화에 직접 넣지 말 것. 이미지 1장이 컨텍스트를 통째로 삼켜 세션이 한 턴 만에 터진다.
- 이미지가 필요하면 `/tmp` 또는 작업 디렉터리에 파일로 저장하고, 답에는 `저장 위치: <경로>`만 적어라.
- base64로 이미지를 출력하는 스크립트를 만들지 말 것.
- 명령 출력이 길어질 것 같으면 파일로 리다이렉트한 뒤 `head`/`tail`/`grep`으로 필요한 부분만 봐라. 긴 로그를 통째로 출력하지 말 것.
- 한 조사에서 도구를 여러 번 쓰게 되면 중간에 알아낸 것을 짧게 정리하고, 이미 확인한 내용을 다시 확인하지 말 것.

[Andy 메시지]
"""


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
    # `codex\n<body>` 섹션이 없으면 codex CLI가 응답 전에 죽었을 확률이 큼.
    # 배너/유저 프롬프트 에코/warning을 모두 걷어내고 남은 것만 반환.
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


def notify(config: Config, text: str) -> None:
    api(config, "sendMessage", {"chat_id": config.chat_id, "text": text[:3900]})


def _terminate_process_group(process: subprocess.Popen[str]) -> None:
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    try:
        process.communicate(timeout=5)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        process.communicate()


def run_command(
    command: list[str], *, timeout: int | float, cwd: str
) -> CommandResult | None:
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=cwd,
        start_new_session=True,
    )
    try:
        stdout, stderr = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        _terminate_process_group(process)
        return None
    return CommandResult(
        returncode=process.returncode,
        stdout=stdout,
        stderr=stderr,
    )


def _context_full(output: str) -> bool:
    lowered = output.lower()
    return any(marker.lower() in lowered for marker in CONTEXT_FULL_MARKERS)


def _run_codex_once(text: str, *, allow_resume: bool) -> tuple[int, str, str | None, str]:
    """Run one codex exec. Returns (rc, combined_output, new_session_id, mode)."""
    session_id = read_session_id() if allow_resume else None
    wrapped = OPERATING_RULES + text
    base = [
        CODEX_BIN,
        "exec",
        "--skip-git-repo-check",
        "--cd",
        WORK_DIR,
        "--model",
        CODEX_MODEL,
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
    try:
        result = run_command(cmd, timeout=EXEC_TIMEOUT, cwd=WORK_DIR)
    except FileNotFoundError:
        log(f"codex binary missing: {CODEX_BIN}")
        return (127, "codex binary missing", None, mode)
    if result is None:
        log("codex exec timeout")
        return (124, "timeout", None, mode)

    output = result.stdout + ("\n" + result.stderr if result.stderr else "")
    new_session = returned_session_id(result.stdout)
    candidate_count = 0
    if new_session is None:
        new_session, candidate_count = select_new_session(before)
        if candidate_count > 1:
            log(f"codex session candidates count={candidate_count}; selecting newest")
    if new_session:
        write_text(SESSION_FILE, new_session)
    if result.returncode != 0:
        stderr_tail = redact_log_text(result.stderr[-2000:])
        stdout_tail = redact_log_text(result.stdout[-500:])
        log(
            f"codex exec failed rc={result.returncode} stderr_tail={stderr_tail!r} "
            f"stdout_tail={stdout_tail!r}"
        )
    return (result.returncode, output, new_session, mode)


def run_codex(text: str) -> str:
    rc, output, new_session, mode = _run_codex_once(text, allow_resume=True)
    if rc == 124:
        return "Codex 응답이 제한 시간을 넘겼습니다. 다시 시도해 주세요."

    if read_session_id() and rc != 0 and "No session" in output:
        SESSION_FILE.unlink(missing_ok=True)
        log("resume failed; session cleared")
        return "이전 Codex 세션을 찾지 못해 초기화했습니다. 같은 메시지를 다시 보내주세요."

    # Context window exhausted on resume → wipe session and retry once as new.
    if _context_full(output):
        SESSION_FILE.unlink(missing_ok=True)
        log(f"context full on {mode}; session cleared, retrying as new")
        rc, output, new_session, mode = _run_codex_once(text, allow_resume=False)
        if rc == 124:
            return "Codex 응답이 제한 시간을 넘겼습니다. 다시 시도해 주세요."
        if _context_full(output):
            SESSION_FILE.unlink(missing_ok=True)
            log("context full even on fresh session")
            return (
                "Codex 컨텍스트가 가득 찼습니다. 세션을 초기화했지만 재시도도 실패했습니다. "
                "메시지를 짧게 나눠 다시 보내주세요."
            )

    response = extract_codex_response(output)
    # rc != 0 이고 `codex\n<body>` 섹션이 없으면 CLI 자체가 죽은 것 — 명확한 에러로 감쌈
    if rc != 0 and not SECTION_RE.search(output) and not _context_full(output):
        response = (
            f"Codex 실행 실패 (rc={rc}). 세션이 손상됐거나 CLI 오류. "
            f"`/new` 로 세션을 초기화한 뒤 다시 시도해 주세요.\n\n"
            f"[표준출력·표준오류 합본 마지막 조각]\n{response[-600:]}"
        )
    # Context-full messages sometimes exit 0 with empty codex body — still surface cleanly.
    if (response == "(empty response)" or not response) and _context_full(output):
        SESSION_FILE.unlink(missing_ok=True)
        response = (
            "Codex 세션 컨텍스트가 가득 차 응답이 비었습니다. 세션을 초기화했습니다. "
            "같은 메시지를 다시 보내주세요."
        )
    log(
        f"codex exec done rc={rc} reply_chars={len(response)} "
        f"next_session={new_session[:8] if new_session else 'none'}"
    )
    return response


def handle_control(config: Config, text: str) -> bool:
    match text.strip():
        case "/new" | "/reset" | "/clear" | "새 세션":
            SESSION_FILE.unlink(missing_ok=True)
            notify(config, "Codex 세션 초기화 완료. 다음 메시지부터 새 대화로 시작합니다.")
            return True
        case "/session" | "/status":
            notify(config, f"현재 Codex 세션: `{read_session_id() or '(없음)'}`")
            return True
        case _:
            return False


def handle_message(config: Config, text: str) -> None:
    with _codex_lock:
        if handle_control(config, text):
            return
        reply = run_codex(text)
        notify(config, reply)


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
    threading.Thread(target=handle_message, args=(config, text), daemon=True).start()


def acquire_singleton_lock() -> None:
    """Ensure only one getUpdates poller runs for this bot (prevents HTTP 409)."""
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
            f"another codex-telegram-bot instance holds {POLL_LOCK_FILE} (pid={other}). "
            "Stop the duplicate before starting."
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


def main() -> int:
    config = load_config()
    if not pathlib.Path(CODEX_BIN).exists():
        raise RuntimeError(f"codex binary missing: {CODEX_BIN}")
    acquire_singleton_lock()
    write_heartbeat()
    offset = read_int(OFFSET_FILE)
    log(f"standalone router started cwd={WORK_DIR} pid={os.getpid()}")
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
            # 409 = another getUpdates client; back off harder so the winner can settle.
            if error.code == 409:
                log("error: HTTPError: HTTP Error 409: Conflict (duplicate getUpdates)")
                time.sleep(15)
            else:
                log(f"error: HTTPError: HTTP Error {error.code}: {error.reason}")
                time.sleep(5)
        except (OSError, RuntimeError, json.JSONDecodeError, TimeoutError) as error:
            log(f"error: {type(error).__name__}: {error}")
            time.sleep(5)
        finally:
            write_heartbeat()


if __name__ == "__main__":
    raise SystemExit(main())
