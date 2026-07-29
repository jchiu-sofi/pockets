// Layout defect detectors, evaluated inside a rendered screen via tools/cdp.mjs.
//
// Measures the computed layout rather than reading markup. Every detector here
// suppresses the patterns that are deliberate in this design — horizontal carousels
// overflow on purpose, avatar stacks overlap on purpose, decorative blur circles sit
// outside the frame on purpose — because a report full of false positives is a
// report nobody acts on.
(() => {
  const findings = [];
  const add = (kind, el, detail, measured, threshold) => findings.push({
    kind,
    tag: el.tagName.toLowerCase(),
    cls: (el.className || '').toString().slice(0, 90),
    text: (el.textContent || '').trim().slice(0, 40),
    detail, measured, threshold,
  });

  const vw = document.documentElement.clientWidth;
  const vh = window.innerHeight;
  const rect = (el) => el.getBoundingClientRect();
  const cs = (el) => getComputedStyle(el);

  const visible = (el) => {
    const c = cs(el);
    if (c.display === 'none' || c.visibility === 'hidden' || +c.opacity === 0) return false;
    const r = rect(el);
    return r.width > 0 && r.height > 0;
  };
  const all = [...document.querySelectorAll('body *')].filter(visible);

  const positioned = (el) => ['absolute', 'fixed', 'sticky'].includes(cs(el).position);
  const hasText = (el) => [...el.childNodes]
    .some((n) => n.nodeType === 3 && n.textContent.trim());

  // A negative margin is how an overlapping avatar stack is built.
  const stacked = (el) => {
    const c = cs(el);
    return parseFloat(c.marginLeft) < 0 || parseFloat(c.marginRight) < 0
      || parseFloat(c.marginTop) < 0;
  };

  // Anything inside a horizontal scroller is meant to extend past the frame.
  const inScroller = (el) => {
    for (let p = el.parentElement; p && p !== document.body; p = p.parentElement) {
      const ox = cs(p).overflowX;
      if (ox === 'auto' || ox === 'scroll') return true;
    }
    return false;
  };

  // --- Overlap between in-flow siblings.
  for (const el of all) {
    const kids = [...el.children].filter(
      (k) => visible(k) && !positioned(k) && !stacked(k),
    );
    for (let i = 0; i < kids.length; i++) {
      for (let j = i + 1; j < kids.length; j++) {
        const a = rect(kids[i]); const b = rect(kids[j]);
        const ox = Math.min(a.right, b.right) - Math.max(a.left, b.left);
        const oy = Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top);
        if (ox > 2 && oy > 2) {
          add('overlap', kids[i],
            `overlaps sibling <${kids[j].tagName.toLowerCase()}>`,
            `${Math.round(ox)}x${Math.round(oy)}px`, '0px');
        }
      }
    }
  }

  // --- Horizontal overflow past the frame, ignoring carousels and decoration.
  for (const el of all) {
    if (inScroller(el)) continue;
    if (positioned(el) && !hasText(el)) continue; // blur circles, sine-wave motifs
    const r = rect(el);
    if (r.right > vw + 1) {
      add('overflow-viewport', el, 'extends past the right edge',
        `${Math.round(r.right - vw)}px over`, '0px');
    } else if (r.left < -1) {
      add('overflow-viewport', el, 'extends past the left edge',
        `${Math.round(-r.left)}px over`, '0px');
    }
  }

  // --- Content stranded below the fold.
  // Only a defect when the page cannot scroll: these sheet layouts are
  // overflow-hidden, so a CTA past the viewport is unreachable rather than merely
  // off-screen. On a normally scrolling screen, below-fold content is just content.
  const rootHidden = cs(document.documentElement).overflowY === 'hidden'
    || cs(document.body).overflowY === 'hidden';
  const canScroll = !rootHidden
    && document.documentElement.scrollHeight > vh + 2;
  if (!canScroll) {
    for (const el of all) {
      const r = rect(el);
      if (r.top >= vh - 2 || (r.top < vh && r.bottom > vh + 2 && r.height < vh)) {
        if (positioned(el) && !hasText(el)) continue; // decorative bleed
        if (!hasText(el) && el.children.length) continue; // report the leaf, not wrappers
        add('below-fold', el, 'unreachable: past the fold on a screen that cannot scroll',
          `bottom ${Math.round(r.bottom)}px of ${vh}px`, `<= ${vh}px`);
      }
    }
  }

  // --- Clipped single-line text.
  for (const el of all) {
    const c = cs(el);
    const single = c.whiteSpace === 'nowrap'
      || parseFloat(c.height) <= parseFloat(c.lineHeight) * 1.4;
    if (hasText(el) && single && el.scrollWidth > el.clientWidth + 1
        && c.overflow !== 'visible' && !c.textOverflow.includes('ellipsis')) {
      add('clipped-text', el, 'text is cut off',
        `${el.scrollWidth}px in ${el.clientWidth}px`, 'fits');
    }
  }

  // --- Text crowding a container edge.
  for (const el of all) {
    if (!hasText(el) || positioned(el)) continue;
    const parent = el.parentElement;
    if (!parent) continue;
    const pc = cs(parent);
    // A single-side border is a divider rule, not a container inset — the
    // horizontal padding comes from an ancestor card in that case.
    const fullBorder = ['borderTopWidth', 'borderRightWidth', 'borderBottomWidth',
      'borderLeftWidth'].every((k) => parseFloat(pc[k]) > 0);
    const bounded = pc.backgroundColor !== 'rgba(0, 0, 0, 0)' || fullBorder;
    if (!bounded) continue;
    // A centred Material icon glyph is not crowded text.
    if (/material-symbols/.test((el.className || '').toString())) continue;
    const a = rect(el); const p = rect(parent);
    const ec = cs(el);
    const padL = parseFloat(ec.paddingLeft) + parseFloat(ec.borderLeftWidth);
    const padR = parseFloat(ec.paddingRight) + parseFloat(ec.borderRightWidth);
    // Distance from the text itself to the parent's visible boundary.
    const gap = Math.min((a.left + padL) - p.left, p.right - (a.right - padR));
    if (gap >= 0 && gap < 8) {
      add('cramped-edge', el, 'text sits within 8px of its container edge',
        `${Math.round(gap)}px`, '8px');
    }
  }

  // --- Undersized tap targets, ignoring icons inside a large enough parent.
  for (const el of document.querySelectorAll(
    'a,button,[role="button"],input,select,textarea,[onclick]')) {
    if (!visible(el)) continue;
    const r = rect(el);
    const p = el.parentElement ? rect(el.parentElement) : null;
    const parentBigEnough = p && p.width >= 44 && p.height >= 44
      && el.parentElement.querySelectorAll('a,button,[role="button"]').length === 1;
    if ((r.width < 44 || r.height < 44) && !parentBigEnough) {
      add('tap-target', el, 'interactive target below 44px',
        `${Math.round(r.width)}x${Math.round(r.height)}px`, '44x44px');
    }
  }

  // --- Border and radius consistency.
  const borders = new Map(); const radii = new Map();
  for (const el of all) {
    const c = cs(el);
    const w = parseFloat(c.borderTopWidth);
    if (w > 0 && c.borderTopStyle !== 'none'
        && c.borderTopColor !== 'rgba(0, 0, 0, 0)') {
      const key = `${c.borderTopColor} ${w}px`;
      borders.set(key, (borders.get(key) || 0) + 1);
    }
    const rad = c.borderTopLeftRadius;
    if (rad && rad !== '0px') radii.set(rad, (radii.get(rad) || 0) + 1);
  }

  return {
    url: location.pathname.split('/').pop(),
    viewport: `${vw}x${vh}`,
    findings,
    borderStyles: [...borders.entries()].sort((a, b) => b[1] - a[1]),
    radiusValues: [...radii.entries()].sort((a, b) => b[1] - a[1]),
  };
})();
