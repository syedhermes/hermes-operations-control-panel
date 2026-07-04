# Public Safety Checklist

Use this checklist before every update to the Hermes Operations Control Panel.

## Static app boundary

- [ ] The app still runs from `docs/` static files only.
- [ ] No backend, server, container, worker, cron, watchdog, or self-evolution behavior was added.
- [ ] No Hermes runtime modification was made.
- [ ] No provider or model configuration was changed.
- [ ] No package install or build step is required.
- [ ] Python validation uses stdlib only.

## Data boundary

- [ ] `docs/status.json` contains sanitized public checkpoint status only.
- [ ] No credentials, API keys, tokens, passwords, cookies, private keys, or recovery material appear anywhere.
- [ ] No private data, private memory recall, live memory query output, or private Hermes runtime state appears anywhere.
- [ ] No Telegram raw content, chat export, message text, message IDs, or conversation logs appear anywhere.
- [ ] No client confidential data appears anywhere.
- [ ] No local secret paths, private configuration paths, or machine-specific secret locations appear anywhere.

## Network boundary

- [ ] No external JavaScript, CSS, CDN, font, image, analytics, tracking, import, or module URLs were added.
- [ ] `docs/app.js` fetches only local `status.json`.
- [ ] No external API calls, WebSocket, event-stream, or live adapter calls were added.

## Integration boundary

- [ ] GitHub Issues integration remains blocked.
- [ ] Notion integration remains blocked.
- [ ] Linear integration remains blocked.
- [ ] No tracker/workspace data was copied into the panel.

## Schema boundary

- [ ] `docs/status.json` follows `docs/STATUS_SCHEMA.md`.
- [ ] New fields, if any, were added to both `docs/STATUS_SCHEMA.md` and `scripts/validate_static_app.py`.
- [ ] Public-safety booleans remain `false` for live runtime reads, private data, chat ingestion, credentials, memory queries, external API calls, backend/server, and analytics.

## Verification commands

Run before commit:

```bash
python3 scripts/validate_static_app.py
python3 -m http.server 8765 --directory docs
```

Then open the local preview and confirm:

- [ ] Current System Status renders.
- [ ] Next 3 Actions renders.
- [ ] Safety Boundary renders.
- [ ] Status-card search/filter works.
- [ ] The layout remains readable on a narrow/mobile viewport.
