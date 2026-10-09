#!/usr/bin/env python3
"""Génère les pages détail (séries et prestations) du site Natishoot.

Usage : python3 tools/build_pages.py   (depuis la racine du dépôt)
Réécrit aussi les cartes Prestations de index.html (entre PRESTATIONS:START et END).
Tarifs : données PRESTATIONS ci-dessous, à tenir à jour avec NatiShoot_Tarifs_2026.md.
Les photos sont lues dans images/ : <serie>-NN.jpg (1920 px) et <serie>-NN-900.jpg (vignette).
Pour ajouter une photo : déposer les deux fichiers puis relancer le script.
"""
import glob
import html
import os
import re
import struct

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PORTFOLIO = "https://natishoot.myportfolio.com/"
# Version des fichiers communs (évite qu'un navigateur garde une ancienne mise en forme en cache)
import hashlib
ASSET_V = hashlib.md5(b"".join(open(os.path.join(ROOT, "assets", f), "rb").read() for f in ("pages.css", "pages.js"))).hexdigest()[:8]

# Séries affichées sur l'accueil (même ordre et mêmes clés que SERIES dans index.html)
SERIES = [
    {"k": "portrait", "t": "Portrait", "d": "Studio, extérieur", "parts": [("Portrait", "portrait", "portrait")]},
    {"k": "createurs", "t": "Créateurs (Collabs)", "d": "Créateurs & marques", "parts": [("Créateurs (Collabs)", "createurs-collabs", "createurs-collabs")]},
    {"k": "defile", "t": "Défilé / Mode", "d": "Podiums & mode", "parts": [("Défilé / Mode", "defile", "defile")]},
    {"k": "concerts", "t": "Concerts", "d": "Scène, festivals, artistes", "parts": [("Concerts", "concerts", "concerts")]},
    {"k": "cosplay", "t": "Cosplay", "d": "Conventions & personnages", "parts": [("Cosplay", "cosplay", "cosplay")]},
    {"k": "grossesse", "t": "Grossesse", "d": "Maternité, lumière douce", "parts": [("Grossesse", "grossesse", "grossesse")]},
    {"k": "sport", "t": "Sport", "d": "Boxe, football, action", "parts": [("Sport", "sport", "sport")]},
    {"k": "reportage", "t": "Reportage", "d": "Rue, manifestations", "parts": [("Reportage", "manifestation", "manifestation")]},
    {"k": "lifestyle", "t": "Lifestyle", "d": "Voyage, food, Paris", "parts": [("Lifestyle", "divers", "divers")]},
]

LEAD_PRESTA = ("Je prends le temps de comprendre votre demande, je me déplace avec mon matériel complet "
               "et je peux constituer une équipe avec des partenaires : vidéaste, make-up artists, "
               "créateurs de vêtements et d’accessoires. Formules et tarifs ci-dessous, ajustables sur devis selon votre projet.")

TARIFS_NOTE = "Prix nets, TVA non applicable (article 293 B du CGI)."
SOLIDAIRE = ("Vous êtes une association ou un artiste indépendant ? Vous pouvez bénéficier d’un tarif solidaire. "
             "Demandez un devis personnalisé.")
ARTISTE = "Vous êtes un artiste indépendant ou un artiste signé en label ? Demandez un devis personnalisé."

