# 🥕 Carrot Castle 3D

Jeu de réflexion / plateformes en **3D réaliste (HD)**, en un seul fichier HTML, inspiré des mécaniques des jeux
« château à carottes » de la fin des années 80. **Personnages, nom et histoire 100 % originaux** (aucun personnage
ni marque protégés).

## Histoire
Le Baron **Grimfang** a enfermé **Clover** au sommet de son château. **Pip**, un lièvre courageux, doit ramasser
toutes les **carottes enchantées** de chaque salle pour monter, étage après étage, jusqu'à elle. 20 niveaux ;
au dernier, la cage s'ouvre (cinématique).

## 🎥 Trois angles de caméra (bouton 🎥 en haut à droite, touche V, ou menu / pause)
| Angle | Description |
|---|---|
| **Côté** (par défaut) | Vue en coupe du château, comme les classiques : on voit tous les étages. |
| **Épaule** | Caméra derrière Pip, dans le couloir. |
| **FPS** | Tu vois par les yeux de Pip : couloirs, fenêtres, torches, escaliers à la première personne. |

- En **épaule / FPS** : la caméra se tourne vers ta direction de marche (demi-tour fluide) ; **glisse le doigt à droite**
  de l'écran (ou la souris, après un clic) pour **regarder autour** (±70°) ; le regard revient seul au centre.
  Dans un escalier, la caméra suit la pente.
- Le château s'ouvre sur une façade intérieure (fenêtres, torches) quand tu quittes la vue de côté.
- Le choix est mémorisé.

## Règles (comme les classiques du genre)
- Ramasse **toutes les carottes** d'un niveau → niveau terminé.
- **Pas de saut, pas d'arme** : on se déplace sur les étages, on prend les **escaliers** (▲/▼) et les **portes**
  (les portes de même couleur sont reliées).
- On se défend avec les **objets** :
  - **Caisse** (dès le niveau 1) : ACTION pour la pousser → elle glisse et assomme tout sur son passage.
  - **Gant à ressort** (niveau 2+) : ACTION à côté → coup de poing de 3,8 m dans ta direction.
  - **Potion verte** (niveau 3+) : 7 s d'invincibilité, fonce sur les ennemis !
- **💨 ROULADE** (Maj ou X, bouton vert) : un saut périlleux qui **traverse les ennemis sans dégât** (recharge 2 s).
  C'est ta **sortie de secours** : plus de situation sans issue.
- Ennemis : **Armure hantée** (lente, tenace), **Corbeau** (imprévisible, vole en rasant le sol quand il te voit),
  **Loup** (trot, puis galop quand il te voit), **Fantôme** (traverse les portes). Un ennemi assommé revient après 7 s.
- 3 vies (5 en Facile), +1 vie tous les 5 niveaux. **Codes de niveau** affichés à chaque fin de niveau, à saisir dans le menu.
- Mini-carte en coupe + **flèches rouges** au bord de l'écran quand un ennemi approche hors champ (même s'il est derrière toi en FPS).

## Difficulté (menu) : Facile / Normal / Difficile
Niveaux 1-2 : **un seul ennemi, lent**, à l'étage du dessus. Ensuite la difficulté monte doucement.
Au début d'un niveau (et après chaque coup), **les ennemis restent calmes quelques secondes** et ne peuvent plus
t'attendre au point de départ. Chaque étage est relié par **2 escaliers éloignés** : il y a toujours une autre issue.
Les ennemis ne te poursuivent d'un étage à l'autre qu'à partir du niveau 3, et seulement s'ils sont proches.

## Contrôles
| | Mobile | Clavier |
|---|---|---|
| Marcher | Joystick gauche | ← → / Q D / A D |
| Monter / descendre (escalier, porte) | ▲ / ▼ (ou joystick haut/bas) | ↑ ↓ / Z S / W S |
| Action (caisse, gant, porte) | ✊ ACTION | E ou Espace |
| Roulade | 💨 ROULADE | Maj ou X |
| Regarder autour (épaule / FPS) | Glisser à droite | Souris (clic pour capturer) |
| Caméra | 🎥 | V |
| Pause | ⏸ | P / Échap |

Les boutons ▲ ▼ ACTION **brillent** quand une action est possible.

## Mouvements réalistes
- Cycle de marche **synchronisé avec la distance parcourue** (les pieds ne patinent pas) : genoux, chevilles et
  coudes articulés, bras opposés aux jambes, buste qui penche et pivote, tête qui accompagne.
- **Inertie** : démarrage et arrêt en douceur ; **demi-tours progressifs** ; respiration, clignement des yeux,
  oreilles à ressort qui se couchent en courant, écharpe qui flotte.
- Ennemis : l'armure marche d'un pas raide en tenant sa hallebarde verticale ; le loup passe du pas au **trot puis au
  galop** (allure et pattes coordonnées en diagonale) ; le corbeau sautille comme un pigeon ou vole en rasant le sol ;
  le fantôme flotte et ondule avec sa traîne. Au repos : ils scrutent, reniflent, picorent.
- Roulade : vrai saut périlleux en boule.

## Rendu HD réaliste
- Résolution native jusqu'à 2x, **MSAA 4x**, filtrage anisotrope 16x, filtre de netteté, textures procédurales
  1024 px (2048 px en High), ombres douces 2048 (4096 en High), SSAO + ombre de torche en High.
- Pierre fissurée, éclatée et humide ; poutres, plinthes, ombres de contact ; tonneaux, tapis, lanternes suspendues ;
  fenêtres encadrées avec paysage de crépuscule et rayons de lumière ; contre-jour froid ; étalonnage cinéma
  (contraste, saturation, ombres froides / lumières chaudes), aberration chromatique légère, vignette.
- Personnages détaillés : yeux brillants, moustaches, doigts, fourrure à reflet « sheen », armure en acier poli.

| | Low | Medium (mobile par défaut) | High (PC par défaut) |
|---|---|---|---|
| Résolution | 1,25x | 2x | 2x |
| Anti-crénelage | MSAA natif | MSAA 4x | MSAA 4x |
| Textures | 512 | 1024 | 2048 |
| Ombres | 1024 | 2048 | 4096 + torche |
| Bloom / rayons / flou menu | – | ✅ | ✅ |
| SSAO | – | – | ✅ |

Si le jeu passe sous 40 FPS en mode Auto, la qualité baisse d'un cran automatiquement. Si ton téléphone chauffe
ou saccade : choisis **Low** dans le menu.
Réglages fins : objets `QUALITY`, `CONFIG`, `DIFFS` et fonction `levelParams(n)` en haut du script.

## Fichiers
| Fichier | Rôle |
|---|---|
| `index.html` | **Version pour l'APK**, 100 % hors ligne (~860 Ko). |
| `index-cdn.html` | Source à modifier (Three.js via CDN, sinon `libs/`). |
| `libs/` | Three.js r128 + post-processing (licence MIT). |
| `build.py` | `python3 build.py` → régénère `index.html`. |
| `icon.png` | Icône 512×512. |

## APK
Même méthode que les autres jeux : app « Construction rapide » → **Sélectionner un fichier HTML** → `index.html`,
icône `icon.png` → Créer et construire l'APK.
