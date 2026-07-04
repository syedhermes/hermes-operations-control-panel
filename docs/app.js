const STATUS = {
  "schema_version": "iw-2.status.v1",
  "title": "Hermes Operations Control Panel",
  "updated": "2026-07-04",
  "public_safety": {
    "classification": "public-safe sanitized checkpoint status",
    "source": "Generated local Markdown package only",
    "live_runtime_reads": false,
    "private_data": false,
    "chat_ingestion": false,
    "credentials": false,
    "memory_queries": false,
    "external_api_calls": false
  },
  "source_artifacts": [
    "README.md",
    "00-idea-capture.md",
    "01-design-doc.md",
    "02-ui-design-brief.md",
    "03-implementation-spec.md",
    "04-agent-build-handoff.md",
    "05-spec-review.md",
    "preview/index.html"
  ],
  "cards": [
    {
      "id": "gateway-dashboard",
      "title": "Gateway / Dashboard",
      "state": "planned",
      "summary": "Sanitized status placeholder only; no live gateway or dashboard runtime reads were performed.",
      "evidence": [
        "IW-1 package scope",
        "No Hermes runtime modification"
      ],
      "actions": [
        "Define allowed public-safe dashboard fields before any live adapter."
      ]
    },
    {
      "id": "layered-memory",
      "title": "Layered Memory",
      "state": "foundation-pass",
      "summary": "LM-2D and LM-2E are represented only as completed/PASS foundation facts supplied by the operator.",
      "evidence": [
        "Operator-provided checkpoint fact",
        "No memory queries"
      ],
      "actions": [
        "Keep memory status checkpoint-level until a separate safe adapter is approved."
      ]
    },
    {
      "id": "app-builder",
      "title": "App Builder",
      "state": "pass",
      "summary": "App Builder Checkpoint 002 and IW-1 generated package are available as local Markdown artifacts with deterministic review.",
      "evidence": [
        "output/hermes-operations-control-panel/*.md",
        "preview/index.html"
      ],
      "actions": [
        "Use this status export as the bridge to the static control-panel app."
      ]
    },
    {
      "id": "blocked-items",
      "title": "Blocked Items",
      "state": "active",
      "summary": "External integrations and unsafe operations remain blocked unless separately approved.",
      "evidence": [
        "GitHub Issues",
        "Notion",
        "Linear"
      ],
      "actions": [
        "Keep blocked items visible in every preview and deployment."
      ]
    },
    {
      "id": "next-actions",
      "title": "Next Actions",
      "state": "ready",
      "summary": "IW-2 status export and IW-3 static app build are complete; IW-4 public deployment depends on a clean safety scan and available GitHub auth.",
      "evidence": [
        "python3 app_builder_intake_gate.py generate fixtures/hermes-operations-control-panel.json output/hermes-operations-control-panel",
        "python3 app_builder_intake_gate.py review output/hermes-operations-control-panel",
        "python3 app_builder_intake_gate.py preview output/hermes-operations-control-panel output/hermes-operations-control-panel-preview",
        "python3 -m unittest tests_mvp.py -v",
        "sha256sum fixtures/hermes-operations-control-panel.json output/hermes-operations-control-panel/*.md output/hermes-operations-control-panel-preview/index.html"
      ],
      "actions": [
        "Run public safety scan before deploy."
      ]
    },
    {
      "id": "rollback-notes",
      "title": "Rollback Notes",
      "state": "documented",
      "summary": "Rollback remains file/folder based for local phases and commit based for GitHub Pages.",
      "evidence": [
        "Remove output/hermes-operations-control-panel-status to roll back IW-2 status export.",
        "Remove output/hermes-operations-control-panel-app to roll back IW-3 static app build.",
        "For a GitHub Pages rollback, revert the deployment commit or disable Pages in repository settings.",
        "Re-run python3 -m unittest tests_mvp.py -v after local rollback to verify the App Builder baseline."
      ],
      "actions": [
        "Record deployment commit hash if IW-4 deploys."
      ]
    }
  ],
  "blocked_items": [
    {
      "action": "GitHub Issues",
      "reason": "External tracker sync is out of scope for the local control-panel spec",
      "approval_required": "Separate approval required"
    },
    {
      "action": "Notion",
      "reason": "External workspace sync is out of scope for the local control-panel spec",
      "approval_required": "Separate approval required"
    },
    {
      "action": "Linear",
      "reason": "External planning integration is out of scope for the local control-panel spec",
      "approval_required": "Separate approval required"
    }
  ],
  "next_actions": [
    "python3 app_builder_intake_gate.py generate fixtures/hermes-operations-control-panel.json output/hermes-operations-control-panel",
    "python3 app_builder_intake_gate.py review output/hermes-operations-control-panel",
    "python3 app_builder_intake_gate.py preview output/hermes-operations-control-panel output/hermes-operations-control-panel-preview",
    "python3 -m unittest tests_mvp.py -v",
    "sha256sum fixtures/hermes-operations-control-panel.json output/hermes-operations-control-panel/*.md output/hermes-operations-control-panel-preview/index.html"
  ],
  "rollback_notes": [
    "Remove output/hermes-operations-control-panel-status to roll back IW-2 status export.",
    "Remove output/hermes-operations-control-panel-app to roll back IW-3 static app build.",
    "For a GitHub Pages rollback, revert the deployment commit or disable Pages in repository settings.",
    "Re-run python3 -m unittest tests_mvp.py -v after local rollback to verify the App Builder baseline."
  ],
  "acceptance_criteria": [
    "Generate command creates README and artifacts 00 through 05 for Hermes Operations Control Panel",
    "Review command returns VERDICT: PASS for the generated IW-1 package",
    "Preview command writes output/hermes-operations-control-panel-preview/index.html",
    "Preview index.html contains escaped Markdown content and preserves all expected artifact names",
    "Generated handoff contains GitHub Issues, Notion, and Linear as blocked items",
    "Generated package includes no deployment, no external API calls, no package installs, no containers, and no credentials/API keys",
    "Generated package contains rollback commands and next local-only build checkpoint"
  ],
  "done_means": [
    "All expected Markdown artifacts exist in output/hermes-operations-control-panel",
    "Review verdict prints PASS with gate checks passed",
    "Preview writes static local index.html only",
    "Hashes are recorded for fixture, Markdown artifacts, and preview index",
    "Blocked items remain visible and require separate approval",
    "Next practical build step is documented without activating integrations"
  ],
  "risks": [],
  "local_preview": "output/hermes-operations-control-panel-app/index.html"
};
const text = (value) => String(value ?? "");
const el = (tag, className, content) => { const node = document.createElement(tag); if (className) node.className = className; if (content !== undefined) node.textContent = content; return node; };
const list = (items, className) => { const ul = el('ul', className || ''); (items || []).forEach((item) => ul.appendChild(el('li', '', text(item)))); return ul; };
function renderSafety(safety) {
  const grid = document.getElementById('safety-grid');
  const checks = [['Classification', safety.classification], ['Live runtime reads', safety.live_runtime_reads ? 'enabled' : 'disabled'], ['Private data', safety.private_data ? 'present' : 'absent'], ['Chat ingestion', safety.chat_ingestion ? 'enabled' : 'disabled'], ['Credentials', safety.credentials ? 'present' : 'absent'], ['Memory queries', safety.memory_queries ? 'enabled' : 'disabled'], ['External API calls', safety.external_api_calls ? 'enabled' : 'disabled']];
  checks.forEach(([label, value]) => { const pill = el('div', 'safety-pill'); pill.appendChild(el('strong', '', label)); pill.appendChild(el('span', '', value)); grid.appendChild(pill); });
}
function renderCards(cards) {
  const host = document.getElementById('cards');
  cards.forEach((card) => { const article = el('article', ''); article.appendChild(el('span', 'card-state', card.state)); article.appendChild(el('h3', '', card.title)); article.appendChild(el('p', 'card-summary', card.summary)); article.appendChild(el('h4', '', 'Evidence')); article.appendChild(list(card.evidence, 'evidence')); if (card.actions?.length) { article.appendChild(el('h4', '', 'Action')); article.appendChild(list(card.actions)); } host.appendChild(article); });
}
function renderBlocked(items) { const host = document.getElementById('blocked-items'); items.forEach((item) => { const row = el('div', 'blocked-item'); row.appendChild(el('strong', '', item.action)); row.appendChild(el('p', '', item.reason)); row.appendChild(el('small', '', item.approval_required)); host.appendChild(row); }); }
function renderOrdered(id, items) { const host = document.getElementById(id); (items || []).forEach((item) => host.appendChild(el('li', '', text(item)))); }
function render(status) { document.title = status.title || document.title; renderSafety(status.public_safety || {}); renderCards(status.cards || []); renderBlocked(status.blocked_items || []); renderOrdered('next-actions', status.next_actions || []); renderOrdered('rollback-notes', status.rollback_notes || []); document.getElementById('updated').textContent = `Updated ${status.updated || 'unknown'}`; }
render(STATUS);
