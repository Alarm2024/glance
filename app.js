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

  function init() {
    var container = document.getElementById('cards');
    var banner = document.getElementById('synthetic-banner');
    if (!container) return;

    container.className = 'cards cards--loading';
    container.textContent = 'Loading demo fixture…';

    fetch('demo/fixture.json')
      .then(function (res) {
        if (!res.ok) throw new Error('Fixture unavailable');
        return res.json();
      })
      .then(function (fixture) {
        if (banner && fixture.label) {
          banner.textContent = fixture.label;
          banner.hidden = false;
        }
        container.className = 'cards';
        renderCards(fixture, container);
      })
      .catch(function () {
        container.className = 'cards cards--error';
        container.textContent = 'Demo fixture could not be loaded.';
      });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
