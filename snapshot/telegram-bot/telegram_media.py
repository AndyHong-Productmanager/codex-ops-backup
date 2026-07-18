from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re
from typing import Protocol
import urllib.parse
import urllib.request

from pydantic import BaseModel, ConfigDict


type JsonValue = None | bool | int | float | str | list[JsonValue] | dict[str, JsonValue]
type JsonObject = dict[str, JsonValue]


class MediaClient(Protocol):
    def download(self, file_id: str, max_bytes: int) -> bytes: ...


class PhotoSize(BaseModel):
    model_config = ConfigDict(frozen=True, extra="ignore")

    file_id: str
    file_size: int = 0


class Document(BaseModel):
    model_config = ConfigDict(frozen=True, extra="ignore")

    file_id: str
    file_name: str = "document"
    file_size: int = 0


class TelegramMessage(BaseModel):
    model_config = ConfigDict(frozen=True, extra="ignore")

    text: str = ""
    caption: str = ""
    photo: tuple[PhotoSize, ...] = ()
    document: Document | None = None


class TelegramUpdate(BaseModel):
    model_config = ConfigDict(frozen=True, extra="ignore")

    update_id: int
    message: TelegramMessage | None = None
    edited_message: TelegramMessage | None = None


class TelegramFileInfo(BaseModel):
    model_config = ConfigDict(frozen=True, extra="ignore")

    file_path: str


class TelegramFileResponse(BaseModel):
    model_config = ConfigDict(frozen=True, extra="ignore")

    ok: bool
    result: TelegramFileInfo | None = None


@dataclass(frozen=True, slots=True)
class MediaSettings:
    inbound_dir: Path
    max_file_bytes: int


@dataclass(frozen=True, slots=True)
class PreparedUpdate:
    body: str
    attachments: tuple[Path, ...]


@dataclass(frozen=True, slots=True)
class TelegramFileUnavailableError(Exception):
    file_id: str

    def __str__(self) -> str:
        return f"Telegram file unavailable: {self.file_id}"


@dataclass(frozen=True, slots=True)
class TelegramFileTooLargeError(Exception):
    max_bytes: int

    def __str__(self) -> str:
        return f"Telegram file exceeds {self.max_bytes} bytes"


@dataclass(frozen=True, slots=True)
class TelegramMediaClient:
    bot_token: str
    api_root: str = "https://api.telegram.org"

    def download(self, file_id: str, max_bytes: int) -> bytes:
        query = urllib.parse.urlencode({"file_id": file_id}).encode()
        request = urllib.request.Request(
            f"{self.api_root}/bot{self.bot_token}/getFile",
            data=query,
        )
        with urllib.request.urlopen(request, timeout=70) as response:
            file_response = TelegramFileResponse.model_validate(json.load(response))

        match (file_response.ok, file_response.result):
            case (True, TelegramFileInfo(file_path=file_path)):
                encoded_path = urllib.parse.quote(file_path, safe="/")
            case _:
                raise TelegramFileUnavailableError(file_id=file_id)

        file_url = f"{self.api_root}/file/bot{self.bot_token}/{encoded_path}"
        with urllib.request.urlopen(file_url, timeout=70) as response:
            data = response.read(max_bytes + 1)
        if len(data) > max_bytes:
            raise TelegramFileTooLargeError(max_bytes=max_bytes)
        return data


def safe_filename(raw_name: str) -> str:
    basename = Path(raw_name.replace("\\", "/")).name
    sanitized = re.sub(r"[^\w.-]+", "_", basename, flags=re.UNICODE).strip("._")
    return sanitized or "document"


def prepare_telegram_update(
    payload: JsonObject,
    settings: MediaSettings,
    client: MediaClient,
) -> PreparedUpdate | None:
    update = TelegramUpdate.model_validate(payload)
    message = update.message or update.edited_message
    if message is None:
        return None

    body = message.text or message.caption
    match (message.photo, message.document):
        case (photos, _) if photos:
            selected = max(photos, key=lambda item: item.file_size)
            filename = "photo.jpg"
        case ((), Document() as document):
            selected = document
            filename = safe_filename(document.file_name)
        case ((), None):
            return PreparedUpdate(body=body, attachments=()) if body else None

    if selected.file_size > settings.max_file_bytes:
        return PreparedUpdate(body="첨부 이미지가 허용 용량을 초과했습니다.", attachments=())

    data = client.download(selected.file_id, settings.max_file_bytes)
    if len(data) > settings.max_file_bytes:
        return PreparedUpdate(body="첨부 이미지가 허용 용량을 초과했습니다.", attachments=())

    destination = settings.inbound_dir / f"{update.update_id}_{filename}"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(data)
    return PreparedUpdate(body=body, attachments=(destination,))
