/* BeeBlend UK — restrained motion: header state, scroll progress, hero depth, image drift.
   Everything here is decorative; content and buttons work without it. */
(function () {
  if (window.__ukMotion) return; window.__ukMotion = true;
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var raf = window.requestAnimationFrame.bind(window), doc = document.documentElement;
  var bar, hero, heroInner, drifters = [], ticking = false;

  function frame() {
    ticking = false;
    var y = window.scrollY || 0;
    doc.classList.toggle('uk-scrolled', y > 24);
    if (reduce) return;
    var h = doc.scrollHeight - window.innerHeight;
    if (bar) bar.style.transform = 'scaleX(' + (h > 0 ? Math.min(1, y / h) : 0).toFixed(4) + ')';
    if (hero && heroInner) {
      var r = hero.getBoundingClientRect(), p = Math.min(1, Math.max(0, -r.top / (r.height || 1)));
      heroInner.style.transform = 'translate3d(0,' + (p * -40).toFixed(1) + 'px,0)';
      heroInner.style.opacity = (1 - p * 0.9).toFixed(3);
    }
    var vh = window.innerHeight;
    drifters.forEach(function (img) {
      var box = img.parentElement.getBoundingClientRect(); if (box.bottom < 0 || box.top > vh) return;
      img.style.setProperty('--drift', (((box.top + box.height / 2 - vh / 2) / vh) * -22).toFixed(1) + 'px');
    });
  }
  function onScroll() { if (!ticking) { ticking = true; raf(frame); } }

  function init() {
    if (!reduce && !bar) { bar = document.createElement('div'); bar.className = 'uk-progress'; bar.setAttribute('aria-hidden', 'true'); document.body.appendChild(bar); }
    hero = document.querySelector('.bb-hero'); heroInner = hero && hero.querySelector('.bb-hero__inner');
    if (!reduce && window.matchMedia('(max-width: 989px)').matches) {
      document.querySelectorAll('.bb-story__img img, .bb-gift__img img').forEach(function (img) {
        if (img.dataset.ukDrift) return; img.dataset.ukDrift = '1'; img.classList.add('uk-drift'); drifters.push(img);
      });
    }
    frame();
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
  document.addEventListener('shopify:section:load', init);
})();
