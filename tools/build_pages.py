#!/usr/bin/env python3
"""Génère les pages détail (séries et prestations) du site Natishoot.

Usage : python3 tools/build_pages.py   (depuis la racine du dépôt)
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
               "créateurs de vêtements et d’accessoires. Tarifs sur devis, adaptés à votre projet.")

PRESTATIONS = [
    {"k": "portrait-mode", "n": "01", "t": "Portrait", "em": "& mode", "sub": "Studio ou extérieur", "type": "Portrait",
     "cover": "portrait-43",
     "items": ["Portrait individuel", "Shooting mode & créateurs", "Book modèle", "Lumière studio (Godox, Neewer)",
               "Fonds noir, blanc, violet", "Retouche & colorimétrie"],
     "photos": [("portrait", 12), ("createurs-collabs", 4), ("defile", 4)], "series": ["portrait", "createurs", "defile"]},
    {"k": "concerts-evenements", "n": "02", "t": "Concerts", "em": "& événements", "sub": "Scène & événementiel", "type": "Événement",
     "cover": "concerts-03",
     "items": ["Concerts & festivals", "Galas, compétitions sportives", "Conventions & cosplay", "Mariages & anniversaires",
               "Reportage documentaire", "Déplacement possible"],
     "photos": [("concerts", 9), ("sport", 4), ("cosplay", 4), ("manifestation", 3)], "series": ["concerts", "sport", "cosplay", "reportage"]},
    {"k": "grossesse-intime", "n": "03", "t": "Grossesse", "em": "& intime", "sub": "Moments de vie", "type": "Grossesse",
     "cover": "grossesse-08",
     "items": ["Séance grossesse", "Portrait en couple ou famille", "Boudoir & nu artistique (galerie privée)",
               "Mise en scène et accessoires", "Maquillage en option (partenaires)", "Cadre bienveillant"],
     "note": "Les séances boudoir & nu artistique sont présentées uniquement sur demande (galerie privée).",
     "photos": [("grossesse", 9)], "series": ["grossesse", "portrait"]},
    {"k": "video-live", "n": "04", "t": "Vidéo", "em": "& live", "sub": "Production complète", "type": "Vidéo / Live",
     "cover": "concerts-07",
     "items": ["Captation vidéo & photo", "Montage & colorimétrie", "Live streaming, 1 ou plusieurs caméras",
               "Diffusion directe sur votre chaîne", "Équipe : modèles, maquilleuses, coiffeuses", "Location de matériel supplémentaire"],
     "link": ("Voir les vidéos NatiShoot", PORTFOLIO + "videos-natishoot"),
     "photos": [("concerts", 8)], "series": ["concerts"]},
]


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
<link rel="canonical" href="https://natishoot-site.netlify.app/{canonical}">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<link rel="preload" href="../fonts/anton-400.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="../assets/pages.css">
</head>
<body>
<header class="nav">
  <a class="logo" href="../index.html">NATISHOOT <small>photography</small></a>
  <a class="back" href="../index.html#series">← Retour à l’accueil</a>
  <a class="btn" href="../index.html#contact">Réserver un shooting →</a>
</header>
<main>
{body}
</main>
<footer>
  <div class="bot">
    <span>© 2026 NatiShoot Photography — Auteur, SIREN 531 577 955</span>
    <span><a href="https://instagram.com/tfl.971" target="_blank" rel="noopener">Instagram</a> · <a href="https://photo-portal.shop/profiles/natishoot/" target="_blank" rel="noopener">Boutique tirages</a> · <a href="../mentions-legales.html">Mentions légales</a></span>
  </div>
</footer>
<div class="lb" id="lb" role="dialog" aria-modal="true" aria-label="Visionneuse">
  <header><span class="mono" id="lbc"></span><button class="x" id="lbx" aria-label="Fermer">✕</button></header>
  <div class="stage"><img id="lbi" alt=""></div>
  <div class="foot"><span class="mono" id="lbt"></span><div class="arrows"><button id="lbp" aria-label="Précédente">←</button><button id="lbn" aria-label="Suivante">→</button></div></div>
</div>
<script src="../assets/pages.js" defer></script>
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
  <div class="cta"><a class="btn solid" href="../index.html#contact">Réserver un shooting →</a><a class="btn" href="{PORTFOLIO}{s['parts'][0][2]}" target="_blank" rel="noopener">Portfolio Adobe ↗</a></div></div>
</section>"""]
        for label, pics, _ in parts:
            if len(parts) > 1:
                body.append(f'<div class="sub"><h2>{label}</h2><span class="mono">{len(pics)} photos</span></div>')
            body.append('<div class="grid">' + "".join(tile(n, w, h, f"{label} — photographie NatiShoot") for n, w, h in pics) + "</div>")
        body.append(f'<section class="others"><div class="eyebrow">Autres séries</div><h2>Continuer la visite</h2><div class="chips">{series_chips(s["k"])}</div></section>')
        body.append('<section class="band"><p>Un projet <em>en tête ?</em></p><a class="btn" href="../index.html#contact">Parlons de votre shooting →</a></section>')
        out = page(f"{s['t']} — Série photo NatiShoot, photographe à Paris",
                   f"Série {s['t'].lower()} de NatiShoot, photographe à Paris : {s['d'].lower()}.",
                   f"series/{s['k']}.html", "\n".join(body))
        open(os.path.join(ROOT, "series", f"{s['k']}.html"), "w").write(out)


