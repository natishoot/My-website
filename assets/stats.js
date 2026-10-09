/* Mesure d'audience Matomo, hébergée chez o2switch (stats.natishoot.fr) : sans cookie, IP anonymisées.
   Active seulement sur natishoot.fr (pas en local) et jamais sur la galerie privée. */
(function () {
  if (location.hostname !== 'natishoot.fr' || /galerie|photo\.php/.test(location.pathname)) return;
  var u = 'https://stats.natishoot.fr/', _paq = window._paq = window._paq || [];
  _paq.push(['disableCookies'], ['trackPageView'], ['enableLinkTracking'],
            ['setTrackerUrl', u + 'matomo.php'], ['setSiteId', '1']);
  var g = document.createElement('script');
  g.async = true; g.src = u + 'matomo.js';
  document.head.appendChild(g);
})();
