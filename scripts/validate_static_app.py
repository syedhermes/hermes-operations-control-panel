#!/usr/bin/env python3
"""Validate the Hermes Operations Control Panel static app.

Stdlib-only guardrail for public-safe GitHub Pages updates.
"""

from __future__ import annotations

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"

REQUIRED_FILES = [
    DOCS / "index.html",
    DOCS / "styles.css",
    DOCS / "app.js",
    DOCS / "status.json",
    DOCS / "README.md",
]
OPTIONAL_PUBLIC_DOCS = [
    DOCS / "CONTRIBUTING.md",
    DOCS / "STATUS_SCHEMA.md",
    DOCS / "SAFETY_CHECKLIST.md",
    ROOT / "README.md",
]

TOP_LEVEL_REQUIRED = {
    "schema_version": str,
    "title": str,
    "version_label": str,
    "updated": str,
    "deployment": dict,
    "public_safety": dict,
    "system_status": list,
    "cards": list,
    "blocked_items": list,
    "next_actions": list,
    "safety_boundary": list,
    "rollback_notes": list,
    "acceptance_criteria": list,
}
TOP_LEVEL_ALLOWED = set(TOP_LEVEL_REQUIRED)

DEPLOYMENT_REQUIRED = {
    "state": str,
    "surface": str,
    "url": str,
    "mode": str,
    "runtime_dependencies": str,
}
PUBLIC_SAFETY_REQUIRED = {
    "classification": str,
    "source": str,
    "live_runtime_reads": bool,
    "private_data": bool,
    "chat_ingestion": bool,
    "credentials": bool,
    "memory_queries": bool,
    "external_api_calls": bool,
    "backend_server": bool,
    "analytics": bool,
}
SYSTEM_STATUS_REQUIRED = {"id": str, "label": str, "state": str, "summary": str}
CARD_REQUIRED = {"id": str, "title": str, "state": str, "summary": str, "evidence": list, "actions": list}
BLOCKED_REQUIRED = {"action": str, "reason": str, "approval_required": str}

FALSE_PUBLIC_SAFETY_FLAGS = [
    "live_runtime_reads",
    "private_data",
    "chat_ingestion",
    "credentials",
    "memory_queries",
    "external_api_calls",
    "backend_server",
    "analytics",
]

SECRET_PATTERNS = {
    "private_key_block": re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----"),
    "github_token": re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9_]{20,}\b"),
    "openai_like_key": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    "aws_access_key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "jwt": re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b"),
    "secret_assignment": re.compile(
        r"(?i)\b(?:api[_-]?key|secret|token|password|passwd|authorization|bearer)\b\s*[:=]\s*['\"]?[A-Za-z0-9_./+=:-]{16,}"
    ),
    "local_secret_path": re.compile(r"(?i)(?:/\.ssh/|/secrets?/|/\.aws/|/\.config/(?:gh|gcloud|az)|id_rsa|id_ed25519)"),
}

EXTERNAL_URL = re.compile(r"^(?:https?:)?//", re.I)
HTTP_URL = re.compile(r"https?://", re.I)


class ResourceParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.external_resources: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = dict(attrs)
        if tag == "script" and data.get("src") and EXTERNAL_URL.search(data["src"] or ""):
            self.external_resources.append(f"external script src={data['src']}")
        if tag == "link" and (data.get("rel") or "").lower() == "stylesheet":
            href = data.get("href") or ""
            if EXTERNAL_URL.search(href):
                self.external_resources.append(f"external stylesheet href={href}")


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def check_required_files(errors: list[str]) -> None:
    for path in REQUIRED_FILES:
        if not path.exists():
            fail(errors, f"missing required file: {path.relative_to(ROOT)}")


def load_status(errors: list[str]) -> dict[str, Any] | None:
    path = DOCS / "status.json"
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001 - validator should report any parse failure plainly.
        fail(errors, f"status.json parse failed: {exc}")
        return None


def check_object(name: str, obj: Any, required: dict[str, type], errors: list[str], *, exact: bool = True) -> None:
    if not isinstance(obj, dict):
        fail(errors, f"{name} must be an object")
        return
    for key, typ in required.items():
        if key not in obj:
            fail(errors, f"{name}.{key} is required")
        elif not isinstance(obj[key], typ):
            fail(errors, f"{name}.{key} must be {typ.__name__}")
    if exact:
        extra = sorted(set(obj) - set(required))
        if extra:
            fail(errors, f"{name} has unapproved fields: {', '.join(extra)}")


def check_string_array(name: str, value: Any, errors: list[str]) -> None:
    if not isinstance(value, list):
        fail(errors, f"{name} must be an array")
        return
    for index, item in enumerate(value):
        if not isinstance(item, str):
            fail(errors, f"{name}[{index}] must be a string")


