# Contributing to the Hermes Operations Control Panel

This repository publishes a **public-safe static GitHub Pages panel** from the `docs/` folder. Contributions must keep the panel useful without opening private or live gates.

## Core rule

Every change must be safe to publish publicly. If a value came from a private chat, client document, local runtime, secret store, live memory query, or confidential project system, it does **not** belong here.

## Allowed update types

You may update:

- `docs/index.html` for static markup only.
- `docs/styles.css` for local CSS only.
- `docs/app.js` for local client-side rendering only.
- `docs/status.json` for sanitized status data that follows `STATUS_SCHEMA.md`.
- `docs/README.md`, `docs/CONTRIBUTING.md`, `docs/STATUS_SCHEMA.md`, and `docs/SAFETY_CHECKLIST.md` for public-safe documentation.
- `scripts/validate_static_app.py` for stdlib-only validation.

## Public-safe contribution workflow

1. Start from a clean branch or clean `main` working tree.
2. Edit only static files unless the workflow explicitly calls for validator updates.
3. Keep all status content sanitized and checkpoint-level.
4. Run the validator:

   ```bash
   python3 scripts/validate_static_app.py
   ```

5. Preview locally:

   ```bash
   python3 -m http.server 8765 --directory docs
   ```

   Then open `http://127.0.0.1:8765/` in a browser.

6. Check the safety checklist in `docs/SAFETY_CHECKLIST.md`.
7. Commit only after validation and local preview pass.
8. Push to `main`; GitHub Pages serves from `docs/`.
9. Confirm the live page returns HTTP 200.

## Allowed public-safe status content

Status text may include:

- Sanitized checkpoint names.
- Public deployment mode and public URL.
- Static app file names.
- High-level states such as `pass`, `blocked`, `planned-safe-surface`, or `live-static-pages`.
- Public-safe next actions.
- Public-safe rollback instructions using commit IDs only after deployment.
- Explicit safety boundaries.

## Forbidden content

Do **not** include:

- Credentials, API keys, tokens, passwords, cookies, private keys, or recovery material.
- Private user data or private Hermes runtime state.
- Telegram raw content, message IDs, chat exports, or conversation logs.
- Client confidential data, project correspondence, claims details, commercial terms, or private programme data.
- Local secret paths or private machine configuration.
- External script, style, CDN, import, analytics, or tracking URLs.
- Live memory query output or private recall results.
- GitHub Issues, Notion, or Linear integration data.
- Any backend, server, cron, watchdog, or self-evolution behavior.

## Static-only JavaScript rule

`docs/app.js` may fetch only local `status.json` from the same static directory. Do not add external `fetch()`, WebSocket, event-stream, analytics, or runtime adapter calls.

## Deployment

Deployment is commit-based:

```bash
git add docs scripts README.md
git commit -m "docs(iw6): add public-safe contribution workflow"
git push origin main
```

Rollback is also commit-based:

```bash
git revert <commit-sha>
git push origin main
```
