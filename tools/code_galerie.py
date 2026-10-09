#!/usr/bin/env python3
"""Génère un code d'accès à la galerie privée Boudoir & nu.

Usage : python3 tools/code_galerie.py [jours]   (7 jours par défaut, depuis la racine du dépôt)
La clé secrète est lue dans ../natishoot-config.php (hors du site, jamais sur GitHub) :
elle doit être identique à celle du fichier natishoot-config.php installé sur o2switch.
"""
import datetime
import hashlib
import hmac
import os
import re
import secrets
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG = os.path.join(os.path.dirname(ROOT), "natishoot-config.php")
ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"


def signature(base, secret):
    h = hmac.new(secret.encode(), base.encode(), hashlib.sha256).digest()
    return "".join(ALPHABET[b % 32] for b in h[:6])


def main():
    jours = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    secret = re.search(r"GALERIE_SECRET = '([0-9a-f]+)'", open(CONFIG).read()).group(1)
    fin = datetime.date.today() + datetime.timedelta(days=jours)
    base = f"NU-{fin:%Y%m%d}-{''.join(secrets.choice(ALPHABET) for _ in range(4))}"
    print(f"{base}-{signature(base, secret)}")
    print(f"Valable jusqu'au {fin:%d/%m/%Y} inclus.")


if __name__ == "__main__":
    main()