# Tarifs : NatiShoot_Brief_Reference_2026-10-08.md, v4 (prix nets). Formule : (nom, contenu, prix, unité, repère)
# prix None = prestation « artistes » : aucun prix sur le site (« Sur devis »). Formules Élan : jamais affichées.
PRESTATIONS = [
    {"k": "portrait", "n": "01", "t": "Portrait", "em": "& grossesse", "sub": "Portrait, grossesse, boudoir",
     "type": "Portrait", "from": "Dès 150 €", "cover": "portrait-43", "home_img": ("img", "po45"),
     "items": ["Portrait individuel", "Séance grossesse", "Séance boudoir", "Lumière studio (Godox, Neewer)",
               "Fonds noir, blanc, violet", "Retouche & colorimétrie", "Déplacement à domicile en Île-de-France"],
     "note": ("Location du studio à la charge du client s’il souhaite une séance en studio. "
              "Déplacement à domicile en Île-de-France (portrait individuel, grossesse, boudoir) sans supplément en journée. "
              "Les séances boudoir sont au même prix que les portraits ; la galerie boudoir & nu artistique est présentée uniquement sur demande."),
     "groups": [
         ("Portrait", [
             ("Portrait Essentiel", "45 min — 6 photos retouchées — galerie privée", "150 €", "", ""),
             ("Pack Découverte", "2 h — 15 photos — accompagnement poses et sélection", "300 €", "", ""),
             ("Portrait Signature", "2 h 30 — 25 photos — direction artistique", "450 €", "", "reco"),
             ("Portrait professionnel", "8 portraits retouchés pour site et réseaux", "250 €", "", ""),
             ("Déplacement à domicile — soirée", "Île-de-France, à partir de 20 h — portrait individuel, grossesse, boudoir", "100 €", "", ""),
         ]),
     ],
     "photos": [("portrait", 12), ("grossesse", 6)], "series": ["portrait", "grossesse"]},
    {"k": "evenements-mariages", "n": "02", "t": "Événements", "em": "& mariages", "sub": "Fêtes, galas, cérémonies",
     "type": "Événement / mariage", "from": "Dès 300 €", "cover": "portrait-32", "home_img": ("src", "images/portrait-32.jpg"),
     "items": ["Galas, compétitions sportives", "Conventions & cosplay", "Mariages & anniversaires",
               "Reportage documentaire", "Galerie privée en ligne", "Déplacements en France et à l’étranger, chiffrés au devis"],
     "groups": [
         ("Événement", [
             ("Événement Essentiel", "2 h — moments clés — livraison numérique", "300 €", "", ""),
             ("Événement demi-journée", "4 h — ambiance, invités, détails", "550 €", "", "reco"),
             ("Événement journée", "8 h — sélection et galerie privée", "950 €", "", ""),
             ("Événement longue durée", "10 h — couverture élargie", "1 200 €", "", ""),
         ]),
         ("Mariage", [
             ("Mariage civil", "Cérémonie, couple et groupes — galerie privée", "550 €", "", ""),
             ("Mariage Essentiel", "8 h — 300 photos retouchées — album 21 × 28 cm", "1 590 €", "", ""),
             ("Mariage Complet", "10 h — 500 photos — reel 30 s — album 21 × 28 cm", "2 090 €", "", "reco"),
             ("Mariage photo et film", "Forfait complet, film de 5 à 6 min", "Dès 2 990 €", "", ""),
         ]),
     ],
     "photos": [("sport", 8), ("cosplay", 8)], "series": ["sport", "cosplay", "reportage"]},
    {"k": "mode", "n": "03", "t": "Mode", "em": "& défilés", "sub": "Podiums, créateurs, éditorial",
     "type": "Mode", "from": "Dès 300 €", "cover": "defile-08", "home_img": ("src", "images/carte-mode.jpg"),
     "items": ["Défilés : podium, coulisses, ambiance", "Shooting mode & créateurs", "Book modèle",
               "Éditorial dirigé, univers personnalisé", "Sélection retouchée"],
     "groups": [
         ("Mode", [
             ("Défilé Essentiel", "Jusqu’à 2 h — passages clés", "300 €", "", ""),
             ("Défilé Étendu", "Jusqu’à 4 h — podium, coulisses, ambiance selon accès", "550 €", "", "reco"),
             ("Journée Mode", "Jusqu’à 8 h — tout l’événement", "950 €", "", ""),
             ("Éditorial Signature", "Shooting dirigé — 25 images — univers personnalisé", "Dès 450 €", "", ""),
         ]),
     ],
     "photos": [("defile", 8), ("createurs-collabs", 6)], "series": ["defile", "createurs"]},
    {"k": "corporate-photo-video", "n": "04", "t": "Corporate", "em": "& photo + vidéo", "sub": "Entreprises, organisations — tarif pro",
     "type": "Corporate / photo + vidéo", "from": "Dès 650 €", "cover": "carte-corporate", "home_img": ("src", "images/carte-corporate.jpg"),
     "items": ["Équipe, gestes métier, lieu et ambiance", "Banque d’images cohérente", "Portraits et interviews préparées",
               "Films courts et formats verticaux", "Contenu régulier mensuel"],
     "note": ("Tarif pro : cadrage éditorial, interviews préparées et droits d’exploitation pour la communication de l’organisation. "
              "Les droits d’utilisation sont définis au devis (supports, durée, diffusion). Usage publicitaire et grands volumes : sur devis."),
     "groups": [
         ("Corporate", [
             ("Corporate demi-journée", "Jusqu’à 4 h — équipe, gestes métier, lieu et ambiance", "650 €", "", "reco"),
             ("Corporate journée", "Jusqu’à 8 h — banque d’images cohérente", "1 200 €", "", ""),
             ("Campagne de lancement", "Conception légère, production, images de campagne", "Dès 1 290 €", "", ""),
         ]),
         ("Photo + vidéo", [
             ("Visages Essentiel", "1 lieu — 2 h — 10 photos — 1 interview ≤ 60 s — 1 correction", "820 €", "", ""),
             ("Visages Histoire", "1 lieu — 4 h — 20 photos — film ≤ 2 min — 2 interviews — 1 verticale — 2 corrections", "1 850 €", "", "reco"),
             ("Visages Signature", "Cadrage éditorial renforcé — 4 h — 25 photos — film 2 à 3 min — 2 interviews — 2 verticales — 2 corrections", "2 150 €", "", ""),
             ("Événement Récit", "4 h — 40 photos — film récap ≤ 60 s — 1 interview", "1 190 €", "", ""),
             ("Mini-documentaire", "1 jour — 3 intervenants — film 3 à 5 min — 2 corrections", "Dès 2 690 €", "", ""),
             ("Contenu Régulier", "1 séance/mois ≤ 2 h — 10 photos + 2 vidéos ≤ 30 s — engagement 3 mois", "560 €", "mois", ""),
         ]),
     ],
     "link": ("Voir les vidéos NatiShoot", PORTFOLIO + "videos-natishoot"),
     "photos": [("createurs-collabs", 6), ("portrait", 6)], "series": ["createurs", "portrait"]},
    {"k": "artistes", "n": "05", "t": "Artistes", "em": "& musique", "sub": "Concert, contenu, captation", "artiste": True,
     "type": "Artiste", "from": "Sur devis", "cover": "concerts-07", "home_img": ("src", "images/concerts-07.jpg"),
     "items": ["Photo de concert : scène, ambiance, coulisses", "Vidéos verticales pour vos réseaux", "Captation 1 ou 2 angles",
               "Montage & étalonnage", "Multicam sur devis", "Journée de contenu artiste"],
     "groups": [
         ("Concert (photo)", [
             ("Concert Essentiel", "Jusqu’à 2 h — sélection retouchée", None, "", ""),
             ("Concert Étendu", "Jusqu’à 4 h — scène, ambiance, coulisses selon accès", None, "", "reco"),
         ]),
         ("Vidéo — contenu artiste", [
             ("Session Création", "2 h de tournage — 2 vidéos verticales finalisées", None, "", ""),
             ("Demi-journée Contenu", "Jusqu’à 4 h — 4 formats courts finalisés", None, "", "reco"),
             ("Artist Content Day", "4 h — 15 portraits — interview ≤ 90 s — 3 vidéos verticales — 2 corrections", None, "", ""),
         ]),
         ("Vidéo — captation de concert", [
             ("Captation Angle Unique", "3 h de présence dont 2 h de tournage — 1 cadre — rushes étalonnés", None, "", ""),
             ("Captation Angle Unique + montage", "Même captation + montage d’une vidéo de 3 min (autres durées sur devis)", None, "", ""),
             ("Captation Double Regard", "3 h de présence dont 2 h de tournage — 2 angles — rushes étalonnés", None, "", ""),
             ("Captation Double Regard + montage", "Même captation + montage d’une vidéo de 3 min (autres durées sur devis)", None, "", "reco"),
             ("Multicam Monté", "Plusieurs angles, montage, étalonnage, exports", None, "", ""),
         ]),
     ],
     "link": ("Voir les vidéos NatiShoot", PORTFOLIO + "videos-natishoot"),
     "photos": [("concerts", 41)], "skip": ["concerts-02", "concerts-03", "concerts-23"], "max": 12, "series": ["concerts"]},
    {"k": "options", "n": "06", "t": "Options", "em": "à la carte", "sub": "À ajouter à une prestation",
     "type": "Option", "from": "Dès 24 €", "cover": "divers-12", "home_img": ("img", "di12"),
     "items": [],
     "groups": [
         ("Options", [
             ("Heure supplémentaire événement", "", "120 €", "heure", ""),
             ("Reel ajouté à une prestation", "Format court pour les réseaux", "120 €", "", ""),
             ("Album photo", "Format au choix", "Dès 90 €", "", ""),
             ("Interview courte", "1 personne — vidéo ≤ 90 s sous-titrée — 1 correction", "390 €", "", ""),
             ("3 déclinaisons verticales", "À partir du montage validé — ≤ 30 s chacune", "110 €", "", ""),
             ("Retouche avancée", "Par photo — détourage ou retouche localisée", "Dès 24 €", "photo", ""),
         ]),
     ],
     "photos": [], "series": []},
]

