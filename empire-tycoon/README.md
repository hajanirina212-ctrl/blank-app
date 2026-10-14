# 🏙️ Empire Tycoon

Jeu de gestion « idle » en **3D isométrique HD**, en un seul fichier HTML hors ligne. Bâtissez une ville de 12 commerces
répartis en 4 quartiers colorés (clin d'œil au jeu de société, sans aucune marque protégée), faites-les grandir… et
défendez-les face aux pannes, grèves, contrôles et **concurrents**. Noms, personnages et graphismes 100 % originaux.

**Aucune publicité, aucun achat intégré, aucune monétisation.**

## Comment jouer
- **Acheter** un commerce, puis **Améliorer** (maintenez le bouton pour répéter). Chaque commerce a un cycle : la barre se remplit, il rapporte, et recommence.
- Toucher un bâtiment accélère son cycle de 1 s. Glissez pour déplacer la ville, pincez / molette pour zoomer.
- **Paliers** (niveaux 25, 50, 100…) : revenus ×2 ; la boutique s'agrandit (maison → immeuble → hôtel doré). Un **quartier complet** (3 commerces) : revenus ×2.
- Bouton **×1 / ×10 / ×100 / Max** : nombre de niveaux achetés d'un coup.
- **Gains hors ligne** (50 % d'efficacité, jusqu'à 4 h) au retour : « Bon retour, patron ! ».

## Votre vie d'entrepreneur (en euros)
- Vous démarrez à **25 ans avec 2 500 € d'économies** : de quoi ouvrir un premier café (2 000 €). **1 jour = 10 s, 1 mois = 5 min, 1 an = 1 h de jeu** ; vous vieillissez.
- Chaque fin de mois, la **vie courante** (≈ 900 €, qui monte avec votre train de vie) est prélevée. Chaque année, **12 % d'impôts** sur les revenus. Si la caisse est vide, le **découvert** devient une **dette** (1,5 % d'intérêts par mois, 30 % de vos revenus la remboursent).
- Touchez la case de trésorerie en haut pour ouvrir **💶 Finances** : bilan du mois, charges à prévoir, **prêt bancaire** (plafonné selon vos revenus) et remboursement.
- **Rythme réaliste** : les gains hors ligne sont réduits de moitié (4 h max), les récompenses (VIP, quêtes, dés) restent modestes, et il faut des jours de jeu pour tout posséder.
- **Votre pion** (un patron en costume et haut-de-forme) se promène sur l'avenue qui fait le tour de la ville : touchez le bouton rond 🎲 pour lancer les dés et vous le **voyez avancer case par case**, la caméra le suit.

## La vraie vie d'un patron
| Problème | Effet | Solution |
|---|---|---|
| 🔧 Panne, 💧 dégât des eaux, 📋 contrôle sanitaire | le commerce **s'arrête** | payer « Réparer » (coût ≈ 30-50 s de ses revenus) |
| ✊ Grève | commerce à l'arrêt | négocier, ou attendre 2 min 30 |
| 🦹 Cambriolage, 🧾 amende fiscale | perte immédiate d'argent | rester riche… et prudent |
| ⚔️ **Concurrent** (Vantor, Delcourt & Fils, NovaRetail) | ouvre en face : **-35 %** sur tout le quartier | lancer une 📣 campagne (ou attendre 5 min) |
| 🏆 **Classement des empires** | 3 rivaux accumulent leur fortune en même temps que vous | grandissez plus vite ; ils subissent parfois des scandales |

Un patron attentif réagit vite : les incidents ne tombent que si vous avez au moins 2 commerces (concurrents : 3) et jamais pendant votre absence.

## Le reste
- 📜 **Quêtes** avec récompenses, 🧑‍💼 **Conseillers** (12 personnages, 4 raretés, équipez-en 2 à 4, doublons = bonus +50 %), 📰 **Journal & rivaux**.
- 🎲 **Plateau de la fortune** (20 cases : recettes, cartes Fortune, impôts, boosts, contrôle fiscal, recrue, jackpot). Un lancer offert toutes les 4 min.
- 💰 / ⚡ boosts gratuits (revenus ×2 pendant 60 s, cycles ×2 pendant 30 s, avec temps de recharge), 🤵 visiteurs VIP, événements de marché (boom, soldes, heure de pointe).
- ⭐ **Expansion mondiale** (prestige) : +5 % de revenus par étoile.
- Réglages : sons/musique, qualité (Auto / Faible / Moyenne / Élevée), code cadeau (essayez `BIENVENUE`, `EMPIRE`, `TYCOON`), export / import de sauvegarde. Sauvegarde automatique.
- Cycle jour / nuit, voitures, arbres, fenêtres allumées la nuit, ombres douces, MSAA.

## Fichiers
| Fichier | Rôle |
|---|---|
| `index.html` | **Version pour l'APK**, 100 % hors ligne (~730 Ko). |
| `index-cdn.html` | Version assemblée avec Three.js via CDN (secours : `libs/`). |
| `src/` | Sources : `engine.js` (économie), `gfx.js` (ville 3D), `ui.js` (interface, sons), `main.js`, `style.css`, `template.html`. |
| `build.py` | `python3 build.py` → régénère `index-cdn.html` et `index.html`. |
| `icon.png` | Icône 512×512. |

## APK
App « Construction rapide » → **Sélectionner un fichier HTML** → `index.html`, icône `icon.png` → Créer et construire l'APK.
Si le téléphone chauffe : Réglages → Qualité → Faible.
