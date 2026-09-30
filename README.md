# Site Natishoot

Site vitrine statique (HTML/CSS/JS) de Natishoot, photographe.
Déploiement : Netlify relié à ce dépôt (branche `main` = production, autres branches = prévisualisations).

- Galeries : `photos.js` (liste des photos) + dossier `images/` (JPEG sRGB 1920 px q80, vignettes `-900`).
- Indexation ouverte sur `natishoot-site.netlify.app` (robots.txt, sitemap.xml, balises canonical). Au branchement d'un domaine : le définir comme domaine principal dans Netlify (redirection 301 automatique) et remplacer l'adresse dans robots.txt, sitemap.xml, index.html et tools/build_pages.py.
