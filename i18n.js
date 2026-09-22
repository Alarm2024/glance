(function () {
  'use strict';

  var KEY = 'glance-lang';

  var STRINGS = {
    en: {
      title: 'Glance',
      tag: 'Honest status for Solana bots',
      eyebrow: 'Open source · Developer tooling',
      statusStrip: 'Eyes + dry compose · no auto-send',
      tryDemo: 'Try demo',
      tryQuickstart: 'Quickstart',
      sectionWhatYouGet: 'What you get',
      bulletEyes: 'Glance <a href="#vocab-eyes">eyes</a> — fault-first health cards',
      bulletDry: 'Dry simulate — compose without sending',
      bulletClear: 'Operator <a href="#vocab-clear">CLEAR</a> only — human gate, no auto-send',
      sectionVocab: 'Vocabulary',
      vocabIntro: 'Defined once here — every other mention links back.',
      vocabEyesTerm: 'Eyes',
      vocabEyesDef: 'Read-only status cards. Fault-first health display — never suggests send, arm, or mint. Summary lines are marked (read-only · eyes-only).',
      vocabDoctorTerm: 'Doctor',
      vocabDoctorDef: 'Fault-first classifier for operator messages. Status values: ok, warn, eyes_fault, blocking, unknown. Order: blocking flag → hygiene phrases → fault phrases → unknown.',
      vocabPostureTerm: 'Posture',
      vocabPostureDef: 'How your tooling composes transactions. Allowed modes: dry compose, dry simulate, observe-only. Must not imply auto-send, live send, or mint.',
      vocabClearTerm: 'CLEAR',
      vocabClearDef: 'Operator CLEAR only — a human operator must explicitly CLEAR before anything sends. Glance observes and composes dry; it never auto-sends. The refusal is the product.',
      sectionQuickstart: 'Quickstart',
      quickstartIntro: 'Clone the public repo, run the shipped checks, then compare with the synthetic demo below. No sign-in required.',
      qs1Title: '1 · Clone the repo',
      qs1Check: 'You should see a <code>glance/</code> directory containing <code>lib/</code>, <code>demo/</code>, and <code>examples/</code>.',
      qs2Title: '2 · Run posture self-test (dry / eyes-only guard)',
      qs2Check: 'You should see: <code>posture-selftest passed — dry compose / eyes-only across fixture + page sources</code>',
      qs3Title: '3 · Run the library demo CLI',
      qs3Check: 'You should see a line starting with <code>demo ok · status=warn</code> and a redacted URL (no raw token).',
      qs4Title: '4 · Summarize a synthetic fixture',
      qs4Check: 'You should see <code>DEGRADED</code> then <code>OK</code> — two different judgements from two synthetic files.',
      qs5Title: '5 · Match the site demo',
      qs5Hint: 'Scroll to <a href="#demo">Demo</a>, pick a synthetic case tab, or paste the JSON into the playground.',
      qs5Check: 'You should see the same Summary line and six cards as the case label describes — client-side only, not live bot data.',
      quickstartGuide: 'Full integration guide in the repo →',
      caseHoldOracle: 'HOLD · stale oracle',
      caseHoldQueue: 'HOLD · queue backlog',
      caseClear: 'CLEAR · all feeds ok',
      demoPasteToggle: 'Paste-ready JSON for this case',
      sectionTrust: 'Trust',
      trustCanTitle: 'Glance can verify',
      trustCan1: '<a href="#vocab-doctor">Doctor</a> message classification (ok / warn / fault / blocking)',
      trustCan2: 'Secret redaction before display',
      trustCan3: 'Banned overclaim phrases (CI via glance-check action)',
      trustCan4: '<a href="#vocab-posture">Posture</a> stays dry compose / eyes-only (posture self-test)',
      trustCan5: 'Synthetic fixture schema conformance',
      trustCannotTitle: 'Glance cannot verify',
      trustCannot1: 'Live trade correctness, PnL, or strategy alpha',
      trustCannot2: 'Wallet balances or real RPC endpoints',
      trustCannot3: 'Whether an operator actually CLEARs off-site',
      trustCannot4: 'Anything beyond what your status JSON reports',
      trustMeta: 'MIT licence · pre-1.0 (not yet on crates.io or PyPI) · synthetic demo data only · contact <a href="mailto:support@elghaly.dev">support@elghaly.dev</a>',
      what: 'Fault-first doctor status, redaction, and anti-overclaim tests — open-source observability for Solana bot operators. Not a trading bot.',
      sectionWhat: 'What',
      sectionDemo: 'Demo',
      sectionInstall: 'Install',
      sectionLicense: 'License',
      sectionContact: 'Contact',
      sectionAsk: 'Ask us',
      demoHint: 'Synthetic fixtures below — client-side only, not live bot data.',
      playgroundToggle: 'Paste your own status JSON',
      playgroundHint: 'Synthetic fixture below — client-side only, not live bot data.',
      statusJsonLabel: 'Status JSON',
      rustLabel: 'Rust · pre-1.0',
      pythonLabel: 'Python · pre-1.0',
      installNote: 'Pre-1.0 local path install from the repo · MIT · synthetic demo data only',
      licenseLine: 'MIT · free forever · no paid tier · synthetic demo data only',
      contact: 'Contact',
      footer: 'Glance · MIT · pre-1.0',
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
      eyebrow: 'مفتوح المصدر · أدوات للمطورين',
      statusStrip: 'Eyes + dry compose · لا إرسال تلقائي',
      tryDemo: 'جرّب العرض',
      sectionWhatYouGet: 'ما تحصل عليه',
      bulletEyes: 'Glance eyes — بطاقات صحة بأولوية الأعطال',
      bulletDry: 'Dry simulate — تجميع بدون إرسال',
      bulletClear: 'Operator CLEAR فقط — بوابة بشرية، لا إرسال تلقائي',
      what: 'تصنيف الأعطال أولاً، إخفاء البيانات الحساسة، واختبارات منع المبالغة — أدوات مراقبة مفتوحة المصدر لمشغّلي بوتات سولانا. ليس بوت تداول.',
      sectionWhat: 'ما هو',
      sectionDemo: 'عرض',
      sectionInstall: 'تثبيت',
      sectionLicense: 'الترخيص',
      sectionContact: 'تواصل',
      sectionAsk: 'اسألنا',
      demoHint: 'عرض اصطناعي أدناه — على العميل فقط، ليست بيانات بوت حية.',
      playgroundToggle: 'الصق JSON الحالة الخاص بك',
      playgroundHint: 'عرض اصطناعي أدناه — على العميل فقط، ليست بيانات بوت حية.',
      statusJsonLabel: 'JSON الحالة',
      rustLabel: 'Rust · ما قبل 1.0',
      pythonLabel: 'Python · ما قبل 1.0',
      installNote: 'تثبيت محلي من المستودع · MIT · بيانات تجريبية اصطناعية فقط',
      licenseLine: 'MIT · مجاني للأبد · بيانات تجريبية اصطناعية فقط',
      contact: 'تواصل',
      footer: 'Glance · MIT · pre-1.0',
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
      eyebrow: 'Open source · инструменты для разработчиков',
      statusStrip: 'Eyes + dry compose · без авто-отправки',
      tryDemo: 'Попробовать демо',
      sectionWhatYouGet: 'Что вы получаете',
      bulletEyes: 'Glance eyes — карточки здоровья с приоритетом сбоев',
      bulletDry: 'Dry simulate — сборка без отправки',
      bulletClear: 'Operator CLEAR only — человеческий контроль, без авто-отправки',
      what: 'Приоритет блокирующих сбоев, редактирование секретов и тесты против преувеличений — open-source наблюдаемость для операторов Solana-ботов. Не торговый бот.',
      sectionWhat: 'О проекте',
      sectionDemo: 'Демо',
      sectionInstall: 'Установка',
      sectionLicense: 'Лицензия',
      sectionContact: 'Контакт',
      sectionAsk: 'Спросите нас',
      demoHint: 'Синтетическая фикстура ниже — только на клиенте, не данные живого бота.',
      playgroundToggle: 'Вставьте свой JSON статуса',
      playgroundHint: 'Синтетическая фикстура ниже — только на клиенте, не данные живого бота.',
      statusJsonLabel: 'JSON статуса',
      rustLabel: 'Rust · до 1.0',
      pythonLabel: 'Python · до 1.0',
      installNote: 'Локальная установка из репозитория · MIT · только синтетические демо-данные',
      licenseLine: 'MIT · бесплатно · только синтетические демо-данные',
      contact: 'Контакт',
      footer: 'Glance · MIT · pre-1.0',
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
      eyebrow: '开源 · 开发者工具',
      statusStrip: 'Eyes + dry compose · 无自动发送',
      tryDemo: '试用演示',
      sectionWhatYouGet: '你将获得',
      bulletEyes: 'Glance eyes — 故障优先健康卡片',
      bulletDry: 'Dry simulate — 组装但不发送',
      bulletClear: 'Operator CLEAR only — 人工把关，无自动发送',
      what: '故障优先诊断、敏感信息脱敏与反夸大测试 — 面向 Solana 机器人运维的开源可观测性工具。不是交易机器人。',
      sectionWhat: '简介',
      sectionDemo: '演示',
      sectionInstall: '安装',
      sectionLicense: '许可',
      sectionContact: '联系',
      sectionAsk: '联系我们',
      demoHint: '下方为合成示例 — 仅客户端渲染，非实时机器人数据。',
      playgroundToggle: '粘贴你自己的状态 JSON',
      playgroundHint: '下方为合成示例 — 仅客户端渲染，非实时机器人数据。',
      statusJsonLabel: '状态 JSON',
      rustLabel: 'Rust · 1.0 前',
      pythonLabel: 'Python · 1.0 前',
      installNote: '1.0 前从仓库本地安装 · MIT · 仅合成演示数据',
      licenseLine: 'MIT · 永久免费 · 仅合成演示数据',
      contact: '联系',
      footer: 'Glance · MIT · pre-1.0',
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
      eyebrow: 'Open Source · Entwickler-Tools',
      statusStrip: 'Eyes + dry compose · kein Auto-Send',
      tryDemo: 'Demo testen',
      sectionWhatYouGet: 'Was Sie bekommen',
      bulletEyes: 'Glance eyes — Fehler-zuerst-Gesundheitskarten',
      bulletDry: 'Dry simulate — zusammenstellen ohne Senden',
      bulletClear: 'Operator CLEAR only — menschliches Gate, kein Auto-Send',
      what: 'Fehler-zuerst-Diagnose, Schwärzung und Anti-Overclaim-Tests — Open-Source-Observability für Solana-Bot-Betreiber. Kein Trading-Bot.',
      sectionWhat: 'Was',
      sectionDemo: 'Demo',
      sectionInstall: 'Installation',
      sectionLicense: 'Lizenz',
      sectionContact: 'Kontakt',
      sectionAsk: 'Fragen Sie uns',
      demoHint: 'Synthetische Fixture unten — nur clientseitig, keine Live-Bot-Daten.',
      playgroundToggle: 'Eigenes Status-JSON einfügen',
      playgroundHint: 'Synthetische Fixture unten — nur clientseitig, keine Live-Bot-Daten.',
      statusJsonLabel: 'Status-JSON',
      rustLabel: 'Rust · Pre-1.0',
      pythonLabel: 'Python · Pre-1.0',
      installNote: 'Pre-1.0 lokale Installation aus dem Repo · MIT · nur synthetische Demo-Daten',
      licenseLine: 'MIT · dauerhaft kostenlos · nur synthetische Demo-Daten',
      contact: 'Kontakt',
      footer: 'Glance · MIT · pre-1.0',
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
      eyebrow: 'Open source · herramientas para desarrolladores',
      statusStrip: 'Eyes + dry compose · sin envío automático',
      tryDemo: 'Probar demo',
      sectionWhatYouGet: 'Qué obtienes',
      bulletEyes: 'Glance eyes — tarjetas de salud con fallos primero',
      bulletDry: 'Dry simulate — componer sin enviar',
      bulletClear: 'Operator CLEAR only — puerta humana, sin auto-envío',
      what: 'Diagnóstico con fallos primero, redacción y pruebas anti-exageración — observabilidad open source para operadores de bots de Solana. No es un bot de trading.',
      sectionWhat: 'Qué es',
      sectionDemo: 'Demo',
      sectionInstall: 'Instalar',
      sectionLicense: 'Licencia',
      sectionContact: 'Contacto',
      sectionAsk: 'Pregúntanos',
      demoHint: 'Fixture sintética abajo — solo en el cliente, no datos de bot en vivo.',
      playgroundToggle: 'Pega tu propio JSON de estado',
      playgroundHint: 'Fixture sintética abajo — solo en el cliente, no datos de bot en vivo.',
      statusJsonLabel: 'JSON de estado',
      rustLabel: 'Rust · pre-1.0',
      pythonLabel: 'Python · pre-1.0',
      installNote: 'Instalación local pre-1.0 desde el repo · MIT · solo datos demo sintéticos',
      licenseLine: 'MIT · gratis para siempre · solo datos demo sintéticos',
      contact: 'Contacto',
      footer: 'Glance · MIT · pre-1.0',
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
    document.querySelectorAll('[data-i18n-html]').forEach(function (node) {
      var key = node.getAttribute('data-i18n-html');
      if (key) node.innerHTML = t(key);
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