# Anciennes adresses → nouvelles (redirections 301 dans netlify.toml)
OLD_PRESTA = {"portrait-mode": "portrait", "concerts-evenements": "evenements-mariages", "grossesse-intime": "portrait",
              "video-live": "artistes", "portrait-corporate": "portrait", "mode-concerts": "mode",
              "video-captation": "artistes", "photo-video": "corporate-photo-video"}


def jpeg_size(path):
    """Largeur et hauteur d'un JPEG, sans dépendance externe."""
    with open(path, "rb") as f:
        f.read(2)
        while True:
            marker, = struct.unpack(">H", f.read(2))
            length, = struct.unpack(">H", f.read(2))
            if 0xFFC0 <= marker <= 0xFFCF and marker not in (0xFFC4, 0xFFC8, 0xFFCC):
                f.read(1)
                h, w = struct.unpack(">HH", f.read(4))
                return w, h
            f.read(length - 2)


def photos(slug):
    out = []
    for p in sorted(glob.glob(os.path.join(ROOT, "images", f"{slug}-[0-9][0-9].jpg"))):
        name = os.path.basename(p)[:-4]
        w, h = jpeg_size(p)
        out.append((name, w, h))
    return out


def tile(name, w, h, alt):
    return (f'<a class="tile reveal" href="../images/{name}.jpg" data-alt="{html.escape(alt)}">'
            f'<img src="../images/{name}-900.jpg" width="{w}" height="{h}" alt="{html.escape(alt)}" loading="lazy" decoding="async"></a>')


