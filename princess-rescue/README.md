# 👑 Princess Rescue 3D

Jeu d'aventure 3D dans un labyrinthe de pierre au coucher du soleil, en **un seul fichier HTML**.
Personnages, titre et histoire 100 % originaux. Aucune image ni son externe : textures, ciel, modèles et sons sont générés par le code.

## Histoire & but

Le Seigneur des Ombres a enfermé la princesse **Lysa** dans le donjon d'un labyrinthe maudit.
Tu incarnes **Aren** :
1. Trouve les **3 clés dorées** : une au sol, une **sur une caisse**, une **en hauteur** (il faut sauter).
2. Ouvre la **porte du donjon** (bouton ACTION) : le cadenas tombe, la porte pivote.
3. Libère Lysa de sa **cage** : cinématique de victoire.

3 vies, chrono, 5 chapitres de plus en plus grands (9×9 → 17×17, cases de 4 m). +1 vie tous les 2 chapitres.
Couloirs larges, plusieurs chemins (boucles) et des **salles ouvertes** à partir du chapitre 2 pour esquiver.

### ⚡ Le bâton de lumière (arme)
- Bouton **TIR** (maintenir = tir continu) / clic ou **F** au clavier.
- **Visée assistée** : l'Ombre visible la plus proche devant toi est verrouillée (anneau rouge) et les tirs partent vers elle.
- 6 charges, rechargement automatique (~1 par seconde) — le nombre est affiché sur le bouton.
- Chaque tir **sonne** l'Ombre ~1 s (flash blanc). Rôdeur = 3 tirs, Chauve-ombre = 2, Gardien = 5.
- Une Ombre dissipée rapporte +150 et **revient** 25 s plus tard à son point de départ.

### 🔺 Voir le danger arriver
- **Flèches** au bord de l'écran pour les Ombres proches **hors du champ de vision** (rouge qui clignote = elle te poursuit).
- Mini-carte : points rouges = Ombres (rouge vif = poursuite).
- Caméra à l'épaule placée plus haut (au-dessus des murs) pour voir les couloirs voisins.

**Les Ombres** (IA avec pathfinding A*) : patrouille → poursuite quand elles te repèrent (yeux qui brillent, grognement) → retour à leur point de départ si elles te perdent.
- **Rôdeur** (cornes) : chasse au sol.
- **Chauve-ombre** (ailes) : vole, plus rapide, repère de plus loin.
- **Gardien** (grand, yeux orange) : lent, surveille la porte du donjon.
- Chapitre 3+ : un 2e Rôdeur.

## Contrôles

