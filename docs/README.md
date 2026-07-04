# Hermes Operations Control Panel Static App

Public-safe static app generated for IW-3.

## Contents

- `index.html` — static shell
- `styles.css` — local styling, no CDN
- `app.js` — local renderer with embedded sanitized status data so the app works from `file://`
- `status.json` — sanitized IW-2 status export

## Safety

- No package installs
- No external CDN
- No analytics
- No external API calls
- No credentials or private data
- No live runtime reads
- No chat ingestion
- No memory queries

## Local preview

Open `index.html` directly from the folder.
