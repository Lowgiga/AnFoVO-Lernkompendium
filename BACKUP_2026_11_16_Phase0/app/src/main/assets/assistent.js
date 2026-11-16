/*
 * Assistent v1.0 – kontextueller Lern-Assistent (RobotNav-Maskottchen).
 * Extern, offline-first, keine Abhängigkeiten. Nutzt window.KOMP, wenn vorhanden.
 * Features: Hinweise pro Seitentyp, Mood-LEDs, Lob bei richtigen Antworten,
 * Fortschritts-Narration, Inaktivitäts-Tipp, Ausblendbar + persistiert,
 * Web-Speech optional (Standard aus), aria-live=polite.
 */
(function () {
  'use strict';

  var stage = document.getElementById('object-stage');
  if (!stage) return;

  var STORE = 'anfoevo_assistent', SPEECH = 'anfoevo_speech';
  function store(k, d) { try { var v = localStorage.getItem(k); return v === null ? d : v; } catch (e) { return d; } }
  function save(k, v) { try { localStorage.setItem(k, v); } catch (e) {} }

  var on = store(STORE, 'ein') === 'ein';
  var speak = store(SPEECH, 'aus') === 'ein';

  function q(s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); }

  /* ---------- CSS (token-basiert, eigener Style-Block) ---------- */
  var style = document.createElement('style');
  style.id = 'assistent-style';
  style.textContent =
    '#assistBubble{position:fixed;right:max(18px,calc((100vw - 1240px)/2));bottom:calc(5vh + clamp(230px,34vh,360px) + 14px);' +
    'width:clamp(220px,24vw,300px);background:var(--card,#fff);color:var(--ink,#222);border:1px solid var(--line,#ddd);' +
    'border-radius:var(--r,10px);box-shadow:var(--shadow-lg,0 8px 24px rgba(24,43,32,.12));padding:.6rem .7rem;' +
    'font-size:.8125rem;line-height:1.35;z-index:60;opacity:0;transform:translateY(6px);' +
    'transition:opacity .22s ease,transform .22s ease;pointer-events:none;max-width:calc(100vw - 2rem)}' +
    '#assistBubble.show{opacity:1;transform:none;pointer-events:auto}' +
    '#assistBubble .ab-text{margin:0 0 .35rem;overflow-wrap:anywhere}' +
    '#assistBubble .ab-actions{display:flex;gap:.4rem;flex-wrap:wrap}' +
    '#assistBubble button{border:1px solid var(--field,#ccc);background:var(--card,#fff);color:var(--ink,#222);' +
    'border-radius:var(--r-sm,3px);font:inherit;font-size:.75rem;padding:.25rem .5rem;cursor:pointer;touch-action:manipulation}' +
    '#assistBubble button:focus-visible{outline:3px solid var(--focus,#a94738);outline-offset:2px}' +
    '#object-stage[data-assist="hint"] .robot-status{background:#e6c86e;box-shadow:0 0 10px #e6c86e;animation:assistBlink 1s ease-in-out 3}' +
    '#object-stage[data-assist="celebrate"] .robot-status{background:#2ecc71;box-shadow:0 0 12px #2ecc71}' +
    '@keyframes assistBlink{50%{opacity:.2}}' +
    '@media(max-width:760px){#assistBubble{display:none}}' +
    '@media(prefers-reduced-motion:reduce){#assistBubble{transition:none}#object-stage[data-assist] .robot-status{animation:none}}';
  document.head.appendChild(style);

  /* ---------- Bubble ---------- */
  var bubble = document.createElement('div');
  bubble.id = 'assistBubble';
  bubble.setAttribute('role', 'status');
  bubble.setAttribute('aria-live', 'polite');
  bubble.setAttribute('aria-atomic', 'true');
  var t = document.createElement('p'); t.className = 'ab-text';
  var act = document.createElement('div'); act.className = 'ab-actions';
  var bToggle = document.createElement('button');
  bToggle.type = 'button'; bToggle.id = 'assistToggle';
  var bSpeech = document.createElement('button');
  bSpeech.type = 'button'; bSpeech.id = 'assistSpeech';
  act.appendChild(bToggle); act.appendChild(bSpeech);
  bubble.appendChild(t); bubble.appendChild(act);
  document.body.appendChild(bubble);

  var timer = 0, hintTimer = 0, lastPraise = 0, idleTimer = 0, idleArmed = false, idleDone = false, praisedPage = null;

  function mood(m, ms) {
    stage.setAttribute('data-assist', m);
    window.clearTimeout(hintTimer);
    if (m !== 'idle') hintTimer = window.setTimeout(function () { stage.setAttribute('data-assist', 'idle'); }, ms || 6000);
  }

  function speakIt(txt) {
    if (!speak) return;
    try {
      if (!('speechSynthesis' in window)) return;
      var u = new SpeechSynthesisUtterance(txt);
      u.lang = 'de-DE'; u.rate = 1;
      window.speechSynthesis.cancel();
      window.speechSynthesis.speak(u);
    } catch (e) {}
  }

  function show(text) {
    if (!on || !text) return;
    t.textContent = text;
    bubble.classList.add('show');
    window.clearTimeout(timer);
    timer = window.setTimeout(hide, 8000);
    mood('hint', 6000);
    speakIt(text);
  }
  function hide() {
    bubble.classList.remove('show');
    if (stage.getAttribute('data-assist') === 'hint') stage.setAttribute('data-assist', 'idle');
  }

  function current() {
    try {
      if (window.KOMP && KOMP.list) { var L = KOMP.list(), i = KOMP.idx(); if (L && L[i]) return L[i]; }
    } catch (e) {}
    return document.querySelector('article.page.current');
  }

  function hintFor(a) {
    if (!a) return '';
    var type = a.dataset.type || '';
    var le = a.dataset.le;
    var prefix = le ? 'LE ' + le + ' · ' : '';
    var todo = a.querySelector('p.todo');
    var kind = todo ? todo.dataset.kind : '';
    var gaps = q('.gap-in', a);
    if (gaps.length) {
      var open = gaps.filter(function (i) { return !i.value.trim(); });
      if (open.length) return prefix + 'Noch ' + open.length + ' von ' + gaps.length + ' Lücken offen – dann „Lösung“ öffnen.';
      return prefix + 'Alle Lücken ausgefüllt – „Lösung“ öffnet den Vergleich.';
    }
    if (kind === 'checkpoint') {
      var nq = a.dataset.nq || q('fieldset', a).length;
      return prefix + 'Checkpoint: ' + nq + ' Fragen beantworten, dann Lösung öffnen.';
    }
    if (kind === 'darf') {
      var f = q('fieldset.darf', a);
      var done = f.filter(function (x) { return x.querySelector('input:checked'); });
      if (f.length - done.length) return prefix + 'Noch ' + (f.length - done.length) + ' von ' + f.length + ' Zeilen ankreuzen.';
      return prefix + 'Alle Zeilen angekreuzt – Lösung öffnet den Vergleich.';
    }
    if (kind === 'ende' || a.querySelector('.endtest')) {
      return prefix + 'Abschluss-Test: Jede Antwort zeigt sofort, ob sie stimmt.';
    }
    if (type === 'zusammenfassung') return prefix + 'Lies die Zusammenfassung und sichere sie mit den Lücken.';
    if (type === 'situation') return prefix + 'Lies die Situation und fülle danach die Lücken aus.';
    return '';
  }

  function praise(text) {
    if (!on) return;
    var now = Date.now();
    if (now - lastPraise < 2500) return;
    lastPraise = now;
    show(text || 'Richtig! Weiter so. 👏');
    mood('celebrate', 2500);
  }

  /* ---------- Lob: bestehendes setMood wrappen ---------- */
  var origMood = window.setMood;
  if (typeof origMood === 'function') {
    window.setMood = function (ok) {
      origMood(ok);
      if (ok) praise('Richtig! Gut gemacht. 👏');
    };
  }

  /* ---------- Seitenwechsel ---------- */
  var lastId = null;
  function onPage() {
    if (!on) return;
    var a = current();
    if (!a) return;
    lastId = a.dataset.id;
    praisedPage = null;
    idleDone = false;
    armIdle();
    var h = hintFor(a);
    if (h) show(h); else hide();
  }
  window.addEventListener('kompendium:pagechange', onPage);

  /* ---------- Eingaben live verfolgen ---------- */
  function refresh(a) {
    if (!on || !a) return;
    var gaps = q('.gap-in', a);
    if (gaps.length) {
      var open = gaps.filter(function (i) { return !i.value.trim(); });
      if (!open.length) {
        if (praisedPage !== lastId) { praisedPage = lastId; praise('Alle Lücken ausgefüllt! 🎉'); }
        return;
      }
      if (bubble.classList.contains('show')) {
        t.textContent = 'Noch ' + open.length + ' von ' + gaps.length + ' Lücken offen.';
        window.clearTimeout(timer); timer = window.setTimeout(hide, 6000);
      }
    }
  }
  document.addEventListener('input', function (e) {
    if (e.target && e.target.classList && e.target.classList.contains('gap-in')) refresh(e.target.closest('article.page'));
    armIdle();
  }, { passive: true });
  document.addEventListener('change', function (e) {
    if (e.target && e.target.type === 'radio') {
      var a = e.target.closest('article.page');
      if (a) refresh(a);
    }
    armIdle();
  }, { passive: true });
  document.addEventListener('keydown', armIdle, { passive: true });
  document.addEventListener('pointerdown', armIdle, { passive: true });

  /* ---------- Inaktivitäts-Tipp (45 s, einmal pro Seite) ---------- */
  function armIdle() {
    window.clearTimeout(idleTimer);
    if (!on) return;
    idleTimer = window.setTimeout(function () {
      if (!on || idleDone) return;
      var a = current();
      if (!a) return;
      var gaps = q('.gap-in', a);
      var open = gaps.filter(function (i) { return !i.value.trim(); });
      var kind = a.querySelector('p.todo') ? a.querySelector('p.todo').dataset.kind : '';
      if (open.length || kind === 'checkpoint' || kind === 'darf') {
        idleDone = true;
        show('Noch Zeit: ' + (hintFor(a) || 'Weiter so – du schaffst das.'));
      }
      armIdle();
    }, 45000);
  }

  /* ---------- Toggle + Sprache ---------- */
  function render() {
    bToggle.textContent = on ? '💬 Assistent an' : '💬 Assistent aus';
    bToggle.setAttribute('aria-pressed', on ? 'true' : 'false');
    bSpeech.textContent = speak ? '🔊 Sprache an' : '🔇 Sprache aus';
    bSpeech.setAttribute('aria-pressed', speak ? 'true' : 'false');
  }
  bToggle.addEventListener('click', function () {
    on = !on; save(STORE, on ? 'ein' : 'aus');
    render();
    if (on) onPage(); else { hide(); window.clearTimeout(idleTimer); }
  });
  bSpeech.addEventListener('click', function () {
    speak = !speak; save(SPEECH, speak ? 'ein' : 'aus');
    render();
    if (speak && 'speechSynthesis' in window) show('Sprache an. Ich sage dir jetzt die Hinweise vor.');
  });
  render();

  /* ---------- Start ---------- */
  if (on) {
    window.setTimeout(function () {
      show('Hallo! Ich bin dein Lern-Assistent. Ich gebe dir Tipps, wenn du sie brauchst.');
      onPage();
    }, 1200);
  } else {
    bubble.classList.remove('show');
  }
  armIdle();
})();
