#!/usr/bin/env python3
"""Génère le PDF des CGV (fond blanc, prêt à imprimer ou à envoyer) avec Brave en mode headless.

Usage : python3 tools/build_cgv_pdf.py   (depuis la racine du dépôt)
Source : ../NatiShoot_CGV_2026_corrigees.md — sortie : ../NatiShoot_CGV_2026.pdf (hors du site publié).
"""
import os
import re
import subprocess
import tempfile

from build_cgv import ROOT, SRC, convert

OUT = os.path.join(os.path.dirname(ROOT), "NatiShoot_CGV_2026.pdf")
BRAVE = "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"
FONTS = "file://" + os.path.join(ROOT, "fonts")

CSS = """
@font-face{font-family:Anton;src:url(%(f)s/anton-400.woff2)}
@font-face{font-family:Inter;src:url(%(f)s/inter-tight-400.woff2);font-weight:400}
@font-face{font-family:Inter;src:url(%(f)s/inter-tight-500-600.woff2);font-weight:500 600}
@font-face{font-family:Serif;src:url(%(f)s/instrument-serif-400-italic.woff2);font-style:italic}
@page{size:A4;margin:18mm 17mm 20mm}
*{box-sizing:border-box}
body{font:400 9.6pt/1.5 Inter,Helvetica,sans-serif;color:#1d1b19;margin:0}
.top{border-bottom:2px solid #1d1b19;padding-bottom:10pt;margin-bottom:14pt}
.logo{font:26pt/1 Anton,sans-serif;letter-spacing:.02em}
.logo small{font:italic 15pt Serif,serif;letter-spacing:0;margin-left:4pt;color:#b0472d}
h1{font:16pt/1.15 Anton,sans-serif;text-transform:uppercase;letter-spacing:.02em;margin:10pt 0 4pt}
.top p{margin:2pt 0;color:#55504a}
h2{font:600 11pt/1.3 Inter,sans-serif;margin:14pt 0 4pt;break-after:avoid;color:#1d1b19}
h2::after{content:"";display:block;width:24pt;border-bottom:1.5px solid #b0472d;margin-top:3pt}
p{margin:0 0 6pt;orphans:3;widows:3}
ul{margin:0 0 6pt;padding-left:14pt}li{margin-bottom:2pt}
b{font-weight:600}
a{color:inherit;text-decoration:none}
table{width:100%%;border-collapse:collapse;margin:6pt 0 10pt;break-inside:avoid}
th,td{border:1px solid #d8d2ca;padding:4pt 6pt;text-align:left;vertical-align:top}
th{background:#f3efe9;font-weight:600}
.annexe{break-before:page}
"""


def main():
    md = open(SRC).read()
    lines = md.split("\n")
    head = [l for l in lines[1:6] if l.strip() and l.strip() != "---"]
    body = convert(md)
    # L'annexe commence sur une nouvelle page.
    body = body.replace("<h2>Annexe", '<h2 class="annexe">Annexe', 1)
    top = "".join("<p>" + re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", l) + "</p>" for l in head)
    # Le convertisseur reprend les lignes d'en-tête en paragraphe : on les retire du corps.
    body = body.split("</p>", 1)[1] if body.startswith("<p>") else body
    page = f"""<!doctype html><html lang="fr"><head><meta charset="utf-8">
<title>NatiShoot — Conditions générales de vente</title><style>{CSS % {'f': FONTS}}</style></head><body>
<div class="top"><div class="logo">NATISHOOT<small>photography</small></div>
<h1>Conditions générales de vente</h1>{top}</div>
{body}</body></html>"""
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False) as f:
        f.write(page)
    subprocess.run([BRAVE, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                    "--allow-file-access-from-files", f"--print-to-pdf={OUT}", "file://" + f.name],
                   check=True, capture_output=True)
    os.unlink(f.name)
    print("PDF créé :", OUT)


if __name__ == "__main__":
    main()
