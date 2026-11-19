/* PawSorb shared behaviour: drag-scroll rails + "scroll to the bundle picker" CTAs. Safe to load many times. */
(() => {
  if (window.__pawsorbCore) return;
  window.__pawsorbCore = true;

  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* Rails: native touch swipe + mouse/pen drag with snap to the nearest card on release. */
  const initRails = (root = document) => {
    root.querySelectorAll('[data-pawsorb-rail]:not([data-pawsorb-rail-ready])').forEach((rail) => {
      rail.setAttribute('data-pawsorb-rail-ready', '');
      let x0 = 0, s0 = 0, id = -1, moved = false;
      rail.addEventListener('pointerdown', (e) => {
        if (e.pointerType === 'touch' || e.button !== 0 || rail.scrollWidth <= rail.clientWidth + 2) return;
        id = e.pointerId; x0 = e.clientX; s0 = rail.scrollLeft; moved = false;
      });
      rail.addEventListener('pointermove', (e) => {
        if (e.pointerId !== id) return;
        const dx = e.clientX - x0;
        if (!moved && Math.abs(dx) < 4) return;
        if (!moved) { moved = true; rail.classList.add('is-dragging'); try { rail.setPointerCapture(id); } catch (err) {} }
        rail.scrollLeft = s0 - dx;
      });
      const end = () => {
        if (id === -1) return;
        id = -1;
        if (!moved) return;
        const left = rail.scrollLeft;
        rail.classList.remove('is-dragging');
        rail.scrollLeft = left;
        const card = rail.firstElementChild;
        const gap = parseFloat(getComputedStyle(rail).columnGap) || 0;
        const step = card ? card.getBoundingClientRect().width + gap : 0;
        if (step) rail.scrollTo({ left: Math.round(left / step) * step, behavior: reduce ? 'auto' : 'smooth' });
        setTimeout(() => { moved = false; }, 0);
      };
      rail.addEventListener('pointerup', end);
      rail.addEventListener('pointercancel', end);
      rail.addEventListener('click', (e) => { if (moved) { e.preventDefault(); e.stopPropagation(); } }, true);
      rail.addEventListener('dragstart', (e) => e.preventDefault());
    });
  };

  /* CTA buttons: on a page with the picker, scroll to it; elsewhere follow the link to the product. */
  const scrollToPicker = () => {
    const t = document.getElementById('pawsorb-bundle-picker');
    if (!t) return false;
    t.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'start' });
    t.classList.remove('is-flash');
    void t.offsetWidth;
    t.classList.add('is-flash');
    return true;
  };
  window.pawsorbScrollToPicker = scrollToPicker;
  document.addEventListener('click', (e) => {
    const a = e.target.closest && e.target.closest('[data-pawsorb-cta]');
    if (!a) return;
    if (scrollToPicker()) e.preventDefault();
  });

  const boot = () => initRails();
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot); else boot();
  document.addEventListener('shopify:section:load', (e) => initRails(e.target));
})();
