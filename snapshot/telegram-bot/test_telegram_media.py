from __future__ import annotations

from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading

import telegram_codex_bot as bot


class TelegramHandler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:
        body = b'{"ok":true,"result":{"file_path":"photos/screenshot.png"}}'
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        body = b"png-bytes"
        self.send_response(200)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        return


@dataclass(frozen=True, slots=True)
class FakeMediaClient:
    expected_file_id: str
    payload: bytes

    def download(self, file_id: str, max_bytes: int) -> bytes:
        assert file_id == self.expected_file_id
        assert max_bytes == 1024
        return self.payload


def test_photo_is_saved_when_telegram_update_contains_sizes(tmp_path: Path) -> None:
    # Given
    update = {
        "update_id": 42,
        "message": {
            "chat": {"id": 7},
            "caption": "화면 확인해줘",
            "photo": [
                {"file_id": "small-photo", "file_size": 10},
                {"file_id": "large-photo", "file_size": 20},
            ],
        },
    }
    settings = bot.MediaSettings(inbound_dir=tmp_path, max_file_bytes=1024)

    # When
    result = bot.prepare_telegram_update(
        update,
        settings,
        FakeMediaClient(expected_file_id="large-photo", payload=b"image"),
    )

    # Then
    assert result is not None
    assert result.attachments == (tmp_path / "42_photo.jpg",)
    assert result.attachments[0].read_bytes() == b"image"


def test_document_is_safely_named_when_filename_contains_parent_path(tmp_path: Path) -> None:
    # Given
    update = {
        "update_id": 43,
        "message": {
            "chat": {"id": 7},
            "document": {
                "file_id": "document-id",
                "file_name": "../../진료 기록.pdf",
                "file_size": 30,
            },
        },
    }
    settings = bot.MediaSettings(inbound_dir=tmp_path, max_file_bytes=1024)

    # When
    result = bot.prepare_telegram_update(
        update,
        settings,
        FakeMediaClient(expected_file_id="document-id", payload=b"pdf"),
    )

    # Then
    assert result is not None
    assert result.attachments == (tmp_path / "43_진료_기록.pdf",)
    assert result.attachments[0].read_bytes() == b"pdf"


def test_media_client_downloads_file_when_get_file_returns_path() -> None:
    # Given
    server = ThreadingHTTPServer(("127.0.0.1", 0), TelegramHandler)
    thread = threading.Thread(target=server.serve_forever)
    thread.start()
    root = f"http://127.0.0.1:{server.server_port}"

    try:
        client = bot.TelegramMediaClient(bot_token="token", api_root=root)

        # When
        result = client.download("file-id", max_bytes=1024)

        # Then
        assert result == b"png-bytes"
    finally:
        server.shutdown()
        thread.join()
        server.server_close()
