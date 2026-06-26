#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# ///
# ─── How to run ───
# cd /home/ubuntuhong/dev/codex-telegram-bot
# nohup python3 telegram_codex_bot.py > logs/router.stdout.log 2>&1 &
from __future__ import annotations

import glob
import json
import os
import pathlib
import re
import subprocess
import sys
import threading
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Final, TypedDict, assert_never


ROOT: Final = pathlib.Path(__file__).resolve().parent
ENV_FILE: Final = ROOT / ".env"
VAR_DIR: Final = ROOT / "var"
LOG_DIR: Final = ROOT / "logs"
OFFSET_FILE: Final = VAR_DIR / "telegram.offset"
SESSION_FILE: Final = VAR_DIR / "codex.session"
PID_FILE: Final = VAR_DIR / "router.pid"
LOG_FILE: Final = LOG_DIR / "router.log"

CODEX_BIN: Final = os.environ.get(
    "CODEX_BIN", "/home/ubuntuhong/.npm-global/bin/codex"
)
WORK_DIR: Final = os.environ.get("CODEX_WORK_DIR", "/home/ubuntuhong/dev")
EXEC_TIMEOUT: Final = int(os.environ.get("CODEX_EXEC_TIMEOUT", "600"))
CODEX_SESSIONS_DIR: Final = pathlib.Path(
    os.environ.get("CODEX_SESSIONS_DIR", "/home/ubuntuhong/.codex/sessions")
)

SECTION_RE: Final = re.compile(
    r"(?:^|\n)codex\n(?P<body>.*?)(?=\n(?:hook:|tokens used|user\n|codex\n|$))",
    re.DOTALL,
)
SESSION_RE: Final = re.compile(
    r"rollout-[0-9T\-]+-([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})\.jsonl$"
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

[Andy 메시지]
"""


class TelegramResult(TypedDict, total=False):
    ok: bool
    result: list[dict[str, object]]


@dataclass(frozen=True, slots=True)
class Config:
    bot_token: str
    chat_id: str


def log(message: str) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    line = time.strftime("[%Y-%m-%dT%H:%M:%S%z] ") + message
    with LOG_FILE.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")
    print(line, flush=True)


def load_env() -> None:
    if not ENV_FILE.exists():
        return
    for raw in ENV_FILE.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


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


def read_session_id() -> str | None:
    try:
        value = SESSION_FILE.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        return None
    return value or None


def latest_session_uuid(started_at: float) -> str | None:
    pattern = str(CODEX_SESSIONS_DIR / "**" / "rollout-*.jsonl")
    files = [pathlib.Path(path) for path in glob.glob(pattern, recursive=True)]
    recent = [path for path in files if path.stat().st_mtime >= started_at]
    recent.sort(key=lambda path: path.stat().st_mtime, reverse=True)
    for path in recent:
        match = SESSION_RE.search(str(path))
        if match:
            return match.group(1)
    return None


def extract_codex_response(stdout: str) -> str:
    matches = list(SECTION_RE.finditer(stdout))
    if matches:
        return matches[-1].group("body").strip()
    cleaned: list[str] = []
    for line in stdout.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith(("hook:", "tokens used", "model:", "directory:")):
            continue
        cleaned.append(line)
    return "\n".join(cleaned).strip() or "(empty response)"


def notify(config: Config, text: str) -> None:
    api(config, "sendMessage", {"chat_id": config.chat_id, "text": text[:3900]})


def run_codex(text: str) -> str:
    session_id = read_session_id()
    wrapped = OPERATING_RULES + text
    base = [CODEX_BIN, "exec", "--skip-git-repo-check", "--cd", WORK_DIR]
    if session_id:
        cmd = [*base, "resume", session_id, wrapped]
        mode = f"resume({session_id[:8]}...)"
    else:
        cmd = [*base, wrapped]
        mode = "new"

    started_at = time.time()
    log(f"codex exec start {mode} chars={len(text)}")
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=EXEC_TIMEOUT,
            cwd=WORK_DIR,
            check=False,
        )
    except subprocess.TimeoutExpired:
        log("codex exec timeout")
        return "Codex 응답이 제한 시간을 넘겼습니다. 다시 시도해 주세요."

    output = (proc.stdout or "") + ("\n" + proc.stderr if proc.stderr else "")
    if session_id and proc.returncode != 0 and "No session" in output:
        SESSION_FILE.unlink(missing_ok=True)
        log("resume failed; session cleared")
        return "이전 Codex 세션을 찾지 못해 초기화했습니다. 같은 메시지를 다시 보내주세요."

    new_session = latest_session_uuid(started_at)
    if new_session:
        write_text(SESSION_FILE, new_session)
    response = extract_codex_response(output)
    log(
        f"codex exec done rc={proc.returncode} reply_chars={len(response)} "
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


def main() -> int:
    config = load_config()
    if not pathlib.Path(CODEX_BIN).exists():
        raise RuntimeError(f"codex binary missing: {CODEX_BIN}")
    write_text(PID_FILE, str(os.getpid()))
    offset = read_int(OFFSET_FILE)
    log(f"standalone router started cwd={WORK_DIR}")
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
        except (OSError, RuntimeError, json.JSONDecodeError) as error:
            log(f"error: {type(error).__name__}: {error}")
            time.sleep(5)


if __name__ == "__main__":
    raise SystemExit(main())
