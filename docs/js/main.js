/* ═══════════════════════════════════════════════════════════
   MantisClaw — GitHub Pages JavaScript
   Scroll reveal animation
   Language switcher is inline in index.html for instant load.
   ═══════════════════════════════════════════════════════════ */

// ─── Scroll reveal ───
var obs = new IntersectionObserver(
  function(entries) {
    entries.forEach(function(e) {
      if (e.isIntersecting) e.target.classList.add('visible');
    });
  },
  { threshold: 0.08, rootMargin: '0px 0px -30px 0px' }
);
document.querySelectorAll('.reveal').forEach(function(el) { obs.observe(el); });
