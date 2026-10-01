# Site Natishoot

Site vitrine statique (HTML/CSS/JS) de Natishoot, photographe.
Déploiement : Netlify relié à ce dépôt (branche `main` = production, autres branches = prévisualisations).

- Galeries : `photos.js` (liste des photos) + dossier `images/` (JPEG sRGB 1920 px q80, vignettes `-900`).
- Site en construction : en-tête `X-Robots-Tag: noindex` dans `netlify.toml` (robots.txt volontairement ouvert pour que Google lise ce noindex). Au lancement : retirer le noindex, remettre la ligne Sitemap dans robots.txt, resoumettre le sitemap dans Search Console. Ne jamais supprimer `google16495dd5a3978f91.html` (validation Search Console).
- Indexation prévue sur `natishoot-site.netlify.app` (sitemap.xml, balises canonical). Au branchement d'un domaine : le définir comme domaine principal dans Netlify (redirection 301 automatique) et remplacer l'adresse dans robots.txt, sitemap.xml, index.html et tools/build_pages.py.
