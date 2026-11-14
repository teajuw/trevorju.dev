// Enhancements only. Every page reads in full with this file missing.
(() => {
  const $ = s => document.querySelector(s);
  const $$ = s => [...document.querySelectorAll(s)];
  const el = (tag, cls, txt) => {
    const e = document.createElement(tag);
    if (cls) e.className = cls;
    if (txt != null) e.textContent = txt;
    return e;
  };
  // The home page keeps the browser's own scrollbar; the other pages draw theirs.
  const home = document.body.classList.contains('home');
  if (!home) document.documentElement.classList.add('js');

  // ---- section indicator ----
  // Article: the title and each heading; a click jumps there.
  // Home: the intro and each project; a click opens the project.
  const spy = $('#spy'), ticks = $('#spyTicks'), panel = $('#spyPanel');
  const targets = [...$$('[data-spy]'), ...$$('.prose h2')];
  let hover = -1;
  const items = targets.map((t, i) => {
    const isLink = t.tagName === 'A';
    const label = t.dataset.spy || t.textContent.trim();
    const go = isLink
      ? () => { location.href = t.href; }
      : () => scrollTo({ top: i === 0 ? 0 : t.getBoundingClientRect().top + scrollY - 80, behavior: 'smooth' });
    if (isLink) {
      t.addEventListener('mouseenter', () => { hover = i; spyUpdate(); });
      t.addEventListener('mouseleave', () => { hover = -1; spyUpdate(); });
    }
    return { t, label, go };
  });
  if (spy && items.length > 1) {
    spy.hidden = false;
    items.forEach(it => {
      ticks.append(el('i'));
      const a = el('a');
      a.href = it.t.tagName === 'A' ? it.t.href : '#';
      a.append(el('span', null, it.label));
      // A click jumps and shuts the list at once; it can reopen after the pointer has left.
      a.addEventListener('click', e => { e.preventDefault(); spy.classList.remove('open'); spy.classList.add('shut'); a.blur(); it.go(); });
      panel.append(a);
    });
    spy.addEventListener('mouseleave', () => spy.classList.remove('shut'));
    ticks.addEventListener('click', () => spy.classList.toggle('open'));
    document.addEventListener('click', e => { if (!spy.contains(e.target)) spy.classList.remove('open'); });
  }
  function spyUpdate() {
    if (!items.length) return;
    let on = 0;
    items.forEach((it, i) => { if (it.t.getBoundingClientRect().top <= 110) on = i; });
    const H = document.documentElement.scrollHeight;
    if (H > innerHeight + 4 && innerHeight + scrollY >= H - 4) on = items.length - 1;
    if (hover >= 0) on = hover;
    $$('#spyTicks i').forEach((t, i) => t.classList.toggle('on', i === on));
    $$('#spyPanel a').forEach((t, i) => t.classList.toggle('on', i === on));
  }

  // ---- scrollbar ----
  const sb = home ? null : $('#sb'), thumb = $('#sbT');
  let geo = { max: 0, travel: 0 };
  function sbUpdate() {
    if (!sb) return;
    const H = document.documentElement.scrollHeight, max = H - innerHeight;
    if (max <= 2) { sb.hidden = true; return; }
    sb.hidden = false;
    const track = sb.clientHeight, h = Math.max(40, track * innerHeight / H);
    geo = { max, travel: track - h };
    thumb.style.height = h + 'px';
    thumb.style.transform = 'translateY(' + (geo.travel * scrollY / max) + 'px)';
  }
  if (sb) sb.addEventListener('pointerdown', e => {
    e.preventDefault();
    sb.setPointerCapture(e.pointerId);
    sb.classList.add('drag');
    if (e.target !== thumb) {
      const r = sb.getBoundingClientRect();
      scrollTo(0, (e.clientY - r.top - thumb.offsetHeight / 2) / geo.travel * geo.max);
    }
    const y0 = e.clientY, s0 = scrollY;
    const move = ev => scrollTo(0, s0 + (ev.clientY - y0) / geo.travel * geo.max);
    const up = () => { sb.classList.remove('drag'); sb.removeEventListener('pointermove', move); sb.removeEventListener('pointerup', up); };
    sb.addEventListener('pointermove', move);
    sb.addEventListener('pointerup', up);
  });

  // ---- popover on selected text ----
  const prose = $('.prose');
  let pop = null;
  const hideSel = () => { if (pop) { pop.remove(); pop = null; } };
  if (prose) document.addEventListener('mouseup', e => {
    if (pop && pop.contains(e.target)) return;
    setTimeout(() => {
      hideSel();
      const s = getSelection(), txt = s.toString().trim();
      if (!txt || !s.rangeCount || !prose.contains(s.anchorNode)) return;
      const r = s.getRangeAt(0).getBoundingClientRect();
      pop = el('div', 'selpop');
      const copy = el('button', null, 'Copy with source');
      copy.addEventListener('click', async () => {
        try { await navigator.clipboard.writeText('> ' + txt + '\n\n— ' + prose.dataset.source); } catch (_) {}
        copy.textContent = 'Copied';
        setTimeout(hideSel, 700);
      });
      const ask = el('a', null, 'Ask Claude ↗');
      ask.target = '_blank';
      ask.rel = 'noopener';
      ask.href = 'https://claude.ai/new?q=' + encodeURIComponent('From ' + prose.dataset.md + ':\n\n"' + txt + '"\n\nExplain this.');
      pop.append(copy, ask);
      document.body.append(pop);
      pop.style.left = Math.min(Math.max(r.left + r.width / 2, 130), innerWidth - 130) + scrollX + 'px';
      pop.style.top = r.top + scrollY - 8 + 'px';
    }, 0);
  });

  // ---- copy buttons ----
  const flash = (b, txt) => { const o = b.textContent; b.textContent = txt; setTimeout(() => { b.textContent = o; }, 1100); };
  const copyLLM = $('#copyLLM');
  if (copyLLM) {
    // Fetched up front so the click can write to the clipboard straight away.
    let md = '';
    fetch(copyLLM.dataset.md).then(r => r.ok ? r.text() : '').then(t => { md = t; }).catch(() => {});
    copyLLM.addEventListener('click', async () => {
      if (!md) { location.href = copyLLM.dataset.md; return; }
      try { await navigator.clipboard.writeText(md); flash(copyLLM, 'Copied'); }
      catch (_) { location.href = copyLLM.dataset.md; }
    });
  }
  $$('.prose pre').forEach(pre => {
    const b = el('button', 'cp', 'copy');
    b.type = 'button';
    b.addEventListener('click', async () => {
      const code = pre.querySelector('code');
      try { await navigator.clipboard.writeText((code || pre).innerText.trim()); } catch (_) {}
      flash(b, 'copied');
    });
    pre.prepend(b);
  });

  // A project's demo runs in a frame and reports its own height, so the frame never scrolls inside the page.
  addEventListener('message', e => {
    if (e.origin !== location.origin || !e.data || e.data.type !== 'demo-height') return;
    document.querySelectorAll('iframe.demo').forEach(f => {
      if (f.contentWindow === e.source) f.style.height = Math.max(120, Math.min(+e.data.height || 0, 2000)) + 'px';
    });
  });

  // ---- the square on the home page ----
  // Each word is moved left until the upright of its first letter sits on the square's left edge.
  // Where that upright starts depends on the font, so it is read from the letter's own pixels.
  const motif = $('.motif');
  function fitMotif() {
    if (!motif) return;
    const cv = document.createElement('canvas'), cx = cv.getContext('2d', { willReadFrequently: true });
    const S = 200, W = 300, family = getComputedStyle(motif).fontFamily;
    const upright = ch => {
      cv.width = cv.height = W;
      cx.font = '700 ' + S + 'px ' + family;
      cx.fillText(ch, 50, 220);
      const d = cx.getImageData(0, 0, W, W).data, cols = [];
      for (let x = 0; x < W; x++) { let n = 0; for (let y = 0; y < W; y++) if (d[(y * W + x) * 4 + 3] > 128) n++; cols.push(n); }
      const tall = Math.max(...cols) * .8, x = cols.findIndex(n => n >= tall);
      return x < 0 ? null : (x - 50) / S;
    };
    motif.querySelectorAll('.ln').forEach(ln => {
      const o = upright(ln.textContent.trim()[0]);
      if (o != null) ln.style.setProperty('--o', o.toFixed(4) + 'em');
    });
    // Level the top of the name's first letter with the top of the square.
    const h1 = $('.poster h1');
    if (!h1) return;
    const cs = getComputedStyle(h1), F = parseFloat(cs.fontSize), line = parseFloat(cs.lineHeight);
    cx.font = cs.fontWeight + ' ' + F + 'px ' + cs.fontFamily;
    const m = cx.measureText(h1.textContent.trim()[0]);
    if (!m.fontBoundingBoxAscent || !line) return;
    const inkTop = (line - (m.fontBoundingBoxAscent + m.fontBoundingBoxDescent)) / 2 + m.fontBoundingBoxAscent - m.actualBoundingBoxAscent;
    h1.style.marginTop = (-inkTop / F).toFixed(4) + 'em';
  }
  fitMotif();
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(fitMotif);

  const update = () => { spyUpdate(); sbUpdate(); };
  addEventListener('scroll', () => { update(); hideSel(); }, { passive: true });
  addEventListener('resize', update);
  update();
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(update);
})();
