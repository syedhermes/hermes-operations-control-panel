# `status.json` Schema

`docs/status.json` is the only data file the static panel reads. It must contain sanitized, public-safe status data only.

## Schema version

Current schema:

```text
iw-5.status.v2
```

Future changes should update this document and `scripts/validate_static_app.py` in the same commit.

## Top-level fields

| Field | Type | Required | Public-safe purpose |
|---|---:|:---:|---|
| `schema_version` | string | yes | Schema identifier. |
| `title` | string | yes | Public page title. |
| `version_label` | string | yes | Human-readable release/checkpoint label. |
| `updated` | string | yes | ISO-like UTC timestamp or date for the sanitized export. |
| `deployment` | object | yes | Public static deployment summary. |
| `public_safety` | object | yes | Boolean safety switches and public classification. |
| `system_status` | array | yes | Top summary tiles. |
| `cards` | array | yes | Searchable public-safe status cards. |
| `blocked_items` | array | yes | Visible retained blockers. |
| `next_actions` | array | yes | Sanitized future actions. The UI shows the first three at top. |
| `safety_boundary` | array | yes | Plain-language hard boundaries. |
| `rollback_notes` | array | yes | Public-safe rollback guidance. |
| `acceptance_criteria` | array | yes | Static-app acceptance checks. |

No other top-level fields are allowed without updating this schema and the validator.

## `deployment` object

Allowed fields:

| Field | Type | Required |
|---|---:|:---:|
| `state` | string | yes |
| `surface` | string | yes |
| `url` | string | yes |
| `mode` | string | yes |
| `runtime_dependencies` | string | yes |

Allowed content is limited to public deployment facts such as GitHub Pages, the public site URL, static-file mode, and absence of runtime dependencies.

## `public_safety` object

Allowed fields:

| Field | Type | Required | Expected value for this app |
|---|---:|:---:|---|
| `classification` | string | yes | Public-safe sanitized checkpoint status. |
| `source` | string | yes | Sanitized static export only. |
| `live_runtime_reads` | boolean | yes | `false` |
| `private_data` | boolean | yes | `false` |
| `chat_ingestion` | boolean | yes | `false` |
| `credentials` | boolean | yes | `false` |
| `memory_queries` | boolean | yes | `false` |
| `external_api_calls` | boolean | yes | `false` |
| `backend_server` | boolean | yes | `false` |
| `analytics` | boolean | yes | `false` |

If any boolean above needs to become `true`, this static public-safe surface is no longer the right place for the change.

## `system_status` items

Each item must contain only:

| Field | Type | Required |
|---|---:|:---:|
| `id` | string | yes |
| `label` | string | yes |
| `state` | string | yes |
| `summary` | string | yes |

Expected public-safe tiles are Hermes core, layered memory, App Builder, and deployment. Keep summaries high-level and sanitized.

## `cards` items

Each card must contain only:

| Field | Type | Required |
|---|---:|:---:|
| `id` | string | yes |
| `title` | string | yes |
| `state` | string | yes |
| `summary` | string | yes |
| `evidence` | array of strings | yes |
| `actions` | array of strings | yes |

Evidence must refer to public-safe artifacts or sanitized checkpoint facts only. Do not include private logs, raw messages, client details, local paths, or live query output.

## `blocked_items` items

Each item must contain only:

| Field | Type | Required |
|---|---:|:---:|
| `action` | string | yes |
| `reason` | string | yes |
| `approval_required` | string | yes |

GitHub Issues, Notion, and Linear remain blocked unless a separate approved workflow changes the boundary.

## Text arrays

The following must be arrays of strings:

- `next_actions`
- `safety_boundary`
- `rollback_notes`
- `acceptance_criteria`

## Forbidden content in any field

`status.json` must never contain credentials, API keys, tokens, private data, Telegram raw content, client confidential data, local secret paths, external script/style/CDN URLs, live memory query output, or integration output from GitHub Issues, Notion, or Linear.