def build_prestations():
    os.makedirs(os.path.join(ROOT, "prestations"), exist_ok=True)
    for p in PRESTATIONS:
        items = "".join(f"<li>{html.escape(i)}</li>" for i in p["items"])
        note = f'<p class="note">{p["note"]}</p>' if p.get("note") else ""
        link = f'<a class="btn" href="{p["link"][1]}" target="_blank" rel="noopener">{p["link"][0]} ↗</a>' if p.get("link") else ""
        cta = f'../index.html?type={p["type"].replace(" ", "%20")}#contact'
        pics = []
        for slug, n in p["photos"]:
            pics += photos(slug)[:n]
        grid = "".join(tile(n, w, h, f"{p['t']} {p['em']} — photographie NatiShoot") for n, w, h in pics)
        others = "".join(
            f'<a class="chip{" on" if o["k"] == p["k"] else ""}" href="{o["k"]}.html">{o["t"]} {o["em"]}</a>' for o in PRESTATIONS)
        linked = "".join(f'<a class="chip" href="../series/{k}.html">Série {next(s["t"] for s in SERIES if s["k"] == k)}</a>' for k in p["series"])
        body = f"""<section class="head">
  <div><div class="eyebrow">Prestation {p['n']} / 04 — {p['sub']}</div><h1>{p['t']} <em>{p['em']}</em></h1></div>
  <div><p class="lead">{LEAD_PRESTA}</p>
  <div class="cta"><a class="btn solid" href="{cta}">Demander un devis →</a>{link}</div></div>
</section>
<section class="detail">
  <div class="cover"><img src="../images/{p['cover']}.jpg" alt="{p['t']} {p['em']} — NatiShoot"></div>
  <div>
    <h2>Ce qui est inclus</h2>
    <ul>{items}</ul>
    {note}
    <h2>Tarif</h2>
    <p class="lead" style="margin-bottom:28px">Sur devis, selon la durée, le lieu et l’usage des images.</p>
    <div class="chips">{linked}</div>
  </div>
</section>
<div class="sub" style="margin-top:0"><h2>En images</h2><span class="mono">{len(pics)} photos</span></div>
<div class="grid">{grid}</div>
<section class="others"><div class="eyebrow">Autres prestations</div><h2>Tout ce que je propose</h2><div class="chips">{others}</div></section>
<section class="band"><p>{p['t']} <em>{p['em']}</em></p><a class="btn" href="{cta}">Demander un devis →</a></section>"""
        out = page(f"{p['t']} {p['em']} — Prestation photo NatiShoot, Paris",
                   f"{p['t']} {p['em']} par NatiShoot, photographe à Paris : {', '.join(p['items'][:3]).lower()}. Sur devis.",
                   f"prestations/{p['k']}.html", body)
        open(os.path.join(ROOT, "prestations", f"{p['k']}.html"), "w").write(out)


if __name__ == "__main__":
    build_series()
    build_prestations()
    print("Pages générées :", len(SERIES), "séries,", len(PRESTATIONS), "prestations")
