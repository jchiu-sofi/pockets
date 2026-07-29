// Inventory every currency figure: size of the $ sign, the digits, and the cents,
// plus alignment. The real SoFi app uses superscript cents + a reduced $ for hero
// figures, and full-size cents for row amounts.
(() => {
  const out = [];
  const money = /\$\s?[\d,]+/;
  for (const el of document.querySelectorAll('body *')) {
    const own = [...el.childNodes].filter((n) => n.nodeType === 3)
      .map((n) => n.textContent.trim()).join('');
    const full = (el.textContent || '').replace(/\s+/g, '');
    if (!money.test(full)) continue;
    // Only the tightest wrapper around a figure.
    if ([...el.children].some((c) => money.test((c.textContent || '').replace(/\s+/g, '')))) continue;
    const c = getComputedStyle(el);
    const parts = [...el.childNodes].map((n) => {
      if (n.nodeType === 3) {
        const t = n.textContent.trim();
        return t ? { text: t.slice(0, 12), size: parseFloat(c.fontSize), va: 'text', weight: c.fontWeight } : null;
      }
      const cc = getComputedStyle(n);
      return { text: (n.textContent || '').trim().slice(0, 12), size: parseFloat(cc.fontSize),
               va: cc.verticalAlign, weight: cc.fontWeight };
    }).filter(Boolean);
    out.push({
      text: full.slice(0, 22),
      size: Math.round(parseFloat(c.fontSize)),
      align: c.textAlign,
      parentAlign: el.parentElement ? getComputedStyle(el.parentElement).textAlign : '',
      cls: (el.className || '').toString().slice(0, 46),
      parts,
    });
  }
  return { figures: out };
})();
