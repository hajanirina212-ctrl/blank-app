#!/bin/sh
# Prépare www/index.html à partir de gargote.html (la source unique de l'appli).
set -e
cd "$(dirname "$0")"
mkdir -p www
{
  printf '%s\n' '<!doctype html><html lang="fr"><head><meta charset="utf-8">'
  printf '%s\n' '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
  printf '%s\n' '<style>:root{padding:env(safe-area-inset-top,0px) 0 env(safe-area-inset-bottom,0px)}body{margin:0}[hidden]{display:none!important}</style>'
  cat gargote.html
  printf '%s\n' '</body></html>'
} > www/index.html
