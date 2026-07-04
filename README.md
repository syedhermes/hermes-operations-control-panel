# Hermes Operations Control Panel

Public-safe static status app generated from sanitized Hermes Operations checkpoints.

Live site: https://syedhermes.github.io/hermes-operations-control-panel/

## What this repository contains

GitHub Pages serves the static app from `docs/` on `main`.

- `docs/index.html` — static HTML shell.
- `docs/styles.css` — local CSS only.
- `docs/app.js` — local client-side renderer; may fetch only local `status.json`.
- `docs/status.json` — sanitized public-safe status data.
- `docs/CONTRIBUTING.md` — public-safe contribution workflow.
- `docs/STATUS_SCHEMA.md` — schema and allowed fields for `status.json`.
- `docs/SAFETY_CHECKLIST.md` — pre-commit public safety checklist.
- `scripts/validate_static_app.py` — Python stdlib-only validator.

## Hard boundaries

This project must remain a static public-safe panel.

Blocked unless separately approved:

- Credentials, API keys, tokens, passwords, cookies, private keys, or recovery material.
- Private data, client confidential data, Telegram raw content, local secret paths, or live memory query output.
- External script/style/CDN/import URLs, analytics, tracking, backend/server calls, or live adapters.
- Telegram ingestion, Hermes runtime changes, provider/model changes, cron, watchdog, or self-evolution behavior.
- GitHub Issues, Notion, and Linear integrations.

## Local preview

From the repository root:

```bash
python3 -m http.server 8765 --directory docs
```

Open:

```text
http://127.0.0.1:8765/
```

The app reads `docs/status.json` from the same static folder. It should not contact external services.

## Validate before commit

Run:

```bash
python3 scripts/validate_static_app.py
```

The validator checks:

- Required app files exist.
- `docs/status.json` parses as JSON.
- Required schema fields exist.
- Obvious secret/token/private-key patterns are absent.
- External JS/CSS/CDN/import URLs are absent.
- `fetch()` targets are limited to local `status.json`.

Also review:

```text
docs/SAFETY_CHECKLIST.md
```

## Deploy / push steps

After validation and local preview pass:

```bash
git status --short
git add docs scripts README.md
git commit -m "docs(iw6): add public-safe contribution workflow"
git push origin main
```

GitHub Pages serves the updated `docs/` content automatically.

Confirm the live app:

```bash
python3 - <<'PY'
import urllib.request
url = 'https://syedhermes.github.io/hermes-operations-control-panel/'
with urllib.request.urlopen(url, timeout=15) as response:
    print(response.status, response.geturl())
PY
```

## Rollback

Rollback a deployment commit:

```bash
git revert <commit-sha>
git push origin main
```

If the entire public surface must be removed, disable GitHub Pages in repository settings.
