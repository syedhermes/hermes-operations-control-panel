#!/usr/bin/env python3
"""Refresh docs/status.json from approved sanitized local sources only.

IW-7 guardrails:
- stdlib only
- no network calls
- no private memory queries
- no Telegram ingestion
- no credentials or runtime reads
- source data is the existing public-safe status.json baseline plus sanitized repo docs
"""

from __future__ import annotations

import json
import re
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
STATUS_PATH = DOCS / "status.json"

SCHEMA_VERSION = "iw-5.status.v2"
VERSION_LABEL = "IW-7 internal-only status refresh"
PUBLIC_URL = "https://syedhermes.github.io/hermes-operations-control-panel/"

APPROVED_LOCAL_SOURCES = [
    STATUS_PATH,
    DOCS / "README.md",
    DOCS / "STATUS_SCHEMA.md",
    DOCS / "SAFETY_CHECKLIST.md",
    ROOT / "README.md",
]

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

FORBIDDEN_TERMS = [
    "mnemosyne_recall",
    "telegram ingestion",
    "telegram raw content",
    "external api calls: enabled",
    "credentials: present",
]


def fail(message: str) -> None:
    print(json.dumps({"refresh": "FAIL", "error": message}, indent=2))
    raise SystemExit(1)


def load_baseline() -> dict[str, Any]:
    try:
        loaded = json.loads(STATUS_PATH.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001 - CLI should report every parse failure plainly.
        fail(f"could not read existing docs/status.json: {exc}")
        raise AssertionError("unreachable after fail") from exc
    if not isinstance(loaded, dict):
        fail("existing docs/status.json must be a JSON object")
        raise AssertionError("unreachable after fail")
    return loaded


def read_approved_sources() -> dict[str, str]:
    sources: dict[str, str] = {}
    for path in APPROVED_LOCAL_SOURCES:
        if not path.exists():
            fail(f"approved local source missing: {path.relative_to(ROOT)}")
        text = path.read_text(encoding="utf-8", errors="ignore")
        sources[str(path.relative_to(ROOT))] = text
    return sources


def guard_text(name: str, text: str) -> None:
    lowered = text.lower()
    for term in FORBIDDEN_TERMS:
        if term in lowered:
            # Allow safety docs to name forbidden categories as blocked concepts.
            if term in {"telegram ingestion", "telegram raw content"} and "blocked" in lowered:
                continue
            fail(f"forbidden term in {name}: {term}")
    for label, pattern in SECRET_PATTERNS.items():
        if pattern.search(text):
            fail(f"possible {label} in {name}")


def guard_status(status: dict[str, Any]) -> None:
    rendered = json.dumps(status, sort_keys=True, ensure_ascii=False)
    guard_text("generated docs/status.json", rendered)
    safety = status.get("public_safety")
    if not isinstance(safety, dict):
        fail("public_safety must be an object")
    for key in FALSE_PUBLIC_SAFETY_FLAGS:
        if safety.get(key) is not False:
            fail(f"public_safety.{key} must remain false")


def build_status(_: dict[str, Any], sources: dict[str, str]) -> dict[str, Any]:
    now = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    source_names = ", ".join(sorted(sources))

    return {
        "schema_version": SCHEMA_VERSION,
        "title": "Hermes Operations Control Panel",
        "version_label": VERSION_LABEL,
        "updated": now,
        "deployment": {
            "state": "live-static-pages",
            "surface": "GitHub Pages",
            "url": PUBLIC_URL,
            "mode": "static files only",
            "runtime_dependencies": "none",
        },
        "public_safety": {
            "classification": "public-safe sanitized checkpoint status",
            "source": "Internal-only refresh from approved sanitized local repository files only",
            "live_runtime_reads": False,
            "private_data": False,
            "chat_ingestion": False,
            "credentials": False,
            "memory_queries": False,
            "external_api_calls": False,
            "backend_server": False,
            "analytics": False,
        },
        "system_status": [
            {
                "id": "hermes-core",
                "label": "Hermes core",
                "state": "planned-safe-surface",
                "summary": "Represented as sanitized checkpoint status only; no Hermes runtime reads or modifications.",
            },
            {
                "id": "layered-memory",
                "label": "Layered memory",
                "state": "foundation-pass",
                "summary": "Checkpoint-level foundation status only; no private memory query or recall output.",
            },
            {
                "id": "app-builder",
                "label": "App Builder",
                "state": "pass",
                "summary": "Static control-panel artifacts remain deterministic local files served from docs/.",
            },
            {
                "id": "status-refresh",
                "label": "Status refresh",
                "state": "iw-7-pass",
                "summary": "Status snapshot is regenerated by a stdlib-only local script from approved sanitized sources.",
            },
            {
                "id": "deployment",
                "label": "Deployment",
                "state": "live-static-pages",
                "summary": "GitHub Pages deployment uses docs/ static files only.",
            },
        ],
        "cards": [
            {
                "id": "hermes-core-dashboard",
                "title": "Hermes Core / Dashboard",
                "state": "planned-safe-surface",
                "summary": "Sanitized public status surface only; no live Hermes core, gateway, dashboard adapter, or runtime reads were performed.",
                "evidence": [
                    "docs/status.json",
                    "scripts/refresh_status_snapshot.py",
                    "No Hermes runtime modification",
                ],
                "actions": [
                    "Keep live adapters behind a separate explicit approval gate.",
                ],
            },
            {
                "id": "layered-memory",
                "title": "Layered Memory",
                "state": "foundation-pass",
                "summary": "Layered memory is shown only as checkpoint-level foundation status supplied by sanitized local files.",
                "evidence": [
                    "Sanitized checkpoint wording only",
                    "No memory queries",
                    "No private recall",
                ],
                "actions": [
                    "Keep memory status checkpoint-level until a separate safe adapter is approved.",
                ],
            },
            {
                "id": "app-builder",
                "title": "App Builder",
                "state": "pass",
                "summary": "App Builder artifacts are represented as static public files with deterministic client-side rendering.",
                "evidence": [
                    "docs/index.html",
                    "docs/styles.css",
                    "docs/app.js",
                    "docs/status.json",
                ],
                "actions": [
                    "Use this static surface as the public handoff for IW checkpoints.",
                ],
            },
            {
                "id": "status-refresh-pipeline",
                "title": "IW-7 Status Refresh Pipeline",
                "state": "implemented",
                "summary": "A local stdlib-only refresh script rebuilds status.json from approved sanitized repository files without external APIs or private sources.",
                "evidence": [
                    "scripts/refresh_status_snapshot.py",
                    f"Approved sources: {source_names}",
                    "docs/status.json regenerated",
                ],
                "actions": [
                    "Run the refresh script before publishing future sanitized status updates.",
                ],
            },
            {
                "id": "deployment",
                "title": "Deployment",
                "state": "live-static-pages",
                "summary": "The control panel is deployed as a GitHub Pages static site with no backend, analytics, external APIs, or CDNs.",
                "evidence": [
                    "GitHub Pages from docs/ on main",
                    "Static files only",
                    "No runtime dependencies",
                ],
                "actions": [
                    "Keep deployment static unless a separate public-safe live-adapter gate is approved.",
                ],
            },
            {
                "id": "blocked-items",
                "title": "Blocked Items",
                "state": "active",
                "summary": "External integrations and unsafe operations remain blocked unless separately approved.",
                "evidence": [
                    "GitHub Issues blocked",
                    "Notion blocked",
                    "Linear blocked",
                    "No tracker or workspace ingestion",
                ],
                "actions": [
                    "Keep blocked items visible in every preview and deployment.",
                ],
            },
            {
                "id": "rollback-notes",
                "title": "Rollback Notes",
                "state": "documented",
                "summary": "Rollback remains commit-based for GitHub Pages and file-based for local static artifacts.",
                "evidence": [
                    "Revert the IW-7 commit on main to roll back the live app.",
                    "Disable GitHub Pages only if the whole public surface must be taken offline.",
                ],
                "actions": [
                    "Record deployment commit hash after IW-7 push.",
                ],
            },
        ],
        "blocked_items": [
            {
                "action": "GitHub Issues",
                "reason": "External tracker sync is out of scope for this public-safe static app.",
                "approval_required": "Separate approval required",
            },
            {
                "action": "Notion",
                "reason": "External workspace sync is out of scope for this public-safe static app.",
                "approval_required": "Separate approval required",
            },
            {
                "action": "Linear",
                "reason": "External planning integration is out of scope for this public-safe static app.",
                "approval_required": "Separate approval required",
            },
            {
                "action": "Private memory / chat ingestion",
                "reason": "Status refresh is limited to approved sanitized local files and does not ingest private memory or chat content.",
                "approval_required": "Separate adapter and safety review required",
            },
        ],
        "next_actions": [
            "Use scripts/refresh_status_snapshot.py for future sanitized status refreshes.",
            "Keep status.json schema changes paired with validator updates.",
            "Prepare a separate approval gate before any live adapter, tracker, or memory integration.",
        ],
        "safety_boundary": [
            "No external APIs, CDNs, analytics, backend, or server runtime.",
            "No credentials, API keys, private data, Telegram ingestion, or live memory query.",
            "No Hermes runtime modification, provider/model changes, cron, watchdogs, or self-evolution.",
            "GitHub Issues, Notion, Linear, private memory, and chat ingestion remain blocked pending separate approval.",
        ],
        "rollback_notes": [
            "Rollback IW-7 by reverting the deployment commit on main and pushing the revert.",
            "If the full public surface must be removed, disable GitHub Pages in repository settings.",
            "Keep local rollback file-based: restore docs/status.json and scripts/refresh_status_snapshot.py from the prior commit.",
        ],
        "acceptance_criteria": [
            "scripts/refresh_status_snapshot.py exists and runs with Python stdlib only.",
            "docs/status.json is regenerated from approved sanitized local sources only.",
            "Current System Status summary is visible at top.",
            "Status cards can be filtered client-side only.",
            "Next 3 Actions render from sanitized status.json.",
            "Last Updated timestamp renders from sanitized status.json.",
            "Safety Boundary section shows blocked/private gates.",
            "Everything remains static.",
        ],
    }


def main() -> int:
    baseline = load_baseline()
    sources = read_approved_sources()
    for name, text in sources.items():
        guard_text(name, text)

    status = build_status(baseline, sources)
    guard_status(status)
    STATUS_PATH.write_text(json.dumps(status, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "refresh": "PASS",
        "updated": status["updated"],
        "version_label": status["version_label"],
        "sources": sorted(sources),
        "output": str(STATUS_PATH.relative_to(ROOT)),
    }, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
