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
      if (drifters.length) driftTick();
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


  /* 6. Pollen light: a few soft golden motes drift up through the hero */
  function pollen() {
    if (reduce) return;
    var h = document.querySelector('.bb-hero'); if (!h || h.dataset.ukPollen) return; h.dataset.ukPollen = '1';
    var c = document.createElement('canvas'); c.className = 'uk-pollen'; c.setAttribute('aria-hidden', 'true'); h.appendChild(c);
    var ctx = c.getContext('2d'), dpr = Math.min(window.devicePixelRatio || 1, 2), W, H, motes = [], mx = 0, my = 0, run = true;
    var N = window.matchMedia('(max-width: 749px)').matches ? 22 : 46;
    function size() { W = h.clientWidth; H = h.clientHeight; c.width = W * dpr; c.height = H * dpr; c.style.width = W + 'px'; c.style.height = H + 'px'; ctx.setTransform(dpr, 0, 0, dpr, 0, 0); }
    function mote(init) { return { x: Math.random() * W, y: init ? Math.random() * H : H + 10, r: 0.6 + Math.random() * 2.2, z: 0.3 + Math.random() * 0.7, vy: 0.12 + Math.random() * 0.32, ph: Math.random() * 6.28, a: 0.12 + Math.random() * 0.34 }; }
    size(); for (var i = 0; i < N; i++) motes.push(mote(true));
    window.addEventListener('resize', size);
    if (fine) h.addEventListener('pointermove', function (e) { var r = h.getBoundingClientRect(); mx = (e.clientX - r.left) / r.width - 0.5; my = (e.clientY - r.top) / r.height - 0.5; });
    new IntersectionObserver(function (es) { run = es[0].isIntersecting; if (run) raf(draw); }).observe(h);
    var t = 0;
    function draw() {
      if (!run) return; t += 0.01; ctx.clearRect(0, 0, W, H);
      motes.forEach(function (m, i) {
        m.y -= m.vy * m.z; m.x += Math.sin(t * 1.3 + m.ph) * 0.18 * m.z;
        if (m.y < -10) motes[i] = m = mote(false);
        var x = m.x + mx * 24 * m.z, y = m.y + my * 16 * m.z, tw = 0.65 + 0.35 * Math.sin(t * 2 + m.ph);
        var g = ctx.createRadialGradient(x, y, 0, x, y, m.r * 4);
        g.addColorStop(0, 'rgba(255,226,150,' + (m.a * tw).toFixed(3) + ')'); g.addColorStop(1, 'rgba(255,200,90,0)');
        ctx.fillStyle = g; ctx.beginPath(); ctx.arc(x, y, m.r * 4, 0, 6.283); ctx.fill();
      });
      raf(draw);
    }
    raf(function () { c.classList.add('is-on'); draw(); });
  }

  /* 7. Tap ripple on buttons */
  document.addEventListener('pointerdown', function (e) {
    if (reduce) return;
    var b = e.target.closest && e.target.closest('.bb-btn, .uk-size, .button, .product-form__submit');
    if (!b) return;
    if (getComputedStyle(b).position === 'static') b.style.position = 'relative';
    b.style.overflow = 'hidden';
    var r = b.getBoundingClientRect(), s = Math.max(r.width, r.height);
    var dot = document.createElement('span'); dot.className = 'uk-ripple';
    dot.style.width = dot.style.height = s + 'px'; dot.style.left = (e.clientX - r.left - s / 2) + 'px'; dot.style.top = (e.clientY - r.top - s / 2) + 'px';
    b.appendChild(dot); setTimeout(function () { dot.remove(); }, 650);
  }, { passive: true });

  /* 8. Phones: focus the honey card that is centred in the swipe row */
  function journeyFocus() {
    document.querySelectorAll('.ukj__items').forEach(function (row) {
      if (row.dataset.ukFocus) return; row.dataset.ukFocus = '1';
      var items = row.querySelectorAll('.ukj__item');
      var pick = function () {
        if (window.matchMedia('(min-width: 990px)').matches) return;
        var mid = row.getBoundingClientRect().left + row.clientWidth / 2, best = null, bd = 1e9;
        items.forEach(function (it) { var r = it.getBoundingClientRect(), d = Math.abs(r.left + r.width / 2 - mid); if (d < bd) { bd = d; best = it; } });
        items.forEach(function (it) { it.classList.toggle('is-focus', it === best); });
      };
      row.addEventListener('scroll', function () { raf(pick); }, { passive: true }); pick();
    });
  }

  /* 9. Images drift while scrolling, and product cards pop in one by one */
  var drifters = [];
  function drift() {
    if (reduce) return;
    document.querySelectorAll('.bb-story__img img, .bb-gift__img img, .bb-reel img').forEach(function (img) {
      if (img.dataset.ukDrift) return; img.dataset.ukDrift = '1'; img.classList.add('uk-drift'); drifters.push(img);
    });
  }
  function driftTick() {
    var vh = window.innerHeight;
    drifters.forEach(function (img) {
      var box = img.parentElement.getBoundingClientRect(); if (box.bottom < 0 || box.top > vh) return;
      var t = (box.top + box.height / 2 - vh / 2) / vh;
      img.style.setProperty('--drift', (t * -28).toFixed(1) + 'px');
    });
  }

  function init() {
    reveals(); tilt(); magnetic(); pollen(); journeyFocus(); drift();
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
