/* BeeBlend Luxe — progressive enhancement only.
   Without this file every section is fully visible and quick-add falls back to a normal form POST to /cart/add. */
(function () {
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var root = document.documentElement;

  /* 1. Reveal on scroll (opt-in: content is only hidden once we know IO exists) */
  if ('IntersectionObserver' in window && !reduce) {
    root.classList.add('bb-js');
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add('is-in'); io.unobserve(e.target); }
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
    var observe = function (scope) {
      (scope || document).querySelectorAll('.bb-reveal:not(.is-in)').forEach(function (el) {
        // anything already in view on load shows immediately (no blank first frame)
        var r = el.getBoundingClientRect();
        if (r.top < window.innerHeight && r.bottom > 0) { el.classList.add('is-in'); } else { io.observe(el); }
      });
    };
    observe();
    document.addEventListener('shopify:section:load', function (e) { observe(e.target); });
  }

  /* 2. Hero video: never autoplay for reduced-motion users */
  if (reduce) {
    document.querySelectorAll('.bb-hero video').forEach(function (v) { v.removeAttribute('autoplay'); v.pause(); });
  }

  /* 3. Quick add -> native Refresh cart drawer (falls back to /cart) */
  document.addEventListener('submit', function (e) {
    var form = e.target;
    if (!form.matches || !form.matches('form.bb-quick-add')) return;
    var btn = e.submitter;
    if (!btn || !window.fetch) return; // let the browser POST normally
    e.preventDefault();
    var drawer = document.querySelector('cart-drawer');
    var body = new FormData(form);
    body.set('id', btn.value);
    body.set('quantity', '1');
    if (drawer && typeof drawer.getSectionsToRender === 'function') {
      body.set('sections', drawer.getSectionsToRender().map(function (s) { return s.id; }).join(','));
      body.set('sections_url', window.location.pathname);
    }
    btn.setAttribute('aria-busy', 'true');
    fetch((window.routes && window.routes.cart_add_url ? window.routes.cart_add_url : '/cart/add') + '.js', {
      method: 'POST', headers: { 'X-Requested-With': 'XMLHttpRequest', Accept: 'application/json' }, body: body
    })
      .then(function (r) { return r.json().then(function (j) { return { ok: r.ok, j: j }; }); })
      .then(function (res) {
        btn.removeAttribute('aria-busy');
        if (!res.ok || res.j.status) { throw new Error(res.j.description || res.j.message || 'Could not add to bag'); }
        var label = btn.textContent;
        btn.classList.add('bb-added'); btn.textContent = 'Added';
        setTimeout(function () { btn.classList.remove('bb-added'); btn.textContent = label; }, 1800);
        if (drawer && typeof drawer.renderContents === 'function') {
          drawer.classList.remove('is-empty');
          drawer.renderContents(res.j);
        } else {
          window.location.href = (window.routes && window.routes.cart_url) || '/cart';
        }
      })
      .catch(function (err) {
        btn.removeAttribute('aria-busy');
        var msg = form.querySelector('.bb-quick-add__msg');
        if (msg) { msg.textContent = err.message; msg.hidden = false; }
      });
  });
})();
