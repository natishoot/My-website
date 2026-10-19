#!/usr/bin/env python3
"""Signale à Bing (et aux moteurs IndexNow : Yandex, Seznam, Naver…) les pages du sitemap à explorer.

Usage, depuis la racine du dépôt, après une mise en ligne :  python3 tools/indexnow.py
La clé est le fichier <clé>.txt (32 caractères hexadécimaux) à la racine du site.
"""
import glob, json, os, re, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
key = os.path.basename(glob.glob(os.path.join(ROOT, "[0-9a-f]" * 32 + ".txt"))[0])[:-4]
urls = re.findall(r"<loc>([^<]+)</loc>", open(os.path.join(ROOT, "sitemap.xml")).read())
body = json.dumps({"host": "natishoot.fr", "key": key, "keyLocation": f"https://natishoot.fr/{key}.txt", "urlList": urls}).encode()
req = urllib.request.Request("https://api.indexnow.org/indexnow", data=body, headers={"Content-Type": "application/json; charset=utf-8"})
with urllib.request.urlopen(req) as r:
    print(f"IndexNow : {len(urls)} adresses envoyées, réponse {r.status}")
