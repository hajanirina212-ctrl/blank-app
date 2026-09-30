#!/usr/bin/env python3
"""Génère index.html (100 % hors ligne) à partir de index-cdn.html.

Remplace le bloc <!-- THREE:BEGIN --> ... <!-- THREE:END --> par Three.js r128
et les modules de post-processing (dossier libs/) intégrés directement.
Usage : python3 build.py
"""
from pathlib import Path

LIBS = ["three.min.js", "SimplexNoise.js", "CopyShader.js", "FXAAShader.js",
        "LuminosityHighPassShader.js", "SSAOShader.js", "BokehShader.js",
        "EffectComposer.js", "RenderPass.js", "ShaderPass.js", "UnrealBloomPass.js",
        "SSAOPass.js", "BokehPass.js"]

here = Path(__file__).resolve().parent
src = (here / "index-cdn.html").read_text(encoding="utf-8")
parts = ["<!-- Three.js r128 + post-processing (licence MIT) intégrés : aucun accès internet requis -->"]
for name in LIBS:
    code = (here / "libs" / name).read_text(encoding="utf-8").replace("</script", "<\\/script")
    parts.append("<script>/* %s */\n%s\n</script>" % (name, code))

begin, end = "<!-- THREE:BEGIN -->", "<!-- THREE:END -->"
i, j = src.index(begin), src.index(end) + len(end)
out = src[:i] + "\n".join(parts) + src[j:]
(here / "index.html").write_text(out, encoding="utf-8")
print("index.html généré : %.0f Ko" % (len(out.encode("utf-8")) / 1024))
