# Site Natishoot

Site vitrine statique (HTML/CSS/JS) de Natishoot, photographe.
Déploiement : Netlify relié à ce dépôt (branche `main` = production, autres branches = prévisualisations).

- Galeries : `photos.js` (liste des photos) + dossier `images/` (JPEG sRGB 1920 px q80, vignettes `-900`).
- Préproduction : `robots.txt` en `Disallow: /` et en-tête `X-Robots-Tag: noindex` dans `netlify.toml`, à lever au branchement du domaine final.
