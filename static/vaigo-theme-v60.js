(() => {
  'use strict';

  const MODE_KEY = 'vaigo.theme.mode.v60';
  const LEGACY_KEYS = ['vaigo.theme.mode.v57', 'vaigo.theme.mode.v56', 'vaigo.theme.v55'];
  const root = document.documentElement;
  const meta = document.querySelector('meta[name="theme-color"]');

  const normalize = (value) => value === 'black' ? 'black' : 'light';

  function storedMode() {
    try {
      const direct = localStorage.getItem(MODE_KEY);
      if (direct) return normalize(direct);
      // Only carry an old theme forward when the user explicitly chose Black.
      for (const key of LEGACY_KEYS) {
        if (localStorage.getItem(key) === 'black') return 'black';
      }
    } catch (_) {}
    return 'light';
  }

  function updateControls(mode) {
    document.querySelectorAll('[data-vaigo-theme-option]').forEach((button) => {
      const active = normalize(button.dataset.vaigoThemeOption) === mode;
      button.classList.toggle('active', active);
      button.setAttribute('aria-pressed', active ? 'true' : 'false');
    });

    document.querySelectorAll('[data-vaigo-theme-label]').forEach((node) => {
      node.textContent = mode === 'black' ? 'Usar White' : 'Usar Black';
    });

    document.querySelectorAll('[data-vaigo-theme-toggle]').forEach((button) => {
      button.classList.toggle('is-black', mode === 'black');
      button.setAttribute('aria-pressed', mode === 'black' ? 'true' : 'false');
    });

    document.querySelectorAll('[data-theme-state]').forEach((node) => {
      node.textContent = mode === 'black' ? 'Black ativado' : 'White padrão';
    });
    document.querySelectorAll('[data-theme-timezone]').forEach((node) => {
      node.textContent = 'Preferência salva neste dispositivo';
    });
  }

  function apply(mode, { persist = false, reason = 'manual' } = {}) {
    mode = normalize(mode);
    const previous = root.dataset.vaigoTheme;
    root.dataset.vaigoThemeMode = mode;
    root.dataset.vaigoTheme = mode;
    root.style.colorScheme = mode === 'black' ? 'dark' : 'light';
    if (document.body) {
      document.body.dataset.vaigoThemeMode = mode;
      document.body.dataset.vaigoTheme = mode;
    }
    if (meta) meta.setAttribute('content', mode === 'black' ? '#07080D' : '#F7F8FC');

    if (persist) {
      try {
        localStorage.setItem(MODE_KEY, mode);
        // Clear automatic legacy behavior so night time cannot unexpectedly change White to Black.
        for (const key of LEGACY_KEYS) localStorage.removeItem(key);
      } catch (_) {}
    }

    updateControls(mode);
    if (previous !== mode || reason === 'manual') {
      window.dispatchEvent(new CustomEvent('vaigo:themechange', {
        detail: { theme: mode, mode, automatic: false, reason },
      }));
    }
    return mode;
  }

  function setMode(mode) { return apply(mode, { persist: true, reason: 'manual' }); }
  function refresh(reason = 'refresh') { return apply(storedMode(), { persist: false, reason }); }

  window.VAIGOTheme = {
    key: MODE_KEY,
    getMode: storedMode,
    get: () => root.dataset.vaigoTheme || storedMode(),
    setMode,
    set: setMode,
    refresh,
    resolve: normalize,
  };

  apply(storedMode(), { persist: false, reason: 'boot' });

  document.addEventListener('click', (event) => {
    const option = event.target.closest?.('[data-vaigo-theme-option]');
    if (option) {
      event.preventDefault();
      setMode(option.dataset.vaigoThemeOption);
      return;
    }
    const toggle = event.target.closest?.('[data-vaigo-theme-toggle]');
    if (toggle) {
      event.preventDefault();
      setMode(root.dataset.vaigoTheme === 'black' ? 'light' : 'black');
    }
  });

  document.addEventListener('DOMContentLoaded', () => refresh('dom-ready'));
  window.addEventListener('storage', (event) => {
    if (event.key === MODE_KEY || LEGACY_KEYS.includes(event.key)) refresh('storage');
  });
})();
