let ACTIVE_STATUS = null;
let ALL_CARDS = [];

const text = (value) => String(value ?? "");
const el = (tag, className, content) => {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (content !== undefined) node.textContent = content;
  return node;
};
const clear = (node) => { while (node.firstChild) node.removeChild(node.firstChild); };
const list = (items, className) => {
  const ul = el('ul', className || '');
  (items || []).forEach((item) => ul.appendChild(el('li', '', text(item))));
  return ul;
};
const stateTone = (state) => text(state).toLowerCase().replace(/[^a-z0-9]+/g, '-');

async function loadStatus() {
  const response = await fetch('status.json', { cache: 'no-store' });
  if (!response.ok) throw new Error(`status.json HTTP ${response.status}`);
  return response.json();
}

function renderLoadError(error) {
  const main = document.querySelector('main');
  const box = el('section', 'load-error');
  box.appendChild(el('h2', '', 'Status data could not be loaded'));
  box.appendChild(el('p', '', 'This static app expects docs/status.json beside index.html. Serve the docs folder with a static file server or open it from GitHub Pages.'));
  box.appendChild(el('code', '', error.message));
  main.prepend(box);
}

function renderSystemStatus(status) {
  const host = document.getElementById('system-status-grid');
  clear(host);
  (status.system_status || []).forEach((item) => {
    const card = el('article', `status-tile tone-${stateTone(item.state)}`);
    card.appendChild(el('span', 'status-label', item.label));
    card.appendChild(el('strong', 'status-state', item.state));
    card.appendChild(el('p', '', item.summary));
    host.appendChild(card);
  });
}

function renderSafety(safety) {
  const grid = document.getElementById('safety-grid');
  clear(grid);
  const checks = [
    ['Classification', safety.classification],
    ['Source', safety.source],
    ['Live runtime reads', safety.live_runtime_reads ? 'enabled' : 'disabled'],
    ['Private data', safety.private_data ? 'present' : 'absent'],
    ['Chat ingestion', safety.chat_ingestion ? 'enabled' : 'disabled'],
    ['Credentials', safety.credentials ? 'present' : 'absent'],
    ['Memory queries', safety.memory_queries ? 'enabled' : 'disabled'],
    ['External API calls', safety.external_api_calls ? 'enabled' : 'disabled'],
    ['Backend/server', safety.backend_server ? 'enabled' : 'disabled'],
    ['Analytics', safety.analytics ? 'enabled' : 'disabled']
  ];
  checks.forEach(([label, value]) => {
    const pill = el('div', 'safety-pill');
    pill.appendChild(el('strong', '', label));
    pill.appendChild(el('span', '', value));
    grid.appendChild(pill);
  });
}

function renderBoundary(status) {
  const host = document.getElementById('boundary-list');
  clear(host);
  (status.safety_boundary || []).forEach((item) => {
    const row = el('div', 'boundary-item');
    row.appendChild(el('span', 'boundary-icon', 'Blocked'));
    row.appendChild(el('p', '', item));
    host.appendChild(row);
  });
}

function cardSearchText(card) {
  return [card.id, card.title, card.state, card.summary, ...(card.evidence || []), ...(card.actions || [])]
    .map(text)
    .join(' ')
    .toLowerCase();
}

function renderCards(cards) {
  const host = document.getElementById('cards');
  clear(host);
  const count = document.getElementById('filter-count');
  count.textContent = `${cards.length} of ${ALL_CARDS.length} cards shown`;
  if (!cards.length) {
    host.appendChild(el('p', 'empty-state', 'No cards match this filter. Clear the search to see all public-safe status cards.'));
    return;
  }
  cards.forEach((card) => {
    const article = el('article', '');
    article.dataset.search = cardSearchText(card);
    article.appendChild(el('span', 'card-state', card.state));
    article.appendChild(el('h3', '', card.title));
    article.appendChild(el('p', 'card-summary', card.summary));
    article.appendChild(el('h4', '', 'Evidence'));
    article.appendChild(list(card.evidence, 'evidence'));
    if (card.actions?.length) {
      article.appendChild(el('h4', '', 'Action'));
      article.appendChild(list(card.actions));
    }
    host.appendChild(article);
  });
}

function applyFilter() {
  const query = document.getElementById('card-search').value.trim().toLowerCase();
  if (!query) {
    renderCards(ALL_CARDS);
    return;
  }
  renderCards(ALL_CARDS.filter((card) => cardSearchText(card).includes(query)));
}

function renderBlocked(items) {
  const host = document.getElementById('blocked-items');
  clear(host);
  items.forEach((item) => {
    const row = el('div', 'blocked-item');
    row.appendChild(el('strong', '', item.action));
    row.appendChild(el('p', '', item.reason));
    row.appendChild(el('small', '', item.approval_required));
    host.appendChild(row);
  });
}

function renderOrdered(id, items, limit) {
  const host = document.getElementById(id);
  clear(host);
  (items || []).slice(0, limit || items.length).forEach((item) => host.appendChild(el('li', '', text(item))));
}

function render(status) {
  ACTIVE_STATUS = status;
  ALL_CARDS = status.cards || [];
  document.title = status.title || document.title;
  document.getElementById('version-label').textContent = status.version_label || status.schema_version || 'Static status';
  document.getElementById('last-updated').textContent = `Last updated: ${status.updated || 'unknown'}`;
  document.getElementById('updated').textContent = `Updated ${status.updated || 'unknown'}`;
  renderSystemStatus(status);
  renderOrdered('next-3-actions', status.next_actions || [], 3);
  renderBoundary(status);
  renderSafety(status.public_safety || {});
  renderCards(ALL_CARDS);
  renderBlocked(status.blocked_items || []);
  renderOrdered('next-actions', status.next_actions || []);
  renderOrdered('rollback-notes', status.rollback_notes || []);
  document.getElementById('card-search').addEventListener('input', applyFilter);
}

loadStatus().then(render).catch(renderLoadError);
