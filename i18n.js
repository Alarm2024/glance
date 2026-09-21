(function () {
  'use strict';

  var KEY = 'glance-lang';

  var STRINGS = {
    en: {
      title: 'Glance',
      tag: 'Honest status for Solana bots',
      what: 'Fault-first doctor status, redaction, and anti-overclaim tests — open-source observability for Solana bot operators. Not a trading bot. Distinct from validator dashboards such as Solana Validator Mission Control.',
      sectionWhat: 'What',
      sectionDemo: 'Demo',
      sectionInstall: 'Install',
      sectionLicense: 'License',
      sectionContact: 'Contact',
      playgroundHint: 'Live playground — paste your own status JSON below, or leave empty for the synthetic fixture. Renders client-side only.',
      statusJsonLabel: 'Status JSON',
      rustLabel: 'Rust · pre-1.0',
      pythonLabel: 'Python · pre-1.0',
      installNote: 'Pre-1.0 local install. crates.io / PyPI publish is a grant milestone · MIT · synthetic demo data only',
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
      what: 'تصنيف الأعطال أولاً، إخفاء البيانات الحساسة، واختبارات منع المبالغة — أدوات مراقبة مفتوحة المصدر لمشغّلي بوتات سولانا. ليس بوت تداول. يختلف عن لوحات المدققين مثل Solana Validator Mission Control.',
      sectionWhat: 'ما هو',
      sectionDemo: 'عرض',
      sectionInstall: 'تثبيت',
      sectionLicense: 'الترخيص',
      sectionContact: 'تواصل',
      playgroundHint: 'ساحة تجريبية — الصق JSON الحالة أدناه، أو اتركه فارغاً للعرض الاصطناعي. يعرض محلياً فقط.',
      statusJsonLabel: 'JSON الحالة',
      rustLabel: 'Rust · ما قبل 1.0',
      pythonLabel: 'Python · ما قبل 1.0',
      installNote: 'تثبيت محلي ما قبل 1.0. النشر على crates.io و PyPI من أهداف المنحة · MIT · بيانات تجريبية فقط',
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
      what: 'Приоритет блокирующих сбоев, редактирование секретов и тесты против преувеличений — open-source наблюдаемость для операторов Solana-ботов. Не торговый бот. Отличается от дашбордов валидаторов, например Solana Validator Mission Control.',
      sectionWhat: 'О проекте',
      sectionDemo: 'Демо',
      sectionInstall: 'Установка',
      sectionLicense: 'Лицензия',
      sectionContact: 'Контакт',
      playgroundHint: 'Живая площадка — вставьте JSON статуса ниже или оставьте пустым для синтетической фикстуры. Только на клиенте.',
      statusJsonLabel: 'JSON статуса',
      rustLabel: 'Rust · до 1.0',
      pythonLabel: 'Python · до 1.0',
      installNote: 'Локальная установка до 1.0. Публикация на crates.io / PyPI — этап гранта · MIT · только синтетические демо-данные',
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
      what: '故障优先诊断、敏感信息脱敏与反夸大测试 — 面向 Solana 机器人运维的开源可观测性工具。不是交易机器人。与 Solana Validator Mission Control 等验证者仪表盘不同。',
      sectionWhat: '简介',
      sectionDemo: '演示',
      sectionInstall: '安装',
      sectionLicense: '许可',
      sectionContact: '联系',
      playgroundHint: '实时演示区 — 在下方粘贴状态 JSON，或留空使用合成示例。仅客户端渲染。',
      statusJsonLabel: '状态 JSON',
      rustLabel: 'Rust · 1.0 前',
      pythonLabel: 'Python · 1.0 前',
      installNote: '1.0 前本地安装。发布到 crates.io / PyPI 是资助里程碑 · MIT · 仅合成演示数据',
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
      what: 'Fehler-zuerst-Diagnose, Schwärzung und Anti-Overclaim-Tests — Open-Source-Observability für Solana-Bot-Betreiber. Kein Trading-Bot. Unterscheidet sich von Validator-Dashboards wie Solana Validator Mission Control.',
      sectionWhat: 'Was',
      sectionDemo: 'Demo',
      sectionInstall: 'Installation',
      sectionLicense: 'Lizenz',
      sectionContact: 'Kontakt',
      playgroundHint: 'Live-Spielwiese — fügen Sie unten Status-JSON ein oder lassen Sie das Feld leer für die synthetische Fixture. Nur clientseitig.',
      statusJsonLabel: 'Status-JSON',
      rustLabel: 'Rust · Pre-1.0',
      pythonLabel: 'Python · Pre-1.0',
      installNote: 'Pre-1.0 lokale Installation. Veröffentlichung auf crates.io / PyPI ist ein Grant-Meilenstein · MIT · nur synthetische Demo-Daten',
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
      what: 'Diagnóstico con fallos primero, redacción y pruebas anti-exageración — observabilidad open source para operadores de bots de Solana. No es un bot de trading. Distinto de paneles de validadores como Solana Validator Mission Control.',
      sectionWhat: 'Qué es',
      sectionDemo: 'Demo',
      sectionInstall: 'Instalar',
      sectionLicense: 'Licencia',
      sectionContact: 'Contacto',
      playgroundHint: 'Zona de prueba — pegue su JSON de estado abajo o déjelo vacío para la fixture sintética. Solo en el cliente.',
      statusJsonLabel: 'JSON de estado',
      rustLabel: 'Rust · pre-1.0',
      pythonLabel: 'Python · pre-1.0',
      installNote: 'Instalación local pre-1.0. Publicar en crates.io / PyPI es un hito de la subvención · MIT · solo datos de demostración sintéticos',
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
