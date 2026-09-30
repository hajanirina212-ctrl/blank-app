#!/usr/bin/env python3
"""Génère index.html (100 % hors ligne) à partir de index-cdn.html.

Remplace le bloc <!-- THREE:BEGIN --> ... <!-- THREE:END --> par le
contenu de three.min.js intégré dans une balise <script>.

Usage : python3 build.py
"""
from pathlib import Path

here = Path(__file__).resolve().parent
src = (here / "index-cdn.html").read_text(encoding="utf-8")
three = (here / "three.min.js").read_text(encoding="utf-8")

# Sécurité : "</script" dans le JS fermerait la balise trop tôt
three = three.replace("</script", "<\\/script")

begin, end = "<!-- THREE:BEGIN -->", "<!-- THREE:END -->"
i, j = src.index(begin), src.index(end) + len(end)
inline = "<!-- Three.js r128 (MIT) intégré : aucun accès internet requis -->\n<script>\n" + three + "\n</script>"
out = src[:i] + inline + src[j:]

(here / "index.html").write_text(out, encoding="utf-8")
print("index.html généré : %.0f Ko" % (len(out.encode("utf-8")) / 1024))
