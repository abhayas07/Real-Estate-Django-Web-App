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
      navbar.classList.toggle('navbar-scrolled', scrollPos > 30);
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

  /* Scroll reveal animations */
  var revealTargets = document.querySelectorAll(
    '.listing-preview, .service-box, .team-card, .spec-tile, .realtor-card, .reveal-item, .empty-state'
  );

  if ('IntersectionObserver' in window && revealTargets.length > 0 && window.matchMedia('(prefers-reduced-motion: no-preference)').matches) {
    revealTargets.forEach(function (el, index) {
      el.classList.add('reveal-item');
      if (!el.classList.contains('delay-100') && !el.classList.contains('delay-200') && !el.classList.contains('delay-300')) {
        var delayClass = 'delay-' + ((index % 3 + 1) * 100);
        el.classList.add(delayClass);
      }
    });

    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('revealed');
          observer.unobserve(entry.target);
        }
      });
    }, {
      threshold: 0.08,
      rootMargin: '0px 0px -40px 0px'
    });

    revealTargets.forEach(function (el) {
      observer.observe(el);
    });
  } else {
    revealTargets.forEach(function (el) {
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
