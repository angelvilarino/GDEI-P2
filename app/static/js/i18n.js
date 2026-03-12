/**
 * i18n.js — Lightweight client-side internationalisation.
 *
 * Strategy:
 *  - Supported languages: 'es' (default) and 'en'.
 *  - Translation strings live in /static/i18n/<lang>.json.
 *  - Elements that need translating carry a data-i18n="key" attribute.
 *  - Active language is persisted in localStorage under the key 'lang'.
 *  - Changing language re-applies translations in-place without reloading.
 */

(function () {
  'use strict';

  const STORAGE_KEY  = 'lang';
  const DEFAULT_LANG = 'es';
  const SUPPORTED    = ['es', 'en'];

  let translations  = {};
  let currentLang   = DEFAULT_LANG;

  /** Return the language that should be active. */
  function resolveLanguage() {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved && SUPPORTED.includes(saved)) return saved;
    // Fallback: browser language prefix.
    const bcp = (navigator.language || '').slice(0, 2).toLowerCase();
    return SUPPORTED.includes(bcp) ? bcp : DEFAULT_LANG;
  }

  /** Fetch the JSON file for the given language, then apply translations. */
  function loadLanguage(lang) {
    // Use the Flask static endpoint path.
    const url = '/static/i18n/' + lang + '.json';
    return fetch(url)
      .then(function (r) {
        if (!r.ok) throw new Error('Cannot load ' + url);
        return r.json();
      })
      .then(function (data) {
        translations = data;
        currentLang  = lang;
        localStorage.setItem(STORAGE_KEY, lang);
        applyTranslations();
        updateToggleButton();
      })
      .catch(function (err) {
        console.warn('[i18n] ' + err.message);
      });
  }

  /** Walk the DOM and replace text nodes for elements carrying data-i18n. */
  function applyTranslations() {
    document.querySelectorAll('[data-i18n]').forEach(function (el) {
      const key = el.getAttribute('data-i18n');
      if (Object.prototype.hasOwnProperty.call(translations, key)) {
        el.textContent = translations[key];
      }
    });
    // Update the <html lang> attribute for accessibility.
    document.documentElement.setAttribute('lang', currentLang);
  }

  /** Update the label of the language toggle button. */
  function updateToggleButton() {
    const btn = document.getElementById('btn-lang-toggle');
    if (!btn) return;
    // Show the label for the *other* language (what you'll switch TO).
    const key = 'toggle_lang';
    if (Object.prototype.hasOwnProperty.call(translations, key)) {
      btn.textContent = translations[key];
    }
    btn.setAttribute('aria-label', 'Switch language (' + currentLang + ')');
  }

  /** Toggle between supported languages and reload translations. */
  function toggleLanguage() {
    const next = currentLang === 'es' ? 'en' : 'es';
    loadLanguage(next);
  }

  // ----------------------------------------------------------------
  // Initialisation
  // ----------------------------------------------------------------
  document.addEventListener('DOMContentLoaded', function () {
    currentLang = resolveLanguage();
    loadLanguage(currentLang);

    const btn = document.getElementById('btn-lang-toggle');
    if (btn) {
      btn.addEventListener('click', toggleLanguage);
    }
  });

  // Expose minimal public API for templates that need it.
  window.i18n = {
    t: function (key) {
      return Object.prototype.hasOwnProperty.call(translations, key)
        ? translations[key]
        : key;
    },
    setLanguage: loadLanguage,
    getLanguage: function () { return currentLang; }
  };
}());
