# Site Natishoot

Site vitrine statique (HTML/CSS/JS) de Natishoot, photographe.
Déploiement : Netlify relié à ce dépôt (branche `main` = production, autres branches = prévisualisations).

- Galeries : `photos.js` (liste des photos) + dossier `images/` (JPEG sRGB 1920 px q80, vignettes `-900`).
- Site en construction : en-tête `X-Robots-Tag: noindex` dans `netlify.toml` (robots.txt volontairement ouvert pour que Google lise ce noindex). Au lancement : retirer le noindex, remettre la ligne Sitemap dans robots.txt, resoumettre le sitemap dans Search Console. Ne jamais supprimer `google16495dd5a3978f91.html` (validation Search Console).
- Domaine : natishoot.fr, hébergé chez o2switch. `.htaccess` (généré par tools/build_pages.py) : noindex de préproduction, https, redirections. Formulaire de devis : devis.php (mail PHP).
