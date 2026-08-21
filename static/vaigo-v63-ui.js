(() => {
  const app = document.getElementById('wsApp');
  const planner = document.getElementById('planSheet');
  const recenter = document.getElementById('recenterBtn');
  const toggle = document.getElementById('plannerExpandToggle');
  if (!app || !planner || !recenter) return;

  const planningMode = () => !document.body.classList.contains('body-nav') && !planner.classList.contains('hidden');
  let raf = 0;
  const syncPlannerGeometry = () => {
    cancelAnimationFrame(raf);
    raf = requestAnimationFrame(() => {
      if (!planningMode()) {
        recenter.style.removeProperty('--v63-recenter-bottom');
        return;
      }
      const appRect = app.getBoundingClientRect();
      const rect = planner.getBoundingClientRect();
      const gap = window.innerWidth >= 900 ? 12 : 10;
      const bottom = Math.max(16, appRect.bottom - rect.top + gap);
      recenter.style.setProperty('--v63-recenter-bottom', `${Math.round(bottom)}px`);
      if (toggle) toggle.setAttribute('aria-expanded', String(planner.classList.contains('sheet-expanded')));
    });
  };

  if (toggle) {
    toggle.addEventListener('click', () => {
      const expand = !planner.classList.contains('sheet-expanded');
      planner.classList.toggle('sheet-expanded', expand);
      planner.classList.toggle('sheet-collapsed', !expand);
      toggle.setAttribute('aria-expanded', String(expand));
      syncPlannerGeometry();
    });
  }

  const observer = new MutationObserver(syncPlannerGeometry);
  observer.observe(planner, { attributes: true, attributeFilter: ['class', 'style'] });
  const sizeObserver = window.ResizeObserver ? new ResizeObserver(syncPlannerGeometry) : null;
  if (sizeObserver) sizeObserver.observe(planner);
  window.addEventListener('resize', syncPlannerGeometry, { passive: true });
  window.addEventListener('orientationchange', syncPlannerGeometry, { passive: true });
  document.addEventListener('DOMContentLoaded', syncPlannerGeometry, { once: true });
  setTimeout(syncPlannerGeometry, 0);
  setTimeout(syncPlannerGeometry, 250);
  setTimeout(syncPlannerGeometry, 900);
})();
