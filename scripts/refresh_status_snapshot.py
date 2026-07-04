#!/usr/bin/env python3
"""
Refresh docs/status.json from approved sanitized local sources only.

IW-8 guardrails:
- stdlib only
- no network calls
- no private memory queries
- no Telegram ingestion
- no credentials or runtime reads
- source data is the existing public-safe status.json plus sanitized repo docs
- plus two internal Hermes operations files (PROJECT_STATUS.md, NEXT_ACTIONS.md)
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

# Internal Hermes operations directory (approved source)
HERMES_OPS_DIR = Path("/mnt/f/Hermes/projects/syed-layered-memory-system/internal_workspaces/hermes_operations")

SCHEMA_VERSION = "iw-5.status.v2"
VERSION_LABEL = "IW-8 internal-only status refresh with Hermes operations"
PUBLIC_URL = "https://syedhermes.github.io/hermes-operations-control-panel/"

APPROVED_LOCAL_SOURCES = [
    STATUS_PATH,
    DOCS / "README.md",
    DOCS / "STATUS_SCHEMA.md",
    DOCS / "SAFETY_CHECKLIST.md",
    ROOT / "README.md",
    HERMES_OPS_DIR / "PROJECT_STATUS.md",
    HERMES_OPS_DIR / "NEXT_ACTIONS.md",
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
        r"(?i)\b(?:api[_-]?key|secret|token|password|passwd|authorization|bearer)\b\s*[:=]\s*['\\\"]?[A-Za-z0-9_./+=:-]{16,}"
    ),
    "local_secret_path": re.compile(r"(?i)(?:/\\.ssh/|/secrets?/|/\\.aws/|/\\.config/(?:gh|gcloud|az)|id_rsa|id_ed25519)"),
}

FORBIDDEN_TERMS = [
    "mnemosyne_recall",
    "telegram ingestion",
    "telegram raw content",
    "external api calls: enabled",
    "credentials: present",
]


def _get_display_name(path: Path) -> str:
    """Return a display-safe name for a path, suitable for public status.json."""
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        # For files outside ROOT, try to map to a known internal base.
        try:
            relative_to_base = path.relative_to(HERMES_OPS_DIR)
            return f"internal/hermes_operations/{relative_to_base}"
        except ValueError:
            # Fallback: generic internal label (avoid leaking absolute paths)
            return "internal/unknown"


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
        raise AssertionError("unreachable after fail") from exc
    return loaded


def read_approved_sources() -> dict[str, str]:
    sources: dict[str, str] = {}
    for path in APPROVED_LOCAL_SOURCES:
        if not path.exists():
            display_name = _get_display_name(path)
            fail(f"approved local source missing: {display_name}")
        text = path.read_text(encoding="utf-8", errors="ignore")
        display_name = _get_display_name(path)
        sources[display_name] = text
    return sources


def guard_text(name: str, text: str) -> None:
    lowered = text.lower()
    for term in FORBIDDEN_TERMS:
        if term in lowered:
            # Allow safety docs to name forbidden categories as blocked concepts.
            if term in {"telegram ingestion", "telegram raw content", "mnemosyne_recall"} and "blocked" in lowered:
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


def append_unique(items: list[dict[str, Any]], additions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen = {item.get("id") for item in items if isinstance(item, dict)}
    merged = list(items)
    for item in additions:
        if item["id"] not in seen:
            merged.append(item)
            seen.add(item["id"])
    return merged


def sanitize_text(text: str, *, max_len: int = 220) -> str:
    text = re.sub(r"`[^`]*`", "", text)
    text = re.sub(r"\b[0-9a-f]{12,}\b", "", text, flags=re.I)
    text = re.sub(r"/[^\s|)]+", "", text)
    text = re.sub(r"\s+", " ", text).strip(" -|.")
    replacements = {
        "Mnemosyne": "approved workspace reminders",
        "Mem0": "local synthetic memory layer",
        "Honcho": "local synthetic session layer",
        "GBrain": "local synthetic graph-style layer",
        "Qdrant": "local vector layer",
        "TurboVec": "deferred vector option",
        "Telegram": "chat-source",
        "Nango": "external integration",
    }
    for old, new_value in replacements.items():
        text = text.replace(old, new_value)
    forbidden_fragments = ["curl ", "http://", "https://", "127.0.0.1", "localhost", "api key", "credential"]
    lowered = text.lower()
    if any(fragment in lowered for fragment in forbidden_fragments):
        return "Detailed operational content retained only in the approved internal workspace."
    if len(text) > max_len:
        text = text[: max_len - 1].rsplit(" ", 1)[0] + "…"
    return text or "Sanitized internal workspace status available."


def first_matching_line(text: str, prefixes: tuple[str, ...], fallback: str) -> str:
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("|"):
            continue
        clean = line.lstrip("-#* ").strip()
        lowered = clean.lower()
        if any(lowered.startswith(prefix) for prefix in prefixes):
            return sanitize_text(clean)
    return fallback


def extract_hermes_operations_cards(sources: dict[str, str]) -> list[dict[str, Any]]:
    project = sources.get("internal/hermes_operations/PROJECT_STATUS.md", "")
    next_actions = sources.get("internal/hermes_operations/NEXT_ACTIONS.md", "")
    project_summary = first_matching_line(
        project,
        ("the hermes operations workspace is active", "overall lm-2 result", "the workspace is usable"),
        "Hermes operations workspace status is available as sanitized internal project-file summaries only.",
    )
    action_summary = first_matching_line(
        next_actions,
        ("lm-2a:", "required next checkpoint", "first activation candidate", "review lm-0 result"),
        "Next Hermes operations checkpoint is retained as a sanitized internal action summary only.",
    )
    return [
        {
            "id": "hermes-operations-status",
            "title": "Hermes Operations Status",
            "state": "sanitized-summary",
            "summary": project_summary,
            "evidence": [
                "Approved Hermes operations project-status source read locally",
                "Absolute paths and operational details excluded from public status.json",
                "No private memory query, chat ingestion, credentials, external API, containers, or runtime modification",
            ],
            "actions": [
                "Keep Hermes operations output limited to sanitized public-safe summaries.",
            ],
        },
        {
            "id": "hermes-operations-next-checkpoint",
            "title": "Hermes Operations Next Checkpoint",
            "state": "sanitized-summary",
            "summary": action_summary,
            "evidence": [
                "Approved Hermes operations next-actions source read locally",
                "No absolute internal path exposed",
                "Blocked gates remain represented as blocked_items objects",
            ],
            "actions": [
                "Require separate explicit approval before any live adapter, credentialed service, container, or runtime activation.",
            ],
        },
    ]


def build_status(baseline: dict[str, Any], sources: dict[str, str]) -> dict[str, Any]:
    now = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    status = dict(baseline)
    status["schema_version"] = baseline.get("schema_version", "iw-5.status.v2")
    status["version_label"] = VERSION_LABEL
    status["updated"] = now

    safety = dict(status.get("public_safety", {}))
    safety["source"] = "Internal-only refresh from approved sanitized local repository files plus sanitized Hermes operations summaries."
    for key in FALSE_PUBLIC_SAFETY_FLAGS:
        safety[key] = False
    status["public_safety"] = safety

    existing_system_status = status.get("system_status", [])
    if not isinstance(existing_system_status, list):
        existing_system_status = []
    system_updates = [
        {
            "id": "hermes-operations-project-status",
            "label": "Hermes Operations Project Status",
            "state": "sanitized-summary",
            "summary": "Approved internal Hermes operations project status is reflected only as public-safe sanitized card summaries.",
        },
        {
            "id": "hermes-operations-next-actions",
            "label": "Hermes Operations Next Actions",
            "state": "sanitized-summary",
            "summary": "Approved internal Hermes operations next actions are reflected only as public-safe sanitized card summaries.",
        },
    ]
    status["system_status"] = append_unique(existing_system_status, system_updates)

    existing_cards = status.get("cards", [])
    if not isinstance(existing_cards, list):
        existing_cards = []
    status["cards"] = append_unique(existing_cards, extract_hermes_operations_cards(sources))

    existing_blocked = status.get("blocked_items", [])
    if not isinstance(existing_blocked, list):
        existing_blocked = []
    status["blocked_items"] = [item for item in existing_blocked if isinstance(item, dict)]

    next_actions = status.get("next_actions", [])
    if isinstance(next_actions, list):
        addition = "Keep Hermes operations adapter limited to sanitized summaries unless a separate live-adapter approval gate is opened."
        if addition not in next_actions:
            status["next_actions"] = list(next_actions) + [addition]

    criteria = status.get("acceptance_criteria", [])
    if isinstance(criteria, list):
        addition = "Hermes operations summaries preserve the IW-7 status.json schema and expose no absolute internal paths."
        if addition not in criteria:
            status["acceptance_criteria"] = list(criteria) + [addition]

    return status

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