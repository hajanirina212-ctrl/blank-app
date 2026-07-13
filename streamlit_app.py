import streamlit as st
import datetime
import json
import random
import os
import urllib.request
import urllib.error

# Page config & Custom Tab Title
st.set_page_config(
    page_title="KAIZENOS • High Density System",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Helper for elegant mock plans (high quality custom fallback)
def generate_mock_kaizen_plan(goal_name, why_deep, domain):
    name_lower = goal_name.lower()
    
    if "site" in name_lower or "saas" in name_lower or "web" in name_lower or "app" in name_lower or "cod" in name_lower or "programm" in name_lower or "tech" in name_lower:
        p_name = f"Développement Agile de {goal_name}"
        desc = "Une approche pas-à-pas pour lancer une application fonctionnelle de manière incrémentale."
        stages = [
            {
                "name": "Étape 1 : Prototype d'Interface & Design",
                "description": "Visualiser le produit final sans écrire de code lourd.",
                "tasks": [
                    {
                        "name": "Maquetter l'écran principal",
                        "description": "Dessiner les sections de l'application",
                        "microTasks": [
                            {"name": "Dessiner les 3 composants clés sur papier"},
                            {"name": "Lister les boutons interactifs principaux"},
                            {"name": "Choisir une palette de couleurs élégante (Slate/Violet)"}
                        ]
                    },
                    {
                        "name": "Configurer l'environnement de code",
                        "description": "Avoir un serveur de développement prêt",
                        "microTasks": [
                            {"name": "Créer le dossier du projet"},
                            {"name": "Initialiser le dépôt Git"},
                            {"name": "Lancer un serveur de test local 'Hello World'"}
                        ]
                    }
                ]
            },
            {
                "name": "Étape 2 : Core logique & Base de données",
                "description": "Donner vie au projet en gérant les données.",
                "tasks": [
                    {
                        "name": "Modéliser la structure de données",
                        "description": "Définir les champs requis",
                        "microTasks": [
                            {"name": "Lister les variables requises (id, date, statut)"},
                            {"name": "Créer un exemple de JSON de test"},
                            {"name": "Écrire les fonctions de lecture locales"}
                        ]
                    },
                    {
                        "name": "Écrire l'API de base",
                        "description": "Permettre la sauvegarde locale",
                        "microTasks": [
                            {"name": "Créer la fonction d'ajout d'élément"},
                            {"name": "Créer la fonction de suppression d'élément"},
                            {"name": "Vérifier le chargement au démarrage"}
                        ]
                    }
                ]
            },
            {
                "name": "Étape 3 : Polissage & Déploiement",
                "description": "Rendre l'application accessible et esthétique.",
                "tasks": [
                    {
                        "name": "Améliorer l'interface utilisateur",
                        "description": "Ajuster les espacements et contrastes",
                        "microTasks": [
                            {"name": "Vérifier la lisibilité sur mobile"},
                            {"name": "Ajouter des transitions fluides au survol"},
                            {"name": "Intégrer les icônes d'état et validations"}
                        ]
                    },
                    {
                        "name": "Lancer en production",
                        "description": "Mettre l'application en ligne",
                        "microTasks": [
                            {"name": "Créer un compte d'hébergement gratuit"},
                            {"name": "Configurer les variables d'environnement"},
                            {"name": "Lancer le premier déploiement public"}
                        ]
                    }
                ]
            }
        ]
    elif "langue" in name_lower or "anglais" in name_lower or "apprend" in name_lower or "étudi" in name_lower or "livre" in name_lower or "lire" in name_lower:
        p_name = f"Rituel d'Apprentissage Actif : {goal_name}"
        desc = "Intégrer l'apprentissage de manière organique sans surcharge mentale."
        stages = [
            {
                "name": "Étape 1 : Immersion Initiale",
                "description": "Habituer le cerveau à la nouvelle thématique.",
                "tasks": [
                    {
                        "name": "Sélectionner les meilleures ressources",
                        "description": "Filtrer pour ne garder que le contenu captivant",
                        "microTasks": [
                            {"name": "Trouver 2 podcasts de moins de 10 minutes"},
                            {"name": "Identifier 1 chaîne YouTube de référence"},
                            {"name": "Télécharger 1 application de fiches mémo"}
                        ]
                    },
                    {
                        "name": "Créer le rituel quotidien",
                        "description": "Associer l'apprentissage à un signal existant",
                        "microTasks": [
                            {"name": "Choisir le moment idéal (ex: au petit déjeuner)"},
                            {"name": "Préparer le support sur le bureau la veille"},
                            {"name": "Lancer un chronomètre de 5 minutes d'essai"}
                        ]
                    }
                ]
            },
            {
                "name": "Étape 2 : Pratique Active",
                "description": "Passer de la consommation passive à la production.",
                "tasks": [
                    {
                        "name": "Prendre des notes simplifiées",
                        "description": "Retenir l'essentiel en fiches courtes",
                        "microTasks": [
                            {"name": "Créer une fiche Notion ou papier"},
                            {"name": "Écrire 3 concepts clés appris aujourd'hui"},
                            {"name": "Expliquer un concept à voix haute pendant 1 minute"}
                        ]
                    },
                    {
                        "name": "Faire de petites sessions de mémorisation",
                        "description": "Utiliser la répétition espacée",
                        "microTasks": [
                            {"name": "Créer ses 5 premières fiches de révision"},
                            {"name": "Réviser les fiches de la veille en 2 minutes"},
                            {"name": "Faire un mini-test d'auto-évaluation"}
                        ]
                    }
                ]
            },
            {
                "name": "Étape 3 : Consolidation & Usage Réel",
                "description": "Mettre en pratique dans des situations concrètes.",
                "tasks": [
                    {
                        "name": "Converser ou rédiger de manière libre",
                        "description": "S'exprimer sans filtre ni peur du jugement",
                        "microTasks": [
                            {"name": "Rédiger un paragraphe de 3 phrases"},
                            {"name": "S'enregistrer sur son dictaphone pendant 30 secondes"},
                            {"name": "Traduire mentalement 5 objets autour de soi"}
                        ]
                    },
                    {
                        "name": "Faire le bilan de confiance",
                        "description": "Mesurer sa progression de 1%",
                        "microTasks": [
                            {"name": "Lister 5 expressions maîtrisées de plus"},
                            {"name": "Célébrer la régularité du rituel"},
                            {"name": "Planifier l'étape suivante d'apprentissage"}
                        ]
                    }
                ]
            }
        ]
    elif "sport" in name_lower or "sant" in name_lower or "run" in name_lower or "muscl" in name_lower or "poids" in name_lower:
        p_name = f"Transformation Physique Progressive : {goal_name}"
        desc = "Bâtir un corps sain à travers des actions infimes mais régulières."
        stages = [
            {
                "name": "Étape 1 : Réduire la Friction au Minimum",
                "description": "S'installer dans l'action sans effort mental.",
                "tasks": [
                    {
                        "name": "Préparer l'équipement",
                        "description": "Supprimer les obstacles matériels",
                        "microTasks": [
                            {"name": "Placer ses vêtements de sport à côté du lit la veille"},
                            {"name": "Remplir une gourde d'eau fraîche"},
                            {"name": "Sélectionner une playlist dynamique de 15 minutes"}
                        ]
                    },
                    {
                        "name": "Commencer ridiculement petit",
                        "description": "Seulement 5 minutes d'effort",
                        "microTasks": [
                            {"name": "Faire 5 pompes après s'être levé"},
                            {"name": "Faire 2 minutes d'étirements doux"},
                            {"name": "Marcher activement autour du pâté de maisons"}
                        ]
                    }
                ]
            },
            {
                "name": "Étape 2 : Créer un Momentum",
                "description": "Stabiliser la régularité avant d'augmenter l'intensité.",
                "tasks": [
                    {
                        "name": "Fixer le créneau dans la journée",
                        "description": "Rendre le temps non négociable",
                        "microTasks": [
                            {"name": "Bloquer 15 minutes dans l'agenda de demain"},
                            {"name": "Associer la séance à la fin d'une tâche de travail"},
                            {"name": "Suivre sa complétion sur le calendrier"}
                        ]
                    },
                    {
                        "name": "Augmenter l'intensité en douceur",
                        "description": "Appliquer la règle du 1% de surcharge progressive",
                        "microTasks": [
                            {"name": "Ajouter 1 répétition à chaque série"},
                            {"name": "Courir 1 minute de plus que la dernière fois"},
                            {"name": "Tenir 5 secondes de plus en gainage"}
                        ]
                    }
                ]
            },
            {
                "name": "Étape 3 : Alignement Nutrition & Récupération",
                "description": "Pérenniser l'énergie de manière globale.",
                "tasks": [
                    {
                        "name": "Améliorer les apports quotidiens",
                        "description": "Petits ajustements nutritionnels faciles",
                        "microTasks": [
                            {"name": "Remplacer 1 soda par un grand verre d'eau"},
                            {"name": "Ajouter une portion de légumes au déjeuner"},
                            {"name": "Lister 3 collations saines et rapides à préparer"}
                        ]
                    },
                    {
                        "name": "Verrouiller le sommeil réparateur",
                        "description": "Améliorer la qualité de la nuit",
                        "microTasks": [
                            {"name": "Couper les écrans 15 minutes avant le coucher"},
                            {"name": "Aérer la chambre pendant 5 minutes"},
                            {"name": "Faire 3 respirations abdominales lentes dans le noir"}
                        ]
                    }
                ]
            }
        ]
    else:
        p_name = f"Plan d'Action Kaizen : {goal_name}"
        desc = "Méthodologie universelle du pas-à-pas pour éliminer la procrastination."
        stages = [
            {
                "name": "Étape 1 : Clarté & Préparation",
                "description": "Définir précisément le périmètre d'action.",
                "tasks": [
                    {
                        "name": "Cadrer le périmètre",
                        "description": "Rendre l'objectif concret et mesurable",
                        "microTasks": [
                            {"name": "Rédiger le résultat idéal en 1 sentence"},
                            {"name": "Lister les 3 plus grands obstacles potentiels"},
                            {"name": "Écrire la première action de 5 minutes"}
                        ]
                    },
                    {
                        "name": "Rassembler les outils",
                        "description": "Éviter les interruptions techniques",
                        "microTasks": [
                            {"name": "Créer le dossier ou espace de travail dédié"},
                            {"name": "Trouver ou marquer les liens utiles"},
                            {"name": "Éteindre les notifications de téléphone pour 15 min"}
                        ]
                    }
                ]
            },
            {
                "name": "Étape 2 : Lancement & Premières Victoires",
                "description": "Engager l'action rapide de manière ultra-simple.",
                "tasks": [
                    {
                        "name": "Passer le cap des 5 premières minutes",
                        "description": "Briser la friction psychologique",
                        "microTasks": [
                            {"name": "Lancer un minuteur de 5 minutes"},
                            {"name": "Faire la toute première action sans chercher la perfection"},
                            {"name": "Prendre une inspiration profonde pour s'ancrer"}
                        ]
                    },
                    {
                        "name": "Installer la régularité",
                        "description": "Construire l'habitude jour après jour",
                        "microTasks": [
                            {"name": "Fixer un créneau horaire fixe de 15 minutes"},
                            {"name": "Associer la séance à un déclencheur automatique"},
                            {"name": "Noter sa première session sur le calendrier"}
                        ]
                    }
                ]
            },
            {
                "name": "Étape 3 : Optimisation & Amélioration de 1%",
                "description": "Raffiner et pérenniser la méthode.",
                "tasks": [
                    {
                        "name": "Mesurer les progrès réels",
                        "description": "Visualiser les petites étapes franchies",
                        "microTasks": [
                            {"name": "Cocher les tâches complétées"},
                            {"name": "Lister 2 apprentissages clés de la semaine"},
                            {"name": "Ajuster la vitesse pour éviter l'épuisement"}
                        ]
                    },
                    {
                        "name": "Verrouiller l'habitude durablement",
                        "description": "Incarner la nouvelle identité de réussite",
                        "microTasks": [
                            {"name": "Partager sa victoire de la semaine avec un proche"},
                            {"name": "Rédiger sa charte d'engagement pour le mois"},
                            {"name": "Planifier la prochaine séance de 15 minutes"}
                        ]
                    }
                ]
            }
        ]

    return {
        "projectName": p_name,
        "projectDescription": desc,
        "stages": stages
    }

def decompose_goal_with_gemini(goal_name, why_deep, domain):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return generate_mock_kaizen_plan(goal_name, why_deep, domain)
        
    prompt = f"""
    En tant qu'expert mondial de la méthode Kaizen, d'Atomic Habits (James Clear) et de la productivité :
    Décompose l'objectif suivant en 1 projet clé, contenant 3 étapes progressives.
    Chaque étape doit contenir 2 tâches d'action.
    Chaque tâche doit contenir exactement 3 micro-tâches Kaizen ultra-précises, réalisables en moins de 15 minutes.
    
    Détails de l'objectif :
    - Nom : {goal_name}
    - Pourquoi profond (Why) : {why_deep}
    - Domaine de vie : {domain}
    
    Respecte strictement la philosophie Kaizen : les micro-tâches de moins de 15 minutes doivent être extrêmement faciles à commencer pour éliminer TOUTE friction psychologique de démarrage.
    
    Réponds EXCLUSIVEMENT sous forme de JSON valide correspondant à la structure ci-dessous.
    """
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    payload = {
        "contents": [{
            "parts": [{
                "text": prompt
            }]
        }],
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": {
                "type": "OBJECT",
                "properties": {
                    "projectName": {"type": "STRING"},
                    "projectDescription": {"type": "STRING"},
                    "stages": {
                        "type": "ARRAY",
                        "items": {
                            "type": "OBJECT",
                            "properties": {
                                "name": {"type": "STRING"},
                                "description": {"type": "STRING"},
                                "tasks": {
                                    "type": "ARRAY",
                                    "items": {
                                        "type": "OBJECT",
                                        "properties": {
                                            "name": {"type": "STRING"},
                                            "description": {"type": "STRING"},
                                            "microTasks": {
                                                "type": "ARRAY",
                                                "items": {
                                                    "type": "OBJECT",
                                                    "properties": {
                                                        "name": {"type": "STRING"}
                                                    },
                                                    "required": ["name"]
                                                }
                                            }
                                        },
                                        "required": ["name", "description", "microTasks"]
                                    }
                                }
                            },
                            "required": ["name", "description", "tasks"]
                        }
                    }
                },
                "required": ["projectName", "projectDescription", "stages"]
            }
        }
    }
    
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req, timeout=12) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            text = res_data["candidates"][0]["content"]["parts"][0]["text"]
            return json.loads(text)
    except Exception as e:
        return generate_mock_kaizen_plan(goal_name, why_deep, domain)

