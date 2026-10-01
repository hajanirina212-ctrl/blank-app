# 🥕 Carrot Castle 3D

Jeu de plateformes / réflexion en **2,5D réaliste (HD)**, en un seul fichier HTML, inspiré des mécaniques des jeux
« château à carottes » de la fin des années 80. **Personnages, nom et histoire 100 % originaux** (aucun personnage
ni marque protégés).

## Histoire
Le Baron **Grimfang** a enfermé **Clover** au sommet de son château. **Pip**, un lièvre courageux, doit ramasser
toutes les **carottes enchantées** de chaque salle pour monter, étage après étage, jusqu'à elle. 20 niveaux ;
au dernier, la cage s'ouvre (cinématique).

## Règles (comme les classiques du genre)
- Ramasse **toutes les carottes** d'un niveau → niveau terminé.
- **Pas de saut, pas d'arme** : on se déplace sur les étages, on prend les **escaliers** (▲/▼) et les **portes**
  (les portes de même couleur sont reliées).
- On se défend avec les **objets** :
  - **Caisse** (dès le niveau 1) : ACTION pour la pousser → elle glisse et assomme tout sur son passage. Réutilisable.
  - **Gant à ressort** (niveau 2+) : ACTION à côté → coup de poing de 3,8 m dans ta direction.
  - **Potion verte** (niveau 4+) : 7 s d'invincibilité, fonce sur les ennemis !
- Ennemis : **Armure hantée** (lente, tenace), **Corbeau** (imprévisible), **Loup** (rapide quand il te voit),
  **Fantôme** (traverse les portes). Ils changent d'étage pour te rejoindre (recherche de chemin entre étages).
  Un ennemi assommé revient après 7 s.
- 3 vies, +1 vie tous les 5 niveaux. **Codes de niveau** (comme à l'époque) affichés à chaque fin de niveau,
  à saisir dans le menu.
- Mini-carte en coupe (haut à droite) + **flèches rouges** au bord de l'écran quand un ennemi approche hors champ.

## Contrôles
| | Mobile | Clavier |
|---|---|---|
| Marcher | Joystick gauche | ← → / Q D / A D |
| Monter / descendre (escalier, porte) | ▲ / ▼ (ou joystick haut/bas) | ↑ ↓ / Z S / W S |
| Action (caisse, gant, porte) | ✊ ACTION | E ou Espace |
| Pause | ⏸ | P / Échap |

Les boutons ▲ ▼ ACTION **brillent** quand une action est possible.

## Rendu HD
- Résolution native jusqu'à 2x (écrans Retina/AMOLED), **MSAA 4x** (bords nets), filtrage anisotrope 16x,
  filtre de netteté, textures procédurales 1024 px (2048 px en High), modèles lissés.
- Tone mapping ACES, couleurs sRGB, matériaux PBR (métal poli des armures, fourrure avec reflet « sheen »,
  verre de la potion), environnement réfléchi, bloom des torches et fenêtres, rayons de lumière, poussière,
  ombres douces 2048 (4096 en High), SSAO en High, profondeur de champ au menu et dans la cinématique.

| | Low | Medium (mobile par défaut) | High (PC par défaut) |
|---|---|---|---|
| Résolution | 1,25x | 2x | 2x |
| Anti-crénelage | MSAA natif | MSAA 4x | MSAA 4x |
| Textures | 512 | 1024 | 2048 |
| Ombres | 1024 | 2048 | 4096 |
| Bloom / rayons / flou menu | – | ✅ | ✅ |
| SSAO | – | – | ✅ |

Si le jeu passe sous 40 FPS en mode Auto, la qualité baisse d'un cran automatiquement. Si ton téléphone chauffe
ou saccade : choisis **Low** dans le menu.
Réglages fins : objet `QUALITY` et `CONFIG` en haut du script (vitesses, durée de potion, portée du gant…),
`levelParams(n)` pour la difficulté de chaque niveau.

## Fichiers
| Fichier | Rôle |
|---|---|
| `index.html` | **Version pour l'APK**, 100 % hors ligne (~815 Ko). |
| `index-cdn.html` | Source à modifier (Three.js via CDN, sinon `libs/`). |
| `libs/` | Three.js r128 + post-processing (licence MIT). |
| `build.py` | `python3 build.py` → régénère `index.html`. |
| `icon.png` | Icône 512×512. |

## APK
Même méthode que les autres jeux : app « Construction rapide » → **Sélectionner un fichier HTML** → `index.html`,
icône `icon.png` → Créer et construire l'APK.
