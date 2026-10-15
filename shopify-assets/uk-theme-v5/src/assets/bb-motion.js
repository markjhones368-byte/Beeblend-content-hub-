(function () {
  if (window.__bbMotion) return;
  window.__bbMotion = true;
  var doc = document.documentElement;
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  doc.classList.add('bb-js');

  /* Split headings into masked words (text stays readable to screen readers and Google) */
  function split(el, startIndex) {
    if (el.dataset.bbSplit) return;
    el.dataset.bbSplit = '1';
    var i = startIndex || 0;
    var walk = function (node) {
      Array.prototype.slice.call(node.childNodes).forEach(function (n) {
        if (n.nodeType === 3) {
          var parts = n.textContent.split(/(\s+)/);
          var frag = document.createDocumentFragment();
          parts.forEach(function (p) {
            if (!p) return;
            if (/^\s+$/.test(p)) { frag.appendChild(document.createTextNode(' ')); return; }
            var w = document.createElement('span'); w.className = 'bb-w';
            var s = document.createElement('span'); s.textContent = p; s.style.setProperty('--i', i++);
            w.appendChild(s); frag.appendChild(w);
          });
          n.parentNode.replaceChild(frag, n);
        } else if (n.nodeType === 1) { walk(n); }
      });
    };
    walk(el);
  }

  if (!reduce) {
    document.querySelectorAll('.bb-hero h1, .bb-head h1, .bb-head h2').forEach(function (h) { split(h); });
  }

  /* Reveal on scroll */
  var groups = [
    { sel: '.bb-head', cls: '' },
    { sel: '.bb-story__img, .bb-gift__img', cls: 'bb-curtain' },
    { sel: '.bb-card, .bb-rev, .bb-steps li, .bb-assure__badge, .bb-cmp tbody tr, .bb-faq details, .bb-reel, .bb-ct__card, .bb-gift__copy, .bb-crumbs, .product-grid .grid__item, .collection .grid__item, .related-products .grid__item, .jdgm-widget', cls: 'bb-reveal' },
    { sel: '.bb-spec__bars, .bb-steps', cls: '' }
  ];
  var targets = [];
  groups.forEach(function (g) {
    document.querySelectorAll(g.sel).forEach(function (el) {
      if (el.closest('.bb-hero') || el.dataset.bbObs) return;
      el.dataset.bbObs = '1';
      if (g.cls) el.classList.add(g.cls);
      var i = el.parentElement ? Array.prototype.indexOf.call(el.parentElement.children, el) : 0;
      el.style.setProperty('--d', Math.min(i % 4, 4));
      targets.push(el);
    });
  });
  document.querySelectorAll('.bb-spec__bars').forEach(function (b) {
    Array.prototype.forEach.call(b.children, function (c, i) { c.style.setProperty('--d', i); });
  });
  /* Clipped elements (curtain images) report zero size to IntersectionObserver in Chrome,
     so we watch an unclipped "sentinel" (the parent) and reveal the element through it. */
  function reveal(el) { if (el && !el.classList.contains('is-in')) el.classList.add('is-in'); }
  var watchMap = new Map();
  targets.forEach(function (el) {
    var watch = el.classList.contains('bb-curtain') ? (el.parentElement || el) : el;
    if (!watchMap.has(watch)) watchMap.set(watch, []);
    watchMap.get(watch).push(el);
  });
  if (!reduce && 'IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { (watchMap.get(e.target) || []).forEach(reveal); io.unobserve(e.target); }
      });
    }, { threshold: 0.01, rootMargin: '0px 0px -6% 0px' });
    watchMap.forEach(function (_, w) { io.observe(w); });
    /* Safety net: anything that has reached the viewport gets revealed, whatever the browser does */
    var sweep = function () {
      var vh = window.innerHeight;
      targets.forEach(function (el) {
        if (el.classList.contains('is-in')) return;
        var box = (el.classList.contains('bb-curtain') ? el.parentElement : el) || el;
        var r = box.getBoundingClientRect();
        if (r.top < vh * 0.95 && r.bottom > 0) reveal(el);
      });
    };
    var sweepTick = false;
    window.addEventListener('scroll', function () { if (!sweepTick) { sweepTick = true; setTimeout(function () { sweep(); sweepTick = false; }, 150); } }, { passive: true });
    window.addEventListener('load', sweep);
    setTimeout(sweep, 1200);
    setTimeout(sweep, 3000);
  } else {
    targets.forEach(reveal);
  }

  /* Gentle parallax on large images (desktop only) */
  if (!reduce && window.matchMedia('(min-width: 990px)').matches) {
    var imgs = Array.prototype.slice.call(document.querySelectorAll('.bb-story__img img, .bb-gift__img img'));
    var ticking = false;
    var update = function () {
      var vh = window.innerHeight;
      imgs.forEach(function (img) {
        var box = img.parentElement;
        if (!box.classList.contains('is-in')) return;
        var r = box.getBoundingClientRect();
        if (r.bottom < 0 || r.top > vh) return;
        var t = (r.top + r.height / 2 - vh / 2) / vh;
        img.style.transform = 'scale(1.1) translate3d(0,' + (t * -36).toFixed(1) + 'px,0)';
        img.style.transition = 'transform .1s linear';
      });
      ticking = false;
    };
    window.addEventListener('scroll', function () { if (!ticking) { ticking = true; requestAnimationFrame(update); } }, { passive: true });
  }

  /* Toast */
  var toastEl, toastTimer;
  function root() { return (window.Shopify && Shopify.routes && Shopify.routes.root) || '/'; }
  function toast(msg, isErr) {
    if (!toastEl) {
      toastEl = document.createElement('div');
      toastEl.className = 'bb-toast';
      toastEl.setAttribute('role', 'status');
      toastEl.setAttribute('aria-live', 'polite');
      document.body.appendChild(toastEl);
    }
    toastEl.classList.toggle('is-err', !!isErr);
    toastEl.innerHTML = '<span></span>' + (isErr ? '' : '<a href="' + root() + 'cart">View cart</a>');
    toastEl.firstChild.textContent = msg;
    requestAnimationFrame(function () { toastEl.classList.add('is-on'); });
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { toastEl.classList.remove('is-on'); }, 4200);
  }

  function updateCount() {
    fetch(root() + 'cart.js', { headers: { Accept: 'application/json' } }).then(function (r) { return r.json(); }).then(function (cart) {
      var n = cart.item_count;
      var bubbles = document.querySelectorAll('.cart-count-bubble');
      if (!bubbles.length) {
        var icon = document.getElementById('cart-icon-bubble');
        if (icon) { var b = document.createElement('div'); b.className = 'cart-count-bubble'; icon.appendChild(b); bubbles = [b]; }
      }
      Array.prototype.forEach.call(bubbles, function (b) {
        b.innerHTML = '<span aria-hidden="true">' + n + '</span><span class="visually-hidden">' + n + ' items</span>';
      });
    }).catch(function () {});
  }

  /* Add to cart without leaving the page */
  document.addEventListener('submit', function (e) {
    var form = e.target;
    if (!form.matches || !form.matches('[data-bb-quick-add], .bb-sticky form')) return;
    e.preventDefault();
    var btn = form.querySelector('[type="submit"]');
    var label = btn ? btn.innerHTML : '';
    if (btn) { btn.disabled = true; btn.innerHTML = 'Adding\u2026'; }
    fetch(root() + 'cart/add.js', { method: 'POST', body: new FormData(form), headers: { Accept: 'application/json' } })
      .then(function (r) { return r.json().then(function (j) { if (!r.ok) throw new Error(j.description || 'Sorry, that could not be added.'); return j; }); })
      .then(function (item) {
        var name = (item.product_title || 'Item').split('|')[0].trim();
        if (btn) { btn.classList.add('is-added'); btn.innerHTML = 'Added \u2713'; }
        toast(name + ' added to your cart');
        updateCount();
        setTimeout(function () { if (btn) { btn.classList.remove('is-added'); btn.innerHTML = label; btn.disabled = false; } }, 2200);
      })
      .catch(function (err) {
        if (btn) { btn.innerHTML = label; btn.disabled = false; }
        toast(err.message, true);
      });
  });
})();
