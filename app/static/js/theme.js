/**
 * theme.js — Dark/Light mode toggle, CSS-first approach.
 *
 * Strategy:
 *  - The entire theme is handled by CSS variables scoped to :root[data-theme].
 *  - This file ONLY manages state: reads preference on load, writes the HTML
 *    attribute, and persists the choice to localStorage.
 *  - When nothing is saved, the system prefers-color-scheme is respected.
 */

(function () {
  'use strict';

  const STORAGE_KEY = 'theme';
  const LIGHT = 'light';
  const DARK  = 'dark';

  /** Return the active theme name. */
  function resolveTheme() {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved === LIGHT || saved === DARK) return saved;
    // Respect OS preference when no explicit choice has been saved.
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? DARK : LIGHT;
  }

  /** Apply theme to the document root. */
  function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    // Update aria-label on the toggle button (if already in the DOM).
    const btn = document.getElementById('btn-theme-toggle');
    if (btn) {
      btn.setAttribute('aria-label', theme === DARK ? 'Switch to light mode' : 'Switch to dark mode');
    }
  }

  /** Toggle current theme and persist. */
  function toggleTheme() {
    const current = document.documentElement.getAttribute('data-theme') || LIGHT;
    const next = current === DARK ? LIGHT : DARK;
    localStorage.setItem(STORAGE_KEY, next);
    applyTheme(next);
  }

  // Apply as early as possible (before first paint) to avoid flash.
  applyTheme(resolveTheme());

  // Wire up the toggle button after DOM is ready.
  document.addEventListener('DOMContentLoaded', function () {
    const btn = document.getElementById('btn-theme-toggle');
    if (btn) {
      btn.addEventListener('click', toggleTheme);
    }
  });
}());
