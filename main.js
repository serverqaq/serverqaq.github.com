/* ============================================================
   Danyi Wang — main.js
   Modules: lang toggle, works filter, lightbox, mobile nav,
            scroll-aware header, fade-in observer
   ============================================================ */

(function () {
  'use strict';

  /* ── 1. Language Toggle ─────────────────────────────────── */
  const LANG_KEY = 'dw_lang';
  let currentLang = localStorage.getItem(LANG_KEY) || 'en';

  function applyLang(lang) {
    currentLang = lang;
    localStorage.setItem(LANG_KEY, lang);

    document.querySelectorAll('[data-en]').forEach(function (el) {
      const text = lang === 'cn' ? el.dataset.cn : el.dataset.en;
      if (text !== undefined) el.textContent = text;
    });

    // Update toggle button label
    const btn = document.getElementById('lang-toggle');
    if (btn) btn.textContent = lang === 'cn' ? 'EN' : '中文';

    // Update html lang attribute
    document.documentElement.lang = lang === 'cn' ? 'zh' : 'en';
  }

  function initLang() {
    const btn = document.getElementById('lang-toggle');
    if (!btn) return;
    btn.addEventListener('click', function () {
      applyLang(currentLang === 'en' ? 'cn' : 'en');
    });
    applyLang(currentLang);
  }

  /* ── 2. Works Filter ────────────────────────────────────── */
  function initFilter() {
    const bar = document.querySelector('.filter-bar');
    if (!bar) return;

    const buttons = bar.querySelectorAll('.filter-btn');
    const cards   = document.querySelectorAll('.artwork-card[data-category]');

    buttons.forEach(function (btn) {
      btn.addEventListener('click', function () {
        // Active state
        buttons.forEach(function (b) { b.classList.remove('active'); });
        btn.classList.add('active');

        const filter = btn.dataset.filter;

        cards.forEach(function (card) {
          if (filter === 'all' || card.dataset.category === filter) {
            card.classList.remove('hidden');
          } else {
            card.classList.add('hidden');
          }
        });
      });
    });
  }

  /* ── 3. Lightbox ────────────────────────────────────────── */
  let lightboxItems = [];
  let lightboxIndex = 0;

  function buildLightboxItems() {
    lightboxItems = Array.from(
      document.querySelectorAll('.artwork-card[data-src]')
    );
  }

  function openLightbox(index) {
    const lb = document.getElementById('lightbox');
    if (!lb) return;

    lightboxIndex = index;
    const item = lightboxItems[index];
    if (!item) return;

    const img   = lb.querySelector('.lightbox__img');
    const title = lb.querySelector('.lightbox__title');
    const meta  = lb.querySelector('.lightbox__meta');

    img.src = item.dataset.src;
    img.alt = item.dataset.title || '';

    if (title) {
      title.textContent = item.dataset.title || '';
    }
    if (meta) {
      const parts = [];
      if (item.dataset.medium) parts.push(item.dataset.medium);
      if (item.dataset.year)   parts.push(item.dataset.year);
      meta.textContent = parts.join(' · ');
    }

    lb.classList.add('open');
    document.body.style.overflow = 'hidden';
  }

  function closeLightbox() {
    const lb = document.getElementById('lightbox');
    if (!lb) return;
    lb.classList.remove('open');
    document.body.style.overflow = '';
  }

  function navigateLightbox(dir) {
    const visible = lightboxItems.filter(function (item) {
      return !item.classList.contains('hidden');
    });
    const currentVisible = visible.indexOf(lightboxItems[lightboxIndex]);
    const nextVisible    = (currentVisible + dir + visible.length) % visible.length;
    const nextItem       = visible[nextVisible];
    lightboxIndex        = lightboxItems.indexOf(nextItem);
    openLightbox(lightboxIndex);
  }

  function initLightbox() {
    buildLightboxItems();

    // Open on card click
    lightboxItems.forEach(function (item, index) {
      item.addEventListener('click', function () {
        openLightbox(index);
      });
    });

    const lb = document.getElementById('lightbox');
    if (!lb) return;

    // Close button
    const closeBtn = lb.querySelector('.lightbox__close');
    if (closeBtn) closeBtn.addEventListener('click', closeLightbox);

    // Nav buttons
    const prevBtn = lb.querySelector('.lightbox__prev');
    const nextBtn = lb.querySelector('.lightbox__next');
    if (prevBtn) prevBtn.addEventListener('click', function () { navigateLightbox(-1); });
    if (nextBtn) nextBtn.addEventListener('click', function () { navigateLightbox(1); });

    // Click backdrop to close
    lb.addEventListener('click', function (e) {
      if (e.target === lb) closeLightbox();
    });

    // Keyboard navigation
    document.addEventListener('keydown', function (e) {
      if (!lb.classList.contains('open')) return;
      if (e.key === 'Escape')     closeLightbox();
      if (e.key === 'ArrowLeft')  navigateLightbox(-1);
      if (e.key === 'ArrowRight') navigateLightbox(1);
    });
  }

  /* ── 4. Mobile nav ──────────────────────────────────────── */
  function initMobileNav() {
    const hamburger = document.querySelector('.nav-hamburger');
    const drawer    = document.querySelector('.nav-drawer');
    if (!hamburger || !drawer) return;

    hamburger.addEventListener('click', function () {
      const open = drawer.classList.toggle('open');
      hamburger.setAttribute('aria-expanded', open);
    });

    // Close on outside click
    document.addEventListener('click', function (e) {
      if (!drawer.contains(e.target) && !hamburger.contains(e.target)) {
        drawer.classList.remove('open');
        hamburger.setAttribute('aria-expanded', 'false');
      }
    });

    // Close on nav link click
    drawer.querySelectorAll('a').forEach(function (link) {
      link.addEventListener('click', function () {
        drawer.classList.remove('open');
      });
    });
  }

  /* ── 5. Scroll-aware header ─────────────────────────────── */
  function initScrollHeader() {
    const header = document.querySelector('.site-header');
    if (!header) return;

    function update() {
      header.classList.toggle('scrolled', window.scrollY > 60);
    }

    window.addEventListener('scroll', update, { passive: true });
    update();
  }

  /* ── 6. Fade-in on scroll ───────────────────────────────── */
  function initFadeIn() {
    const els = document.querySelectorAll('.fade-up');
    if (!els.length) return;

    if ('IntersectionObserver' in window) {
      const obs = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add('visible');
            obs.unobserve(entry.target);
          }
        });
      }, { threshold: 0.12 });

      els.forEach(function (el) { obs.observe(el); });
    } else {
      // Fallback: just make them visible
      els.forEach(function (el) { el.classList.add('visible'); });
    }
  }

  /* ── Init all ───────────────────────────────────────────── */
  document.addEventListener('DOMContentLoaded', function () {
    initLang();
    initFilter();
    initLightbox();
    initMobileNav();
    initScrollHeader();
    initFadeIn();
  });

})();
