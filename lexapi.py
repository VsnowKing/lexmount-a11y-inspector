#!/usr/bin/env python3
"""Shared helpers for small Lexmount Web Fetch projects."""

from __future__ import annotations

import hashlib
import json
import os
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def run_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def compact(value: Any, limit: int = 800) -> str:
    if value is None:
        return ""
    text = str(value).replace("\r", " ").replace("\n", " ")
    while "  " in text:
        text = text.replace("  ", " ")
    text = text.strip()
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def load_env(path: Path) -> None:
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key, value = key.strip(), value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def credentials(env_file: Path) -> tuple[str, str, str]:
    load_env(env_file)
    return (
        os.environ.get("LEXMOUNT_API_KEY", "").strip(),
        os.environ.get("LEXMOUNT_PROJECT_ID", "").strip(),
        os.environ.get("LEXMOUNT_BASE_URL", "https://api.lexmount.cn").strip().rstrip("/"),
    )


def post_json(url: str, payload: dict[str, Any], api_key: str, project_id: str, timeout: int = 60) -> tuple[int, dict[str, Any] | bytes, dict[str, str]]:
    data = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "lexmount-project/1.0",
        "X-API-Key": api_key,
        "X-Project-Id": project_id,
    }
    request = urllib.request.Request(url=url, data=data, method="POST", headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read()
            try:
                parsed: dict[str, Any] | bytes = json.loads(body.decode("utf-8"))
            except Exception:
                parsed = body
            return response.status, parsed, dict(response.headers.items())
    except urllib.error.HTTPError as exc:
        body = exc.read()
        try:
            parsed = json.loads(body.decode("utf-8"))
        except Exception:
            parsed = body
        return exc.code, parsed, dict(exc.headers.items())
    except Exception as exc:
        return 0, {"error": {"code": "client_request_failed", "message": str(exc)}}, {}


def retry_call(url: str, payload: dict[str, Any], api_key: str, project_id: str, attempts: int = 3, timeout: int = 60) -> tuple[dict[str, Any], int, list[dict[str, Any]]]:
    attempts_log: list[dict[str, Any]] = []
    for attempt in range(1, attempts + 1):
        started = utc_now()
        status, response, headers = post_json(url, payload, api_key, project_id, timeout)
        finished = utc_now()
        if isinstance(response, bytes):
            response = {"raw_response": response.decode("utf-8", errors="replace")}
        request_id = ""
        if isinstance(response, dict):
            request_id = compact(response.get("request_id"), 100)
        request_id = request_id or compact(headers.get("X-Request-ID"), 100)
        attempts_log.append({"attempt": attempt, "started_at": started, "finished_at": finished, "http_status": status, "request_id": request_id})
        if status == 200:
            return response, status, attempts_log
        if status not in {408, 425, 429, 500, 502, 503, 504} or attempt == attempts:
            return response, status, attempts_log
        time.sleep(min(8, 0.75 * (2 ** (attempt - 1))))
    raise AssertionError("unreachable")


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def checksum_dir(base: Path, files: list[Path]) -> Path:
    sums = base / "SHA256SUMS.txt"
    with sums.open("w", encoding="utf-8", newline="\n") as handle:
        for path in sorted(set(files)):
            if path.is_file() and base in path.parents:
                handle.write(f"{sha256_file(path)}  {path.relative_to(base).as_posix()}\n")
    return sums
