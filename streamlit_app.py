import streamlit as st
import sqlite3
import json
from datetime import date, datetime, timedelta
import pandas as pd

DB_PATH = "kaizen.db"

# ----------------------------- DB -----------------------------

def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            horizon TEXT NOT NULL,
            target_date TEXT,
            progress INTEGER DEFAULT 0,
            auto_progress INTEGER DEFAULT 0,
            created_at TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            time TEXT NOT NULL,
            goal_id INTEGER,
            created_at TEXT,
            FOREIGN KEY (goal_id) REFERENCES goals(id) ON DELETE SET NULL
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS completions (
            date TEXT NOT NULL,
            task_id INTEGER NOT NULL,
            done INTEGER DEFAULT 1,
            PRIMARY KEY (date, task_id)
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS kaizen_notes (
            date TEXT PRIMARY KEY,
            note TEXT
        )
    """)
    conn.commit()
    try:
        c.execute("ALTER TABLE goals ADD COLUMN auto_progress INTEGER DEFAULT 0")
        conn.commit()
    except sqlite3.OperationalError:
        pass
    conn.close()


def df(query, params=()):
    conn = get_conn()
    result = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return result


def execute(query, params=()):
    conn = get_conn()
    c = conn.cursor()
    c.execute(query, params)
    conn.commit()
    last_id = c.lastrowid
    conn.close()
    return last_id


# ----------------------------- Data helpers -----------------------------

def add_goal(title, horizon, target_date):
    execute(
        "INSERT INTO goals (title, horizon, target_date, progress, auto_progress, created_at) VALUES (?, ?, ?, 0, 0, ?)",
        (title, horizon, target_date, datetime.now().isoformat()),
    )


def update_goal(goal_id, title, horizon, target_date):
    execute(
        "UPDATE goals SET title = ?, horizon = ?, target_date = ? WHERE id = ?",
        (title, horizon, target_date, goal_id),
    )


def update_goal_progress(goal_id, progress):
    execute("UPDATE goals SET progress = ? WHERE id = ?", (progress, goal_id))


def update_goal_auto(goal_id, auto):
    execute("UPDATE goals SET auto_progress = ? WHERE id = ?", (1 if auto else 0, goal_id))


def delete_goal(goal_id):
    execute("UPDATE tasks SET goal_id = NULL WHERE goal_id = ?", (goal_id,))
    execute("DELETE FROM goals WHERE id = ?", (goal_id,))


def add_task(title, time_str, goal_id):
    execute(
        "INSERT INTO tasks (title, time, goal_id, created_at) VALUES (?, ?, ?, ?)",
        (title, time_str, goal_id if goal_id else None, datetime.now().isoformat()),
    )


def update_task(task_id, title, time_str, goal_id):
    execute(
        "UPDATE tasks SET title = ?, time = ?, goal_id = ? WHERE id = ?",
        (title, time_str, goal_id, task_id),
    )


def delete_task(task_id):
    execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    execute("DELETE FROM completions WHERE task_id = ?", (task_id,))


def toggle_completion(task_id, iso_date, currently_done):
    if currently_done:
        execute("DELETE FROM completions WHERE date = ? AND task_id = ?", (iso_date, task_id))
    else:
        execute(
            "INSERT OR REPLACE INTO completions (date, task_id, done) VALUES (?, ?, 1)",
            (iso_date, task_id),
        )


def save_kaizen_note(iso_date, note):
    execute(
        "INSERT INTO kaizen_notes (date, note) VALUES (?, ?) "
        "ON CONFLICT(date) DO UPDATE SET note = excluded.note",
        (iso_date, note),
    )


def completion_rate(iso_date, all_tasks_df):
    if all_tasks_df.empty:
        return None
    done = df(
        "SELECT COUNT(*) as n FROM completions WHERE date = ?", (iso_date,)
    )["n"].iloc[0]
    return done / len(all_tasks_df)


def compute_overall_streak(all_tasks_df):
    if all_tasks_df.empty:
        return 0
    streak = 0
    cursor = date.today() - timedelta(days=1)
    while True:
        rate = completion_rate(cursor.isoformat(), all_tasks_df)
        if rate == 1:
            streak += 1
            cursor -= timedelta(days=1)
        else:
            break
        if streak > 3650:
            break
    return streak


def compute_kaizen_streak():
    streak = 0
    cursor = date.today()
    while True:
        row = df("SELECT note FROM kaizen_notes WHERE date = ?", (cursor.isoformat(),))
        if not row.empty and row["note"].iloc[0] and row["note"].iloc[0].strip():
            streak += 1
            cursor -= timedelta(days=1)
        else:
            break
        if streak > 3650:
            break
    return streak


def compute_task_streak(task_id, created_at):
    """Jours consécutifs où cette tâche précise a été faite (aujourd'hui inclus s'il est fait)."""
    done_dates = set(df("SELECT date FROM completions WHERE task_id = ?", (task_id,))["date"].tolist())
    created_date = date.fromisoformat(created_at[:10]) if created_at else date(2000, 1, 1)
    streak = 0
    cursor = date.today()
    if cursor.isoformat() in done_dates:
        streak = 1
    cursor -= timedelta(days=1)
    while cursor >= created_date:
        if cursor.isoformat() in done_dates:
            streak += 1
            cursor -= timedelta(days=1)
        else:
            break
    return streak


def compute_auto_progress(goal_id, created_at, tasks_df):
    linked = tasks_df[tasks_df["goal_id"] == goal_id]
    if linked.empty:
        return None
    start_date = date.fromisoformat(created_at[:10]) if created_at else date.today()
    if start_date > date.today():
        start_date = date.today()
    total_days = (date.today() - start_date).days + 1
    total_possible = len(linked) * total_days
    if total_possible <= 0:
        return 0
    comp_df = df("SELECT date, task_id FROM completions WHERE date >= ?", (start_date.isoformat(),))
    done_count = len(comp_df[comp_df["task_id"].isin(linked["id"].tolist())])
    return round(min(done_count / total_possible, 1.0) * 100)


def period_label(time_str):
    h = int(time_str.split(":")[0])
    if h < 12:
        return "🌅 Matin"
    elif h < 18:
        return "☀️ Après-midi"
    else:
        return "🌙 Soir"


def get_missed_yesterday(tasks_df):
    yesterday = date.today() - timedelta(days=1)
    y_iso = yesterday.isoformat()
    eligible = tasks_df[tasks_df["created_at"].str[:10] <= y_iso]
    if eligible.empty:
        return []
    done_rows = df("SELECT task_id FROM completions WHERE date = ?", (y_iso,))
    done_ids = set(done_rows["task_id"].tolist()) if not done_rows.empty else set()
    missed = eligible[~eligible["id"].isin(done_ids)]
    return missed["title"].tolist()


HORIZON_LABELS = {"court": "Court terme", "moyen": "Moyen terme", "long": "Long terme"}
HORIZON_COLORS = {"court": "🟢", "moyen": "🟠", "long": "🔴"}


def confirm_delete(key, on_confirm, label="Supprimer"):
    confirm_key = f"confirm_{key}"
    if not st.session_state.get(confirm_key):
        if st.button("🗑️", key=f"del_{key}", help=label):
            st.session_state[confirm_key] = True
            st.rerun()
        return False
    else:
        st.warning(f"Confirmer : {label} ?", icon="⚠️")
        cc1, cc2 = st.columns(2)
        if cc1.button("Oui, supprimer", key=f"yes_{key}", type="primary"):
            on_confirm()
            st.session_state[confirm_key] = False
            st.rerun()
        if cc2.button("Annuler", key=f"no_{key}"):
            st.session_state[confirm_key] = False
            st.rerun()
        return True


# ----------------------------- Export / Import -----------------------------

def export_data():
    return {
        "goals": df("SELECT * FROM goals").to_dict(orient="records"),
        "tasks": df("SELECT * FROM tasks").to_dict(orient="records"),
        "completions": df("SELECT * FROM completions").to_dict(orient="records"),
        "kaizen_notes": df("SELECT * FROM kaizen_notes").to_dict(orient="records"),
        "exported_at": datetime.now().isoformat(),
    }


def import_data(data):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM completions")
    c.execute("DELETE FROM kaizen_notes")
    c.execute("DELETE FROM tasks")
    c.execute("DELETE FROM goals")
    for g in data.get("goals", []):
        c.execute(
            "INSERT INTO goals (id, title, horizon, target_date, progress, auto_progress, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (g["id"], g["title"], g["horizon"], g.get("target_date"), g.get("progress", 0),
             g.get("auto_progress", 0), g.get("created_at")),
        )
    for t in data.get("tasks", []):
        c.execute(
            "INSERT INTO tasks (id, title, time, goal_id, created_at) VALUES (?, ?, ?, ?, ?)",
            (t["id"], t["title"], t["time"], t.get("goal_id"), t.get("created_at")),
        )
    for comp in data.get("completions", []):
        c.execute(
            "INSERT INTO completions (date, task_id, done) VALUES (?, ?, ?)",
            (comp["date"], comp["task_id"], comp.get("done", 1)),
        )
    for k in data.get("kaizen_notes", []):
        c.execute(
            "INSERT INTO kaizen_notes (date, note) VALUES (?, ?)",
            (k["date"], k.get("note", "")),
        )
    conn.commit()
    conn.close()


# ----------------------------- UI -----------------------------

st.set_page_config(page_title="Kaizen — Suivi quotidien", page_icon="改", layout="centered")
init_db()

today = date.today()
today_iso = today.isoformat()
now = datetime.now()

st.markdown(
    """
    <style>
    .stApp { background-color: #EFEBE1; }
    div[data-testid="stMetricValue"] { color: #AE3A2C; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("改 Kaizen — Suivi quotidien")
st.caption("Une petite amélioration chaque jour, chaque semaine")

tasks_df = df("SELECT * FROM tasks ORDER BY time ASC")
goals_df = df("SELECT * FROM goals ORDER BY horizon, created_at")

# ---------------- Sidebar : sauvegarde / restauration ----------------
with st.sidebar:
    st.header("💾 Sauvegarde")
    st.caption("Recommandé régulièrement, surtout si l'app est hébergée gratuitement (stockage non garanti dans le temps).")

    backup_json = json.dumps(export_data(), indent=2, ensure_ascii=False, default=str)
    st.download_button(
        "Exporter mes données (.json)",
        data=backup_json,
        file_name=f"kaizen-backup-{today_iso}.json",
        mime="application/json",
        use_container_width=True,
    )

    st.divider()
    st.subheader("Restaurer")
    uploaded = st.file_uploader("Fichier de sauvegarde (.json)", type="json")
    if uploaded is not None:
        confirm_restore = st.checkbox("Je confirme vouloir écraser mes données actuelles")
        if st.button("Restaurer", disabled=not confirm_restore, use_container_width=True):
            try:
                data = json.loads(uploaded.read())
                import_data(data)
                st.success("Données restaurées.")
                st.rerun()
            except Exception as e:
                st.error(f"Erreur lors de la restauration : {e}")

# ---------------- Bandeau tâches manquées hier ----------------
missed = get_missed_yesterday(tasks_df)
if missed:
    with st.expander(f"↩️ Hier, {len(missed)} tâche(s) non complétée(s)", expanded=False):
        for m in missed:
            st.markdown(f"- {m}")
        st.caption("C'est une information, pas un reproche — un jour manqué ne casse pas la démarche kaizen.")

col1, col2, col3 = st.columns(3)
overall_streak = compute_overall_streak(tasks_df)
today_rate = completion_rate(today_iso, tasks_df)
kaizen_streak = compute_kaizen_streak()

col1.metric("Jours à 100% (série)", overall_streak)
col2.metric("Aujourd'hui", "—" if today_rate is None else f"{round(today_rate*100)}%")
col3.metric("Jours de kaizen notés", kaizen_streak)

st.markdown(f"**{today.strftime('%A %d %B %Y')}** · {now.strftime('%H:%M')}")

tab_today, tab_goals, tab_review = st.tabs(["📋 Aujourd'hui", "🎯 Objectifs", "📊 Bilan"])

# ---------------- Tab: Today ----------------
with tab_today:
    st.subheader("Tâches du jour — à heure fixe")

    done_rows = df("SELECT task_id FROM completions WHERE date = ?", (today_iso,))
    done_ids = set(done_rows["task_id"].tolist()) if not done_rows.empty else set()

    if tasks_df.empty:
        st.info("Aucune tâche encore. Ajoutez votre première tâche quotidienne ci-dessous.")
    else:
        current_min = now.hour * 60 + now.minute
        tasks_df["_period"] = tasks_df["time"].apply(period_label)

        for period in ["🌅 Matin", "☀️ Après-midi", "🌙 Soir"]:
            period_tasks = tasks_df[tasks_df["_period"] == period]
            if period_tasks.empty:
                continue
            st.markdown(f"**{period}**")
            for _, t in period_tasks.iterrows():
                h, m = map(int, t["time"].split(":"))
                diff = abs(current_min - (h * 60 + m))
                is_current = diff <= 20
                is_done = t["id"] in done_ids
                edit_key = f"edit_task_{t['id']}"

                if st.session_state.get(edit_key):
                    with st.form(f"edit_form_{t['id']}"):
                        ec1, ec2, ec3 = st.columns([0.25, 0.5, 0.25])
                        e_time = ec1.time_input("Heure", value=datetime.strptime(t["time"], "%H:%M").time())
                        e_title = ec2.text_input("Titre", value=t["title"])
                        goal_opts = ["Aucun objectif lié"] + goals_df["title"].tolist() if not goals_df.empty else ["Aucun objectif lié"]
                        current_goal_title = "Aucun objectif lié"
                        if pd.notna(t["goal_id"]):
                            g_match = goals_df[goals_df["id"] == t["goal_id"]]
                            if not g_match.empty:
                                current_goal_title = g_match["title"].iloc[0]
                        e_goal = ec3.selectbox("Objectif", goal_opts, index=goal_opts.index(current_goal_title) if current_goal_title in goal_opts else 0)
                        fc1, fc2 = st.columns(2)
                        if fc1.form_submit_button("Enregistrer", type="primary"):
                            goal_id = None
                            if e_goal != "Aucun objectif lié":
                                goal_id = int(goals_df[goals_df["title"] == e_goal]["id"].iloc[0])
                            update_task(int(t["id"]), e_title.strip(), e_time.strftime("%H:%M"), goal_id)
                            st.session_state[edit_key] = False
                            st.rerun()
                        if fc2.form_submit_button("Annuler"):
                            st.session_state[edit_key] = False
                            st.rerun()
                    continue

                goal_label = ""
                if pd.notna(t["goal_id"]):
                    g = goals_df[goals_df["id"] == t["goal_id"]]
                    if not g.empty:
                        goal_label = f" · → {g['title'].iloc[0]}"

                streak_n = compute_task_streak(int(t["id"]), t["created_at"])
                streak_label = f" 🔥{streak_n}" if streak_n > 0 else ""

                c1, c2, c3, c4 = st.columns([0.1, 0.65, 0.13, 0.12])
                with c1:
                    checked = st.checkbox("", value=is_done, key=f"chk_{t['id']}_{today_iso}")
                    if checked != is_done:
                        toggle_completion(int(t["id"]), today_iso, is_done)
                        st.rerun()
                with c2:
                    prefix = "🔶 " if is_current else ""
                    strike = f"~~{t['title']}~~" if is_done else t["title"]
                    st.markdown(f"{prefix}`{t['time']}` {strike}{goal_label}{streak_label}")
                with c3:
                    if st.button("✏️", key=f"editbtn_{t['id']}"):
                        st.session_state[edit_key] = True
                        st.rerun()
                with c4:
                    confirm_delete(f"task_{t['id']}", lambda tid=int(t["id"]): delete_task(tid), label=f"supprimer « {t['title']} »")

    with st.form("add_task_form", clear_on_submit=True):
        st.markdown("**Ajouter une tâche**")
        fc1, fc2, fc3 = st.columns([0.25, 0.5, 0.25])
        new_time = fc1.time_input("Heure", value=datetime.strptime("08:00", "%H:%M").time())
        new_title = fc2.text_input("Titre de la tâche")
        goal_options = ["Aucun objectif lié"] + goals_df["title"].tolist() if not goals_df.empty else ["Aucun objectif lié"]
        selected_goal_label = fc3.selectbox("Objectif", goal_options)
        submitted = st.form_submit_button("Ajouter")
        if submitted:
            if not new_title.strip():
                st.warning("Le titre de la tâche ne peut pas être vide.")
            else:
                goal_id = None
                if selected_goal_label != "Aucun objectif lié":
                    goal_id = int(goals_df[goals_df["title"] == selected_goal_label]["id"].iloc[0])
                add_task(new_title.strip(), new_time.strftime("%H:%M"), goal_id)
                st.rerun()

    st.divider()
    st.subheader("Kaizen du jour")
    existing_note = df("SELECT note FROM kaizen_notes WHERE date = ?", (today_iso,))
    note_value = existing_note["note"].iloc[0] if not existing_note.empty else ""
    note = st.text_area(
        "Quelle petite amélioration avez-vous apportée aujourd'hui ?",
        value=note_value,
        placeholder="1% mieux qu'hier suffit.",
        key="kaizen_note_input",
    )
    if note != note_value:
        save_kaizen_note(today_iso, note)

    history = df(
        "SELECT date, note FROM kaizen_notes WHERE note IS NOT NULL AND note != '' AND date != ? "
        "ORDER BY date DESC LIMIT 8",
        (today_iso,),
    )
    if not history.empty:
        with st.expander("Historique du kaizen"):
            for _, row in history.iterrows():
                st.markdown(f"**{row['date']}** — {row['note']}")

# ---------------- Tab: Goals ----------------
with tab_goals:
    st.subheader("Objectifs")

    if goals_df.empty:
        st.info("Aucun objectif défini. Ajoutez un objectif court, moyen ou long terme.")
    else:
        for _, g in goals_df.iterrows():
            edit_key = f"edit_goal_{g['id']}"
            with st.container(border=True):
                if st.session_state.get(edit_key):
                    with st.form(f"edit_goal_form_{g['id']}"):
                        e_title = st.text_input("Titre", value=g["title"])
                        gc1, gc2 = st.columns(2)
                        e_horizon = gc1.selectbox(
                            "Horizon", ["court", "moyen", "long"],
                            index=["court", "moyen", "long"].index(g["horizon"]),
                            format_func=lambda h: HORIZON_LABELS[h],
                        )
                        e_date = gc2.date_input(
                            "Échéance",
                            value=date.fromisoformat(g["target_date"]) if g["target_date"] else None,
                        )
                        fc1, fc2 = st.columns(2)
                        if fc1.form_submit_button("Enregistrer", type="primary"):
                            update_goal(int(g["id"]), e_title.strip(), e_horizon, e_date.isoformat() if e_date else "")
                            st.session_state[edit_key] = False
                            st.rerun()
                        if fc2.form_submit_button("Annuler"):
                            st.session_state[edit_key] = False
                            st.rerun()
                    continue

                gc1, gc2, gc3, gc4 = st.columns([0.55, 0.2, 0.12, 0.13])
                gc1.markdown(f"**{g['title']}**")
                gc2.markdown(f"{HORIZON_COLORS[g['horizon']]} {HORIZON_LABELS[g['horizon']]}")
                if gc3.button("✏️", key=f"editbtn_goal_{g['id']}"):
                    st.session_state[edit_key] = True
                    st.rerun()
                with gc4:
                    confirm_delete(f"goal_{g['id']}", lambda gid=int(g["id"]): delete_goal(gid), label=f"supprimer « {g['title']} »")

                if g["target_date"]:
                    st.caption(f"Échéance : {g['target_date']}")

                has_linked_tasks = not tasks_df[tasks_df["goal_id"] == g["id"]].empty
                auto = bool(g["auto_progress"]) if has_linked_tasks else False
                if has_linked_tasks:
                    new_auto = st.checkbox(
                        "Calculer automatiquement à partir des tâches liées",
                        value=auto, key=f"auto_{g['id']}",
                    )
                    if new_auto != auto:
                        update_goal_auto(int(g["id"]), new_auto)
                        st.rerun()
                    auto = new_auto

                if auto:
                    auto_val = compute_auto_progress(int(g["id"]), g["created_at"], tasks_df)
                    st.progress(auto_val / 100, text=f"{auto_val}% (calculé automatiquement)")
                else:
                    new_progress = st.slider(
                        "Progression", 0, 100, int(g["progress"]), key=f"prog_{g['id']}"
                    )
                    if new_progress != g["progress"]:
                        update_goal_progress(int(g["id"]), new_progress)
                        st.rerun()

    with st.form("add_goal_form", clear_on_submit=True):
        st.markdown("**Ajouter un objectif**")
        goal_title = st.text_input("Titre de l'objectif")
        gc1, gc2 = st.columns(2)
        horizon = gc1.selectbox("Horizon", ["court", "moyen", "long"], format_func=lambda h: HORIZON_LABELS[h])
        target_date = gc2.date_input("Échéance (optionnel)", value=None)
        submitted_goal = st.form_submit_button("Ajouter l'objectif")
        if submitted_goal:
            if not goal_title.strip():
                st.warning("Le titre de l'objectif ne peut pas être vide.")
            else:
                add_goal(goal_title.strip(), horizon, target_date.isoformat() if target_date else "")
                st.rerun()

# ---------------- Tab: Review ----------------
with tab_review:
    st.subheader("Bilan de la semaine")

    if tasks_df.empty:
        st.info("Ajoutez des tâches pour voir apparaître votre bilan hebdomadaire.")
    else:
        rows = []
        for i in range(6, -1, -1):
            d = today - timedelta(days=i)
            rate = completion_rate(d.isoformat(), tasks_df)
            rows.append({
                "Jour": d.strftime("%a %d/%m"),
                "Taux (%)": 0 if rate is None else round(rate * 100),
            })
        chart_df = pd.DataFrame(rows).set_index("Jour")
        st.bar_chart(chart_df, color="#AE3A2C")

        st.divider()
        st.subheader("Régularité par tâche")
        for _, t in tasks_df.iterrows():
            s = compute_task_streak(int(t["id"]), t["created_at"])
            st.markdown(f"🔥 **{s}** jour(s) — {t['title']} (`{t['time']}`)")

    st.divider()
    st.subheader("Progression des objectifs")
    if not goals_df.empty:
        for horizon in ["court", "moyen", "long"]:
            subset = goals_df[goals_df["horizon"] == horizon]
            if subset.empty:
                continue
            st.markdown(f"**{HORIZON_LABELS[horizon]}**")
            for _, g in subset.iterrows():
                if g["auto_progress"]:
                    val = compute_auto_progress(int(g["id"]), g["created_at"], tasks_df) or 0
                else:
                    val = int(g["progress"])
                st.progress(val / 100, text=f"{g['title']} — {val}%")
    else:
        st.info("Aucun objectif à afficher pour le moment.")

st.caption("Les données sont enregistrées dans une base SQLite locale (kaizen.db). Pensez à exporter une sauvegarde régulièrement via le menu latéral.")
