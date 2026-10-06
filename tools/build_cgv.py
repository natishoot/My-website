#!/usr/bin/env python3
"""Génère cgv.html à partir du texte des CGV en Markdown.

Usage : python3 tools/build_cgv.py [chemin du .md]   (depuis la racine du dépôt)
Par défaut : ../NatiShoot_CGV_2026_corrigees.md (fichier de travail, hors du site publié).
"""
import html
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "..", "NatiShoot_CGV_2026_corrigees.md")
MAIL = "natishoot.tipix@gmail.com"


def inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"\[VARIABLE[^\]]*\]", lambda m: f'<span class="var">{m.group(0)}</span>', t)
    return t.replace(MAIL, f'<a href="mailto:{MAIL}">{MAIL}</a>')


def convert(md):
    out, para, lines, i = [], [], md.split("\n"), 0

    def flush():
        if para:
            out.append("<p>" + "<br>".join(inline(x) for x in para) + "</p>")
            para.clear()

    while i < len(lines):
        l = lines[i]
        if l.startswith("# ") or l.strip() == "---":
            flush()
        elif l.startswith("## "):
            flush()
            out.append(f"<h2>{inline(l[3:])}</h2>")
        elif l.startswith("|"):
            flush()
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                if not set(lines[i]) <= set("|- "):
                    rows.append([x.strip() for x in lines[i].strip("|").split("|")])
                i += 1
            head = "".join(f"<th>{inline(x)}</th>" for x in rows[0])
            body = "".join("<tr>" + "".join(f"<td>{inline(x)}</td>" for x in r) + "</tr>" for r in rows[1:])
            out.append(f"<table><tr>{head}</tr>{body}</table>")
            continue
        elif l.startswith("- "):
            flush()
            items = []
            while i < len(lines) and lines[i].startswith("- "):
                items.append(f"<li>{inline(lines[i][2:])}</li>")
                i += 1
            out.append("<ul>" + "".join(items) + "</ul>")
            continue
        elif not l.strip():
            flush()
        else:
            para.append(l)
        i += 1
    flush()
    return "\n  ".join(out)


def main():
    body = convert(open(SRC).read())
    path = os.path.join(ROOT, "cgv.html")
    page = open(path).read()
    a = page.index("<h1>Conditions générales de vente</h1>") + len("<h1>Conditions générales de vente</h1>")
    b = page.index("</main>")
    open(path, "w").write(page[:a] + "\n  " + body + "\n" + page[b:])
    print("cgv.html régénéré :", body.count('class="var"'), "[VARIABLE] restants")


if __name__ == "__main__":
    main()