def page(title, desc, canonical, body):
    return f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<meta name="theme-color" content="#0b0a09">
<meta name="color-scheme" content="dark">
<link rel="canonical" href="https://natishoot.fr/{canonical}">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:image" content="https://natishoot.fr/images/portrait-01.jpg">
<link rel="preload" href="../fonts/anton-400.woff2" as="font" type="font/woff2" crossorigin>
<link rel="icon" type="image/png" sizes="32x32" href="../assets/favicon-32.png">
<link rel="icon" type="image/png" sizes="192x192" href="../assets/favicon-192.png">
<link rel="apple-touch-icon" href="../assets/apple-touch-icon.png">
<link rel="stylesheet" href="../assets/pages.css?v={ASSET_V}">
</head>
<body>
<header class="nav">
  <a class="logo" href="../index.html">NATISHOOT <small>photography</small></a>
  <a class="back" href="../index.html#series">← Retour à l’accueil</a>
  <a class="btn" href="../index.html#devis">Demander un devis →</a>
</header>
<main>
{body}
</main>
<footer>
  <div class="bot">
    <span>© 2026 NatiShoot Photography — Patrick Rhino EI · SIRET 531 577 955 00036 · TVA non applicable, art. 293 B du CGI</span>
    <span><a href="https://instagram.com/tfl.971" target="_blank" rel="noopener">Instagram</a> · <a href="../mentions-legales.html">Mentions légales</a> · <a href="../cgv.html">CGV</a></span>
  </div>
</footer>
<div class="lb" id="lb" role="dialog" aria-modal="true" aria-label="Visionneuse">
  <header><span class="mono" id="lbc"></span><button class="x" id="lbx" aria-label="Fermer">✕</button></header>
  <div class="stage"><img id="lbi" alt=""></div>
  <div class="foot"><span class="mono" id="lbt"></span><div class="arrows"><button id="lbp" aria-label="Précédente">←</button><button id="lbn" aria-label="Suivante">→</button></div></div>