# Initialize Session States
if "initialized" not in st.session_state:
    st.session_state["initialized"] = True
    st.session_state["level"] = 1
    st.session_state["xp"] = 150
    st.session_state["streak"] = 12
    st.session_state["deep_work_hours"] = 2.0
    st.session_state["target_deep_work"] = 4.0
    
    # Vision
    st.session_state["identity"] = "Je suis un créateur rigoureux et concentré qui s'améliore de 1% par jour."
    st.session_state["one_year_vision"] = "Consolider mes rituels de micro-actions quotidiennes et maîtriser l'art de démarrer sans friction."
    st.session_state["long_term_vision"] = "Incarner pleinement la philosophie Kaizen et accomplir de grands projets grâce aux petits pas."
    
    # Pre-populated initial Goal with full Kaizen action plan
    st.session_state["goals"] = [
        {
            "id": "init-goal",
            "name": "Lancer ma propre application web professionnelle",
            "description": "Créer et publier une application moderne simple en ligne pour mes clients.",
            "why": "Pour être indépendant financièrement, libre de mon temps et fier d'avoir construit un outil utile.",
            "startDate": "2026-07-13",
            "targetDate": "2026-10-31",
            "domain": "Carrière / Professionnel",
            "progress": 33,
            "projects": [
                {
                    "id": "init-proj",
                    "name": "Projet de Lancement KaizenOS",
                    "description": "Planification progressive et agile conçue pour éliminer la procrastination.",
                    "completed": False,
                    "stages": [
                        {
                            "id": "stage-1",
                            "name": "Étape 1 : Cadrage du Produit & Prototype",
                            "description": "Poser les bases visuelles et conceptuelles de l'application.",
                            "completed": False,
                            "stages": [],
                            "tasks": [
                                {
                                    "id": "task-1-1",
                                    "name": "Spécifier l'idée",
                                    "description": "Définir l'architecture et l'audience cible.",
                                    "status": "TODO",
                                    "microTasks": [
                                        {"id": "mt-1-1-1", "name": "Créer le fichier Notion/Word principal", "completed": True},
                                        {"id": "mt-1-1-2", "name": "Lister les 3 fonctionnalités absolument vitales", "completed": True},
                                        {"id": "mt-1-1-3", "name": "Rédiger le pitch d'identité en 1 paragraphe", "completed": False}
                                    ]
                                },
                                {
                                    "id": "task-1-2",
                                    "name": "Maquetter la page d'accueil",
                                    "description": "Dessiner l'expérience utilisateur.",
                                    "status": "TODO",
                                    "microTasks": [
                                        {"id": "mt-1-2-1", "name": "Prendre une feuille blanche et crayonner les 3 blocs principaux", "completed": False},
                                        {"id": "mt-1-2-2", "name": "Choisir une palette de 2 couleurs dominantes", "completed": False},
                                        {"id": "mt-1-2-3", "name": "Écrire le titre principal d'accroche", "completed": False}
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    ]
    
    st.session_state["habits"] = [
        {"id": 1, "name": "Session Deep Work : Code sans distraction", "cue": "À 9h00 • Téléphone éteint", "category": "Professionnel", "done": True},
        {"id": 2, "name": "Micro-action : Réviser 1 concept technique", "cue": "10 min • Immédiatement après mon café", "category": "Mindset", "done": False}
    ]
    
    st.session_state["procrastinations"] = [
        {"date": "2026-07-13", "task": "Acheter le nom de domaine de l'application", "trigger": "Peur d'échouer ou de dépenser pour rien", "cost": "Retard de lancement du projet", "win": "Ouvrir l'onglet d'enregistrement de domaine et juste chercher la disponibilité"}
    ]

# Calculate levels and XP
xp_needed = int(100 * (st.session_state["level"] ** 1.5))
xp_percent = min(1.0, float(st.session_state["xp"]) / xp_needed)

total_habits = len(st.session_state["habits"])
done_habits = sum(1 for h in st.session_state["habits"] if h["done"])
discipline_score = int((done_habits / total_habits) * 100) if total_habits > 0 else 100

# Custom Style (High Contrast slate theme)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #0B0F19 !important;
        color: #E2E8F0 !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    [data-testid="stHeader"] {
        background: rgba(11, 15, 25, 0.9) !important;
        backdrop-filter: blur(12px) !important;
        border-bottom: 1px solid #1E293B !important;
    }
    
    [data-testid="stSidebar"] {
        background-color: #070A13 !important;
        border-right: 1px solid #1E293B !important;
    }
    
    .kaizen-card {
        background-color: #111827;
        border: 1px solid #1F2937;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }
    
    .database-card {
        background: linear-gradient(135deg, rgba(79, 70, 229, 0.1) 0%, rgba(129, 140, 248, 0.02) 100%);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
    }

    .kaizen-header {
        font-weight: 900;
        font-size: 24px;
        letter-spacing: -1px;
        color: #F8FAFC;
        margin-bottom: 15px;
    }
    
    .kaizen-header span {
        color: #6366F1;
    }

    .identity-pill {
        background: #111827;
        border: 1px solid #1F2937;
        padding: 12px 18px;
        border-radius: 12px;
        margin-bottom: 24px;
    }

    .xp-bar {
        width: 100%;
        height: 6px;
        background: #1F2937;
        border-radius: 999px;
        position: relative;
        overflow: hidden;
        margin-top: 8px;
    }

    .xp-progress {
        position: absolute;
        left: 0;
        top: 0;
        height: 100%;
        background: #6366F1;
        border-radius: 999px;
    }

    .mono {
        font-family: 'JetBrains Mono', monospace;
    }

    .status-badge {
        font-size: 10px;
        font-family: 'JetBrains Mono', monospace;
        color: #818CF8;
        background: rgba(99, 102, 241, 0.1);
        padding: 2px 8px;
        border-radius: 4px;
        border: 1px solid rgba(99, 102, 241, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# Helper function to recalculate progress
def recalculate_goal_progress(goal_idx):
    goal = st.session_state["goals"][goal_idx]
    total_mt = 0
    completed_mt = 0
    if "projects" in goal and goal["projects"]:
        for p in goal["projects"]:
            for s in p["stages"]:
                for t in s["tasks"]:
                    for mt in t["microTasks"]:
                        total_mt += 1
                        if mt["completed"]:
                            completed_mt += 1
    
    if total_mt > 0:
        new_prog = int((completed_mt / total_mt) * 100)
    else:
        new_prog = 0
    st.session_state["goals"][goal_idx]["progress"] = new_prog

# SIDEBAR PORTRAIT
with st.sidebar:
    st.markdown('<div class="kaizen-header">🛡️ KAIZEN<span>OS</span></div>', unsafe_allow_html=True)
    
    # Progress Widget
    st.markdown(f"""
    <div class="identity-pill">
        <div style="font-size: 11px; color: #94A3B8; text-transform: uppercase; font-weight: 700; tracking-wide">Avatar de Progrès</div>
        <div style="font-size: 15px; font-weight: 800; color: #F1F5F9; margin-top: 4px;">Utilisateur • Level {st.session_state['level']}</div>
        <div style="display: flex; justify-content: space-between; align-items: center; font-size: 10px; color: #94A3B8; margin-top: 6px;">
            <span>XP : {st.session_state['xp']} / {xp_needed}</span>
            <span style="color: #34D399; font-weight: bold;">🔥 {st.session_state['streak']} Jours de Streak</span>
        </div>
        <div class="xp-bar">
            <div class="xp-progress" style="width: {xp_percent * 100}%;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🗺️ Hubs")
    menu = st.radio(
        "Sélectionnez un hub :",
        ["🎯 Mes Objectifs & IA Sensei", "🗄️ Base de Données & Stockage", "🧘 Mes Rituels quotidiens", "⚡ Anti-Procrastination"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.markdown(
        '<div style="font-style: italic; color: #94A3B8; border-left: 2px solid #6366F1; padding-left: 12px; font-size: 12px; line-height: 1.5">'
        '"Le secret pour avancer, c\'est de commencer en découpant vos tâches en actions de moins de 15 minutes."<br>— Philosophie Kaizen'
        '</div>',
        unsafe_allow_html=True
    )

# ----------------- Tab 1: Mes Objectifs & IA Sensei -----------------
if menu == "🎯 Mes Objectifs & IA Sensei":
    st.markdown("## 🎯 Gestion d'Objectifs Simplifiée par l'IA")
    st.markdown("Déclarez votre objectif de vie simple ou complexe. Notre IA Sensei se charge de concevoir instantanément vos **micro-tâches concrètes de moins de 15 minutes** pour éliminer toute friction d'action.")
    
    # Simple Mode toggle or settings
    col_view_left, col_view_right = st.columns([8, 4])
    with col_view_right:
        view_mode = st.selectbox("Format d'affichage :", ["Mode Simple (Conseillé)", "Mode Projet Structuré"], key="view_mode_select")
    
    # EXPANDER FORM TO ADD A GOAL
    with st.expander("➕ Déclarer un nouvel Objectif de vie", expanded=False):
        g_name = st.text_input("Nom de l'objectif :", placeholder="Ex: Lancer mon propre site internet, apprendre l'anglais, etc.")
        g_why = st.text_input("Pourquoi cet objectif est capital pour vous ? (Motivation profonde) :", placeholder="Ex: Pour me sentir plus indépendant financièrement et fier de mon temps.")
        g_desc = st.text_area("Description courte optionnelle :", placeholder="Ajouter des notes ou détails supplémentaires...")
        
        col_form1, col_form2 = st.columns(2)
        with col_form1:
            g_target = st.date_input("Date limite visée :", value=datetime.date.today() + datetime.timedelta(days=90))
        with col_form2:
            g_domain = st.selectbox("Domaine de Vie :", ["Carrière / Professionnel", "Santé / Physique", "Mental / Sagesse", "Finances", "Social / Famille"])
            
        if st.button("Créer l'Objectif 🚀", use_container_width=True):
            if g_name and g_why:
                new_goal = {
                    "id": f"goal-{random.randint(1000,9999)}",
                    "name": g_name,
                    "description": g_desc,
                    "why": g_why,
                    "startDate": str(datetime.date.today()),
                    "targetDate": str(g_target),
                    "domain": g_domain,
                    "progress": 0,
                    "projects": []
                }
                st.session_state["goals"].append(new_goal)
                st.success("Objectif créé ! Choisissez-le maintenant ci-dessous pour lancer sa décomposition.")
                st.rerun()
            else:
                st.warning("Veuillez renseigner au moins le Nom et votre Motivation profonde (Why).")

    # GOALS GRID & SELECTION
    if not st.session_state["goals"]:
        st.info("Vous n'avez pas encore défini d'objectif. Utilisez le formulaire ci-dessus pour déclarer votre premier objectif !")
    else:
        st.markdown("### 🏆 Sélectionnez un objectif actif pour voir ses micro-actions :")
        goal_names = [g["name"] for g in st.session_state["goals"]]
        selected_goal_name = st.selectbox("Objectif actif :", goal_names, label_visibility="collapsed")
        
        # Get selected goal and its index
        goal_idx = next(i for i, g in enumerate(st.session_state["goals"]) if g["name"] == selected_goal_name)
        goal = st.session_state["goals"][goal_idx]
        
        # Layout of details
        st.markdown(f"""
        <div class="kaizen-card">
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
                <span class="status-badge">{goal['domain']}</span>
                <span style="font-size:11px; color:#94A3B8; font-family:'JetBrains Mono';">Date limite : {goal['targetDate']}</span>
            </div>
            <h3 style="margin:10px 0 6px 0; font-size:20px; font-weight:800; color:#F8FAFC;">{goal['name']}</h3>
            <p style="font-size:13px; color:#94A3B8; margin-bottom:12px;">{goal['description']}</p>
            <div style="background-color:#070A13; padding:12px 16px; border-radius:10px; border:1px dashed #1E293B; font-size:12px; color:#F1F5F9; font-style:italic;">
                💡 <strong>Motivation profonde (Mon Why) :</strong> « {goal['why']} »
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Action plan presence check
        has_plan = "projects" in goal and len(goal["projects"]) > 0
        
        # AI Decomposer block if no plan exists
        if not has_plan:
            st.markdown("""
            <div style="background-color:rgba(99, 102, 241, 0.05); border-left:4px solid #6366F1; padding:16px; border-radius:8px; margin-bottom:20px;">
                <h4 style="margin:0 0 6px 0; font-size:14px; font-weight:700; color:#F8FAFC;">🤖 Votre plan d'action n'est pas encore initialisé</h4>
                <p style="margin:0; font-size:12px; color:#94A3B8;">
                    La philosophie Kaizen recommande d'éviter la surcharge en découpant vos objectifs en tâches de moins de 15 minutes. 
                    Laissez notre Intelligence Artificielle concevoir votre plan d'action instantanément !
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("✨ Décomposer cet objectif par l'IA (+100 XP)", type="primary", use_container_width=True):
                with st.spinner("L'IA Sensei analyse votre objectif et décompose les frictions..."):
                    action_plan = decompose_goal_with_gemini(goal["name"], goal["why"], goal["domain"])
                    
                    # Convert action plan structure
                    new_project = {
                        "id": f"proj-{random.randint(1000,9999)}",
                        "name": action_plan.get("projectName", f"Plan d'action de {goal['name']}"),
                        "description": action_plan.get("projectDescription", "Décomposition en actions rapides."),
                        "completed": False,
                        "stages": []
                    }
                    
                    for stage_idx, s in enumerate(action_plan.get("stages", [])):
                        new_stage = {
                            "id": f"stage-{stage_idx}-{random.randint(100,999)}",
                            "name": s.get("name", f"Étape {stage_idx+1}"),
                            "description": s.get("description", ""),
                            "completed": False,
                            "tasks": []
                        }
                        
                        for task_idx, t in enumerate(s.get("tasks", [])):
                            new_task = {
                                "id": f"task-{stage_idx}-{task_idx}-{random.randint(100,999)}",
                                "name": t.get("name", "Tâche d'action"),
                                "description": t.get("description", ""),
                                "status": "TODO",
                                "microTasks": []
                            }
                            
                            for mt_idx, mt in enumerate(t.get("microTasks", [])):
                                new_task["microTasks"].append({
                                    "id": f"mt-{stage_idx}-{task_idx}-{mt_idx}-{random.randint(1000,9999)}",
                                    "name": mt.get("name", "Action rapide de 15m"),
                                    "completed": False
                                })
                                
                            new_stage["tasks"].append(new_task)
                        new_project["stages"].append(new_stage)
                    
                    st.session_state["goals"][goal_idx]["projects"] = [new_project]
                    st.session_state["xp"] += 100
                    recalculate_goal_progress(goal_idx)
                    st.balloons()
                    st.success("Plan d'action conçu avec succès par l'IA Sensei ! +100 XP accordés !")
                    st.rerun()
        else:
            # Plan exists! We render it
            flat_mts = []
            for p_idx, p in enumerate(goal["projects"]):
                for s_idx, s in enumerate(p["stages"]):
                    for t_idx, t in enumerate(s["tasks"]):
                        for mt_idx, mt in enumerate(t["microTasks"]):
                            flat_mts.append({
                                "id": mt["id"],
                                "name": mt["name"],
                                "completed": mt["completed"],
                                "p_idx": p_idx,
                                "s_idx": s_idx,
                                "t_idx": t_idx,
                                "mt_idx": mt_idx,
                                "parent_task": t["name"]
                            })
            
            # Recalculate and show Progress bar
            done_cnt = sum(1 for m in flat_mts if m["completed"])
            total_cnt = len(flat_mts)
            progress_val = int((done_cnt / total_cnt) * 100) if total_cnt > 0 else 0
            st.session_state["goals"][goal_idx]["progress"] = progress_val
            
            st.markdown(f"**Progression globale de l'objectif : {progress_val}%**")
            st.progress(progress_val / 100.0)
            
            if view_mode == "Mode Simple (Conseillé)":
                st.markdown("#### ⚡ Vos micro-actions de moins de 15 minutes :")
                st.write("Faites un petit pas aujourd'hui. Cochez une action rapide pour l'archiver.")
                
                # Render list
                for m in flat_mts:
                    col_chk, col_txt = st.columns([1, 15])
                    with col_chk:
                        # Streamlit Checkbox
                        is_mt_done = st.checkbox("", value=m["completed"], key=f"chk_mt_{m['id']}")
                        if is_mt_done != m["completed"]:
                            st.session_state["goals"][goal_idx]["projects"][m["p_idx"]]["stages"][m["s_idx"]]["tasks"][m["t_idx"]]["microTasks"][m["mt_idx"]]["completed"] = is_mt_done
                            if is_mt_done:
                                st.session_state["xp"] += 15
                            else:
                                st.session_state["xp"] = max(0, st.session_state["xp"] - 15)
                            recalculate_goal_progress(goal_idx)
                            st.rerun()
                    with col_txt:
                        text_style = "text-decoration: line-through; color: #64748B;" if m["completed"] else "color: #E2E8F0;"
                        st.markdown(f"""
                        <div style="font-size:13px; font-weight:500; {text_style} margin-top: 2px;">
                            {m['name']} <span style="font-size:10px; color:#6366F1; font-family:'JetBrains Mono'; margin-left:8px;">[Tâche : {m['parent_task']}]</span>
                        </div>
                        """, unsafe_allow_html=True)
                
                # Form to add a manual custom micro-task simply
                st.markdown("---")
                st.markdown("##### ➕ Ajouter une micro-action personnalisée :")
                new_custom_mt = st.text_input("Saisir une action rapide à accomplir en moins de 15 min :", placeholder="Ex: Envoyer un email de relance...", key="new_custom_mt_input")
                if st.button("Ajouter à la liste active", use_container_width=True):
                    if new_custom_mt:
                        proj = st.session_state["goals"][goal_idx]["projects"][0]
                        if not proj["stages"]:
                            proj["stages"] = [{
                                "id": f"stage-{random.randint(100,999)}",
                                "name": "Actions complémentaires",
                                "description": "Micro-actions ajoutées manuellement",
                                "completed": False,
                                "tasks": []
                            }]
                        stage = proj["stages"][0]
                        if not stage["tasks"]:
                            stage["tasks"] = [{
                                "id": f"task-{random.randint(100,999)}",
                                "name": "Actions Libres",
                                "description": "Actions simples",
                                "status": "TODO",
                                "microTasks": []
                            }]
                        task = stage["tasks"][0]
                        task["microTasks"].append({
                            "id": f"mt-custom-{random.randint(1000,9999)}",
                            "name": new_custom_mt,
                            "completed": False
                        })
                        st.session_state["xp"] += 5
                        recalculate_goal_progress(goal_idx)
                        st.success("Micro-action ajoutée ! +5 XP.")
                        st.rerun()
            else:
                # Mode Projet Structuré (stages, tasks, microTasks details)
                st.markdown("#### 🧩 Structure Détaillée de votre Plan d'Action :")
                
                for p_idx, p in enumerate(goal["projects"]):
                    st.markdown(f"##### Projet : {p['name']}")
                    st.write(p["description"])
                    
                    for s_idx, s in enumerate(p["stages"]):
                        with st.expander(f"📌 {s['name']}", expanded=True):
                            st.caption(s["description"])
                            
                            for t_idx, t in enumerate(s["tasks"]):
                                st.markdown(f"**🔹 Tâche principale : {t['name']}**")
                                st.markdown(f"<span style='font-size:11px; color:#94A3B8; margin-left: 12px;'>{t['description']}</span>", unsafe_allow_html=True)
                                
                                # Render micro tasks
                                for mt_idx, mt in enumerate(t["microTasks"]):
                                    col_chk_adv, col_txt_adv = st.columns([1, 15])
                                    with col_chk_adv:
                                        is_mt_done = st.checkbox("", value=mt["completed"], key=f"chk_mt_adv_{mt['id']}")
                                        if is_mt_done != mt["completed"]:
                                            st.session_state["goals"][goal_idx]["projects"][p_idx]["stages"][s_idx]["tasks"][t_idx]["microTasks"][mt_idx]["completed"] = is_mt_done
                                            if is_mt_done:
                                                st.session_state["xp"] += 15
                                            else:
                                                st.session_state["xp"] = max(0, st.session_state["xp"] - 15)
                                            recalculate_goal_progress(goal_idx)
                                            st.rerun()
                                    with col_txt_adv:
                                        text_style = "text-decoration: line-through; color: #64748B;" if mt["completed"] else "color: #E2E8F0;"
                                        st.markdown(f"""
                                        <div style="font-size:12px; {text_style} margin-top:2px;">
                                            {mt['name']}
                                        </div>
                                        """, unsafe_allow_html=True)
                                st.markdown('<div style="margin-bottom:12px;"></div>', unsafe_allow_html=True)

        # BUTTON TO RESET OR REMOVE AN OBJECTIVE
        st.markdown("---")
        if st.button("❌ Supprimer cet objectif", type="secondary", use_container_width=True):
            st.session_state["goals"].pop(goal_idx)
            st.warning("Objectif supprimé.")
            st.rerun()

# ----------------- Tab 2: Base de Données & Stockage -----------------
elif menu == "🗄️ Base de Données & Stockage":
    st.markdown("## 🗄️ Architecture de Données & Stockage de KaizenOS")
    
    st.markdown("""
    <div class="database-card">
        <h3 style="margin:0 0 10px 0; font-size:18px; font-weight:800; color:#F8FAFC;">📁 Où se trouve notre base de données ?</h3>
        <p style="margin:0 0 12px 0; font-size:13px; color:#E2E8F0; line-height:1.6;">
            Actuellement, l'application fonctionne avec un système de stockage hybride hautement performant :
        </p>
        <ul style="font-size:13px; color:#94A3B8; line-height:1.6; margin-left:20px;">
            <li><strong>Streamlit Session State :</strong> Pour l'interface Streamlit Python, vos données sont conservées en mémoire vive applicative (<code style="background-color:#0F172A; padding:2px 6px; border-radius:4px; color:#F43F5E;">st.session_state</code>). C'est ce qui permet une réactivité instantanée à la milliseconde sans aucune latence réseau.</li>
            <li><strong>Browser localStorage (Navigateur client) :</strong> Pour la version Web interactive React, vos données sont automatiquement enregistrées et persistées directement dans la mémoire physique locale de votre propre navigateur (<code style="background-color:#0F172A; padding:2px 6px; border-radius:4px; color:#F43F5E;">localStorage</code>).</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    col_db1, col_db2 = st.columns(2)
    with col_db1:
        st.markdown("""
        <div class="kaizen-card" style="height:100%;">
            <h4 style="margin:0 0 10px 0; font-size:14px; font-weight:700; color:#F8FAFC;">✔️ Avantages de cette approche</h4>
            <ul style="font-size:12px; color:#94A3B8; line-height:1.6; margin-left:15px; padding-left:0;">
                <li><strong>Zéro connexion requise :</strong> L'application fonctionne entièrement hors-ligne, vous permettant de rester concentré sans dépendre d'une connexion internet fluctuante.</li>
                <li><strong>Confidentialité absolue :</strong> Vos objectifs de vie, vos motivations profondes et vos rituels quotidiens restent stockés chez vous, sur votre appareil, et ne sont jamais revendus à des tiers.</li>
                <li><strong>Vitesse instantanée :</strong> Aucune requête SQL distante n'interrompt votre flux de Deep Work (zéro délai de chargement).</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
    with col_db2:
        st.markdown("""
        <div class="kaizen-card" style="height:100%;">
            <h4 style="margin:0 0 10px 0; font-size:14px; font-weight:700; color:#F8FAFC;">💡 Besoin d'une Synchronisation Cloud ?</h4>
            <p style="font-size:12px; color:#94A3B8; line-height:1.6; margin:0 0 10px 0;">
                Si vous souhaitez utiliser KaizenOS sur plusieurs appareils simultanément (comme votre téléphone portable et votre ordinateur de bureau) tout en conservant vos progrès à jour, nous pouvons configurer une base de données Cloud persistante !
            </p>
            <p style="font-size:12px; color:#E2E8F0; line-height:1.6; margin:0;">
                Dites-moi simplement : <strong>« Configure Firebase Firestore »</strong> et j'activerai le module de base de données à distance sécurisé pour synchroniser vos données sur le Cloud.
            </p>
        </div>
        """, unsafe_allow_html=True)

    # VIEW DATABASE CONTENT (JSON INSPECTOR)
    st.markdown("### 🔍 Inspecteur de Base de Données en direct :")
    st.write("Voici la représentation JSON de vos données en temps réel telles qu'elles sont stockées dans l'application :")
    
    inspect_data = {
        "level": st.session_state["level"],
        "xp": st.session_state["xp"],
        "streak": st.session_state["streak"],
        "goals": st.session_state["goals"],
        "habits": st.session_state["habits"],
        "procrastinations": st.session_state["procrastinations"]
    }
    st.json(inspect_data)

# ----------------- Tab 3: Mes Rituels quotidiens -----------------
elif menu == "🧘 Mes Rituels quotidiens":
    st.markdown("## 🧘 Rituels & Habitudes d'Identité")
    st.markdown("James Clear (Atomic Habits) : « Chaque action que vous entreprenez est un vote pour le type de personne que vous souhaitez devenir. »")
    
    # Simple form to add a habit
    with st.expander("➕ Enregistrer un nouveau Rituel quotidien (Conditionnement)", expanded=False):
        h_name = st.text_input("Nom du rituel :", placeholder="Ex: Faire 20 pushups, Méditer 5 min...")
        h_cue = st.text_input("Signal de démarrage (Cue) :", placeholder="Ex: Immédiatement après avoir posé ma tasse de café le matin...")
        h_cat = st.selectbox("Catégorie :", ["Professionnel", "Santé / Physique", "Mindset / Mental", "Social / Autre"])
        if st.button("Enregistrer le Rituel 💾", use_container_width=True):
            if h_name and h_cue:
                st.session_state["habits"].append({
                    "id": random.randint(100, 999),
                    "name": h_name,
                    "cue": h_cue,
                    "category": h_cat,
                    "done": False
                })
                st.success("Rituel quotidien ajouté !")
                st.rerun()

    # Habit Tracker List
    st.markdown("### Vos Rituels pour aujourd'hui :")
    for idx, h in enumerate(st.session_state["habits"]):
        col_chk_hab, col_det_hab, col_del_hab = st.columns([1, 8, 1])
        with col_chk_hab:
            is_done = st.checkbox("", value=h["done"], key=f"hab_chk_{h['id']}")
            if is_done != h["done"]:
                st.session_state["habits"][idx]["done"] = is_done
                if is_done:
                    st.session_state["xp"] += 25
                else:
                    st.session_state["xp"] = max(0, st.session_state["xp"] - 25)
                st.rerun()
        with col_det_hab:
            style_h = "text-decoration: line-through; color: #64748B;" if h["done"] else "color: #E2E8F0;"
            st.markdown(f"""
            <div style="{style_h} margin-top:2px;">
                <span style="font-weight:700; font-size:13px;">{h['name']}</span> <span style="font-size:10px; color:#A1A1AA;" class="mono">[{h['category']}]</span><br>
                <span style="font-size:11px; color:#94A3B8;">⚡ Déclencheur : {h['cue']}</span>
            </div>
            """, unsafe_allow_html=True)
        with col_del_hab:
            if st.button("❌", key=f"del_hab_{h['id']}"):
                st.session_state["habits"].pop(idx)
                st.warning("Rituel supprimé.")
                st.rerun()

# ----------------- Tab 4: Anti-Procrastination -----------------
elif menu == "⚡ Anti-Procrastination":
    st.markdown("## 🛡️ Anti-Procrastination : Journal d'Évitement")
    st.markdown("Comprenez les mécanismes psychologiques de l'évitement comportemental et brisez-les avec la règle des 2 minutes d'Atomic Habits.")
    
    with st.expander("📝 Consigner une friction d'action", expanded=True):
        ap_task = st.text_input("Tâche évitée :", placeholder="Ex: Rédiger le rapport trimestriel...")
        ap_trigger = st.selectbox("Facteur déclencheur (La cause) :", [
            "Peur de l'imperfection / Perfectionnisme",
            "Manque de clarté / Ambiguité de la tâche",
            "Fatigue / Surcharge cognitive",
            "Tâche ennuyeuse / Absence de récompense immédiate"
        ])
        ap_cost = st.text_input("Coût du délai (Conséquence si repoussé) :", placeholder="Ex: Stress intense et retard de livraison...")
        ap_win = st.text_input("La Micro-Victoire d'Entrée (Moins de 2 minutes) :", placeholder="Ex: Ouvrir le document Word et écrire juste un titre.")
        
        if st.button("Enregistrer l'Analyse 🛡️", use_container_width=True):
            if ap_task and ap_win:
                st.session_state["procrastinations"].append({
                    "date": str(datetime.date.today()),
                    "task": ap_task,
                    "trigger": ap_trigger,
                    "cost": ap_cost,
                    "win": ap_win
                })
                st.success("Analyse enregistrée ! Réalisez votre micro-victoire de 2 minutes maintenant.")
                st.rerun()

    # Display procrastination log
    st.markdown("### Analyses de Friction Passées :")
    for idx, log in enumerate(st.session_state["procrastinations"]):
        st.markdown(f"""
        <div class="kaizen-card">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                <span style="font-weight:700; font-size:14px; color:#F8FAFC;">{log['task']}</span>
                <span style="font-size:10px; color:#94A3B8;" class="mono">{log['date']}</span>
            </div>
            <div style="font-size:12px; line-height:1.6; color:#94A3B8;">
                ⚠️ <strong>Déclencheur :</strong> {log['trigger']}<br>
                📉 <strong>Coût de l'évitement :</strong> {log['cost']}<br>
                🛡️ <strong>Micro-Victoire conseillée :</strong> <span style="color:#818CF8; font-weight:700;">{log['win']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"Supprimer l'analyse {idx+1}", key=f"del_ap_{idx}"):
            st.session_state["procrastinations"].pop(idx)
            st.rerun()
