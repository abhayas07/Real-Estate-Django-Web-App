/* =========================================
   Real Estate — Site Scripts
   ========================================= */
(function () {
  'use strict';

  /* Footer year */
  var yearEl = document.querySelector('.year');
  if (yearEl) {
    yearEl.innerHTML = new Date().getFullYear();
  }

  /* Navbar shrink on scroll + back-to-top visibility */
  var navbar = document.getElementById('main-navbar');
  var backToTop = document.getElementById('back-to-top');

  function onScroll() {
    var scrolled = window.scrollY > 40;
    if (navbar) {
      navbar.classList.toggle('navbar-scrolled', scrolled);
    }
    if (backToTop) {
      backToTop.classList.toggle('visible', window.scrollY > 400);
    }
  }

  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  if (backToTop) {
    backToTop.addEventListener('click', function () {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }

  /* Auto-dismiss flash messages after 6 seconds */
  var alerts = document.querySelectorAll('#message .alert');
  alerts.forEach(function (alert) {
    setTimeout(function () {
      alert.style.opacity = '0';
      alert.style.transform = 'translateY(-8px)';
      setTimeout(function () {
        if (alert.parentNode) {
          alert.parentNode.removeChild(alert);
        }
      }, 500);
    }, 6000);
  });

  /* Close mobile navbar after clicking a link */
  var navCollapse = document.getElementById('navbarNavAltMarkup');
  if (navCollapse) {
    navCollapse.addEventListener('click', function (e) {
      if (e.target.closest('a, button') && navCollapse.classList.contains('show')) {
        $(navCollapse).collapse('hide');
      }
    });
  }

  /* Scroll reveal — subtle fade-up for cards/sections (progressive enhancement) */
  var revealTargets = document.querySelectorAll('.card, .empty-state, .dashboard-header, .dashboard-stats');
  if ('IntersectionObserver' in window && revealTargets.length > 0 && window.matchMedia('(prefers-reduced-motion: no-preference)').matches) {
    document.body.classList.add('has-reveal');
    revealTargets.forEach(function (el) { el.classList.add('reveal'); });

    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('in-view');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.08 });

    revealTargets.forEach(function (el) { observer.observe(el); });
  }
})();


setTimeout(function() {
    $('#message').fadeOut('slow');
  }, 3000)
