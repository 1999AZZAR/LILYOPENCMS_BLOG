(function () {
  'use strict';

  var ICON_MAP = {
    facebook: 'fa-facebook-f',
    twitter: 'fa-x-twitter',
    x: 'fa-x-twitter',
    instagram: 'fa-instagram',
    youtube: 'fa-youtube',
    tiktok: 'fa-tiktok',
    linkedin: 'fa-linkedin-in',
    github: 'fa-github',
    telegram: 'fa-telegram',
    whatsapp: 'fa-whatsapp',
    discord: 'fa-discord',
    pinterest: 'fa-pinterest',
    snapchat: 'fa-snapchat',
    reddit: 'fa-reddit-alien',
    threads: 'fa-threads',
    bluesky: 'fa-bluesky',
    website: 'fa-globe',
    link: 'fa-link',
  };

  var container = document.getElementById('social-links-container');
  if (!container) return;

  fetch('/api/social-media')
    .then(function (r) { return r.json(); })
    .then(function (links) {
      if (!links || !links.length) return;
      links.forEach(function (sm) {
        var name = (sm.name || '').toLowerCase().trim();
        var icon = ICON_MAP[name] || 'fa-link';
        var a = document.createElement('a');
        a.href = sm.url;
        a.target = '_blank';
        a.rel = 'noopener noreferrer';
        a.className =
          'flex items-center justify-center w-9 h-9 rounded-full text-sm transition-all duration-200 hover:scale-110';
        a.style.backgroundColor = 'hsl(var(--surface-tonal))';
        a.style.color = 'hsl(var(--muted-foreground))';
        a.setAttribute('aria-label', sm.name);
        a.onmouseover = function () { this.style.color = 'hsl(var(--primary))'; };
        a.onmouseout = function () { this.style.color = 'hsl(var(--muted-foreground))'; };
        a.innerHTML = '<i class="fa-brands ' + icon + '" aria-hidden="true"></i>';
        container.appendChild(a);
      });
    })
    .catch(function () {});
})();
