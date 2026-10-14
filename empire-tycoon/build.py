#!/usr/bin/env python3
"""Assemble Empire Tycoon.

  src/template.html + src/style.css + src/{engine,gfx,ui,main}.js  ->  index-cdn.html (source, Three.js via CDN)
  index-cdn.html + libs/three.min.js                               ->  index.html (100 % hors ligne, pour l'APK)

Usage : python3 build.py
"""
from pathlib import Path

here = Path(__file__).resolve().parent
rd = lambda p: p.read_text(encoding="utf-8")
tpl = rd(here / "src" / "template.html")
out = tpl.replace("/*STYLE*/", rd(here / "src" / "style.css"))
for key in ("ENGINE", "GFX", "UI", "MAIN"):
    out = out.replace("/*%s*/" % key, rd(here / "src" / (key.lower() + ".js")).replace("</script", "<\\/script"))
(here / "index-cdn.html").write_text(out, encoding="utf-8")

code = rd(here / "libs" / "three.min.js").replace("</script", "<\\/script")
begin, end = "<!-- THREE:BEGIN -->", "<!-- THREE:END -->"
i, j = out.index(begin), out.index(end) + len(end)
off = out[:i] + "<!-- Three.js r128 (licence MIT) intégré : aucun accès internet requis -->\n<script>/* three.min.js */\n" + code + "\n</script>" + out[j:]
(here / "index.html").write_text(off, encoding="utf-8")
print("index-cdn.html : %.0f Ko | index.html : %.0f Ko" % (len(out.encode()) / 1024, len(off.encode()) / 1024))
