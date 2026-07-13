import streamlit as st
import sqlite3
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
        "INSERT INTO goals (title, horizon, target_date, progress, created_at) VALUES (?, ?, ?, 0, ?)",
        (title, horizon, target_date, datetime.now().isoformat()),
    )


def update_goal_progress(goal_id, progress):
    execute("UPDATE goals SET progress = ? WHERE id = ?", (progress, goal_id))


def delete_goal(goal_id):
    execute("UPDATE tasks SET goal_id = NULL WHERE goal_id = ?", (goal_id,))
    execute("DELETE FROM goals WHERE id = ?", (goal_id,))


def add_task(title, time_str, goal_id):
    execute(
        "INSERT INTO tasks (title, time, goal_id, created_at) VALUES (?, ?, ?, ?)",
        (title, time_str, goal_id if goal_id else None, datetime.now().isoformat()),
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


HORIZON_LABELS = {"court": "Court terme", "moyen": "Moyen terme", "long": "Long terme"}
HORIZON_COLORS = {"court": "🟢", "moyen": "🟠", "long": "🔴"}


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
        for _, t in tasks_df.iterrows():
            h, m = map(int, t["time"].split(":"))
            diff = abs(current_min - (h * 60 + m))
            is_current = diff <= 20
            is_done = t["id"] in done_ids

            goal_label = ""
            if pd.notna(t["goal_id"]):
                g = goals_df[goals_df["id"] == t["goal_id"]]
                if not g.empty:
                    goal_label = f" · → {g['title'].iloc[0]}"

            c1, c2, c3 = st.columns([0.12, 0.75, 0.13])
            with c1:
                checked = st.checkbox("", value=is_done, key=f"chk_{t['id']}_{today_iso}")
                if checked != is_done:
                    toggle_completion(int(t["id"]), today_iso, is_done)
                    st.rerun()
            with c2:
                prefix = "🔶 " if is_current else ""
                strike = f"~~{t['title']}~~" if is_done else t["title"]
                st.markdown(f"{prefix}`{t['time']}` {strike}{goal_label}")
            with c3:
                if st.button("×", key=f"del_task_{t['id']}"):
                    delete_task(int(t["id"]))
                    st.rerun()

    with st.form("add_task_form", clear_on_submit=True):
        st.markdown("**Ajouter une tâche**")
        fc1, fc2, fc3 = st.columns([0.25, 0.5, 0.25])
        new_time = fc1.time_input("Heure", value=datetime.strptime("08:00", "%H:%M").time())
        new_title = fc2.text_input("Titre de la tâche")
        goal_options = ["Aucun objectif lié"] + goals_df["title"].tolist() if not goals_df.empty else ["Aucun objectif lié"]
        selected_goal_label = fc3.selectbox("Objectif", goal_options)
        submitted = st.form_submit_button("Ajouter")
        if submitted and new_title.strip():
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
            with st.container(border=True):
                gc1, gc2 = st.columns([0.75, 0.25])
                gc1.markdown(f"**{g['title']}**")
                gc2.markdown(f"{HORIZON_COLORS[g['horizon']]} {HORIZON_LABELS[g['horizon']]}")
                if g["target_date"]:
                    st.caption(f"Échéance : {g['target_date']}")
                new_progress = st.slider(
                    "Progression", 0, 100, int(g["progress"]), key=f"prog_{g['id']}"
                )
                if new_progress != g["progress"]:
                    update_goal_progress(int(g["id"]), new_progress)
                    st.rerun()
                if st.button("Supprimer l'objectif", key=f"del_goal_{g['id']}"):
                    delete_goal(int(g["id"]))
                    st.rerun()

    with st.form("add_goal_form", clear_on_submit=True):
        st.markdown("**Ajouter un objectif**")
        goal_title = st.text_input("Titre de l'objectif")
        gc1, gc2 = st.columns(2)
        horizon = gc1.selectbox("Horizon", ["court", "moyen", "long"], format_func=lambda h: HORIZON_LABELS[h])
        target_date = gc2.date_input("Échéance (optionnel)", value=None)
        submitted_goal = st.form_submit_button("Ajouter l'objectif")
        if submitted_goal and goal_title.strip():
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
    st.subheader("Progression des objectifs")
    if not goals_df.empty:
        for horizon in ["court", "moyen", "long"]:
            subset = goals_df[goals_df["horizon"] == horizon]
            if subset.empty:
                continue
            st.markdown(f"**{HORIZON_LABELS[horizon]}**")
            for _, g in subset.iterrows():
                st.progress(int(g["progress"]) / 100, text=f"{g['title']} — {g['progress']}%")
    else:
        st.info("Aucun objectif à afficher pour le moment.")

st.caption("Les données sont enregistrées dans une base SQLite locale (kaizen.db), propre à cette instance de l'app.")
