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
