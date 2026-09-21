(function () {
  'use strict';

  var KEY = 'glance-lang';

  var STRINGS = {
    en: {
      title: 'Glance',
      tag: 'Honest status for Solana bots',
      what: 'Fault-first doctor status, redaction, and anti-overclaim tests — open-source observability for Solana operators. Not a trading bot.',
      sectionWhat: 'What',
      sectionDemo: 'Demo',
      sectionInstall: 'Install',
      sectionLicense: 'License',
      installNote: 'Published on crates.io and PyPI · MIT · synthetic demo data only',
      licenseLine: 'MIT · free forever · no paid tier · synthetic demo data only',
      contact: 'Contact',
      footer: 'Glance · MIT',
      loading: 'Loading demo fixture…',
      loadError: 'Demo fixture could not be loaded.',
      syntheticFallback: 'DEMO / SYNTHETIC — not live bot data',
      cardOnline: 'Online',
      cardPosture: 'Posture',
      cardDoctor: 'Doctor',
      cardFeeds: 'Feeds',
      cardLastSignal: 'Last signal',
      cardBuild: 'Build',
      uptime: 'Uptime',
      received: 'Received',
      ago: 'ago',
      commit: 'Commit',
      live: 'live'
    },
    ar: {
      title: 'غلانس',
      tag: 'حالة صادقة لبوتات سولانا',
      what: 'تصنيف الأعطال أولاً، إخفاء البيانات الحساسة، واختبارات منع المبالغة — أدوات مراقبة مفتوحة المصدر لمشغّلي سولانا. ليس بوت تداول.',
      sectionWhat: 'ما هو',
      sectionDemo: 'عرض',
      sectionInstall: 'تثبيت',
      sectionLicense: 'الترخيص',
      installNote: 'منشور على crates.io و PyPI · MIT · بيانات تجريبية فقط',
      licenseLine: 'MIT · مجاني للأبد · بيانات تجريبية اصطناعية فقط',
      contact: 'تواصل',
      footer: 'Glance · MIT',
      loading: 'جاري تحميل العرض التجريبي…',
      loadError: 'تعذّر تحميل العرض التجريبي.',
      syntheticFallback: 'عرض تجريبي / اصطناعي — ليست بيانات بوت حية',
      cardOnline: 'متصل',
      cardPosture: 'الوضع',
      cardDoctor: 'الفحص',
      cardFeeds: 'التغذيات',
      cardLastSignal: 'آخر إشارة',
      cardBuild: 'البناء',
      uptime: 'وقت التشغيل',
      received: 'استُلم',
      ago: 'منذ',
      commit: 'الالتزام',
      live: 'نشط'
    },
    ru: {
      title: 'Glance',
      tag: 'Честный статус для Solana-ботов',
      what: 'Приоритет блокирующих сбоев, редактирование секретов и тесты против преувеличений — open-source наблюдаемость для операторов Solana. Не торговый бот.',
      sectionWhat: 'О проекте',
      sectionDemo: 'Демо',
      sectionInstall: 'Установка',
      sectionLicense: 'Лицензия',
      installNote: 'Опубликовано на crates.io и PyPI · MIT · только синтетические демо-данные',
      licenseLine: 'MIT · бесплатно · только синтетические демо-данные',
      contact: 'Контакт',
      footer: 'Glance · MIT',
      loading: 'Загрузка демо-фикстуры…',
      loadError: 'Не удалось загрузить демо-фикстуру.',
      syntheticFallback: 'ДЕМО / СИНТЕТИКА — не данные живого бота',
      cardOnline: 'Онлайн',
      cardPosture: 'Режим',
      cardDoctor: 'Диагностика',
      cardFeeds: 'Потоки',
      cardLastSignal: 'Последний сигнал',
      cardBuild: 'Сборка',
      uptime: 'Аптайм',
      received: 'Получено',
      ago: 'назад',
      commit: 'Коммит',
      live: 'активно'
    },
    zh: {
      title: 'Glance',
      tag: 'Solana 机器人的诚实状态',
      what: '故障优先诊断、敏感信息脱敏与反夸大测试 — 面向 Solana 运维的开源可观测性工具。不是交易机器人。',
      sectionWhat: '简介',
      sectionDemo: '演示',
      sectionInstall: '安装',
      sectionLicense: '许可',
      installNote: '已发布至 crates.io 和 PyPI · MIT · 仅合成演示数据',
      licenseLine: 'MIT · 永久免费 · 仅合成演示数据',
      contact: '联系',
      footer: 'Glance · MIT',
      loading: '正在加载演示数据…',
      loadError: '无法加载演示数据。',
      syntheticFallback: '演示 / 合成 — 非实时机器人数据',
      cardOnline: '在线',
      cardPosture: '姿态',
      cardDoctor: '诊断',
      cardFeeds: '数据源',
      cardLastSignal: '最近信号',
      cardBuild: '构建',
      uptime: '运行时间',
      received: '收到于',
      ago: '前',
      commit: '提交',
      live: '正常'
    },
    de: {
      title: 'Glance',
      tag: 'Ehrlicher Status für Solana-Bots',
      what: 'Fehler-zuerst-Diagnose, Schwärzung und Anti-Overclaim-Tests — Open-Source-Observability für Solana-Betreiber. Kein Trading-Bot.',
      sectionWhat: 'Was',
      sectionDemo: 'Demo',
      sectionInstall: 'Installation',
      sectionLicense: 'Lizenz',
      installNote: 'Veröffentlicht auf crates.io und PyPI · MIT · nur synthetische Demo-Daten',
      licenseLine: 'MIT · dauerhaft kostenlos · nur synthetische Demo-Daten',
      contact: 'Kontakt',
      footer: 'Glance · MIT',
      loading: 'Demo-Fixture wird geladen…',
      loadError: 'Demo-Fixture konnte nicht geladen werden.',
      syntheticFallback: 'DEMO / SYNTHETISCH — keine Live-Bot-Daten',
      cardOnline: 'Online',
      cardPosture: 'Haltung',
      cardDoctor: 'Diagnose',
      cardFeeds: 'Feeds',
      cardLastSignal: 'Letztes Signal',
      cardBuild: 'Build',
      uptime: 'Laufzeit',
      received: 'Empfangen',
      ago: 'her',
      commit: 'Commit',
      live: 'live'
    },
    es: {
      title: 'Glance',
      tag: 'Estado honesto para bots de Solana',
      what: 'Diagnóstico con fallos primero, redacción y pruebas anti-exageración — observabilidad open source para operadores de Solana. No es un bot de trading.',
      sectionWhat: 'Qué es',
      sectionDemo: 'Demo',
      sectionInstall: 'Instalar',
      sectionLicense: 'Licencia',
      installNote: 'Publicado en crates.io y PyPI · MIT · solo datos de demostración sintéticos',
      licenseLine: 'MIT · gratis para siempre · solo datos demo sintéticos',
      contact: 'Contacto',
      footer: 'Glance · MIT',
      loading: 'Cargando fixture de demo…',
      loadError: 'No se pudo cargar el fixture de demo.',
      syntheticFallback: 'DEMO / SINTÉTICO — no son datos de bot en vivo',
      cardOnline: 'En línea',
      cardPosture: 'Postura',
      cardDoctor: 'Diagnóstico',
      cardFeeds: 'Feeds',
      cardLastSignal: 'Última señal',
      cardBuild: 'Build',
      uptime: 'Tiempo activo',
      received: 'Recibido',
      ago: 'hace',
      commit: 'Commit',
      live: 'activo'
    }
  };

  var currentLang = 'en';

  function t(key) {
    var pack = STRINGS[currentLang] || STRINGS.en;
    return pack[key] || STRINGS.en[key] || key;
  }

  function applyDom() {
    document.querySelectorAll('[data-i18n]').forEach(function (node) {
      var key = node.getAttribute('data-i18n');
      if (key) node.textContent = t(key);
    });
    document.documentElement.lang = currentLang;
    document.documentElement.dir = currentLang === 'ar' ? 'rtl' : 'ltr';
    document.querySelectorAll('.lang-btn').forEach(function (btn) {
      btn.classList.toggle('on', btn.getAttribute('data-lang') === currentLang);
    });
    document.dispatchEvent(new CustomEvent('glance:lang', { detail: { lang: currentLang } }));
  }

  function setLang(lang) {
    if (!STRINGS[lang]) return;
    currentLang = lang;
    try { localStorage.setItem(KEY, lang); } catch (e) { /* ignore */ }
    applyDom();
  }

  function mount() {
    var host = document.getElementById('langs');
    if (!host) return;
    host.addEventListener('click', function (e) {
      var btn = e.target.closest('[data-lang]');
      if (!btn) return;
      setLang(btn.getAttribute('data-lang'));
    });
    try { currentLang = localStorage.getItem(KEY) || 'en'; } catch (e) { /* ignore */ }
    if (!STRINGS[currentLang]) currentLang = 'en';
    applyDom();
  }

  window.GlanceI18n = { t: t, setLang: setLang, getLang: function () { return currentLang; } };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', mount);
  } else {
    mount();
  }
})();