</div>
<script src="../assets/pages.js?v={ASSET_V}" defer></script>
</body>
</html>
"""


def series_chips(current=None):
    return "".join(
        f'<a class="chip{" on" if s["k"] == current else ""}" href="../series/{s["k"]}.html">{s["t"]}</a>' for s in SERIES)


def build_series():
    os.makedirs(os.path.join(ROOT, "series"), exist_ok=True)
    for s in SERIES:
        parts = [(label, photos(slug), pf) for label, slug, pf in s["parts"]]
        total = sum(len(p) for _, p, _ in parts)
        body = [f"""<section class="head">
  <div><div class="eyebrow">Série</div><h1>{s['t']} <em>en images</em></h1></div>
  <div><p class="lead">{s['d']}. Cliquez sur une photo pour l’afficher en grand, format d’origine.</p>
  <div class="meta"><div><b>{total}</b><span class="mono">photos</span></div></div>
  <div class="cta"><a class="btn solid" href="../index.html#devis">Demander un devis →</a><a class="btn" href="{PORTFOLIO}{s['parts'][0][2]}" target="_blank" rel="noopener">Portfolio Adobe ↗</a></div></div>
</section>"""]
        for label, pics, _ in parts:
            if len(parts) > 1:
                body.append(f'<div class="sub"><h2>{label}</h2><span class="mono">{len(pics)} photos</span></div>')
            body.append('<div class="grid">' + "".join(tile(n, w, h, f"{label} — photographie NatiShoot") for n, w, h in pics) + "</div>")
        body.append(f'<section class="others"><div class="eyebrow">Autres séries</div><h2>Continuer la visite</h2><div class="chips">{series_chips(s["k"])}</div></section>')
        body.append('<section class="band"><p>Un projet <em>en tête ?</em></p><a class="btn" href="../index.html#devis">Parlons de votre shooting →</a></section>')
        out = page(f"{s['t']} — Série photo NatiShoot, photographe à Paris",
                   f"Série {s['t'].lower()} de NatiShoot, photographe à Paris : {s['d'].lower()}.",
                   f"series/{s['k']}.html", "\n".join(body))
        open(os.path.join(ROOT, "series", f"{s['k']}.html"), "w").write(out)


UNITS = {"": "", "heure": " / heure", "mois": " / mois", "photo": " / photo"}
TAGS = {"": "", "reco": '<em class="tag">Recommandé</em>'}


def nb(t):
    """Espaces insécables dans les montants."""
    return t.replace(" ", "\u00a0")


def price(f):
    if f[2] is None:  # prestation « artistes » : pas de prix affiché
        return "Sur devis"
    return nb(f[2]) + UNITS[f[3]]


def callout(text, cta):
    return f'<div class="callout"><p>{text}</p><a class="btn" href="{cta}">Demander un devis →</a></div>'


def formulas(p):
    return [f for _, fs in p["groups"] for f in fs]


def tarifs_html(p, cta):
    out = ['<h2>Formules &amp; tarifs</h2>']
    if p.get("artiste"):
        out.append(callout(ARTISTE, cta))
    for name, fs in p["groups"]:
        if len(p["groups"]) > 1:
            out.append(f'<h3 class="tg">{html.escape(name)}</h3>')
        rows = "".join(
            f'<li><div class="tn"><b>{html.escape(f[0])}</b>{TAGS[f[4]]}'
            + (f'<span>{html.escape(f[1])}</span>' if f[1] else "")
            + f'</div><span class="tp">{html.escape(price(f))}</span></li>' for f in fs)
        out.append(f'<ul class="tarifs">{rows}</ul>')
    if not p.get("artiste"):
        out.append(f'<p class="note">{TARIFS_NOTE}</p>')
    out.append(callout(SOLIDAIRE, cta))
    return "\n    ".join(out)


def build_prestations():
    os.makedirs(os.path.join(ROOT, "prestations"), exist_ok=True)
    keep = {f"{p['k']}.html" for p in PRESTATIONS}
    for old in glob.glob(os.path.join(ROOT, "prestations", "*.html")):
        if os.path.basename(old) not in keep:
            os.remove(old)
    total = f"{len(PRESTATIONS):02d}"
    for p in PRESTATIONS:
        items = "".join(f"<li>{html.escape(i)}</li>" for i in p["items"])
        inclus = f"<h2>Ce qui est inclus</h2>\n    <ul>{items}</ul>" if items else ""
        note = f'<p class="note">{p["note"]}</p>' if p.get("note") else ""
        link = f'<a class="btn" href="{p["link"][1]}" target="_blank" rel="noopener">{p["link"][0]} ↗</a>' if p.get("link") else ""
        cta = f'../index.html?type={p["type"].replace(" ", "%20")}#devis'
        cw, ch = jpeg_size(os.path.join(ROOT, "images", p["cover"] + ".jpg"))
        cover_cls = " wide" if cw > ch else ""  # photo horizontale : affichée en entier, sans recadrage
        pics = []
        for slug, n in p["photos"]:
            pics += [x for x in photos(slug) if x[0] not in p.get("skip", [])][:n]
        pics = pics[:p.get("max", len(pics))]
        grid = "".join(tile(n, w, h, f"{p['t']} {p['em']} — photographie NatiShoot") for n, w, h in pics)
        images = (f'<div class="sub" style="margin-top:0"><h2>En images</h2><span class="mono">{len(pics)} photos</span></div>\n'
                  f'<div class="grid">{grid}</div>\n') if pics else ""
        others = "".join(
            f'<a class="chip{" on" if o["k"] == p["k"] else ""}" href="{o["k"]}.html">{o["t"]} {o["em"]}</a>' for o in PRESTATIONS)
        linked = "".join(f'<a class="chip" href="../series/{k}.html">Série {next(s["t"] for s in SERIES if s["k"] == k)}</a>' for k in p["series"])
        body = f"""<section class="head">
  <div><div class="eyebrow">Prestation {p['n']} / {total} — {p['sub']}</div><h1>{p['t']} <em>{p['em']}</em></h1></div>
  <div><p class="lead">{LEAD_PRESTA}</p>
  <div class="meta"><div><b>{nb(p['from'])}</b><span class="mono">{'Devis personnalisé' if p.get('artiste') else 'Prix net'}</span></div></div>
  <div class="cta"><a class="btn solid" href="{cta}">Demander un devis →</a>{link}</div></div>
