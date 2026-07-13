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
    Décompose l'objectif de vie suivant en 1 projet clé, contenant 3 étapes progressives.
    Chaque étape doit contenir 2 tâches d'action.
    Chaque tâche doit contenir exactement 3 micro-tâches Kaizen ultra-précises, pragmatiques, prêtes à être exécutées immédiatement en moins de 15 minutes.
    
    CRUCIAL POUR LES MICRO-TÂCHES KAIZEN : Ne donne pas de notions vagues comme "Planifier", "Analyser", "Faire des recherches" ou "Rédiger le contenu". Donne à la place l'ACTION PHYSIQUE OU DIGITALE EXACTE, ULTRA-CIBLÉE ET FACILE.
    Exemples de micro-actions Kaizen à imiter :
    - "Ouvrir un Google Doc vide et écrire le titre principal en gras"
    - "Écrire une liste de 3 questions clés à poser au client sur un post-it"
    - "Ouvrir l'application de vocabulaire et traduire 5 mots simples"
    - "Prendre une feuille blanche, un crayon et dessiner le logo sous forme de 3 carrés simples"
    - "Envoyer un SMS de 1 phrase à mon mentor pour lui demander s'il est libre"
    - "Ouvrir mon navigateur sur la page d'inscription de l'hébergeur et remplir le champ email"
    
    Chaque micro-tâche doit être formulée comme un premier pas si ridiculeusement petit qu'il est IMPOSSIBLE de procrastiner dessus.
    
    De plus, génère également 2 à 3 rituels et habitudes saines (Atomic Habits) qui soutiennent directement la réalisation de cet objectif au quotidien. Chaque habitude doit comprendre : un nom simple, un signal déclencheur clair (Cue) (ex: 'Dès que je ferme mon ordinateur à 18h'), une routine Kaizen rapide (moins de 10-15 minutes) pour éliminer toute friction, et une récompense immédiate saine (Reward).
    
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
                    },
                    "suggestedHabits": {
                        "type": "ARRAY",
                        "items": {
                            "type": "OBJECT",
                            "properties": {
                                "name": {"type": "STRING"},
                                "cue": {"type": "STRING"},
                                "routine": {"type": "STRING"},
                                "reward": {"type": "STRING"},
                                "frequency": {"type": "STRING"}
                            },
                            "required": ["name", "cue", "routine", "reward", "frequency"]
                        }
                    }
                },
                "required": ["projectName", "projectDescription", "stages", "suggestedHabits"]
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
            "name": "Bâtir un système d'apprentissage autonome",
            "description": "Mettre en place des outils d'études quotidiens sans surcharge cognitive.",
            "why": "Pour acquérir de nouvelles compétences clés et grandir de 1% chaque jour en toute liberté.",
            "startDate": "2026-07-13",
            "targetDate": "2026-10-31",
            "domain": "Mental / Sagesse",
            "progress": 33,
            "projects": [
                {
                    "id": "init-proj",
                    "name": "Projet d'Études Kaizen",
                    "description": "Planification progressive conçue pour assimiler des connaissances sans effort et éliminer la procrastination.",
                    "completed": False,
                    "stages": [
                        {
                            "id": "stage-1",
                            "name": "Étape 1 : Poser les bases du rituel d'études",
                            "description": "Prendre de bonnes habitudes de lecture et de prise de note.",
                            "completed": False,
                            "tasks": [
                                {
                                    "id": "task-1-1",
                                    "name": "Identifier les sujets d'apprentissage prioritaires",
                                    "description": "Définir la direction d'apprentissage de l'année.",
                                    "status": "TODO",
                                    "microTasks": [
                                        {"id": "mt-1-1-1", "name": "Créer un espace Notion ou un carnet de notes physique", "completed": True},
                                        {"id": "mt-1-1-2", "name": "Lister les 3 thématiques d'études prioritaires", "completed": True},
                                        {"id": "mt-1-1-3", "name": "Sélectionner 1 livre ou article de référence de départ", "completed": False}
                                    ]
                                },
                                {
                                    "id": "task-1-2",
                                    "name": "Préparer l'environnement d'étude idéal",
                                    "description": "Créer un espace propice au Deep Work sans distractions.",
                                    "status": "TODO",
                                    "microTasks": [
                                        {"id": "mt-1-2-1", "name": "Nettoyer mon bureau de travail physique", "completed": False},
                                        {"id": "mt-1-2-2", "name": "Installer un bloqueur d'applications ou éteindre le téléphone", "completed": False},
                                        {"id": "mt-1-2-3", "name": "Écrire une affirmation d'intention claire sur un post-it", "completed": False}
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
        {"id": 1, "name": "Lecture réflexive", "cue": "À 18h • Dès que je ferme mon ordinateur", "category": "Mindset / Mental", "done": True},
        {"id": 2, "name": "Micro-méditation", "cue": "2 min • Dès que mon café du matin coule", "category": "Santé / Physique", "done": False}
    ]
    
    st.session_state["procrastinations"] = [
        {"date": "2026-07-13", "task": "Acheter le nom de domaine de l'application", "trigger": "Peur d'échouer ou de dépenser pour rien", "cost": "Retard de lancement du projet", "win": "Ouvrir l'onglet d'enregistrement de domaine et juste chercher la disponibilité"}
    ]

# Sanitize and normalize Session State to prevent any KeyError or TypeError across runs
if "goals" not in st.session_state or not isinstance(st.session_state["goals"], list):
    st.session_state["goals"] = []

sanitized_goals = []
for idx, g in enumerate(st.session_state["goals"]):
    if isinstance(g, dict):
        sanitized_g = {
            "id": g.get("id") or f"goal-{random.randint(1000,9999)}",
            "name": g.get("name") or g.get("description") or f"Objectif #{idx + 1}",
            "description": g.get("description") or "",
            "why": g.get("why") or "Motivation non spécifiée",
            "startDate": g.get("startDate") or str(datetime.date.today()),
            "targetDate": g.get("targetDate") or str(datetime.date.today() + datetime.timedelta(days=90)),
            "domain": g.get("domain") or "Carrière / Professionnel",
            "progress": int(g.get("progress", 0)) if str(g.get("progress", 0)).isdigit() else 0,
            "projects": g.get("projects") or []
        }
        if not isinstance(sanitized_g["projects"], list):
            sanitized_g["projects"] = []
            
        sanitized_projects = []
        for p in sanitized_g["projects"]:
            if isinstance(p, dict):
                sanitized_p = {
                    "id": p.get("id") or f"proj-{random.randint(1000,9999)}",
                    "name": p.get("name") or "Plan d'action",
                    "description": p.get("description") or "",
                    "completed": bool(p.get("completed", False)),
                    "stages": p.get("stages") or []
                }
                if not isinstance(sanitized_p["stages"], list):
                    sanitized_p["stages"] = []
                    
                sanitized_stages = []
                for s in sanitized_p["stages"]:
                    if isinstance(s, dict):
                        sanitized_s = {
                            "id": s.get("id") or f"stage-{random.randint(100,999)}",
                            "name": s.get("name") or "Étape",
                            "description": s.get("description") or "",
                            "completed": bool(s.get("completed", False)),
                            "tasks": s.get("tasks") or []
                        }
                        if not isinstance(sanitized_s["tasks"], list):
                            sanitized_s["tasks"] = []
                            
                        sanitized_tasks = []
                        for t in sanitized_s["tasks"]:
                            if isinstance(t, dict):
                                sanitized_t = {
                                    "id": t.get("id") or f"task-{random.randint(100,999)}",
                                    "name": t.get("name") or "Tâche",
                                    "description": t.get("description") or "",
                                    "status": t.get("status") or "TODO",
                                    "microTasks": t.get("microTasks") or []
                                }
                                if not isinstance(sanitized_t["microTasks"], list):
                                    sanitized_t["microTasks"] = []
                                    
                                sanitized_mts = []
                                for mt in sanitized_t["microTasks"]:
                                    if isinstance(mt, dict):
                                        sanitized_mts.append({
                                            "id": mt.get("id") or f"mt-{random.randint(1000,9999)}",
                                            "name": mt.get("name") or "Action rapide",
                                            "completed": bool(mt.get("completed", False))
                                        })
                                sanitized_t["microTasks"] = sanitized_mts
                                sanitized_tasks.append(sanitized_t)
                        sanitized_s["tasks"] = sanitized_tasks
                        sanitized_stages.append(sanitized_s)
                sanitized_p["stages"] = sanitized_stages
                sanitized_projects.append(sanitized_p)
        sanitized_g["projects"] = sanitized_projects
        sanitized_goals.append(sanitized_g)
st.session_state["goals"] = sanitized_goals

if "habits" not in st.session_state or not isinstance(st.session_state["habits"], list):
    st.session_state["habits"] = []

sanitized_habits = []
for h in st.session_state["habits"]:
    if isinstance(h, dict):
        sanitized_habits.append({
            "id": h.get("id") or random.randint(100, 999),
            "name": h.get("name") or "Rituel sans nom",
            "cue": h.get("cue") or "Signal non spécifié",
            "category": h.get("category") or "Mindset / Mental",
            "done": bool(h.get("done", False))
        })
st.session_state["habits"] = sanitized_habits

if "procrastinations" not in st.session_state or not isinstance(st.session_state["procrastinations"], list):
    st.session_state["procrastinations"] = []

sanitized_procrastinations = []
for pr in st.session_state["procrastinations"]:
    if isinstance(pr, dict):
        sanitized_procrastinations.append({
            "date": pr.get("date") or str(datetime.date.today()),
            "task": pr.get("task") or "Tâche",
            "trigger": pr.get("trigger") or "Friction",
            "cost": pr.get("cost") or "Délai",
            "win": pr.get("win") or "Action rapide"
        })
st.session_state["procrastinations"] = sanitized_procrastinations

# Ensure fundamental metrics exist and are integers
try:
    st.session_state["level"] = int(st.session_state.get("level", 1))
except Exception:
    st.session_state["level"] = 1

try:
    st.session_state["xp"] = int(st.session_state.get("xp", 150))
except Exception:
    st.session_state["xp"] = 150

try:
    st.session_state["streak"] = int(st.session_state.get("streak", 12))
except Exception:
    st.session_state["streak"] = 12

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

# Helper function to recalculate the completion progress of a goal based on completed micro-tasks
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
        goal_names = [g.get("name", "Objectif sans nom") for g in st.session_state["goals"]]
        selected_goal_name = st.selectbox("Objectif actif :", goal_names, label_visibility="collapsed")
        
        # Get selected goal and its index safely
        goal_idx = 0
        for i, g in enumerate(st.session_state["goals"]):
            if g.get("name") == selected_goal_name:
                goal_idx = i
                break
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
                        "description": action_plan.get("projectDescription", ""),
                        "completed": False,
                        "stages": []
                    }
                    
                    for s_idx, stage_data in enumerate(action_plan.get("stages", [])):
                        new_stage = {
                            "id": f"stage-{s_idx}-{random.randint(100,999)}",
                            "name": stage_data.get("name", f"Étape {s_idx + 1}"),
                            "description": stage_data.get("description", ""),
                            "completed": False,
                            "tasks": []
                        }
                        
                        for t_idx, task_data in enumerate(stage_data.get("tasks", [])):
                            new_task = {
                                "id": f"task-{s_idx}-{t_idx}-{random.randint(100,999)}",
                                "name": task_data.get("name", f"Tâche {t_idx + 1}"),
                                "description": task_data.get("description", ""),
                                "status": "TODO",
                                "microTasks": []
                            }
                            
                            for mt_idx, mt_data in enumerate(task_data.get("microTasks", [])):
                                new_task["microTasks"].append({
                                    "id": f"mt-{s_idx}-{t_idx}-{mt_idx}-{random.randint(1000,9999)}",
                                    "name": mt_data.get("name", "Action rapide"),
                                    "completed": False
                                })
                                
                            new_stage["tasks"].append(new_task)
                        new_project["stages"].append(new_stage)
                        
                    # Also append suggested atomic habits
                    for h_data in action_plan.get("suggestedHabits", []):
                        # Avoid duplicates
                        if not any(h["name"].lower() == h_data["name"].lower() for h in st.session_state["habits"]):
                            st.session_state["habits"].append({
                                "id": random.randint(1000, 9999),
                                "name": h_data["name"],
                                "cue": f"{h_data['cue']} • Routine: {h_data['routine']} • Récompense: {h_data['reward']}",
                                "category": goal["domain"],
                                "done": False
                            })
                            
                    goal["projects"] = [new_project]
                    st.session_state["xp"] += 100
                    st.success("Plan d'action Kaizen généré avec succès ! +100 XP d'apprentissage !")
                    st.rerun()
                    
        # RENDER EXISTING ACTION PLAN
        else:
            project = goal["projects"][0]
            st.markdown(f"### 📋 {project['name']}")
            if project.get("description"):
                st.markdown(f"*{project['description']}*")
                
            # Progress bar
            recalculate_goal_progress(goal_idx)
            progress_pct = goal["progress"]
            st.markdown(f"""
            <div style="margin-bottom:20px;">
                <div style="display:flex; justify-content:space-between; align-items:center; font-size:11px; color:#94A3B8; margin-bottom:4px;">
                    <span>Progression globale de l'objectif</span>
                    <span style="font-weight:700; color:#818CF8;">{progress_pct}%</span>
                </div>
                <div class="xp-bar" style="height:10px;">
                    <div class="xp-progress" style="width: {progress_pct}%;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # STAGES RENDERER
            for s_idx, stage in enumerate(project["stages"]):
                with st.expander(f"📌 {stage['name']}", expanded=(s_idx == 0)):
                    if stage.get("description"):
                        st.markdown(f"<p style='font-size:12px; color:#94A3B8;'>{stage['description']}</p>", unsafe_allow_html=True)
                        
                    # Tasks in stage
                    for t_idx, task in enumerate(stage["tasks"]):
                        st.markdown(f"""
                        <div style="background-color:#070A13; padding:12px 16px; border-radius:10px; border:1px solid #1E293B; margin-top:10px;">
                            <div style="font-weight:700; font-size:13px; color:#F1F5F9;">{task['name']}</div>
                            <div style="font-size:11px; color:#94A3B8; margin-top:2px;">{task['description']}</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Micro tasks listed directly with checkboxes
                        for mt_idx, mt in enumerate(task["microTasks"]):
                            checkbox_id = f"chk-{goal['id']}-{s_idx}-{t_idx}-{mt_idx}"
                            is_checked = st.checkbox(
                                f"🔬 {mt['name']} (< 15 mins)",
                                value=mt["completed"],
                                key=checkbox_id
                            )
                            
                            # Update and handle XP
                            if is_checked != mt["completed"]:
                                mt["completed"] = is_checked
                                if is_checked:
                                    st.session_state["xp"] += 15
                                    st.toast(f"Félicitations ! Micro-tâche complétée. +15 XP", icon="🔬")
                                else:
                                    st.session_state["xp"] = max(0, st.session_state["xp"] - 15)
                                recalculate_goal_progress(goal_idx)
                                st.rerun()

            # DELETE GOAL ZONE
            st.markdown("---")
            if st.button("🗑️ Supprimer cet objectif", key=f"del_g_{goal['id']}", use_container_width=True):
                st.session_state["goals"].pop(goal_idx)
                st.warning("Objectif supprimé.")
                st.rerun()

# ----------------- Tab 2: Base de Données & Stockage -----------------
elif menu == "🗄️ Base de Données & Stockage":
    st.markdown("## 🗄️ Base de Données & Indicateurs Kaizen")
    st.markdown("Suivi d'avancement technique, de l'XP et de la persistance de vos rituels.")
    
    st.markdown(f"""
    <div class="database-card">
        <h3 style="margin:0 0 8px 0; font-size:18px; font-weight:800; color:#F8FAFC;">🛡️ KAIZEN CORE v1.0.0</h3>
        <p style="margin:0 0 16px 0; font-size:13px; color:#94A3B8;">
            Toutes vos informations de progression, de niveau et de rituels atomiques sont stockées de manière réactive.
        </p>
        <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap:12px;">
            <div style="background:rgba(11, 15, 25, 0.6); padding:12px; border-radius:8px; border:1px solid rgba(255,255,255,0.05);">
                <div style="font-size:10px; color:#94A3B8; text-transform:uppercase;">NIVEAU ACTUEL</div>
                <div style="font-size:18px; font-weight:900; color:#F1F5F9; margin-top:2px;">Niveau {st.session_state['level']}</div>
            </div>
            <div style="background:rgba(11, 15, 25, 0.6); padding:12px; border-radius:8px; border:1px solid rgba(255,255,255,0.05);">
                <div style="font-size:10px; color:#94A3B8; text-transform:uppercase;">EXPÉRIENCE TOTAL</div>
                <div style="font-size:18px; font-weight:900; color:#F1F5F9; margin-top:2px;">{st.session_state['xp']} XP</div>
            </div>
            <div style="background:rgba(11, 15, 25, 0.6); padding:12px; border-radius:8px; border:1px solid rgba(255,255,255,0.05);">
                <div style="font-size:10px; color:#94A3B8; text-transform:uppercase;">STREAK DE JOURS</div>
                <div style="font-size:18px; font-weight:900; color:#F1F5F9; margin-top:2px;">🔥 {st.session_state['streak']} Jours</div>
            </div>
            <div style="background:rgba(11, 15, 25, 0.6); padding:12px; border-radius:8px; border:1px solid rgba(255,255,255,0.05);">
                <div style="font-size:10px; color:#94A3B8; text-transform:uppercase;">DISCIPLINE RATE</div>
                <div style="font-size:18px; font-weight:900; color:#F1F5F9; margin-top:2px;">{discipline_score}%</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # LEVEL UP TRIGGER
    if st.session_state["xp"] >= xp_needed:
        st.balloons()
        st.session_state["level"] += 1
        st.session_state["xp"] = st.session_state["xp"] - xp_needed
        st.success(f"🎉 Niveau supérieur ! Vous venez de franchir le Niveau {st.session_state['level']} ! Continuez ainsi !")
        st.rerun()

    # SECTION: SCHEMA SQL repliable
    with st.expander("📊 Schéma Relationnel SQL complet (Pour déploiement PostgreSQL / Cloud SQL)", expanded=False):
        st.markdown("""
        Pour assurer la pérennité du projet, voici les structures SQL robustes de l'application :
        """)
        st.code("""
-- Table principale des Objectifs prioritaires
CREATE TABLE goals (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  name VARCHAR(255) NOT NULL,
  description TEXT,
  why TEXT NOT NULL, -- Simon Sinek "Start with Why"
  start_date DATE NOT NULL,
  target_date DATE NOT NULL,
  priority VARCHAR(20) DEFAULT 'Moyenne',
  difficulty VARCHAR(20) DEFAULT 'Moyen',
  domain VARCHAR(50) NOT NULL,
  progress INT DEFAULT 0,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table des Habitudes (Atomic Habits)
CREATE TABLE habits (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  name VARCHAR(255) NOT NULL,
  frequency VARCHAR(20) DEFAULT 'daily', -- daily, weekly, monthly
  cue TEXT NOT NULL, -- Le signal déclencheur
  routine TEXT NOT NULL, -- L'action micro-Kaizen
  reward TEXT NOT NULL, -- La récompense d'ancrage
  domain VARCHAR(50) NOT NULL,
  streak INT DEFAULT 0,
  best_streak INT DEFAULT 0,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table Historique de Validation (Suivi précis)
CREATE TABLE habit_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  habit_id UUID REFERENCES habits(id) ON DELETE CASCADE,
  completed_date DATE NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(habit_id, completed_date)
);
        """, language="sql")

    # ADMIN ACTIONS
    st.markdown("### ⚙️ Actions Administrateur")
    col_reset1, col_reset2 = st.columns([8, 4])
    with col_reset1:
        st.write("Si vous souhaitez vider le cache et repartir sur une base de démonstration vide :")
    with col_reset2:
        if st.button("⚠️ Réinitialiser toutes les données", type="secondary", use_container_width=True):
            st.session_state.clear()
            st.rerun()

# ----------------- Tab 3: Mes Rituels quotidiens -----------------
elif menu == "🧘 Mes Rituels quotidiens":
    st.markdown("## 🧘 Rituels d'Identité & Habitudes Saines")
    st.markdown("James Clear (Atomic Habits) enseigne que le changement durable naît d'une identité renforcée par des rituels réguliers. Plus un rituel est petit, moins il engendre de friction.")
    
    # Habit status list
    st.markdown("### Vos Rituels actifs du Jour")
    
    if not st.session_state["habits"]:
        st.info("Aucun rituel d'identité n'a été créé.")
    else:
        for idx, h in enumerate(st.session_state["habits"]):
            col_h1, col_h2, col_h3 = st.columns([8, 2, 2])
            with col_h1:
                st.markdown(f"""
                <div style="background-color:#111827; padding:12px; border-radius:8px; border:1px solid #1F2937;">
                    <div style="font-weight:700; font-size:14px; color:#F1F5F9;">{h['name']}</div>
                    <div style="font-size:11px; color:#94A3B8; margin-top:2px;">⚡ {h['cue']}</div>
                </div>
                """, unsafe_allow_html=True)
            with col_h2:
                # Button to validate habit
                if h["done"]:
                    st.button("✓ Validé", key=f"hab_done_{h['id']}", disabled=True, use_container_width=True)
                else:
                    if st.button("Valider", key=f"hab_val_{h['id']}", type="primary", use_container_width=True):
                        h["done"] = True
                        st.session_state["xp"] += 15
                        st.session_state["streak"] += 1
                        st.toast(f"Rituel validé ! +15 XP / Streak incrémentée !", icon="🧘")
                        st.rerun()
            with col_h3:
                if st.button("Supprimer", key=f"hab_del_{h['id']}", use_container_width=True):
                    st.session_state["habits"].pop(idx)
                    st.rerun()
                    
    # Form to add an Habit
    st.markdown("---")
    st.markdown("### ➕ Créer un rituel sur mesure")
    with st.form("add_habit_form"):
        h_name = st.text_input("Nom de l'habitude :", placeholder="Ex: Journal d'idées, Yoga, Rangement de bureau")
        h_cue = st.text_input("Signal déclencheur de l'action (Cue) :", placeholder="Ex: Dès que je ferme mon ordinateur à 18h...")
        h_cat = st.selectbox("Catégorie :", ["Mindset / Mental", "Santé / Physique", "Relations", "Finances", "Travail"])
        
        if st.form_submit_button("Programmer le Rituel 🚀", use_container_width=True):
            if h_name and h_cue:
                st.session_state["habits"].append({
                    "id": random.randint(1000, 9999),
                    "name": h_name,
                    "cue": h_cue,
                    "category": h_cat,
                    "done": False
                })
                st.success("Rituel programmé !")
                st.rerun()
            else:
                st.warning("Veuillez remplir tous les champs obligatoires.")

# ----------------- Tab 4: Anti-Procrastination -----------------
elif menu == "⚡ Anti-Procrastination":
    st.markdown("## ⚡ Outil Anti-Procrastination Kaizen")
    st.markdown("La procrastination est une réponse biologique d'évitement face à une tâche perçue comme trop lourde, ennuyeuse ou stressante. Pour la vaincre, déconstruisons la friction !")
    
    with st.expander("🎯 Enregistrer un blocage d'action", expanded=True):
        p_task = st.text_input("Quelle tâche repoussez-vous depuis plusieurs jours ?", placeholder="Ex: Préparer ma déclaration de revenus, aller courir...")
        p_trigger = st.selectbox("Quelle est la nature du blocage psychologique ?", [
            "Peur de l'échec (Perfectionnisme)",
            "Peur de l'inconnu (Séquence floue)",
            "Manque d'énergie immédiate",
            "Tâche perçue comme ennuyeuse / fastidieuse"
        ])
        p_cost = st.text_input("Quel est le coût réel de cet évitement ?", placeholder="Ex: Sentiment de culpabilité permanent, retard accumulé...")
        
        st.markdown("""
        **💡 La Règle Kaizen des 5 minutes :**
        Définissez un premier pas ridiculement petit et facile, à réaliser en moins de 5 minutes chrono pour amorcer l'action sans effort.
        """)
        p_win = st.text_input("Votre micro-action de déblocage (< 5 min) :", placeholder="Ex: Ouvrir le site des impôts et retrouver mon mot de passe")
        
        if st.button("Enregistrer & Débloquer (+15 XP) 🚀", use_container_width=True):
            if p_task and p_win:
                st.session_state["procrastinations"].append({
                    "date": str(datetime.date.today()),
                    "task": p_task,
                    "trigger": p_trigger,
                    "cost": p_cost,
                    "win": p_win
                })
                st.session_state["xp"] += 15
                st.success("Félicitations pour cette prise de conscience ! Votre micro-victoire est planifiée. +15 XP")
                st.rerun()
            else:
                st.warning("Veuillez spécifier la tâche et l'action de déblocage.")

    # List of Logs
    if st.session_state["procrastinations"]:
        st.markdown("### Vos Déblocages en cours")
        for idx, log in enumerate(st.session_state["procrastinations"]):
            st.markdown(f"""
            <div class="kaizen-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span class="status-badge" style="background-color:rgba(239, 68, 68, 0.1); color:#F87171; border: 1px solid rgba(239, 68, 68, 0.2)">BLOQUÉ</span>
                    <span style="font-size:11px; color:#94A3B8; font-family:'JetBrains Mono';">{log['date']}</span>
                </div>
                <h4 style="margin:8px 0 4px 0; font-size:15px; font-weight:800; color:#F1F5F9;">{log['task']}</h4>
                <div style="font-size:12px; line-height:1.6; color:#94A3B8; margin-bottom: 12px;">
                    ⚠️ <strong>Déclencheur :</strong> {log['trigger']}<br>
                    📉 <strong>Coût de l'évitement :</strong> {log['cost']}<br>
                    🛡️ <strong>Micro-Victoire conseillée :</strong> <span style="color:#818CF8; font-weight:700;">{log['win']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Supprimer l'analyse {idx+1}", key=f"del_ap_{idx}"):
                st.session_state["procrastinations"].pop(idx)
                st.rerun()
