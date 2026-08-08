from __future__ import annotations

import os
from pathlib import Path
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

import telegram_codex_bot as bot


class CodexTelegramReliabilityTests(unittest.TestCase):
    def test_router_heartbeat_is_written_for_healthcheck(self) -> None:
        # Given
        with tempfile.TemporaryDirectory() as directory:
            heartbeat_file = Path(directory) / "router.heartbeat"

            with patch.object(bot, "HEARTBEAT_FILE", heartbeat_file):
                # When
                bot.write_heartbeat()

            # Then
            self.assertGreater(int(heartbeat_file.read_text(encoding="utf-8")), 0)

    def test_returned_session_id_is_preferred(self) -> None:
        # Given
        session_id = "33333333-3333-3333-3333-333333333333"

        # When
        result = bot.returned_session_id(f"session id: {session_id}\ncodex\nok")

        # Then
        self.assertEqual(result, session_id)

    def test_new_session_selection_rejects_other_cwd(self) -> None:
        # Given
        with tempfile.TemporaryDirectory() as directory:
            sessions_dir = Path(directory) / "sessions"
            sessions_dir.mkdir()
            bot_work_dir = Path(directory) / "bot"
            other_work_dir = Path(directory) / "other"
            before: set[Path] = set()
            own_id = "11111111-1111-1111-1111-111111111111"
            other_id = "22222222-2222-2222-2222-222222222222"
            (sessions_dir / f"rollout-2026-08-03T09-00-00-{own_id}.jsonl").write_text(
                '{"type":"session_meta","payload":{"session_id":"'
                + own_id
                + '","cwd":"'
                + str(bot_work_dir)
                + '"}}\n',
                encoding="utf-8",
            )
            (sessions_dir / f"rollout-2026-08-03T09-00-01-{other_id}.jsonl").write_text(
                '{"type":"session_meta","payload":{"session_id":"'
                + other_id
                + '","cwd":"'
                + str(other_work_dir)
                + '"}}\n',
                encoding="utf-8",
            )

            with (
                patch.object(bot, "CODEX_SESSIONS_DIR", sessions_dir),
                patch.object(bot, "WORK_DIR", str(bot_work_dir)),
            ):
                # When
                session_id, candidates = bot.select_new_session(before)

            # Then
            self.assertEqual(session_id, own_id)
            self.assertEqual(candidates, 1)

    def test_no_new_session_keeps_existing_session_file(self) -> None:
        # Given
        with tempfile.TemporaryDirectory() as directory:
            session_file = Path(directory) / "codex.session"
            session_file.write_text("existing-session", encoding="utf-8")
            sessions_dir = Path(directory) / "sessions"
            sessions_dir.mkdir()

            with (
                patch.object(bot, "SESSION_FILE", session_file),
                patch.object(bot, "CODEX_SESSIONS_DIR", sessions_dir),
                patch.object(
                    bot,
                    "run_command",
                    return_value=bot.CommandResult(0, "codex\nok", ""),
                ),
                patch.object(bot, "log"),
            ):
                # When
                _, _, new_session, _ = bot._run_codex_once("test", allow_resume=False)

            # Then
            self.assertIsNone(new_session)
            self.assertEqual(session_file.read_text(encoding="utf-8"), "existing-session")

    def test_failed_command_logs_masked_stderr_tail(self) -> None:
        # Given
        with tempfile.TemporaryDirectory() as directory:
            sessions_dir = Path(directory) / "sessions"
            sessions_dir.mkdir()
            log_messages: list[str] = []

            with (
                patch.object(bot, "CODEX_SESSIONS_DIR", sessions_dir),
                patch.object(
                    bot,
                    "run_command",
                    return_value=bot.CommandResult(
                        1,
                        "stdout-tail",
                        "stderr-tail Authorization: Bearer sk-secret-token",
                    ),
                ),
                patch.object(bot, "log", side_effect=log_messages.append),
            ):
                # When
                bot._run_codex_once("test", allow_resume=False)

            # Then
            failure_log = next(message for message in log_messages if "failed rc=1" in message)
            self.assertIn("stderr-tail", failure_log)
            self.assertIn("stdout-tail", failure_log)
            self.assertNotIn("sk-secret-token", failure_log)

    def test_context_full_new_session_is_discarded_after_retry_fails(self) -> None:
        # Given
        with tempfile.TemporaryDirectory() as directory:
            session_file = Path(directory) / "codex.session"
            session_file.write_text("previous-session", encoding="utf-8")

            def context_full_run(_: str, *, allow_resume: bool) -> tuple[int, str, str | None, str]:
                if allow_resume:
                    return (1, "context window", None, "resume(previous...)")
                session_file.write_text("failed-new-session", encoding="utf-8")
                return (1, "context window", "failed-new-session", "new")

            with (
                patch.object(bot, "SESSION_FILE", session_file),
                patch.object(bot, "_run_codex_once", side_effect=context_full_run),
            ):
                # When
                bot.run_codex("test")

                # Then
                self.assertFalse(session_file.exists())

    def test_timed_out_command_terminates_its_process_group(self) -> None:
        # Given
        with tempfile.TemporaryDirectory() as directory:
            child_pid_path = Path(directory) / "child.pid"
            child_code = (
                "from pathlib import Path; import os, sys, time; "
                "Path(sys.argv[1]).write_text(str(os.getpid())); time.sleep(30)"
            )
            parent_code = (
                "import subprocess, sys, time; "
                "subprocess.Popen([sys.executable, '-c', sys.argv[2], sys.argv[1]]); "
                "time.sleep(30)"
            )

            # When
            result = bot.run_command(
                [sys.executable, "-c", parent_code, str(child_pid_path), child_code],
                timeout=0.2,
                cwd=directory,
            )

            # Then
            self.assertIsNone(result)
            child_pid = int(child_pid_path.read_text(encoding="utf-8"))
            for _ in range(20):
                try:
                    os.kill(child_pid, 0)
                except ProcessLookupError:
                    break
                time.sleep(0.01)
            else:
                self.fail("timed-out child process is still alive")


if __name__ == "__main__":
    unittest.main()
