(function () {
  if (window.__ukMotion) return; window.__ukMotion = true;
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var fine = window.matchMedia('(hover: hover) and (pointer: fine)').matches;
  var raf = window.requestAnimationFrame.bind(window);

  /* 1. Reveal for [data-uk-reveal] sections */
  function reveals() {
    var els = document.querySelectorAll('[data-uk-reveal]:not(.is-in)');
    if (reduce || !('IntersectionObserver' in window)) { els.forEach(function (e) { e.classList.add('is-in'); }); return; }
    var io = new IntersectionObserver(function (es) { es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('is-in'); io.unobserve(e.target); } }); }, { rootMargin: '0px 0px -12% 0px', threshold: 0.05 });
    els.forEach(function (e) { io.observe(e); });
  }

  /* 2. Scroll progress line + hero lift */
  var bar, hero, heroInner, heroMedia, ticking = false;
  function onScroll() {
    if (ticking) return; ticking = true;
    raf(function () {
      var h = document.documentElement.scrollHeight - window.innerHeight;
      if (bar) bar.style.transform = 'scaleX(' + (h > 0 ? Math.min(1, window.scrollY / h) : 0).toFixed(4) + ')';
      if (hero && heroInner) {
        var r = hero.getBoundingClientRect(), p = Math.min(1, Math.max(0, -r.top / (r.height || 1)));
        heroInner.style.transform = 'translate3d(0,' + (p * -60).toFixed(1) + 'px,0)';
        heroInner.style.opacity = (1 - p * 1.1).toFixed(3);
        if (heroMedia) heroMedia.style.transform = 'scale(' + (1 + p * 0.08).toFixed(4) + ')';
      }
      ticking = false;
    });
  }

  /* 3. Product cards: tilt + light sweep (mouse only) */
  function tilt() {
    if (reduce || !fine) return;
    document.querySelectorAll('.bb-card__media, .card-wrapper .card__inner, .ukct__tile').forEach(function (el) {
      if (el.dataset.ukTilt) return; el.dataset.ukTilt = '1'; el.classList.add('uk-tilt');
      if (getComputedStyle(el).position === 'static') el.style.position = 'relative';
      el.addEventListener('pointermove', function (e) {
        var r = el.getBoundingClientRect(), x = (e.clientX - r.left) / r.width, y = (e.clientY - r.top) / r.height;
        el.classList.add('is-tilting');
        el.style.transform = 'perspective(900px) rotateX(' + ((0.5 - y) * 7).toFixed(2) + 'deg) rotateY(' + ((x - 0.5) * 9).toFixed(2) + 'deg) translateZ(0)';
        el.style.setProperty('--gx', (x * 100).toFixed(1) + '%'); el.style.setProperty('--gy', (y * 100).toFixed(1) + '%');
      });
      el.addEventListener('pointerleave', function () { el.classList.remove('is-tilting'); el.style.transform = ''; });
    });
  }

  /* 4. Magnetic buttons on the main calls to action (mouse only) */
  function magnetic() {
    if (reduce || !fine) return;
    document.querySelectorAll('.bb-hero .bb-btn, .bb-rs__cta .bb-btn, .bb-gift .bb-btn, .ukh__cta .bb-btn').forEach(function (b) {
      if (b.dataset.ukMag) return; b.dataset.ukMag = '1';
      b.addEventListener('pointermove', function (e) {
        var r = b.getBoundingClientRect();
        b.style.transform = 'translate(' + ((e.clientX - r.left - r.width / 2) * 0.18).toFixed(1) + 'px,' + ((e.clientY - r.top - r.height / 2) * 0.28).toFixed(1) + 'px)';
      });
      b.addEventListener('pointerleave', function () { b.style.transform = ''; });
    });
  }

  /* 5. Fly-to-cart: the product photo flies into the cart icon when added */
  document.addEventListener('submit', function (e) {
    var form = e.target;
    if (reduce || !form.matches || !form.matches('[data-bb-quick-add], .bb-sticky form, .product-form form, form[action*="/cart/add"]')) return;
    var scope = form.closest('.bb-card, .ukj__item, .card-wrapper, .product, .bb-fp, section') || document;
    var img = scope.querySelector('img');
    var cart = document.getElementById('cart-icon-bubble') || document.querySelector('.header__icon--cart');
    if (!img || !cart) return;
    var a = img.getBoundingClientRect(), c = cart.getBoundingClientRect();
    if (!a.width) return;
    var size = Math.min(a.width, a.height, 160);
    var fly = img.cloneNode(); fly.removeAttribute('srcset'); fly.removeAttribute('sizes'); fly.className = 'uk-fly';
    fly.style.width = fly.style.height = size + 'px';
    fly.style.left = (a.left + a.width / 2 - size / 2) + 'px'; fly.style.top = (a.top + a.height / 2 - size / 2) + 'px';
    document.body.appendChild(fly);
    var dx = c.left + c.width / 2 - (a.left + a.width / 2), dy = c.top + c.height / 2 - (a.top + a.height / 2);
    var anim = fly.animate([
      { transform: 'translate(0,0) scale(1)', opacity: 1 },
      { transform: 'translate(' + dx * 0.55 + 'px,' + (dy * 0.55 - 120) + 'px) scale(.6)', opacity: 1, offset: 0.55 },
      { transform: 'translate(' + dx + 'px,' + dy + 'px) scale(.12)', opacity: 0.2 }
    ], { duration: 900, easing: 'cubic-bezier(.5,0,.3,1)' });
    anim.onfinish = function () { fly.remove(); cart.classList.remove('uk-bump'); void cart.offsetWidth; cart.classList.add('uk-bump'); };
  }, true);

  function init() {
    reveals(); tilt(); magnetic();
    if (!reduce && !bar) { bar = document.createElement('div'); bar.className = 'uk-progress'; bar.setAttribute('aria-hidden', 'true'); document.body.appendChild(bar); }
    hero = document.querySelector('.bb-hero'); heroInner = hero && hero.querySelector('.bb-hero__inner'); heroMedia = hero && hero.querySelector('.bb-hero__media video, .bb-hero__media img');
    if (reduce) { hero = null; }
    onScroll();
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
  document.addEventListener('shopify:section:load', init);
  /* cards added later (quick view, infinite scroll) */
  if ('MutationObserver' in window) { var t; new MutationObserver(function () { clearTimeout(t); t = setTimeout(function () { tilt(); magnetic(); }, 300); }).observe(document.documentElement, { childList: true, subtree: true }); }
})();
