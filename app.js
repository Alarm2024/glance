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

  var LABELS = {
    online: 'Online',
    posture: 'Posture',
    doctor: 'Doctor',
    feeds: 'Feeds',
    last_signal: 'Last signal',
    build: 'Build'
  };

  var DEMO_LOAD_TIMEOUT_MS = 3000;
  var demoLoadTimeoutId = null;
  var activeCaseId = 'hold-stale-oracle';
  var loadedFixtures = {};
  var userPasted = false;

  var DEMO_FIXTURE = {
    synthetic: true,
    label: 'DEMO / SYNTHETIC — not live bot data',
    generated_at: '2026-09-20T20:00:00Z',
    online: {
      status: 'connected',
      uptime: '4h 12m',
      detail: 'Process heartbeat OK (demo fixture)'
    },
    posture: {
      mode: 'dry compose',
      detail: 'Eyes + dry compose · no auto-send'
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
      version: '0.1.0-demo',
      commit: 'fixture-hold-stale-oracle',
      detail: 'Pre-1.0 demo build'
    }
  };

  var DEMO_CASE_FILES = {
    'hold-stale-oracle': 'demo/fixture-hold-stale-oracle.json',
    'hold-queue': 'demo/fixture-hold-queue.json',
    clear: 'demo/fixture-clear.json'
  };

  var INLINE_FIXTURES = {
    'hold-stale-oracle': DEMO_FIXTURE,
    'hold-queue': {
      synthetic: true,
      label: 'DEMO / SYNTHETIC — not live bot data',
      generated_at: '2026-09-22T18:00:00Z',
      online: { status: 'connected', uptime: '2h 41m', detail: 'Process heartbeat OK (demo fixture)' },
      posture: { mode: 'dry compose', detail: 'Eyes + dry compose · no auto-send' },
      doctor: {
        status: 'warn',
        summary: 'Compose queue backlog · depth 12',
        detail: 'Dry compose paused — operator HOLD until queue drains'
      },
      feeds: [
        { name: 'slot-stream', state: 'ok', age: '1.0s' },
        { name: 'account-delta', state: 'ok', age: '0.7s' },
        { name: 'price-oracle', state: 'ok', age: '1.3s' }
      ],
      last_signal: { kind: 'heartbeat', ago: '19s', detail: 'Synthetic tick — no strategy payload' },
      build: { version: '0.1.0-demo', commit: 'fixture-hold-queue', detail: 'Pre-1.0 demo build' }
    },
    clear: {
      synthetic: true,
      label: 'DEMO / SYNTHETIC — not live bot data',
      generated_at: '2026-09-22T18:00:00Z',
      online: { status: 'connected', uptime: '6h 03m', detail: 'Process heartbeat OK (demo fixture)' },
      posture: { mode: 'dry compose', detail: 'Eyes + dry compose · no auto-send' },
      doctor: {
        status: 'ok',
        summary: 'No blocking flags, no active faults',
        detail: 'Hygiene checks passed · config exclusions applied'
      },
      feeds: [
        { name: 'slot-stream', state: 'ok', age: '0.9s' },
        { name: 'account-delta', state: 'ok', age: '0.6s' },
        { name: 'price-oracle', state: 'ok', age: '1.1s' }
      ],
      last_signal: { kind: 'heartbeat', ago: '8s', detail: 'Synthetic tick — no strategy payload' },
      build: { version: '0.1.0-demo', commit: 'fixture-clear', detail: 'Pre-1.0 demo build' }
    }
  };

  function t(key, fallback) {
    if (window.GlanceI18n && window.GlanceI18n.t) {
      var value = window.GlanceI18n.t(key);
      if (value && value !== key) return value;
    }
    return fallback;
  }

  function armDemoLoadTimeout(container) {
    if (demoLoadTimeoutId) clearTimeout(demoLoadTimeoutId);
    demoLoadTimeoutId = setTimeout(function () {
      if (!container || !container.classList.contains('cards--loading')) return;
      showRenderError(container, t('loadError', 'Demo fixture could not be loaded.'));
    }, DEMO_LOAD_TIMEOUT_MS);
  }

  function clearDemoLoadTimeout() {
    if (demoLoadTimeoutId) {
      clearTimeout(demoLoadTimeoutId);
      demoLoadTimeoutId = null;
    }
  }

  function showLoading(container) {
    container.className = 'cards cards--loading';
    container.textContent = t('loading', 'Loading demo fixture…');
    armDemoLoadTimeout(container);
  }

  function el(tag, className, text) {
    var node = document.createElement(tag);
    if (className) node.className = className;
    if (text != null) node.textContent = text;
    return node;
  }

  function badge(text, status) {
    return el('span', 'card__badge card__badge--' + (status || 'info'), text);
  }

  function detail(text) {
    return el('p', 'card__detail', text);
  }

  function renderOnline(data) {
    var card = el('article', 'card');
    var header = el('div', 'card__header');
    header.appendChild(el('span', 'card__name', LABELS.online));
    header.appendChild(badge(data.status || 'unknown', data.status === 'connected' ? 'ok' : 'unknown'));
    card.appendChild(header);
    if (data.uptime) card.appendChild(detail('Uptime · ' + data.uptime));
    if (data.detail) card.appendChild(detail(data.detail));
    return card;
  }

  function renderPosture(data) {
    var card = el('article', 'card');
    var header = el('div', 'card__header');
    header.appendChild(el('span', 'card__name', LABELS.posture));
    header.appendChild(badge(data.mode || 'unknown', 'info'));
    card.appendChild(header);
    if (data.detail) card.appendChild(detail(data.detail));
    return card;
  }

  function renderDoctor(data) {
    var card = el('article', 'card');
    var header = el('div', 'card__header');
    header.appendChild(el('span', 'card__name', LABELS.doctor));
    header.appendChild(badge(data.status || 'unknown', data.status || 'unknown'));
    card.appendChild(header);
    if (data.summary) card.appendChild(detail(data.summary));
    if (data.detail) card.appendChild(detail(data.detail));
    return card;
  }

  function renderFeeds(data) {
    var card = el('article', 'card');
    var header = el('div', 'card__header');
    header.appendChild(el('span', 'card__name', LABELS.feeds));
    var feeds = data || [];
    var okCount = 0;
    feeds.forEach(function (f) { if (f.state === 'ok') okCount++; });
    header.appendChild(badge(okCount + '/' + feeds.length + ' ok', okCount === feeds.length ? 'ok' : 'warn'));
    card.appendChild(header);

    var list = el('ul', 'feeds-list');
    feeds.forEach(function (feed) {
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
    header.appendChild(el('span', 'card__name', LABELS.last_signal));
    header.appendChild(badge(data.kind || 'signal', 'info'));
    card.appendChild(header);
    if (data.ago) card.appendChild(detail('Received ' + data.ago + ' ago'));
    if (data.detail) card.appendChild(detail(data.detail));
    return card;
  }

  function renderBuild(data) {
    var card = el('article', 'card');
    var header = el('div', 'card__header');
    header.appendChild(el('span', 'card__name', LABELS.build));
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

  /* Read-only cards — eyes-only display; never suggest CLEAR, send, arm, or mint. */
  function summarizeStatus(fixture) {
    if (!fixture || typeof fixture !== 'object') return '';
    var doctor = fixture.doctor || {};
    var doctorStatus = (doctor.status || '').toLowerCase();
    if (doctorStatus === 'blocking' || doctorStatus === 'eyes_fault') return 'FAULT';
    if (doctorStatus === 'warn') return 'DEGRADED';
    var online = fixture.online || {};
    var onlineStatus = (online.status || '').toLowerCase();
    if (onlineStatus && onlineStatus !== 'connected' && onlineStatus !== 'ok') return 'FAULT';
    var feeds = fixture.feeds || [];
    var degraded = false;
    for (var i = 0; i < feeds.length; i++) {
      var state = (feeds[i].state || '').toLowerCase();
      if (state === 'fault' || state === 'error' || state === 'down' || state === 'blocking') {
        return 'FAULT';
      }
      if (state === 'stale' || state === 'warn' || state === 'degraded' || state === 'unknown') {
        degraded = true;
      }
    }
    return degraded ? 'DEGRADED' : 'OK';
  }

  function updateSummaryLine(fixture, summaryEl) {
    if (!summaryEl) return;
    var line = summarizeStatus(fixture);
    if (!line) {
      summaryEl.hidden = true;
      summaryEl.textContent = '';
      return;
    }
    summaryEl.hidden = false;
    summaryEl.textContent = 'Summary · ' + line + ' (read-only · eyes-only)';
    summaryEl.className = 'status-summary status-summary--' + line.toLowerCase();
  }

  function updatePasteJson(fixture) {
    var pasteEl = document.getElementById('demo-paste-json');
    if (!pasteEl || !fixture) return;
    pasteEl.textContent = JSON.stringify(fixture, null, 2);
  }

  function showFixture(fixture, container, banner, summaryEl) {
    if (!container) return;
    clearDemoLoadTimeout();
    if (banner) {
      banner.textContent = fixture.label || 'DEMO / SYNTHETIC — not live bot data';
      banner.hidden = false;
      banner.setAttribute('data-synthetic', fixture.synthetic === false ? 'false' : 'true');
    }
    container.className = 'cards';
    try {
      renderCards(fixture, container);
      updateSummaryLine(fixture, summaryEl);
      if (!userPasted) updatePasteJson(fixture);
    } catch (err) {
      container.className = 'cards';
    }
    if (!container.querySelector('.card')) {
      renderCards(DEMO_FIXTURE, container);
      updateSummaryLine(DEMO_FIXTURE, summaryEl);
      if (!userPasted) updatePasteJson(DEMO_FIXTURE);
    }
  }

  function showRenderError(container, message) {
    container.className = 'cards cards--error';
    container.textContent = message;
  }

  function parsePlaygroundInput(raw) {
    var trimmed = (raw || '').trim();
    if (!trimmed) return { ok: true, fixture: null, empty: true };
    try {
      return { ok: true, fixture: JSON.parse(trimmed), empty: false };
    } catch (err) {
      return { ok: false, error: 'Invalid JSON — fix syntax or clear the field to use the demo fixture.' };
    }
  }

  function fetchWithTimeout(url, ms) {
    if (typeof AbortController === 'undefined') {
      return fetch(url, { cache: 'no-store' });
    }
    var controller = new AbortController();
    var timer = setTimeout(function () { controller.abort(); }, ms);
    return fetch(url, { cache: 'no-store', signal: controller.signal }).finally(function () {
      clearTimeout(timer);
    });
  }

  function fetchJson(paths) {
    var attempt = function (index) {
      if (index >= paths.length) {
        return Promise.reject(new Error('all paths failed'));
      }
      return fetchWithTimeout(paths[index], 4000).then(function (res) {
        if (!res.ok) throw new Error('Fixture unavailable');
        return res.json();
      }).catch(function () {
        return attempt(index + 1);
      });
    };
    return attempt(0);
  }

  function fixturePaths(relativePath) {
    return ['/' + relativePath, './' + relativePath, relativePath];
  }

  function loadCaseFixture(caseId) {
    if (loadedFixtures[caseId]) {
      return Promise.resolve(loadedFixtures[caseId]);
    }
    var relative = DEMO_CASE_FILES[caseId];
    if (!relative) {
      return Promise.reject(new Error('unknown case'));
    }
    return fetchJson(fixturePaths(relative)).then(function (fixture) {
      loadedFixtures[caseId] = fixture;
      return fixture;
    }).catch(function () {
      if (INLINE_FIXTURES[caseId]) {
        loadedFixtures[caseId] = INLINE_FIXTURES[caseId];
        return INLINE_FIXTURES[caseId];
      }
      return Promise.reject(new Error('case load failed'));
    });
  }

  function setActiveCaseTab(caseId) {
    document.querySelectorAll('.demo-case').forEach(function (btn) {
      var on = btn.getAttribute('data-case') === caseId;
      btn.classList.toggle('on', on);
      btn.setAttribute('aria-selected', on ? 'true' : 'false');
    });
  }

  function applyCase(caseId, container, banner, summaryEl, textarea) {
    activeCaseId = caseId;
    setActiveCaseTab(caseId);
    userPasted = false;
    if (textarea) textarea.value = '';
    return loadCaseFixture(caseId).then(function (fixture) {
      showFixture(fixture, container, banner, summaryEl);
      if (textarea) textarea.placeholder = JSON.stringify(fixture, null, 2);
    });
  }

  function initDemo() {
    var container = document.getElementById('cards');
    var banner = document.getElementById('synthetic-banner');
    var summaryEl = document.getElementById('status-summary');
    var textarea = document.getElementById('playground-input');
    var caseButtons = document.querySelectorAll('.demo-case');
    if (!container) return;

    function isPlaygroundEmpty() {
      return !textarea || !textarea.value.trim();
    }

    function applyFromPlayground() {
      if (isPlaygroundEmpty()) {
        userPasted = false;
        applyCase(activeCaseId, container, banner, summaryEl, null);
        return;
      }
      var result = parsePlaygroundInput(textarea.value);
      if (result.ok && result.fixture) {
        userPasted = true;
        showFixture(result.fixture, container, banner, summaryEl);
      } else if (!result.ok) {
        showRenderError(container, result.error);
        if (banner) banner.hidden = true;
        updateSummaryLine(null, summaryEl);
      }
    }

    if (!container.querySelector('.card')) {
      showLoading(container);
    } else {
      armDemoLoadTimeout(container);
    }

    showFixture(DEMO_FIXTURE, container, banner, summaryEl);

    caseButtons.forEach(function (btn) {
      btn.addEventListener('click', function () {
        var caseId = btn.getAttribute('data-case');
        if (!caseId || userPasted && textarea && textarea.value.trim()) return;
        applyCase(caseId, container, banner, summaryEl, textarea);
      });
    });

    if (textarea) {
      textarea.value = '';
      textarea.placeholder = JSON.stringify(DEMO_FIXTURE, null, 2);
      var debounceTimer;
      textarea.addEventListener('input', function () {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(applyFromPlayground, 200);
      });
    }

    Object.keys(DEMO_CASE_FILES).forEach(function (caseId) {
      loadCaseFixture(caseId).catch(function () { /* inline fallback */ });
    });

    fetchJson(fixturePaths('demo/fixture.json'))
      .then(function (fixture) {
        loadedFixtures['hold-stale-oracle'] = loadedFixtures['hold-stale-oracle'] || fixture;
        if (isPlaygroundEmpty() && activeCaseId === 'hold-stale-oracle') {
          showFixture(fixture, container, banner, summaryEl);
        }
      })
      .catch(function () {
        if (container.classList.contains('cards--loading')) {
          showFixture(DEMO_FIXTURE, container, banner, summaryEl);
        }
      });
  }

  function scrollToHashIfRequested() {
    if (!location.hash) return;
    var target = document.querySelector(location.hash);
    if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  function mount() {
    initDemo();
    scrollToHashIfRequested();
    window.addEventListener('hashchange', scrollToHashIfRequested);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', mount);
  } else {
    mount();
  }
})();
