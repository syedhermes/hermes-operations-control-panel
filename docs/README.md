# Hermes Operations Control Panel Static App

Public-safe static app for the Hermes Operations Control Panel, updated in IW-5 as a practical v2 for GitHub Pages.

## Contents

- `index.html` — static shell and visible sections
- `styles.css` — local styling, responsive layout, no CDN
- `app.js` — local renderer and client-side filtering
- `status.json` — sanitized IW-5 status export used by the app
- `.nojekyll` — keeps GitHub Pages static serving simple

## IW-5 improvements

- Current System Status summary for Hermes core, layered memory, App Builder, and deployment
- Client-side search/filter for status cards
- Next 3 Actions section from sanitized `status.json`
- Last Updated timestamp from sanitized `status.json`
- Safety Boundary section showing blocked/private gates
- Improved mobile readability

## Safety

- No package installs
- No external CDN
- No analytics
- No external API calls
- No backend/server
- No credentials or private data
- No Telegram ingestion
- No live runtime reads
- No memory queries
- No Hermes runtime modification
- GitHub Issues, Notion, and Linear remain blocked pending separate approval

## Local preview

Serve the `docs/` folder with any static file server and open `index.html`. The app reads local `status.json` from the same folder and does not contact external services.