</section>
<section class="detail">
  <div class="cover{cover_cls}"><img src="../images/{p['cover']}.jpg" width="{cw}" height="{ch}" alt="{p['t']} {p['em']} — NatiShoot"></div>
  <div>
    {inclus}
    {note}
    {tarifs_html(p, cta)}
    <div class="chips">{linked}</div>
  </div>
</section>
{images}<section class="others"><div class="eyebrow">Autres prestations</div><h2>Tout ce que je propose</h2><div class="chips">{others}</div></section>
<section class="band"><p>{p['t']} <em>{p['em']}</em></p><a class="btn" href="{cta}">Demander un devis →</a></section>"""
        resume = p["items"][:3] or [f[0] for f in formulas(p)[:3]]
        out = page(f"{p['t']} {p['em']} — Prestation photo NatiShoot, Paris",
                   f"{p['t']} {p['em']} par NatiShoot, photographe à Paris : {', '.join(resume).lower()}. {p['from']}.",
                   f"prestations/{p['k']}.html", body)
        open(os.path.join(ROOT, "prestations", f"{p['k']}.html"), "w").write(out)


HTACCESS = """# Hébergement o2switch (Apache). Fichier généré par tools/build_pages.py.

# Préproduction : site non indexé. À SUPPRIMER au lancement (avec la ligne Sitemap à remettre dans robots.txt).
<IfModule mod_headers.c>
  Header set X-Robots-Tag "noindex"
</IfModule>

# Toujours https://natishoot.fr (sans www)
RewriteEngine On
RewriteCond %{HTTPS} off [OR]
RewriteCond %{HTTP_HOST} ^www\\. [NC]
RewriteRule ^ https://natishoot.fr%{REQUEST_URI} [L,R=301]

# Anciennes pages prestations
{REDIRECTS}
# Fichiers de travail jamais servis
RedirectMatch 404 ^/(tools|\\.git)(/|$)
<FilesMatch "\\.(md|py|toml|txt)$">
  Require all denied
</FilesMatch>
<Files "robots.txt">
  Require all granted
