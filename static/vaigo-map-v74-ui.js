(() => {
  'use strict';

  const root = document.documentElement;
  const app = document.getElementById('wsApp');
  const sheet = document.getElementById('planSheet');
  if (!app) return;

  root.dataset.vaigoMapUi = 'v74';
  app.dataset.uiVersion = '74';

  // Mobile browsers change the visual viewport while the address bar/keyboard moves.
  // Keep the map shell stable without fighting the existing Mapbox resize logic.
  const syncViewport = () => {
    const vv = window.visualViewport;
    const h = vv?.height || window.innerHeight;
    const w = vv?.width || window.innerWidth;
    root.style.setProperty('--vg-viewport-h', `${Math.round(h)}px`);
    root.style.setProperty('--vg-viewport-w', `${Math.round(w)}px`);
    root.dataset.vaigoForm = w >= 1180 ? 'desktop' : w >= 768 ? 'tablet' : 'phone';
  };
  syncViewport();
  window.addEventListener('resize', syncViewport, { passive:true });
  window.visualViewport?.addEventListener('resize', syncViewport, { passive:true });

  // Keep labels in the new visual language while the legacy sheet-state JS remains
  // responsible for the actual drag/collapse behavior.
  const syncSheetCopy = () => {
    if (!sheet) return;
    const collapsed = sheet.classList.contains('sheet-collapsed');
    const btn = document.getElementById('plannerExpandToggle');
    const label = btn?.querySelector('span');
    if (label) label.textContent = collapsed ? 'Ver mais opções' : 'Mostrar menos';
  };
  syncSheetCopy();
  if (sheet && window.MutationObserver) {
    new MutationObserver(syncSheetCopy).observe(sheet,{attributes:true,attributeFilter:['class']});
  }

  // More descriptive title for the visible theme button.
  const syncThemeButton = () => {
    const black = root.dataset.vaigoTheme === 'black';
    document.querySelectorAll('.map-theme-action').forEach(btn => {
      btn.setAttribute('aria-label', black ? 'Usar aparência White' : 'Usar aparência Black');
      btn.setAttribute('title', black ? 'Usar White' : 'Usar Black');
    });
  };
  syncThemeButton();
  window.addEventListener('vaigo:themechange', syncThemeButton);

  // Prevent sideways sheet drift caused by browser gesture rounding.
  const lockHorizontalSheet = () => {
    if (!sheet) return;
    sheet.style.removeProperty('left');
    sheet.style.removeProperty('right');
  };
  sheet?.addEventListener('pointerup', lockHorizontalSheet, { passive:true });
  sheet?.addEventListener('pointercancel', lockHorizontalSheet, { passive:true });
})();