| | Mobile | Clavier / souris |
|---|---|---|
| Bouger | Joystick (pouce à gauche) | ZQSD / WASD / flèches |
| Regarder | Glisser le doigt à droite | Souris (clic = capture du pointeur) |
| Sauter | SAUT | Espace |
| Action | ACTION (brille quand c'est possible) | E |
| Tirer | ⚡ TIR (maintenir) | Clic gauche (souris capturée) ou F |
| Sprint | SPRINT (maintenir) — jauge d'endurance | Maj |
| Vue FPS / épaule | 👁 | V |
| Pause | ⏸ | P ou Échap |

## Caméra plus facile
- **Sensibilité** réglable dans le menu et dans la pause : Lente / Normale / Rapide.
- Mouvement **lissé** (fini les à-coups), axe vertical moins sensible, inclinaison limitée en FPS.
- Champ de vision plus large en FPS (78°, +12° en portrait).
- Conseil mobile : la vue **à l'épaule** (par défaut) est la plus confortable ; la vue FPS (👁) est plus immersive.
- Réglages fins dans `CONFIG` : `LOOK_TOUCH`, `LOOK_SMOOTH`, `FOV`, `FOV_FPS`, `CAM_DIST`, `CAM_PITCH`.
- Arme : `ENERGY_MAX`, `ENERGY_REGEN`, `FIRE_CD`, `AIM_ASSIST`, `ENEMY_HP`, `RESPAWN_TIME`.

## Fichiers

| Fichier | Rôle |
|---|---|
| `index.html` | **Version pour l'APK** : Three.js + effets intégrés, fonctionne **sans internet** (~840 Ko). |
| `index-cdn.html` | Fichier **source** à modifier : charge Three.js via CDN (cdnjs/unpkg), sinon depuis `libs/`. |
| `libs/` | Three.js r128 + modules de post-processing (licence MIT) pour le mode local. |
| `build.py` | Régénère `index.html` : `python3 build.py` |
| `icon.png` | Icône 512×512 pour l'APK. |

## Réglage de la qualité (Low / Medium / High)

Dans le menu : **Auto** (par défaut), **Low**, **Medium**, **High**. Le choix est mémorisé.
- **Auto** = Medium sur téléphone, High sur PC, Low si l'appareil n'a pas WebGL 2.
  Si le jeu passe **sous 40 FPS**, il descend automatiquement d'un cran (message « Qualité ajustée »).
- Qualité forcée (Low/Medium/High) : seules les ombres sont réduites si ça rame.

| Réglage | Low | Medium | High |
|---|---|---|---|
| Résolution max (pixel ratio) | 1 | 1,5 | 2 |
| Ombre du soleil | 1024 | 2048 | 2048 |
| Ombre d'une torche | – | – | ✅ |
| Lumières de torches | 2 | 3 | 4 |
| Bloom (halos) | – | ✅ | ✅ |
| SSAO (ombres de contact) | – | – | ✅ |
| Flou d'arrière-plan (menu, cinématique) | – | ✅ | ✅ |
| FXAA + vignette + grain | vignette CSS | ✅ | ✅ |
| Particules | 50 | 150 | 300 |
| Touffes d'herbe | 0 | 350 | 900 |
| Textures | 256 px | 512 px | 1024 px |

**Personnaliser** : en haut du script, objet `QUALITY` (section 1). Exemples :
- Le jeu rame sur ton téléphone en Medium → mets `bloom: false` ou `pixelRatio: 1` dans `medium`.
- Plus de brillance → `new THREE.UnrealBloomPass(..., 0.55, 0.5, 0.8)` dans `buildComposer()` : 1er nombre = force, dernier = seuil.
- Ambiance : `CONFIG.SUN_DIR` (position du soleil), `CONFIG.ENV_GAIN` (reflets), `FogExp2(..., 0.018)` (brouillard), `toneMappingExposure` (luminosité).
- Difficulté : `levelParams(n)` (taille, chrono, vitesse et portée de détection des ennemis), `CONFIG.ENEMY_*`, `CONFIG.STAMINA_*`.

Après modification de `index-cdn.html`, lance `python3 build.py` pour mettre à jour `index.html`.

## Transformer en APK

### Avec ton app « Construction rapide » (téléphone)
1. Télécharge `index.html` et `icon.png`.
2. Nom : `Princess Rescue 3D` → **Sélectionner un fichier HTML** → `index.html` → icône `icon.png`.
3. **Créer et construire l'APK**, installe-le.
4. Premier test : menu → Jouer. Si c'est saccadé, choisis **Low** dans le menu.

### Méthode B — Claude Code + projet Android
Demande à Claude Code : « Crée une app Android (WebView plein écran, minSdk 24) qui charge
`file:///android_asset/index.html`, avec JavaScript + DOM Storage activés, zoom désactivé, orientation libre,
accélération matérielle ; copie `princess-rescue/index.html` dans `app/src/main/assets/` et `icon.png` comme icône ;
puis `./gradlew assembleDebug`. »

## Limites honnêtes
- Rendu « cinématique » crédible, mais pas un AAA : les personnages sont assemblés à partir de formes géométriques (aucun modèle 3D externe).
- Les effets High (SSAO, ombres de torche) sont lourds : réservés aux PC et téléphones haut de gamme.
- Three.js r128 : `SRGBColorSpace` n'existe pas encore, on utilise son équivalent `outputEncoding = sRGBEncoding`.
