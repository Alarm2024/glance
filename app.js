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
      version: '0.1.0-demo',
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
    header.appendChild(badge(okCount + '/' + feeds.length + ' live', okCount === feeds.length ? 'ok' : 'warn'));
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

  function showFixture(fixture, container, banner) {
    if (!container) return;
    if (banner) {
      banner.textContent = fixture.label || 'DEMO / SYNTHETIC — not live bot data';
      banner.hidden = false;
    }
    container.className = 'cards';
    try {
      renderCards(fixture, container);
    } catch (err) {
      /* keep any existing static HTML cards; never leave cards--loading */
      container.className = 'cards';
    }
    if (!container.querySelector('.card')) {
      renderCards(DEMO_FIXTURE, container);
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

  function fetchFixture() {
    var paths = ['/demo/fixture.json', './demo/fixture.json', 'demo/fixture.json'];
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

  function initDemo() {
    var container = document.getElementById('cards');
    var banner = document.getElementById('synthetic-banner');
    if (!container) return;

    /* Always paint inline fixture first — never leave cards--loading */
    showFixture(DEMO_FIXTURE, container, banner);

    fetchFixture()
      .then(function (fixture) {
        showFixture(fixture, container, banner);
      })
      .catch(function () {
        /* static HTML / DEMO_FIXTURE already rendered */
        if (container.classList.contains('cards--loading')) {
          showFixture(DEMO_FIXTURE, container, banner);
        }
      });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initDemo);
  } else {
    initDemo();
  }
})();
