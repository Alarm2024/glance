(function () {
  'use strict';

  var CARD_ORDER = [
    'online',
    'posture',
    'doctor',
    'feeds',
    'last_signal',
    'build'
  ];

  var CARD_LABELS = {
    online: 'Online',
    posture: 'Posture',
    doctor: 'Doctor',
    feeds: 'Feeds',
    last_signal: 'Last signal',
    build: 'Build'
  };

  /** Synthetic demo fixture — same data as demo/fixture.json, inlined for instant render. */
  var DEFAULT_FIXTURE = {
    synthetic: true,
    label: 'DEMO / SYNTHETIC — not live bot data',
    generated_at: '2026-09-20T20:00:00Z',
    online: {
      status: 'connected',
      uptime: '4h 12m',
      detail: 'Process heartbeat OK (demo fixture)'
    },
    posture: {
      mode: 'observe-only',
      detail: 'No live-send path armed — monitoring posture'
    },
    doctor: {
      status: 'ok',
      summary: 'No blocking flags, no active faults',
      detail: 'Hygiene checks passed · config exclusions applied'
    },
    feeds: [
      { name: 'slot-stream', state: 'ok', age: '1.2s' },
      { name: 'account-delta', state: 'ok', age: '0.8s' },
      { name: 'price-oracle', state: 'stale', age: '47s' }
    ],
    last_signal: {
      kind: 'heartbeat',
      ago: '12s',
      detail: 'Synthetic tick — no strategy payload'
    },
    build: {
      version: '0.0.0-demo',
      commit: 'fixture',
      detail: 'Pre-1.0 grant demo build'
    }
  };

  function el(tag, className, text) {
    var node = document.createElement(tag);
    if (className) node.className = className;
    if (text != null) node.textContent = text;
    return node;
  }

  function badge(text, status) {
    var b = el('span', 'card__badge card__badge--' + (status || 'info'), text);
    return b;
  }

  function detail(text) {
    return el('p', 'card__detail', text);
  }

  function renderOnline(data) {
    var card = el('article', 'card');
    var header = el('div', 'card__header');
    header.appendChild(el('span', 'card__name', CARD_LABELS.online));
    header.appendChild(badge(data.status || 'unknown', data.status === 'connected' ? 'ok' : 'unknown'));
    card.appendChild(header);
    if (data.uptime) card.appendChild(detail('Uptime · ' + data.uptime));
    if (data.detail) card.appendChild(detail(data.detail));
    return card;
  }

  function renderPosture(data) {
    var card = el('article', 'card');
    var header = el('div', 'card__header');
    header.appendChild(el('span', 'card__name', CARD_LABELS.posture));
    header.appendChild(badge(data.mode || 'unknown', 'info'));
    card.appendChild(header);
    if (data.detail) card.appendChild(detail(data.detail));
    return card;
  }

  function renderDoctor(data) {
    var card = el('article', 'card');
    var header = el('div', 'card__header');
    header.appendChild(el('span', 'card__name', CARD_LABELS.doctor));
    header.appendChild(badge(data.status || 'unknown', data.status || 'unknown'));
    card.appendChild(header);
    if (data.summary) card.appendChild(detail(data.summary));
    if (data.detail) card.appendChild(detail(data.detail));
    return card;
  }

  function renderFeeds(data) {
    var card = el('article', 'card');
    var header = el('div', 'card__header');
    header.appendChild(el('span', 'card__name', CARD_LABELS.feeds));
    var okCount = 0;
    (data || []).forEach(function (f) { if (f.state === 'ok') okCount++; });
    header.appendChild(badge(okCount + '/' + (data || []).length + ' live', okCount === (data || []).length ? 'ok' : 'warn'));
    card.appendChild(header);

    var list = el('ul', 'feeds-list');
    (data || []).forEach(function (feed) {
      var li = el('li');
      li.appendChild(el('span', 'feeds-list__name', feed.name));
      var state = el('span', 'feeds-list__state feeds-list__state--' + (feed.state || 'unknown'));
      state.textContent = (feed.state || 'unknown') + (feed.age ? ' · ' + feed.age : '');
      li.appendChild(state);
      list.appendChild(li);
    });
    card.appendChild(list);
    return card;
  }

  function renderLastSignal(data) {
    var card = el('article', 'card');
    var header = el('div', 'card__header');
    header.appendChild(el('span', 'card__name', CARD_LABELS.last_signal));
    header.appendChild(badge(data.kind || 'signal', 'info'));
    card.appendChild(header);
    if (data.ago) card.appendChild(detail('Received ' + data.ago + ' ago'));
    if (data.detail) card.appendChild(detail(data.detail));
    return card;
  }

  function renderBuild(data) {
    var card = el('article', 'card');
    var header = el('div', 'card__header');
    header.appendChild(el('span', 'card__name', CARD_LABELS.build));
    header.appendChild(badge(data.version || 'unknown', 'info'));
    card.appendChild(header);
    if (data.commit) card.appendChild(detail('Commit · ' + data.commit));
    if (data.detail) card.appendChild(detail(data.detail));
    return card;
  }

  var RENDERERS = {
    online: renderOnline,
    posture: renderPosture,
    doctor: renderDoctor,
    feeds: renderFeeds,
    last_signal: renderLastSignal,
    build: renderBuild
  };

  function renderCards(fixture, container) {
    container.innerHTML = '';
    CARD_ORDER.forEach(function (key) {
      var data = fixture[key];
      if (data == null) return;
      var renderer = RENDERERS[key];
      if (renderer) container.appendChild(renderer(data));
    });
  }

  function updateBanner(banner, fixture) {
    if (!banner) return;
    if (fixture.label) {
      banner.textContent = fixture.label;
      banner.hidden = false;
    } else if (fixture.synthetic) {
      banner.textContent = 'DEMO / SYNTHETIC — not live bot data';
      banner.hidden = false;
    } else {
      banner.hidden = true;
    }
  }

  function showRenderError(container, message) {
    container.className = 'cards cards--error';
    container.textContent = message;
  }

  function applyFixture(fixture, container, banner) {
    container.className = 'cards';
    updateBanner(banner, fixture);
    renderCards(fixture, container);
  }

  function parsePlaygroundInput(raw) {
    var trimmed = (raw || '').trim();
    if (!trimmed) return { ok: true, fixture: DEFAULT_FIXTURE };
    try {
      return { ok: true, fixture: JSON.parse(trimmed) };
    } catch (err) {
      return { ok: false, error: 'Invalid JSON — fix syntax or clear the field to use the demo fixture.' };
    }
  }

  function init() {
    var container = document.getElementById('cards');
    var banner = document.getElementById('synthetic-banner');
    var textarea = document.getElementById('playground-input');
    if (!container) return;

    applyFixture(DEFAULT_FIXTURE, container, banner);

    if (!textarea) return;

    textarea.value = '';
    textarea.placeholder = JSON.stringify(DEFAULT_FIXTURE, null, 2);

    var debounceTimer;
    textarea.addEventListener('input', function () {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(function () {
        var result = parsePlaygroundInput(textarea.value);
        if (result.ok) {
          applyFixture(result.fixture, container, banner);
        } else {
          showRenderError(container, result.error);
          if (banner) banner.hidden = true;
        }
      }, 200);
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