</Files>
<Files "galerie-lib.php">
  Require all denied
</Files>

# Sécurité et cache
<IfModule mod_headers.c>
  Header set X-Content-Type-Options "nosniff"
  Header set Referrer-Policy "strict-origin-when-cross-origin"
  <FilesMatch "\\.(jpg|jpeg|png|webp|woff2)$">
    Header set Cache-Control "public, max-age=31536000, immutable"
  </FilesMatch>
</IfModule>
ErrorDocument 404 /index.html
"""


def build_home():
    """Réécrit les cartes Prestations de l'accueil entre les repères PRESTATIONS:START / END."""
    total = f"{len(PRESTATIONS):02d}"
    cards = []
    for p in PRESTATIONS:
        if p.get("artiste"):
            lis = "".join(f"<li>{html.escape(f[0])}</li>" for f in formulas(p)[:6])
        else:
            lis = "".join(f"<li>{html.escape(f[0])} — {html.escape(price(f))}</li>" for f in formulas(p)[:6])
        kind, val = p["home_img"]
        alt = f"{p['t']} {html.escape(p['em'])} — photographie NatiShoot"
        img = f'data-img="{val}"' if kind == "img" else f'data-src="{val}" data-alt="{alt}"'
        cards.append(f"""    <article class="svc">
      <div class="l">
        <div class="top mono"><span>{p['n']} / {total}</span><span>{html.escape(p['sub'])}</span></div>
        <h3><a class="stretch" href="prestations/{p['k']}.html">{p['t']} <em>{html.escape(p['em'])}</em></a></h3>
        <p class="price">{nb(p['from'])}</p>
        <ul>{lis}</ul>
        <div class="foot"><span class="more-link">Toutes les formules <span class="arr">→</span></span><a href="#devis" class="btn mag" data-type="{p['type']}">Demander un devis <span class="arr">→</span></a></div>
      </div>
      <div class="r" {img}></div>
    </article>""")
    path = os.path.join(ROOT, "index.html")
    s = open(path).read()
    a = s.index("<!-- PRESTATIONS:START -->") + len("<!-- PRESTATIONS:START -->")
    b = s.index("    <!-- PRESTATIONS:END -->")
    s = s[:a] + "\n" + "\n".join(cards) + "\n" + s[b:]
    # mention tarif solidaire sous les cartes
    a = s.index("<!-- SOLIDAIRE:START -->") + len("<!-- SOLIDAIRE:START -->")
    b = s.index("<!-- SOLIDAIRE:END -->")
    s = s[:a] + f'\n  <div class="callout home"><p>{SOLIDAIRE}</p><a href="#devis" class="btn mag" data-devis>Demander un devis <span class="arr">→</span></a></div>\n  ' + s[b:]
    open(path, "w").write(s)
    # redirections des anciennes pages prestations
    t = os.path.join(ROOT, "netlify.toml")
    toml = open(t).read().split("\n# Anciennes pages prestations")[0].rstrip() + "\n"
    toml += "\n# Anciennes pages prestations (réorganisations des tarifs 2026)\n" + "".join(
        f'[[redirects]]\n  from = "/prestations/{o}.html"\n  to = "/prestations/{n}.html"\n  status = 301\n\n' for o, n in OLD_PRESTA.items())
    open(t, "w").write(toml.rstrip() + "\n")
    # .htaccess (hébergement o2switch / Apache)
    redir = "".join(f"Redirect 301 /prestations/{o}.html /prestations/{n}.html\n" for o, n in OLD_PRESTA.items())
    open(os.path.join(ROOT, ".htaccess"), "w").write(HTACCESS.replace("{REDIRECTS}", redir))


def stamp_static():
    """Met à jour la version des fichiers communs dans les pages écrites à la main."""
    for name in ("mentions-legales.html", "cgv.html"):
        path = os.path.join(ROOT, name)
        t = open(path).read()
        t = re.sub(r'assets/pages\.(css|js)(\?v=\w+)?"', lambda m: f'assets/pages.{m.group(1)}?v={ASSET_V}"', t)
        open(path, "w").write(t)


if __name__ == "__main__":
    build_series()
    build_prestations()
    build_home()
    stamp_static()
    print("Pages générées :", len(SERIES), "séries,", len(PRESTATIONS), "prestations")
