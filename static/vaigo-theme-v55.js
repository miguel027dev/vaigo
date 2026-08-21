(() => {
  'use strict';
  const KEY = 'vaigo.theme.v55';
  const root = document.documentElement;
  const meta = document.querySelector('meta[name="theme-color"]');

  function normalize(value){ return value === 'black' ? 'black' : 'light'; }
  function read(){
    try { return normalize(localStorage.getItem(KEY)); } catch (_) { return normalize(root.dataset.vaigoTheme); }
  }
  function syncControls(theme){
    document.querySelectorAll('[data-vaigo-theme-toggle]').forEach(btn => {
      const black = theme === 'black';
      btn.classList.toggle('is-black', black);
      btn.setAttribute('aria-pressed', black ? 'true' : 'false');
      const state = btn.querySelector('[data-theme-state]');
      if(state) state.textContent = black ? 'Black ativado' : 'Tema claro';
      const label = btn.querySelector('[data-theme-action]');
      if(label) label.textContent = black ? 'Usar claro' : 'Ativar Black';
    });
  }
  function apply(theme, persist = true){
    theme = normalize(theme);
    root.dataset.vaigoTheme = theme;
    root.style.colorScheme = theme === 'black' ? 'dark' : 'light';
    if(document.body) document.body.dataset.vaigoTheme = theme;
    if(meta) meta.setAttribute('content', theme === 'black' ? '#07070A' : '#F6F7FB');
    if(persist){ try { localStorage.setItem(KEY, theme); } catch (_) {} }
    syncControls(theme);
    window.dispatchEvent(new CustomEvent('vaigo:themechange', { detail: { theme } }));
    return theme;
  }
  function toggle(){ return apply(read() === 'black' ? 'light' : 'black'); }

  window.VAIGOTheme = { key: KEY, get: read, set: apply, toggle };
  const boot = read();
  apply(boot, false);

  document.addEventListener('click', e => {
    const btn = e.target.closest?.('[data-vaigo-theme-toggle]');
    if(!btn) return;
    e.preventDefault();
    toggle();
  });
  document.addEventListener('DOMContentLoaded', () => syncControls(read()));
})();