def check_status_schema(status: dict[str, Any] | None, errors: list[str]) -> None:
    if status is None:
        return
    check_object("status", status, TOP_LEVEL_REQUIRED, errors, exact=False)
    extra = sorted(set(status) - TOP_LEVEL_ALLOWED)
    if extra:
        fail(errors, f"status has unapproved top-level fields: {', '.join(extra)}")

    check_object("deployment", status.get("deployment"), DEPLOYMENT_REQUIRED, errors)
    check_object("public_safety", status.get("public_safety"), PUBLIC_SAFETY_REQUIRED, errors)

    safety = status.get("public_safety")
    if isinstance(safety, dict):
        for key in FALSE_PUBLIC_SAFETY_FLAGS:
            if safety.get(key) is not False:
                fail(errors, f"public_safety.{key} must remain false for the static public-safe app")

    for index, item in enumerate(status.get("system_status", [])):
        check_object(f"system_status[{index}]", item, SYSTEM_STATUS_REQUIRED, errors)
    for index, item in enumerate(status.get("cards", [])):
        check_object(f"cards[{index}]", item, CARD_REQUIRED, errors)
        if isinstance(item, dict):
            check_string_array(f"cards[{index}].evidence", item.get("evidence"), errors)
            check_string_array(f"cards[{index}].actions", item.get("actions"), errors)
    for index, item in enumerate(status.get("blocked_items", [])):
        check_object(f"blocked_items[{index}]", item, BLOCKED_REQUIRED, errors)

    for key in ["next_actions", "safety_boundary", "rollback_notes", "acceptance_criteria"]:
        check_string_array(key, status.get(key), errors)


def scan_for_secrets(errors: list[str]) -> None:
    files = [path for path in REQUIRED_FILES + OPTIONAL_PUBLIC_DOCS + [Path(__file__)] if path.exists()]
    validator_path = Path(__file__).resolve()
    for path in files:
        text = path.read_text(encoding="utf-8", errors="ignore")
        for name, pattern in SECRET_PATTERNS.items():
            # The validator necessarily contains literal regex examples for local secret paths.
            # Do not let guardrail definitions self-trigger; still scan the public app/docs.
            if path.resolve() == validator_path and name == "local_secret_path":
                continue
            if pattern.search(text):
                fail(errors, f"possible {name} in {path.relative_to(ROOT)}")


def check_external_resources(errors: list[str]) -> None:
    index = (DOCS / "index.html").read_text(encoding="utf-8", errors="ignore")
    parser = ResourceParser()
    parser.feed(index)
    for issue in parser.external_resources:
        fail(errors, issue)

    css = (DOCS / "styles.css").read_text(encoding="utf-8", errors="ignore")
    if re.search(r"@import\s+['\"]?https?://", css, re.I):
        fail(errors, "external CSS @import detected")
    if re.search(r"url\(\s*['\"]?https?://", css, re.I):
        fail(errors, "external CSS url() detected")

    app = (DOCS / "app.js").read_text(encoding="utf-8", errors="ignore")
    if re.search(r"\bimport\s+(?:[^;]*?\s+from\s+)?['\"]https?://", app, re.I):
        fail(errors, "external JavaScript import URL detected")
    if re.search(r"import\(['\"]https?://", app, re.I):
        fail(errors, "external dynamic import URL detected")

    for match in re.finditer(r"fetch\(\s*(['\"])(.*?)\1", app):
        target = match.group(2)
        if target not in {"status.json", "./status.json", "/status.json"}:
            fail(errors, f"unsafe fetch target: {target}")

    for path in [DOCS / "index.html", DOCS / "styles.css", DOCS / "app.js"]:
        text = path.read_text(encoding="utf-8", errors="ignore")
        # Public links in docs/status are allowed. Executable app assets should not introduce http resources.
        if path.name != "app.js":
            # index may link to local status.json only; CSS should not contain remote URLs at all.
            remote_hits = [m.group(0) for m in HTTP_URL.finditer(text)]
            if remote_hits:
                fail(errors, f"external URL in executable asset {path.relative_to(ROOT)}: {remote_hits[0]}")


def main() -> int:
    errors: list[str] = []
    check_required_files(errors)
    status = load_status(errors)
    check_status_schema(status, errors)
    scan_for_secrets(errors)
    check_external_resources(errors)

    if errors:
        print(json.dumps({"validation": "FAIL", "errors": errors}, indent=2))
        return 1
    print(json.dumps({
        "validation": "PASS",
        "checked": {
            "required_files": [str(p.relative_to(ROOT)) for p in REQUIRED_FILES],
            "status_schema": True,
            "secret_patterns": True,
            "external_js_css_cdn_imports": True,
            "fetch_targets": "local status.json only",
        },
    }, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
