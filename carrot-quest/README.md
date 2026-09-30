# 🥕 Carrot Quest 3D

Jeu 3D de labyrinthe (vue du dessus) en un seul fichier HTML, prêt à être transformé en APK Android.
Personnages, titre et code 100 % originaux. Aucune image, aucun son externe : tout est généré par le code.

## Fichiers

| Fichier | Rôle |
|---|---|
| `index.html` | **Version à utiliser pour l'APK.** Three.js est intégré dedans : fonctionne **sans internet**. (~650 Ko) |
| `index-cdn.html` | Version légère (~65 Ko) : charge Three.js depuis internet, sinon depuis `three.min.js` à côté. C'est le **fichier source** à modifier. |
| `three.min.js` | Three.js r128 (licence MIT), pour la variante locale. |
| `build.py` | Régénère `index.html` à partir de `index-cdn.html` : `python3 build.py` |
| `icon.png` | Icône 512×512 pour l'application. |

## Le jeu

- **Pipo** (capsule turquoise) doit ramasser toutes les carottes 🥕 : la porte passe alors du rouge au vert, une flèche jaune la montre.
- 3 gardiens avec IA et pathfinding A* :
  - **Grumble** (cube rouge) te poursuit dès qu'il te repère ;
  - **Zigzag** (sphère violette) vise la case *devant* toi pour te couper la route ;
  - **Sneaky** (cône jaune) est plus lent mais se téléporte près de toi à partir du niveau 4.
- 3 vies, score, chrono. 8 niveaux de plus en plus grands (11×11 → 23×23) et rapides. +1 vie tous les 3 niveaux.
- **Dash ⚡** : petite accélération pour esquiver (recharge 4 s).
- Sauvegarde automatique (meilleur score + dernier niveau atteint → bouton « Continuer »).

**Contrôles** : joystick = pose le pouce n'importe où dans la moitié gauche · bouton ⚡ à droite.
Clavier : ZQSD / WASD / flèches, E ou Espace = dash, P ou Échap = pause.

## Modifier le jeu facilement

Tout est en haut du script, section **`1. CONFIG`** :
- `MAX_LEVEL`, `START_LIVES`, `PLAYER_SPEED`, `DASH_COOLDOWN`, `ENEMY_BASE_SPEED`…
- `COLORS` : toutes les couleurs (joueur, ennemis, murs, sol…).
- `levelParams(n)` : taille du labyrinthe, nombre de carottes, temps, vitesse des ennemis par niveau.

Modifie `index-cdn.html`, puis lance `python3 build.py` pour mettre à jour `index.html`.
(Sans Python : tu peux aussi modifier directement `index.html`, le code du jeu est tout en bas du fichier.)

## Variante « three.min.js en local »

`index-cdn.html` essaie d'abord internet (unpkg). S'il échoue, il charge automatiquement `three.min.js` placé **dans le même dossier**.
Donc : mets `index-cdn.html` + `three.min.js` ensemble → ça marche hors ligne aussi.
Pour un générateur qui n'accepte **qu'un seul fichier**, utilise simplement `index.html` (Three.js déjà intégré).

## Méthode A — APK depuis le téléphone (app « Construction rapide » / WebIntoApp / Median…)

1. Télécharge `index.html` et `icon.png` sur ton téléphone.
2. Dans l'app : **Nom** = `Carrot Quest 3D`.
3. **Source du contenu** → **Sélectionner un fichier HTML** → choisis `index.html`.
   (Évite « Coller le HTML » : 650 Ko de texte risquent d'être tronqués.)
4. **Sélectionner une icône** → `icon.png`.
5. **Créer et construire l'APK**, puis installe-le (autorise « sources inconnues » si demandé).
6. Test : termine un niveau, ferme l'app complètement, rouvre-la → « Meilleur score » et « Continuer » doivent apparaître.
   Sinon, l'app de construction a désactivé le stockage (le jeu reste jouable, sans mémoire).

**Option URL** (Median, WebIntoApp…) : héberge le dossier sur GitHub Pages ou Netlify (glisser-déposer le dossier sur app.netlify.com/drop),
puis donne l'URL de `index.html`. Avantage : tu mets à jour le jeu sans reconstruire l'APK. Inconvénient : internet obligatoire.

Conseils : choisis l'orientation « auto » (ou paysage), le plein écran / masquer la barre de titre, et active JavaScript + DOM Storage si l'option existe.

## Méthode B — Claude Code + MCP Android (compilation depuis le terminal)

Pré-requis sur ton PC : Android Studio (ou SDK Android + JDK 17) et Claude Code.

1. Ajoute un MCP Android à Claude Code (ex. `claude mcp add ...` selon la doc du MCP choisi), ou laisse Claude utiliser Gradle directement.
2. Demande à Claude Code :
   > « Crée un projet Android minimal (Kotlin, minSdk 21) avec une seule Activity plein écran contenant une WebView
   > qui charge `file:///android_asset/index.html`. Active javaScriptEnabled, domStorageEnabled, mediaPlaybackRequiresUserGesture=false,
   > désactive le zoom, orientation fullSensor. Copie `carrot-quest/index.html` dans `app/src/main/assets/` et `icon.png` comme icône.
   > Puis compile avec `./gradlew assembleDebug`. »
3. L'APK se trouve dans `app/build/outputs/apk/debug/app-debug.apk`.
4. Pour le Play Store : il faudra un **AAB signé** (`./gradlew bundleRelease` + une clé de signature que tu gardes précieusement).

## Compatibilité

- Three.js **r128** (dernière version avec un fichier `three.min.js` classique, sans modules) → Android 5+ avec « Android System WebView » à jour (moteur Chrome 60 ou plus).
- Si WebGL est indisponible, un message clair s'affiche au lieu d'un écran noir.
- Qualité automatique : si le jeu tombe sous 40 FPS, la résolution baisse, puis les ombres se coupent.
- Pause automatique quand l'app passe en arrière-plan.
