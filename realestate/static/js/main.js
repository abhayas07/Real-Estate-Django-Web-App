/* =========================================================
   Real Estate — Portal Interactive Scripts & Animations
   ========================================================= */

(function () {
  'use strict';

  /* Update current year in footer */
  var yearEl = document.querySelector('.year');
  if (yearEl) {
    yearEl.textContent = new Date().getFullYear();
  }

  /* Navbar shrink on scroll + back-to-top visibility */
  var navbar = document.getElementById('main-navbar');
  var backToTop = document.getElementById('back-to-top');

  function handleScroll() {
    var scrollPos = window.pageYOffset || document.documentElement.scrollTop;
    if (navbar) {
      navbar.classList.toggle('navbar-scrolled', scrollPos > 20);
    }
    if (backToTop) {
      backToTop.classList.toggle('visible', scrollPos > 350);
    }
  }

  window.addEventListener('scroll', handleScroll, { passive: true });
  handleScroll();

  if (backToTop) {
    backToTop.addEventListener('click', function (e) {
      e.preventDefault();
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }

  /* Auto-dismiss flash messages with smooth slide out */
  var alerts = document.querySelectorAll('#message .alert');
  alerts.forEach(function (alert) {
    setTimeout(function () {
      alert.style.transition = 'all 0.5s cubic-bezier(0.16, 1, 0.3, 1)';
      alert.style.opacity = '0';
      alert.style.transform = 'translateY(-15px)';
      setTimeout(function () {
        if (alert && alert.parentNode) {
          alert.parentNode.removeChild(alert);
        }
      }, 500);
    }, 5000);
  });

  /* Close mobile navbar after clicking link */
  var navCollapse = document.getElementById('navbarNavAltMarkup');
  if (navCollapse) {
    navCollapse.addEventListener('click', function (e) {
      if (e.target.closest('a:not(.dropdown-toggle), button') && navCollapse.classList.contains('show')) {
        if (window.jQuery) {
          window.jQuery(navCollapse).collapse('hide');
        }
      }
    });
  }

  /* Password Toggle (show/hide password) */
  document.addEventListener('click', function (e) {
    var toggleBtn = e.target.closest('.auth-password-toggle');
    if (toggleBtn) {
      e.preventDefault();
      var targetInputId = toggleBtn.getAttribute('data-target') || 'password';
      var passwordInput = document.getElementById(targetInputId) || toggleBtn.parentElement.querySelector('input');
      var icon = toggleBtn.querySelector('i');
      
      if (passwordInput) {
        if (passwordInput.type === 'password') {
          passwordInput.type = 'text';
          if (icon) {
            icon.classList.remove('fa-eye');
            icon.classList.add('fa-eye-slash');
          }
        } else {
          passwordInput.type = 'password';
          if (icon) {
            icon.classList.remove('fa-eye-slash');
            icon.classList.add('fa-eye');
          }
        }
      }
    }
  });

  /* =========================================================
     Day / Night Theme Controller
     Values: 'day' | 'night'
     Stored in localStorage('realestate_theme')
     ========================================================= */
  var themeToggleBtn = document.getElementById('theme-toggle');

  function getPreferredTheme() {
    var saved = localStorage.getItem('realestate_theme');
    if (saved === 'day' || saved === 'night') {
      return saved;
    }
    // Fallback to system preference
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      return 'night';
    }
    return 'day';
  }

  function applyTheme(theme, animate) {
    if (theme !== 'day' && theme !== 'night') {
      theme = 'day';
    }

    document.documentElement.setAttribute('data-theme', theme);
    try {
      localStorage.setItem('realestate_theme', theme);
    } catch (e) {}

    // Update Toggle Button Accessibility States
    if (themeToggleBtn) {
      var isNight = (theme === 'night');
      themeToggleBtn.setAttribute('aria-checked', isNight ? 'true' : 'false');
      themeToggleBtn.setAttribute(
        'aria-label',
        isNight ? 'Current theme: Night mode. Switch to Day mode' : 'Current theme: Day mode. Switch to Night mode'
      );
      themeToggleBtn.setAttribute(
        'title',
        isNight ? 'Switch to Day mode' : 'Switch to Night mode'
      );

      if (animate) {
        themeToggleBtn.style.transform = 'scale(1.08)';
        setTimeout(function () {
          themeToggleBtn.style.transform = '';
        }, 300);
      }
    }
  }

  // Initialize theme on script execution
  var currentTheme = getPreferredTheme();
  applyTheme(currentTheme, false);

  // Toggle click & keyboard listeners
  if (themeToggleBtn) {
    themeToggleBtn.addEventListener('click', function (e) {
      e.preventDefault();
      var active = document.documentElement.getAttribute('data-theme') || getPreferredTheme();
      var nextTheme = active === 'night' ? 'day' : 'night';
      applyTheme(nextTheme, true);
    });

    themeToggleBtn.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' || e.key === ' ' || e.code === 'Space') {
        e.preventDefault();
        var active = document.documentElement.getAttribute('data-theme') || getPreferredTheme();
        var nextTheme = active === 'night' ? 'day' : 'night';
        applyTheme(nextTheme, true);
      }
    });
  }

  // Listen to system preference changes if user hasn't set explicit manual preference
  if (window.matchMedia) {
    try {
      window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function (e) {
        var manualChoice = localStorage.getItem('realestate_theme');
        if (!manualChoice) {
          applyTheme(e.matches ? 'night' : 'day', true);
        }
      });
    } catch (err) {}
  }

  /* =========================================================
     Reusable Scroll Reveal System (IntersectionObserver)
     Classes: .reveal, .reveal-left, .reveal-right, .reveal-scale,
              .listing-preview, .service-box
     ========================================================= */
  var revealSelector = '.reveal, .reveal-left, .reveal-right, .reveal-scale, .listing-preview, .service-box, .team-card, .spec-tile, .realtor-card, .empty-state';
  var revealElements = document.querySelectorAll(revealSelector);

  var prefersReducedMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  if ('IntersectionObserver' in window && !prefersReducedMotion && revealElements.length > 0) {
    // Dynamic staggering for grid children
    var rows = document.querySelectorAll('.row');
    rows.forEach(function (row) {
      var rowItems = row.querySelectorAll('.reveal, .listing-preview, .service-box');
      rowItems.forEach(function (item, idx) {
        if (!item.classList.contains('delay-50') &&
            !item.classList.contains('delay-100') &&
            !item.classList.contains('delay-150') &&
            !item.classList.contains('delay-200') &&
            !item.classList.contains('delay-250') &&
            !item.classList.contains('delay-300')) {
          var staggerStep = (idx % 3 + 1) * 90; // ~90ms, 180ms, 270ms
          item.style.transitionDelay = staggerStep + 'ms';
        }
      });
    });

    var revealObserver = new IntersectionObserver(function (entries, observer) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('revealed');
          observer.unobserve(entry.target); // Animate only once!
        }
      });
    }, {
      threshold: 0.08,
      rootMargin: '0px 0px -40px 0px'
    });

    revealElements.forEach(function (el) {
      revealObserver.observe(el);
    });
  } else {
    // Immediately reveal if IntersectionObserver not supported or user prefers reduced motion
    revealElements.forEach(function (el) {
      el.classList.add('revealed');
    });
  }

  /* =========================================================
     Background Tone System Controller
     Tones: soft-slate (#F8FAFC, Default), slate-100 (#F1F5F9), pure-white (#FFFFFF), warm-linen (#FDFBF7)
     ========================================================= */
  var bgToneNames = {
    'soft-slate': 'Soft Slate (#F8FAFC)',
    'slate-100': 'Slate-100 (#F1F5F9)',
    'pure-white': 'Pure White (#FFFFFF)',
    'warm-linen': 'Warm Linen (#FDFBF7)'
  };

  var bgToneSwatches = {
    'soft-slate': '#f8fafc',
    'slate-100': '#f1f5f9',
    'pure-white': '#ffffff',
    'warm-linen': '#fdfbf7'
  };

  function setBackgroundTone(tone) {
    if (!bgToneNames[tone]) tone = 'soft-slate';
    document.documentElement.setAttribute('data-bg', tone);
    try {
      localStorage.setItem('realestate_bg_tone', tone);
    } catch (e) {}

    // Update Topbar buttons
    document.querySelectorAll('.topbar-tone-btn').forEach(function (btn) {
      btn.classList.toggle('active', btn.getAttribute('data-bg-tone') === tone);
    });

    // Update Footer buttons
    document.querySelectorAll('.footer-tone-btn').forEach(function (btn) {
      btn.classList.toggle('active', btn.getAttribute('data-bg-tone') === tone);
    });

    // Update Widget buttons
    document.querySelectorAll('.bg-option-item').forEach(function (btn) {
      var isActive = btn.getAttribute('data-bg-tone') === tone;
      btn.classList.toggle('active', isActive);
      btn.setAttribute('aria-pressed', isActive ? 'true' : 'false');
    });

    // Update Widget Toggle Trigger Text & Swatch
    var activeNameEl = document.getElementById('widget-active-name');
    var activeSwatchEl = document.getElementById('widget-active-swatch');
    if (activeNameEl) {
      activeNameEl.textContent = tone === 'soft-slate' ? 'Soft Slate' : (tone === 'slate-100' ? 'Slate-100' : (tone === 'pure-white' ? 'Pure White' : 'Warm Linen'));
    }
    if (activeSwatchEl) {
      activeSwatchEl.style.backgroundColor = bgToneSwatches[tone];
    }
  }

  // Initialize current active tone on DOM ready
  var initialTone = localStorage.getItem('realestate_bg_tone') || 'soft-slate';
  setBackgroundTone(initialTone);

  // Global click listeners for all background tone buttons and widget
  document.addEventListener('click', function (e) {
    var toneBtn = e.target.closest('[data-bg-tone]');
    if (toneBtn) {
      e.preventDefault();
      var selectedTone = toneBtn.getAttribute('data-bg-tone');
      if (selectedTone) {
        setBackgroundTone(selectedTone);
      }
    }

    // Toggle widget popup
    var widgetToggle = e.target.closest('#bg-tone-widget-toggle');
    var widgetPopup = document.getElementById('bg-tone-popup');
    var widget = document.getElementById('bg-tone-widget');
    if (widgetToggle && widgetPopup) {
      e.preventDefault();
      var isExpanded = widget.classList.toggle('open');
      widgetToggle.setAttribute('aria-expanded', isExpanded ? 'true' : 'false');
      return;
    }

    var closeBtn = e.target.closest('#bg-tone-close-btn');
    if (closeBtn && widget) {
      widget.classList.remove('open');
      var toggleBtn = document.getElementById('bg-tone-widget-toggle');
      if (toggleBtn) toggleBtn.setAttribute('aria-expanded', 'false');
      return;
    }

    // Close when clicking outside widget
    if (widget && widget.classList.contains('open') && !e.target.closest('#bg-tone-widget')) {
      widget.classList.remove('open');
      var toggleBtn = document.getElementById('bg-tone-widget-toggle');
      if (toggleBtn) toggleBtn.setAttribute('aria-expanded', 'false');
    }
  });

})();
