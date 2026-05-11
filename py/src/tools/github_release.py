import fnmatch
import json
from typing import Any

from .common import die, get_json


def parse_tag(tag: str) -> tuple[int, int]:
    tag = tag.strip()
    if tag[:1] in ("v", "V"):
        tag = tag[1:]
    major, minor = tag.split(".")
    return int(major), int(minor)


def asset_url(data: dict[str, Any], pattern: str) -> str:
    assets = data.get("assets")
    if not isinstance(assets, list):
        die("GitHub release JSON does not contain an assets list")

    matches: list[tuple[str, str]] = []
    for asset in assets:
        if not isinstance(asset, dict):
            continue
        name = asset.get("name")
        url = asset.get("browser_download_url")
        if not isinstance(name, str) or not isinstance(url, str):
            continue
        if fnmatch.fnmatch(name, pattern):
            matches.append((name, url))

    if not matches:
        die(f"No release asset found matching pattern: {pattern}")

    if len(matches) > 1:
        names = ", ".join(name for name, _ in matches)
        die(f"Multiple release assets matched pattern {pattern}: {names}")

    return matches[0][1]


def asset_url_json(stdin_text: str, pattern: str) -> str:
    try:
        data: dict[str, Any] = json.loads(stdin_text)
    except json.JSONDecodeError as e:
        die(f"Invalid GitHub release JSON: {e}")

    return asset_url(data, pattern)


def asset_url_api(api_url: str, pattern: str) -> str:
    data = get_json(api_url)
    if not isinstance(data, dict):
        die("GitHub release API did not return a release object")
    return asset_url(data, pattern)


def next_tag(repo: str) -> str:
    data = get_json(f"https://api.github.com/repos/{repo}/releases?per_page=100")
    if not isinstance(data, list):
        die("GitHub releases API did not return a release list")

    tags = [item["tag_name"] for item in data if isinstance(item, dict) and item.get("tag_name")]

    if not tags:
        return "v1.0"

    latest = max(tags, key=parse_tag)
    major, minor = parse_tag(latest)

    if minor >= 9:
        major += 1
        minor = 0
    else:
        minor += 1

    return f"v{major}.{minor}"
