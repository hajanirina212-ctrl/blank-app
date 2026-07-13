import streamlit as st
import datetime
import json
import random

# Page config & Custom Tab Title
st.set_page_config(
    page_title="KAIZENOS • High Density System",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Session States
if "initialized" not in st.session_state:
    st.session_state["initialized"] = True
    st.session_state["level"] = 42
    st.session_state["xp"] = 3500
    st.session_state["streak"] = 114
    st.session_state["deep_work_hours"] = 3.5
    st.session_state["target_deep_work"] = 4.0
    
    # James Clear Identity Vision Board
    st.session_state["identity"] = "Je suis un créateur discipliné et concentré qui s'améliore de 1% par jour."
    st.session_state["one_year_vision"] = "Avoir consolidé mes rituels de deep work quotidiens et atteint mes objectifs prioritaires."
    st.session_state["long_term_vision"] = "Incarner pleinement la sagesse comportementale et inspirer mon entourage par ma constance."
    
    # Habits initialization
    st.session_state["habits"] = [
        {"id": 1, "name": "Deep Work Session: Architecture Design", "cue": "90 min • High Focus", "category": "Mindset", "done": True},
        {"id": 2, "name": "Micro-action: Review 2 landing pages", "cue": "15 min • Skill Building", "category": "Professional", "done": False},
        {"id": 3, "name": "Daily Reflection: Gratitude & Pivot", "cue": "5 min • Mindset", "category": "Mindset", "done": False},
        {"id": 4, "name": "Atomic Habit: 20 Pushups after Coffee", "cue": "Habit Stack • Physical", "category": "Physical", "done": False}
    ]
    
    # Goals Pyramid
    st.session_state["goals"] = [
        {"id": 1, "text": "Lancer le SaaS KaizenOS en production", "level": "🏆 Vision Ultime", "domain": "Professionnel", "completed": False},
        {"id": 2, "text": "Compléter 100 sessions de Deep Work de 90min", "level": "🎯 Jalon (1 An)", "domain": "Professionnel", "completed": False},
        {"id": 3, "text": "Écrire une page de spécifications chaque matin", "level": "⚡ Micro-Action", "domain": "Mental", "completed": True},
    ]

    # Timeblock Planner
    st.session_state["timeblocks"] = [
        {"start": "08:00", "end": "09:00", "task": "Routine Matinale & Alignement", "type": "Rituel"},
        {"start": "09:00", "end": "10:30", "task": "Deep Work : Architecture Core", "type": "Deep Work"},
        {"start": "11:00", "end": "12:00", "task": "Shallow Work & Réponses Emails", "type": "Shallow"},
    ]
    
    # Procrastination logs
    st.session_state["procrastinations"] = [
        {"date": "2026-07-12", "task": "Rédiger le rapport trimestriel", "trigger": "Peur de l'imperfection", "cost": "Retard de livraison", "win": "Ouvrir le doc 5 minutes et écrire le titre principal"}
    ]

# Calculations
xp_needed = int(100 * (st.session_state["level"] ** 1.5))
xp_percent = min(1.0, float(st.session_state["xp"]) / xp_needed)

total_habits = len(st.session_state["habits"])
done_habits = sum(1 for h in st.session_state["habits"] if h["done"])
discipline_score = int((done_habits / total_habits) * 100) if total_habits > 0 else 92

# Custom High Density Styling CSS Injection
st.markdown("""
<style>
    /* Global Reset & Streamlit UI overrides to match KaizenOS High Density Style */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #09090B !important;
        color: #F4F4F5 !important;
        font-family: 'Inter', -apple-system, sans-serif !important;
    }
    
    [data-testid="stHeader"] {
        background: rgba(9, 9, 11, 0.8) !important;
        backdrop-filter: blur(12px) !important;
        border-bottom: 1px solid #27272A !important;
    }
    
    [data-testid="stSidebar"] {
        background-color: #09090B !important;
        border-right: 1px solid #27272A !important;
    }

    /* Cards */
    .kaizen-card {
        background-color: #18181B;
        border: 1px solid #27272A;
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 16px;
    }
    
    .kaizen-header {
        font-weight: 900;
        font-size: 20px;
        letter-spacing: -1px;
        color: #F4F4F5;
        margin-bottom: 15px;
    }
    
    .kaizen-header span {
        color: #6366F1;
    }

    .stat-card {
        background-color: #18181B;
        border: 1px solid #27272A;
        padding: 16px;
        border-radius: 12px;
        display: flex;
        flex-direction: column;
        gap: 6px;
        margin-bottom: 12px;
    }

    .stat-label {
        font-size: 10px;
        color: #A1A1AA;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 700;
    }

    .stat-value {
        font-size: 24px;
        font-weight: 800;
        color: #818CF8;
        font-family: 'JetBrains Mono', monospace;
    }

    .stat-sub {
        font-size: 11px;
        color: #10B981;
    }

    /* Identity Pill */
    .identity-pill {
        display: flex;
        align-items: center;
        gap: 12px;
        background: #18181B;
        border: 1px solid #27272A;
        padding: 6px 16px;
        border-radius: 999px;
        margin-bottom: 20px;
    }

    .xp-bar {
        width: 120px;
        height: 6px;
        background: #27272A;
        border-radius: 3px;
        position: relative;
        overflow: hidden;
        display: inline-block;
        margin-left: 8px;
    }

    .xp-progress {
        position: absolute;
        left: 0;
        top: 0;
        height: 100%;
        background: #6366F1;
    }

    /* Heatmap Grid */
    .heatmap {
        display: grid;
        grid-template-columns: repeat(10, 1fr);
        gap: 6px;
        margin-top: 10px;
    }

    .heat-box {
        aspect-ratio: 1;
        background: #27272A;
        border-radius: 3px;
        width: 100%;
    }

    .lvl-1 { background-color: #1E1B4B; }
    .lvl-2 { background-color: #3730A3; }
    .lvl-3 { background-color: #4F46E5; }
    .lvl-4 { background-color: #818CF8; }

    /* Badges */
    .badge-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 8px;
        margin-top: 10px;
    }

    .badge-item {
        aspect-ratio: 1;
        background: #18181B;
        border: 1px solid #27272A;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 16px;
        opacity: 0.4;
        transition: all 0.2s;
    }

    .badge-item.unlocked {
        opacity: 1;
        border-color: #6366F1;
        background-color: rgba(99, 102, 241, 0.1);
        box-shadow: 0 0 10px rgba(99, 102, 241, 0.15);
    }

    /* Kaizen intelligence hint block */
    .kaizen-suggestion {
        background: rgba(99, 102, 241, 0.08);
        border-left: 3px solid #6366F1;
        padding: 12px;
        border-radius: 4px;
        font-size: 13px;
        margin-bottom: 15px;
        line-height: 1.4;
    }

    /* Interactive lists */
    .habit-row {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid #27272A;
        padding: 10px 14px;
        border-radius: 8px;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }

    /* Typography helpers */
    .mono {
        font-family: 'JetBrains Mono', monospace;
    }
</style>
""", unsafe_allow_html=True)

# SIDEBAR NAVIGATION & IDENTITY PORTRAIT
with st.sidebar:
    st.markdown('<div class="kaizen-header">KAIZEN<span>OS</span></div>', unsafe_allow_html=True)
    
    # Identity Pill
    xp_bar_html = f"""
    <div class="identity-pill">
        <div>
            <div style="font-size: 10px; color: #A1A1AA; text-transform: uppercase;">Alexandre • Lvl {st.session_state['level']}</div>
            <div style="display: flex; align-items: center; margin-top: 4px;">
                <span style="font-size: 11px; font-weight: 600; color: #10B981;">+{st.session_state['streak']} Days</span>
                <div class="xp-bar"><div class="xp-progress" style="width: {xp_percent * 100}%;"></div></div>
            </div>
        </div>
    </div>
    """
    st.markdown(xp_bar_html, unsafe_allow_html=True)
    
    # Navigation Radio Selector
    st.markdown("### 🗺️ Navigation")
    menu = st.radio(
        "Sélectionnez un hub :",
        ["Dashboard & Rituels", "Vision & Objectifs", "Habit Tracker", "Time Blocker", "Review Center", "Anti-Procrastination"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    # Quote of the day
    st.markdown(
        '<div style="font-style: italic; color: #A1A1AA; border-left: 2px solid #6366F1; padding-left: 12px; font-size: 12px;">'
        '"Le secret pour avancer, c\'est de commencer."<br>— Mark Twain'
        '</div>',
        unsafe_allow_html=True
    )

# VIEW ROUTER
if menu == "Dashboard & Rituels":
    # HEADER GRID
    st.markdown("## 🛡️ Aujourd'hui : Votre Chemin")
    st.markdown("Un focus absolu sur les actions d'identité pour une amélioration constante de 1%.")
    
    # KAIZEN INTELLIGENCE SUGGESTION
    st.markdown(
        f"""
        <div class="kaizen-suggestion">
            <strong>Kaizen Intelligence :</strong> Vous avez retardé "Rédiger le rapport trimestriel" récemment.<br>
            <span style="color: #818CF8; font-size: 12px;">Recommandation : Consacrez seulement 5 minutes aujourd'hui à ouvrir le document et écrire un titre.</span>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            f"""
            <div class="stat-card">
                <span class="stat-label">Discipline Quotidienne</span>
                <span class="stat-value">{discipline_score}%</span>
                <span class="stat-sub">+2.4% depuis hier</span>
            </div>
            """, unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            f"""
            <div class="stat-card">
                <span class="stat-label">Micro-Rituels</span>
                <span class="stat-value">{done_habits} / {total_habits}</span>
                <span class="stat-sub">Restant : {total_habits - done_habits}</span>
            </div>
            """, unsafe_allow_html=True
        )
    with col3:
        st.markdown(
            f"""
            <div class="stat-card">
                <span class="stat-label">Deep Work</span>
                <span class="stat-value">{st.session_state['deep_work_hours']} / {st.session_state['target_deep_work']}h</span>
                <span class="stat-sub">Focus cognitif pur</span>
            </div>
            """, unsafe_allow_html=True
        )

    # TWO COLUMN CONTENT
    left_panel, right_panel = st.columns([7, 5])
    
    with left_panel:
        st.markdown('<div class="kaizen-card">', unsafe_allow_html=True)
        st.markdown("### 🧬 Rituels et Habitudes du Jour")
        
        # Toggle buttons for habits
        for i, habit in enumerate(st.session_state["habits"]):
            col_check, col_details = st.columns([1, 9])
            with col_check:
                is_checked = st.checkbox("", value=habit["done"], key=f"dash_habit_{habit['id']}")
                if is_checked != habit["done"]:
                    st.session_state["habits"][i]["done"] = is_checked
                    # Award or deduct XP
                    if is_checked:
                        st.session_state["xp"] += 150
                    else:
                        st.session_state["xp"] = max(0, st.session_state["xp"] - 150)
                    st.rerun()
            with col_details:
                text_style = "text-decoration: line-through; opacity: 0.5;" if habit["done"] else ""
                st.markdown(
                    f"""
                    <div style="{text_style}">
                        <div style="font-weight:700; font-size:13px; color:#F4F4F5;">{habit['name']}</div>
                        <div style="font-size:10px; color:#A1A1AA;">{habit['cue']}</div>
                    </div>
                    """, unsafe_allow_html=True
                )
            st.markdown('<div style="margin-bottom:8px;"></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Vision alignment quote
        st.markdown(
            f"""
            <div class="kaizen-card">
                <div style="font-size:10px; color:#818CF8; font-weight:700; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:4px;">Identité d'Alignement :</div>
                <div style="font-size:13px; font-style:italic; font-weight:500; color:#F4F4F5;">« {st.session_state['identity']} »</div>
            </div>
            """, unsafe_allow_html=True
        )

    with right_panel:
        # Discipline Momentum Score card
        st.markdown('<div class="kaizen-card" style="text-align: center;">', unsafe_allow_html=True)
        st.markdown('<div style="font-size:10px; font-weight:700; color:#A1A1AA; uppercase; tracking-wider;">DISCIPLINE MOMENTUM</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="font-size:42px; font-weight:900; color:#10B981; font-family:\'JetBrains Mono\';">{discipline_score}.2<span style="font-size:14px; color:#A1A1AA; font-weight:400;">/100</span></div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size:9px; color:#A1A1AA; font-family:\'JetBrains Mono\';">+2.4% DEPUIS HIER</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Consistency Heatmap
        st.markdown('<div class="kaizen-card">', unsafe_allow_html=True)
        st.markdown('<div style="font-size:10px; font-weight:700; color:#A1A1AA; uppercase; tracking-wider; display:flex; justify-content:space-between;"><span>RÉGULARITÉ (30 J)</span><span style="color:#6366F1;">KAIZEN</span></div>', unsafe_allow_html=True)
        
        # Grid of boxes
        heatmap_html = '<div class="heatmap">'
        for i in range(30):
            # Simulated levels
            level_cls = "lvl-4" if i % 4 == 0 else ("lvl-3" if i % 3 == 0 else ("lvl-2" if i % 2 == 0 else "lvl-1"))
            heatmap_html += f'<div class="heat-box {level_cls}"></div>'
        heatmap_html += '</div>'
        st.markdown(heatmap_html, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Badges & Progress
        st.markdown('<div class="kaizen-card">', unsafe_allow_html=True)
        st.markdown('<div style="font-size:10px; font-weight:700; color:#A1A1AA; uppercase; tracking-wider;">BADGES & PROGRESSION</div>', unsafe_allow_html=True)
        
        badges = [
            {"icon": "🔥", "unlocked": st.session_state["streak"] >= 3},
            {"icon": "🧘", "unlocked": True},
            {"icon": "⚡", "unlocked": st.session_state["deep_work_hours"] > 0},
            {"icon": "🛡️", "unlocked": discipline_score >= 70},
            {"icon": "🏆", "unlocked": st.session_state["level"] >= 10},
            {"icon": "📚", "unlocked": True},
            {"icon": "🌊", "unlocked": True},
            {"icon": "💎", "unlocked": st.session_state["xp"] > 1000},
        ]
        
        badge_html = '<div class="badge-grid">'
        for b in badges:
            cls = "unlocked" if b["unlocked"] else ""
            badge_html += f'<div class="badge-item {cls}">{b["icon"]}</div>'
        badge_html += '</div>'
        st.markdown(badge_html, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

elif menu == "Vision & Objectifs":
    st.markdown("## 🔮 Alignement d'Identité & Pyramide des Objectifs")
    st.markdown("James Clear : « Chaque action que vous entreprenez est un vote pour le type de personne que vous souhaitez devenir. »")

    # Vision settings
    st.markdown('<div class="kaizen-card">', unsafe_allow_html=True)
    st.markdown("### 🧘 Rituels d'Alignement Identitaire")
    
    st.session_state["identity"] = st.text_area(
        "Mon Identité Profonde (Qui je veux devenir) :",
        value=st.session_state["identity"],
        help="Ex: Je suis un auteur rigoureux qui valorise la clarté mentale et l'impact de ses écrits."
    )
    
    col_vis1, col_vis2 = st.columns(2)
    with col_vis1:
        st.session_state["one_year_vision"] = st.text_area(
            "Vision à 1 an (Mes rituels clés) :",
            value=st.session_state["one_year_vision"]
        )
    with col_vis2:
        st.session_state["long_term_vision"] = st.text_area(
            "Vision à Long Terme (Impact de vie) :",
            value=st.session_state["long_term_vision"]
        )
    st.markdown('</div>', unsafe_allow_html=True)

    # Goal Pyramid Manager
    st.markdown('<div class="kaizen-card">', unsafe_allow_html=True)
    st.markdown("### 🏆 Pyramide d'Objectifs Kaizen")
    
    # Form to add goals
    with st.expander("➕ Ajouter un élément à la Pyramide", expanded=False):
        g_text = st.text_input("Objectif / Action :")
        g_level = st.selectbox("Niveau dans la Pyramide :", ["🏆 Vision Ultime", "🎯 Jalon (1 An)", "⚡ Micro-Action"])
        g_domain = st.selectbox("Domaine de Vie :", ["Professionnel", "Physique", "Mindset/Mental", "Social", "Finances"])
        if st.button("Ajouter à la pyramide"):
            if g_text:
                new_id = max([g["id"] for g in st.session_state["goals"]]) + 1 if st.session_state["goals"] else 1
                st.session_state["goals"].append({
                    "id": new_id,
                    "text": g_text,
                    "level": g_level,
                    "domain": g_domain,
                    "completed": False
                })
                st.success(f"Objectif ajouté à la pyramide !")
                st.rerun()

    # List current goals
    for g in st.session_state["goals"]:
        col_status, col_desc, col_lvl, col_del = st.columns([1, 6, 3, 1])
        with col_status:
            completed = st.checkbox("Fait", value=g["completed"], key=f"goal_{g['id']}")
            if completed != g["completed"]:
                g["completed"] = completed
                st.rerun()
        with col_desc:
            st.markdown(f"**{g['text']}**")
        with col_lvl:
            st.markdown(f"`{g['level']}` | <span style='color:#A1A1AA; font-size:11px;'>{g['domain']}</span>", unsafe_allow_html=True)
        with col_del:
            if st.button("❌", key=f"del_goal_{g['id']}"):
                st.session_state["goals"] = [item for item in st.session_state["goals"] if item["id"] != g["id"]]
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

elif menu == "Habit Tracker":
    st.markdown("## 🧬 Atomic Habits Suite")
    st.markdown("Construisez des rituels robustes basés sur le conditionnement comportemental d'Atomic Habits.")

    with st.expander("➕ Concevoir une nouvelle Habitude (Habit Design Form)", expanded=True):
        col_name, col_cue = st.columns(2)
        with col_name:
            h_name = st.text_input("Nom de l'Habitude :", placeholder="Ex: Lire 10 pages")
        with col_cue:
            h_cue = st.text_input("Le Signal (Cue) :", placeholder="Ex: Juste après avoir servi mon café")
            
        col_routine, col_reward = st.columns(2)
        with col_routine:
            h_routine = st.text_input("La Routine :", placeholder="Ex: Ouvrir le livre physique sur mon bureau")
        with col_reward:
            h_reward = st.text_input("La Récompense :", placeholder="Ex: Savourer mon expresso")
            
        h_category = st.selectbox("Catégorie :", ["Physical", "Mindset", "Professional", "Social"])
        
        if st.button("Enregistrer l'Habitude"):
            if h_name and h_cue:
                new_id = max([h["id"] for h in st.session_state["habits"]]) + 1 if st.session_state["habits"] else 1
                st.session_state["habits"].append({
                    "id": new_id,
                    "name": h_name,
                    "cue": h_cue,
                    "category": h_category,
                    "done": False
                })
                st.success("Rituel enregistré !")
                st.rerun()

    # Habit list management
    st.markdown("### Mes Rituels Actifs")
    for i, h in enumerate(st.session_state["habits"]):
        st.markdown(f"""
        <div class="kaizen-card">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                <span style="font-weight:700; font-size:15px; color:#818CF8;">{h['name']}</span>
                <span style="font-size:10px; background:#27272A; padding:2px 8px; border-radius:12px; color:#A1A1AA;">{h['category']}</span>
            </div>
            <div style="font-size:12px; line-height:1.6; color:#F4F4F5;">
                👉 <strong>Signal (Cue) :</strong> {h['cue']}<br>
                🧠 <strong>Identité Associée :</strong> Rapproche de votre identité Kaizen
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Supprimer ce rituel", key=f"del_h_{h['id']}"):
            st.session_state["habits"] = [item for item in st.session_state["habits"] if item["id"] != h["id"]]
            st.rerun()

elif menu == "Time Blocker":
    st.markdown("## ⚡ Time Blocking (Cal Newport Methodology)")
    st.markdown("Planifiez votre journée par blocs temporels pour éliminer la fragmentation cognitive.")

    col_tb_left, col_tb_right = st.columns([5, 7])
    
    with col_tb_left:
        st.markdown('<div class="kaizen-card">', unsafe_allow_html=True)
        st.markdown("### Planifier un Bloc")
        tb_start = st.text_input("Heure de Début :", value="09:00")
        tb_end = st.text_input("Heure de Fin :", value="10:30")
        tb_task = st.text_input("Activité prévue :", placeholder="Ex: Deep Work: Architecture")
        tb_type = st.selectbox("Type de Bloc :", ["Rituel", "Deep Work", "Shallow Work", "Break"])
        
        if st.button("Inscrire le Bloc"):
            if tb_task:
                st.session_state["timeblocks"].append({
                    "start": tb_start,
                    "end": tb_end,
                    "task": tb_task,
                    "type": tb_type
                })
                st.success("Bloc inscrit !")
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col_tb_right:
        st.markdown('<div class="kaizen-card">', unsafe_allow_html=True)
        st.markdown("### Chronologie de la Journée")
        for idx, block in enumerate(st.session_state["timeblocks"]):
            badge_color = "#10B981" if block["type"] == "Deep Work" else ("#6366F1" if block["type"] == "Rituel" else "#A1A1AA")
            st.markdown(
                f"""
                <div style="display:flex; align-items:center; justify-content:space-between; border-left:4px solid {badge_color}; padding-left:12px; margin-bottom:12px;">
                    <div>
                        <span class="mono" style="font-weight:700; color:#818CF8;">{block['start']} - {block['end']}</span><br>
                        <span style="font-size:14px; font-weight:600; color:#F4F4F5;">{block['task']}</span>
                    </div>
                    <span style="font-size:10px; background:#27272A; padding:2px 8px; border-radius:12px; color:{badge_color}; font-weight:700;">{block['type']}</span>
                </div>
                """, unsafe_allow_html=True
            )
            if st.button("Retirer", key=f"del_block_{idx}"):
                st.session_state["timeblocks"].pop(idx)
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

elif menu == "Review Center":
    st.markdown("## 📊 Centre de Réflexion & de Revue Kaizen")
    st.markdown("Faites le bilan de vos rituels, analysez vos blocages et recalibrez vos comportements.")

    st.markdown('<div class="kaizen-card">', unsafe_allow_html=True)
    st.markdown("### Formulaire de Bilan Journalier")
    st.markdown("*Posez-vous les 3 questions fondamentales pour l'ajustement de 1% :*")
    
    q1 = st.text_area("1. Qu'est-ce qui a extrêmement bien fonctionné aujourd'hui ?")
    q2 = st.text_area("2. Quelle a été la source principale de distraction ou de friction cognitive ?")
    q3 = st.text_area("3. Quelle micro-correction simple puis-je appliquer dès demain matin ?")
    
    review_score = st.slider("Note de Discipline Globale (0 - 100) :", 0, 100, 85)
    
    if st.button("Enregistrer la Revue"):
        st.balloons()
        st.success("Revue Kaizen enregistrée avec succès ! +100 XP d'apprentissage.")
        st.session_state["xp"] += 100
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

elif menu == "Anti-Procrastination":
    st.markdown("## 🛡️ Discipline Center : Journal d'Anti-Procrastination")
    st.markdown("Comprenez les mécanismes neuro-émotionnels qui déclenchent l'évitement comportemental.")

    st.markdown('<div class="kaizen-card">', unsafe_allow_html=True)
    st.markdown("### Consigner une Friction / Évitement")
    
    ap_task = st.text_input("Tâche évitée :", placeholder="Ex: Rédiger le rapport trimestriel")
    ap_trigger = st.selectbox("Facteur Déclencheur (Trigger) :", [
        "Peur de l'imperfection / Perfectionnisme",
        "Ambiguité de la tâche / Manque de clarté",
        "Épuisement cognitif / Fatigue",
        "Tâche ennuyeuse / Absence de récompense immédiate"
    ])
    ap_cost = st.text_input("Coût du Délai (Conséquence si repoussé) :", placeholder="Ex: Stress intense le jour de la date limite")
    ap_win = st.text_input("La Micro-Victoire d'Entrée (Règle des 2 minutes) :", placeholder="Ex: Ouvrir le document Word et écrire un seul paragraphe")
    
    if st.button("Consigner l'Analyse"):
        if ap_task and ap_win:
            st.session_state["procrastinations"].append({
                "date": str(datetime.date.today()),
                "task": ap_task,
                "trigger": ap_trigger,
                "cost": ap_cost,
                "win": ap_win
            })
            st.success("Analyse de friction enregistrée ! Prenez la micro-victoire maintenant.")
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # Historical Log
    st.markdown("### Analyses de Friction Passées")
    for idx, log in enumerate(st.session_state["procrastinations"]):
        st.markdown(
            f"""
            <div class="kaizen-card">
                <div style="display:flex; justify-content:space-between; margin-bottom:6px;">
                    <span style="font-weight:700; font-size:14px; color:#F4F4F5;">{log['task']}</span>
                    <span style="font-size:10px; color:#A1A1AA;" class="mono">{log['date']}</span>
                </div>
                <div style="font-size:12px; line-height:1.6; color:#A1A1AA;">
                    ⚠️ <strong>Déclencheur :</strong> {log['trigger']}<br>
                    📉 <strong>Coût de l'évitement :</strong> {log['cost']}<br>
                    🛡️ <strong>Micro-Victoire :</strong> <span style="color:#818CF8; font-weight:600;">{log['win']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True
        )
