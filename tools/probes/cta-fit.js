// Is the primary call-to-action fully inside the viewport?
(() => {
  const cta = [...document.querySelectorAll('button,a')]
    .find((b) => /^(Move|Join|Send|Create|Pay|Add money|Set up)/i.test(b.textContent.trim()));
  if (!cta) return { cta: 'not found' };
  const r = cta.getBoundingClientRect();
  return {
    label: cta.textContent.trim().replace(/\s+/g, ' ').slice(0, 28),
    viewport: window.innerHeight,
    ctaTop: Math.round(r.top), ctaBottom: Math.round(r.bottom),
    clippedBy: Math.max(0, Math.round(r.bottom - window.innerHeight)),
  };
})();
