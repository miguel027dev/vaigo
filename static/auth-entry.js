(() => {
  const splash = document.querySelector('.sparker-splash');
  if (splash) {
    let seen = false;
    try { seen = sessionStorage.getItem('vaigo-html-splash-v60') === '1'; } catch (_) {}
    if (seen) {
      splash.classList.add('skip');
      setTimeout(() => splash.remove(), 40);
    } else {
      const hide = () => {
        splash.classList.add('is-hidden');
        try { sessionStorage.setItem('vaigo-html-splash-v60', '1'); } catch (_) {}
        setTimeout(() => splash.remove(), 500);
      };
      setTimeout(() => splash.classList.add('is-complete'), 240);
      setTimeout(hide, 980);
    }
  }

  const refreshIcons = () => {
    if (window.lucide) window.lucide.createIcons();
  };

  document.querySelectorAll('[data-password-toggle]').forEach((btn) => {
    btn.addEventListener('click', () => {
      const input = document.getElementById(btn.dataset.passwordToggle);
      if (!input) return;
      const show = input.type === 'password';
      input.type = show ? 'text' : 'password';
      btn.setAttribute('aria-label', show ? 'Ocultar senha' : 'Mostrar senha');
      btn.innerHTML = `<i data-lucide="${show ? 'eye-off' : 'eye'}" width="18"></i>`;
      refreshIcons();
      input.focus({ preventScroll: true });
    });
  });

  const authSheets = [...document.querySelectorAll('.auth-sheet')];
  const currentSheetId = () => decodeURIComponent((location.hash || '').replace(/^#/, ''));

  const setSheetState = (id, { focus = false } = {}) => {
    authSheets.forEach((sheet) => {
      const open = Boolean(id) && sheet.id === id;
      sheet.classList.toggle('is-open', open);
      sheet.setAttribute('aria-hidden', open ? 'false' : 'true');
      if (open && focus) {
        requestAnimationFrame(() => {
          const field = sheet.querySelector('input:not([type="hidden"]), select, button.sheet-submit');
          if (field) field.focus({ preventScroll: true });
        });
      }
    });
  };

  const openSheet = (id) => {
    const sheet = document.getElementById(id);
    if (!sheet) return;
    if (currentSheetId() !== id) {
      try { history.pushState(null, '', `#${encodeURIComponent(id)}`); } catch (_) {}
    }
    setSheetState(id, { focus: true });
  };

  const closeSheets = () => {
    setSheetState('');
    if (location.hash) {
      try { history.replaceState(null, '', `${location.pathname}${location.search}`); } catch (_) {}
    }
  };

  document.querySelectorAll('[data-sheet-open]').forEach((trigger) => {
    trigger.addEventListener('click', (event) => {
      event.preventDefault();
      openSheet(trigger.getAttribute('data-sheet-open'));
    });
  });

  document.querySelectorAll('[data-sheet-close]').forEach((trigger) => {
    trigger.addEventListener('click', (event) => {
      event.preventDefault();
      closeSheets();
    });
  });

  window.addEventListener('hashchange', () => setSheetState(currentSheetId()));
  window.addEventListener('popstate', () => setSheetState(currentSheetId()));
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && authSheets.some((sheet) => sheet.classList.contains('is-open'))) closeSheets();
  });
  setSheetState(currentSheetId());

  document.querySelectorAll('[data-google-auth]').forEach((link) => {
    link.addEventListener('click', () => {
      if (link.getAttribute('aria-disabled') === 'true') return;
      link.classList.add('oauth-loading');
      link.setAttribute('aria-busy', 'true');
    });
  });

  document.querySelectorAll('.sheet-form').forEach((form) => {
    form.addEventListener('submit', () => {
      if (!form.checkValidity()) return;
      const submit = form.querySelector('.sheet-submit');
      if (!submit || submit.disabled) return;
      submit.disabled = true;
      submit.dataset.originalText = submit.textContent;
      submit.textContent = document.querySelector('[data-auth-page="register"]') ? 'Criando conta…' : 'Entrando…';
    });
  });
})();
