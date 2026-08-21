(() => {
  'use strict';

  const MODE_KEY = 'vaigo.theme.mode.v56';
  const LEGACY_KEY = 'vaigo.theme.v55';
  const root = document.documentElement;
  const meta = document.querySelector('meta[name="theme-color"]');
  let timer = null;

  const normalizeMode = (value) => ['auto', 'light', 'black'].includes(value) ? value : 'auto';
  const localHour = () => new Date().getHours();
  const localTimeZone = () => {
    try { return Intl.DateTimeFormat().resolvedOptions().timeZone || 'Horário local'; }
    catch (_) { return 'Horário local'; }
  };
  const resolvedFromMode = (mode) => {
    if (mode === 'light' || mode === 'black') return mode;
    const hour = localHour();
    return (hour >= 19 || hour < 7) ? 'black' : 'light';
  };

  function storedMode() {
    try {
      const saved = localStorage.getItem(MODE_KEY);
      if (saved) return normalizeMode(saved);
      // Migration: keep an explicitly selected old Black mode. Old light mode
      // becomes Auto so existing users get the new 19:00 behavior by default.
      const legacy = localStorage.getItem(LEGACY_KEY);
      return legacy === 'black' ? 'black' : 'auto';
    } catch (_) {
      return normalizeMode(root.dataset.vaigoThemeMode);
    }
  }

  function updateControlState(mode, resolved) {
    document.querySelectorAll('[data-vaigo-theme-option]').forEach((button) => {
      const active = button.dataset.vaigoThemeOption === mode;
      button.classList.toggle('active', active);
      button.setAttribute('aria-pressed', active ? 'true' : 'false');
    });

    document.querySelectorAll('[data-theme-state]').forEach((node) => {
      if (mode === 'auto') {
        node.textContent = resolved === 'black'
          ? 'Automático · Black ativo até 07:00'
          : 'Automático · Black ativa às 19:00';
      } else {
        node.textContent = mode === 'black' ? 'Black sempre ativo' : 'Claro sempre ativo';
      }
    });

    document.querySelectorAll('[data-theme-timezone]').forEach((node) => {
      node.textContent = `${localTimeZone()} · ${String(localHour()).padStart(2, '0')}:${String(new Date().getMinutes()).padStart(2, '0')}`;
    });
  }

  function applyResolved(mode, { persist = false, reason = 'manual' } = {}) {
    mode = normalizeMode(mode);
    const resolved = resolvedFromMode(mode);
    const previous = root.dataset.vaigoTheme;

    root.dataset.vaigoThemeMode = mode;
    root.dataset.vaigoTheme = resolved;
    root.style.colorScheme = resolved === 'black' ? 'dark' : 'light';
    if (document.body) {
      document.body.dataset.vaigoThemeMode = mode;
      document.body.dataset.vaigoTheme = resolved;
    }
    if (meta) meta.setAttribute('content', resolved === 'black' ? '#07080D' : '#F7F8FC');

    if (persist) {
      try {
        localStorage.setItem(MODE_KEY, mode);
        // Keep the old key in sync for pages cached from V55.
        localStorage.setItem(LEGACY_KEY, resolved);
      } catch (_) {}
    }

    updateControlState(mode, resolved);
    if (previous !== resolved || reason === 'manual') {
      window.dispatchEvent(new CustomEvent('vaigo:themechange', {
        detail: {
          theme: resolved,
          mode,
          automatic: mode === 'auto',
          hour: localHour(),
          timeZone: localTimeZone(),
          reason,
        },
      }));
    }
    return resolved;
  }

  function setMode(mode) {
    return applyResolved(mode, { persist: true, reason: 'manual' });
  }

  function refresh(reason = 'clock') {
    return applyResolved(storedMode(), { persist: false, reason });
  }

  function scheduleClockCheck() {
    clearInterval(timer);
    timer = setInterval(() => {
      if (document.visibilityState === 'visible') refresh('clock');
    }, 60 * 1000);
  }

  window.VAIGOTheme = {
    key: MODE_KEY,
    getMode: storedMode,
    get: () => root.dataset.vaigoTheme || resolvedFromMode(storedMode()),
    setMode,
    set: setMode,
    resolve: resolvedFromMode,
    refresh,
    timeZone: localTimeZone,
  };

  applyResolved(storedMode(), { persist: false, reason: 'boot' });
  scheduleClockCheck();

  document.addEventListener('click', (event) => {
    const button = event.target.closest?.('[data-vaigo-theme-option]');
    if (!button) return;
    event.preventDefault();
    setMode(button.dataset.vaigoThemeOption || 'auto');
  });

  // Compatibility with V55 toggle markup if a cached template survives a deploy.
  document.addEventListener('click', (event) => {
    const legacyToggle = event.target.closest?.('[data-vaigo-theme-toggle]');
    if (!legacyToggle || event.target.closest?.('[data-vaigo-theme-option]')) return;
    event.preventDefault();
    setMode(root.dataset.vaigoTheme === 'black' ? 'light' : 'black');
  });

  document.addEventListener('DOMContentLoaded', () => refresh('dom-ready'));
  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible') refresh('visibility');
  });
  window.addEventListener('focus', () => refresh('focus'));
  window.addEventListener('storage', (event) => {
    if (event.key === MODE_KEY || event.key === LEGACY_KEY) refresh('storage');
  });
})();
