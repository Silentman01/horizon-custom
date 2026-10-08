/**
 * Ceriva sections: shared behaviour.
 * Loaded as a module by every Ceriva section, so it runs once per page whatever the number of sections.
 */

const reducedMotion = () => window.matchMedia('(prefers-reduced-motion: reduce)').matches;

/** Header height, so scrolled-to targets land below the sticky header. */
const headerOffset = () => {
  const value = getComputedStyle(document.body).getPropertyValue('--header-height');
  return (parseFloat(value) || 64) + 16;
};

/**
 * Scrolls an element into view inside whichever container scrolls the page
 * (Horizon scrolls `.page-wrapper` on desktop and the document on mobile).
 * @param {Element} target
 */
function scrollToElement(target) {
  if (target instanceof HTMLElement) target.style.scrollMarginTop = `${headerOffset()}px`;
  target.scrollIntoView({ behavior: reducedMotion() ? 'auto' : 'smooth', block: 'start' });
}

/** The offer selector, falling back to the buy buttons, then the product details. */
const findOffer = () =>
  document.querySelector('.cvb') ||
  document.querySelector('.buy-buttons-block') ||
  document.querySelector('[id^="ProductInformation-"]');

/** Briefly highlights an element so the eye finds it after scrolling. */
function flash(target) {
  target.classList.remove('cv-flash');
  // Restart the animation if it is clicked twice in a row.
  void /** @type {HTMLElement} */ (target).offsetWidth;
  target.classList.add('cv-flash');
  setTimeout(() => target.classList.remove('cv-flash'), 1600);
}

function goToOffer() {
  const target = findOffer();
  if (!target) return false;
  scrollToElement(target);
  setTimeout(() => flash(target), reducedMotion() ? 0 : 450);
  return true;
}

/** Clicks the main add-to-cart button, so the theme adds the selected offer and opens the cart drawer. */
function addToCart() {
  const button = document.querySelector('.buy-buttons-block button[name="add"]');
  if (!(button instanceof HTMLButtonElement) || button.disabled) return goToOffer();
  button.click();
  return true;
}

document.addEventListener('click', (event) => {
  if (!(event.target instanceof Element)) return;

  const trigger = event.target.closest('[data-cv-action]');
  if (trigger) {
    const action = trigger.getAttribute('data-cv-action');
    const handled = action === 'cart' ? addToCart() : goToOffer();
    if (handled) event.preventDefault();
    return;
  }

  // In-page links inside Ceriva blocks (e.g. the rating → #avis) scroll smoothly and clear the header.
  const link = event.target.closest('.cv a[href^="#"]');
  const id = link?.getAttribute('href')?.slice(1);
  const target = id ? document.getElementById(decodeURIComponent(id)) : null;
  if (target) {
    event.preventDefault();
    scrollToElement(target);
  }
});

/* ---------- Scroll reveal ---------- */

const revealObserver =
  'IntersectionObserver' in window
    ? new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            if (!entry.isIntersecting) return;
            entry.target.classList.add('is-visible');
            revealObserver?.unobserve(entry.target);
          });
        },
        { rootMargin: '0px 0px -10% 0px' }
      )
    : null;

function initReveal() {
  document.documentElement.classList.add('cv-reveal-on');
  document.querySelectorAll('.cv-reveal:not(.is-visible)').forEach((el) => {
    if (revealObserver) revealObserver.observe(el);
    else el.classList.add('is-visible');
  });
}

/* ---------- Muted autoplay videos, playing only while on screen ---------- */

const videoObserver =
  'IntersectionObserver' in window
    ? new IntersectionObserver(
        (entries) => {
          entries.forEach(({ target, isIntersecting }) => {
            const video = /** @type {HTMLVideoElement} */ (target);
            if (isIntersecting) video.play().catch(() => {});
            else video.pause();
          });
        },
        { threshold: 0.4 }
      )
    : null;

function initVideos() {
  document.querySelectorAll('video.cv-autoplay:not([data-cv-watched])').forEach((el) => {
    const video = /** @type {HTMLVideoElement} */ (el);
    video.dataset.cvWatched = '';
    video.muted = true;
    if (videoObserver) videoObserver.observe(video);
    else video.play().catch(() => {});
  });
}

/* ---------- Sound toggle on customer videos (one unmuted at a time) ---------- */

document.addEventListener('click', (event) => {
  if (!(event.target instanceof Element)) return;
  const toggle = event.target.closest('[data-cv-sound]');
  if (!toggle) return;

  const video = toggle.closest('.cv-ugc__card')?.querySelector('video');
  if (!video) return;

  const unmute = video.muted;
  document.querySelectorAll('.cv-ugc__card video').forEach((other) => {
    if (other === video) return;
    other.muted = true;
    other.closest('.cv-ugc__card')?.classList.remove('is-unmuted');
  });

  video.muted = !unmute;
  if (unmute) video.play().catch(() => {});
  toggle.closest('.cv-ugc__card')?.classList.toggle('is-unmuted', unmute);
  toggle.setAttribute('aria-pressed', String(unmute));
});

/* ---------- Mouse drag-to-scroll for horizontal rails (touch keeps native swipe) ---------- */

function initDrag() {
  document.querySelectorAll('[data-cv-drag]:not([data-cv-drag-ready])').forEach((el) => {
    const rail = /** @type {HTMLElement} */ (el);
    rail.dataset.cvDragReady = '';
    let startX = 0;
    let startScroll = 0;
    let moved = false;
    let pointerId = -1;

    rail.addEventListener('pointerdown', (event) => {
      if (event.pointerType !== 'mouse' || event.button !== 0) return;
      if (event.target instanceof Element && event.target.closest('button, a')) return;
      if (rail.scrollWidth <= rail.clientWidth) return;
      pointerId = event.pointerId;
      startX = event.clientX;
      startScroll = rail.scrollLeft;
      moved = false;
    });

    rail.addEventListener('pointermove', (event) => {
      if (event.pointerId !== pointerId) return;
      const dx = event.clientX - startX;
      if (!moved && Math.abs(dx) < 4) return;
      if (!moved) {
        moved = true;
        rail.classList.add('is-dragging');
        rail.setPointerCapture(pointerId);
      }
      rail.scrollLeft = startScroll - dx;
    });

    const end = () => {
      if (pointerId === -1) return;
      pointerId = -1;
      if (!moved) return;
      // Re-enable snapping, then settle on the nearest card.
      const left = rail.scrollLeft;
      rail.classList.remove('is-dragging');
      rail.scrollLeft = left;
      const card = rail.firstElementChild;
      const step = card ? card.getBoundingClientRect().width + parseFloat(getComputedStyle(rail).columnGap || '0') : 0;
      if (step) rail.scrollTo({ left: Math.round(left / step) * step, behavior: reducedMotion() ? 'auto' : 'smooth' });
    };
    rail.addEventListener('pointerup', end);
    rail.addEventListener('pointercancel', end);

    // A drag should not also count as a click on a card (e.g. the sound button).
    rail.addEventListener('click', (event) => {
      if (moved) {
        event.preventDefault();
        event.stopPropagation();
        moved = false;
      }
    }, true);
  });
}

function init() {
  initReveal();
  initVideos();
  initDrag();
}

init();
document.addEventListener('shopify:section:load', init);
