(function () {
  if (window.__ukMotion) return; window.__ukMotion = true;
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  function init() {
    var els = document.querySelectorAll('[data-uk-reveal]:not(.is-in)');
    if (reduce || !('IntersectionObserver' in window)) { els.forEach(function (e) { e.classList.add('is-in'); }); return; }
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('is-in'); io.unobserve(e.target); } });
    }, { rootMargin: '0px 0px -12% 0px', threshold: 0.05 });
    els.forEach(function (e) { io.observe(e); });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
  document.addEventListener('shopify:section:load', init);
})();
