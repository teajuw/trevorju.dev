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
  document.documentElement.classList.add('js');

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
      a.addEventListener('click', e => { e.preventDefault(); spy.classList.remove('open'); a.blur(); it.go(); });
      panel.append(a);
    });
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
  const sb = $('#sb'), thumb = $('#sbT');
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

  const update = () => { spyUpdate(); sbUpdate(); };
  addEventListener('scroll', () => { update(); hideSel(); }, { passive: true });
  addEventListener('resize', update);
  update();
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(update);
})();
