(function () {
  'use strict';

  var KEY = 'glance-theme';
  var THEMES = {
    midnight: { bg: '#0b1214', ink: '#e8fbf6', dim: '#9ab3ad', accent: '#2ee6c7', card: '#121a19', line: 'rgba(46,230,199,.22)', dot: '#2ee6c7' },
    dawn: { bg: '#f4f1ea', ink: '#1a1814', dim: '#5c574e', accent: '#0f766e', card: '#fffaf3', line: 'rgba(15,118,110,.22)', dot: '#e8efe8' },
    nord: { bg: '#2e3440', ink: '#eceff4', dim: '#88c0d0', accent: '#88c0d0', card: '#3b4252', line: 'rgba(136,192,208,.28)', dot: '#88c0d0' },
    solarized: { bg: '#002b36', ink: '#eee8d5', dim: '#93a1a1', accent: '#b58900', card: '#073642', line: 'rgba(181,137,0,.28)', dot: '#b58900' },
    dracula: { bg: '#282a36', ink: '#f8f8f2', dim: '#bd93f9', accent: '#50fa7b', card: '#21222c', line: 'rgba(80,250,123,.28)', dot: '#bd93f9' },
    ocean: { bg: '#0b1c24', ink: '#d8f3ff', dim: '#7fadb8', accent: '#2ec4b6', card: '#12262e', line: 'rgba(46,196,182,.28)', dot: '#2ec4b6' }
  };
  var LABELS = { midnight: 'Midnight', dawn: 'Dawn', nord: 'Nord', solarized: 'Solarized', dracula: 'Dracula', ocean: 'Ocean' };
  var ORDER = ['midnight', 'dawn', 'nord', 'solarized', 'dracula', 'ocean'];

  function apply(name) {
    if (!(name in THEMES)) name = 'midnight';
    var t = THEMES[name];
    var root = document.documentElement;
    root.setAttribute('data-theme', name);
    root.style.setProperty('--bg', t.bg);
    root.style.setProperty('--ink', t.bg);
    root.style.setProperty('--text', t.ink);
    root.style.setProperty('--text-muted', t.dim);
    root.style.setProperty('--gold', t.accent);
    root.style.setProperty('--gold-warm', t.accent);
    root.style.setProperty('--gold-dim', t.line);
    root.style.setProperty('--ink-soft', t.card);
    root.style.setProperty('--ink-muted', t.card);
    root.style.setProperty('--accent', t.accent);
    root.style.setProperty('--muted', t.dim);
    root.style.setProperty('--surface', t.card);
    root.style.setProperty('--line', t.line);
    if (document.body) {
      document.body.style.background = t.bg;
      document.body.style.color = t.ink;
    }
    var bar = document.querySelector('.topbar');
    if (bar) bar.style.background = t.bg;
    try { localStorage.setItem(KEY, name); } catch (e) { /* ignore */ }
    document.querySelectorAll('[data-theme-item]').forEach(function (el) {
      el.classList.toggle('on', el.getAttribute('data-theme-item') === name);
    });
    var cur = document.getElementById('themeCur');
    if (cur) cur.textContent = LABELS[name];
  }

  function mount() {
    if (document.getElementById('themeMenu')) return;
    var wrap = document.createElement('div');
    wrap.className = 'theme-wrap';
    wrap.id = 'themeMenu';
    wrap.innerHTML = '<button type="button" class="theme-btn" id="themeOpen" aria-haspopup="listbox" aria-expanded="false"><i class="theme-dot"></i><span id="themeCur">Midnight</span></button>';
    var panel = document.createElement('div');
    panel.className = 'theme-panel';
    panel.setAttribute('role', 'listbox');
    panel.innerHTML = '<p>Choose theme</p>';
    ORDER.forEach(function (key) {
      var btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'theme-item';
      btn.setAttribute('data-theme-item', key);
      btn.setAttribute('role', 'option');
      btn.innerHTML = '<i style="background:' + THEMES[key].dot + '"></i><span>' + LABELS[key] + '</span><span class="ck">\u2713</span>';
      btn.onclick = function () {
        apply(key);
        wrap.classList.remove('open');
        document.getElementById('themeOpen').setAttribute('aria-expanded', 'false');
      };
      panel.appendChild(btn);
    });
    wrap.appendChild(panel);
    var host = document.querySelector('.header-right') || document.querySelector('.topbar');
    if (host) host.appendChild(wrap);
    var openBtn = document.getElementById('themeOpen');
    if (openBtn) {
      openBtn.onclick = function (e) {
        e.stopPropagation();
        var open = wrap.classList.toggle('open');
        openBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
      };
    }
    document.addEventListener('click', function () {
      wrap.classList.remove('open');
      if (openBtn) openBtn.setAttribute('aria-expanded', 'false');
    });
  }

  var start = 'midnight';
  try { start = localStorage.getItem(KEY) || 'midnight'; } catch (e) { /* ignore */ }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () { mount(); apply(start); });
  } else {
    mount();
    apply(start);
  }
})();
