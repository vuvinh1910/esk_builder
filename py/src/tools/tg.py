from pathlib import Path
from typing import Any

import requests

from .common import die, env


def tg_api_url(method: str) -> str:
    return f"https://api.telegram.org/bot{env('TG_BOT_TOKEN')}/{method}"


def send_message(text: str) -> None:
    payload = {
        "chat_id": env("TG_CHAT_ID"),
        "parse_mode": "MarkdownV2",
        "disable_web_page_preview": "true",
        "text": text,
    }
    try:
        response = requests.post(tg_api_url("sendMessage"), json=payload, timeout=30)
        response.raise_for_status()
    except requests.RequestException as e:
        die(f"sendMessage request failed: {e}")

    data: dict[str, Any] = response.json()
    if not data.get("ok"):
        die(f"sendMessage failed: {data.get('description', 'Unknown error')}")


def send_document(file_path: Path, caption: str) -> None:
    if not file_path.exists():
        die(f"File not found: {file_path}")

    payload = {
        "chat_id": env("TG_CHAT_ID"),
        "parse_mode": "MarkdownV2",
        "caption": caption,
        "disable_web_page_preview": "true",
    }
    with file_path.open("rb") as handle:
        try:
            response = requests.post(
                tg_api_url("sendDocument"),
                data=payload,
                files={"document": (file_path.name, handle)},
                timeout=180,
            )
            response.raise_for_status()
        except requests.RequestException as e:
            die(f"sendDocument request failed: {e}")

    data: dict[str, Any] = response.json()
    if not data.get("ok"):
        die(f"sendDocument failed: {data.get('description', 'Unknown error')}")
