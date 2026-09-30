import json
import uuid
from datetime import date, datetime
from pathlib import Path

import streamlit as st

DATA_FILE = Path(__file__).parent / "tirelire.json"
CURRENCIES = {"Ariary": "Ar", "€": "€", "$": "$"}

st.set_page_config(page_title="Ma Tirelire", page_icon="🐷", layout="centered")


def load() -> dict:
    if DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    return {"currency": "Ariary", "jars": []}


def save() -> None:
    DATA_FILE.write_text(
        json.dumps(st.session_state.data, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def balance(jar: dict) -> float:
    return sum(t["amount"] for t in jar["transactions"])


def money(value: float) -> str:
    cur = st.session_state.data["currency"]
    digits = 0 if cur == "Ariary" else 2
    return f"{value:,.{digits}f} {CURRENCIES[cur]}".replace(",", " ")


if "data" not in st.session_state:
    st.session_state.data = load()
data = st.session_state.data

st.title("🐷 Ma Tirelire")
st.caption("Épargnez pour vos objectifs : lancement de boutique, publicité, stock, LLC…")

# ---------- Barre latérale : réglages et nouvelle tirelire ----------
with st.sidebar:
    st.header("Réglages")
    data["currency"] = st.selectbox(
        "Devise", list(CURRENCIES), index=list(CURRENCIES).index(data["currency"])
    )

    st.header("Nouvelle tirelire")
    with st.form("new_jar", clear_on_submit=True):
        name = st.text_input("Nom", placeholder="Ex : Budget publicité Meta")
        target = st.number_input("Objectif", min_value=0.0, step=10.0)
        deadline = st.date_input("Date limite (optionnel)", value=None, min_value=date.today())
        if st.form_submit_button("Créer", width="stretch"):
            if name.strip() and target > 0:
                data["jars"].append(
                    {
                        "id": uuid.uuid4().hex,
                        "name": name.strip(),
                        "target": target,
                        "deadline": deadline.isoformat() if deadline else None,
                        "transactions": [],
                    }
                )
                save()
                st.rerun()
            else:
                st.error("Indiquez un nom et un objectif supérieur à 0.")

save()

# ---------- Vue d'ensemble ----------
jars = data["jars"]
if not jars:
    st.info("Aucune tirelire pour l'instant. Créez la première dans la barre latérale 👈")
    st.stop()

total = sum(balance(j) for j in jars)
total_target = sum(j["target"] for j in jars)
c1, c2, c3 = st.columns(3)
c1.metric("Total épargné", money(total))
c2.metric("Objectifs cumulés", money(total_target))
c3.metric("Reste à épargner", money(max(total_target - total, 0)))

# ---------- Une section par tirelire ----------
for jar in jars:
    bal = balance(jar)
    pct = min(bal / jar["target"], 1.0) if jar["target"] else 0
    done = bal >= jar["target"]

    with st.container(border=True):
        st.subheader(f"{'✅' if done else '🎯'} {jar['name']}")
        st.progress(pct, text=f"{money(bal)} sur {money(jar['target'])} ({pct:.0%})")

        if jar["deadline"] and not done:
            days_left = (date.fromisoformat(jar["deadline"]) - date.today()).days
            remaining = jar["target"] - bal
            if days_left > 0:
                st.caption(
                    f"⏳ {days_left} jours restants → "
                    f"il faut mettre de côté **{money(remaining / days_left)} par jour** "
                    f"({money(remaining / max(days_left / 7, 1))} par semaine)."
                )
            else:
                st.caption("⚠️ Date limite dépassée.")
        if done:
            st.success("Objectif atteint, bravo !")

        with st.form(f"tx_{jar['id']}", clear_on_submit=True):
            a, b, c = st.columns([2, 3, 2])
            amount = a.number_input("Montant", min_value=0.0, step=5.0, key=f"amt_{jar['id']}")
            note = b.text_input("Note", key=f"note_{jar['id']}", placeholder="Ex : vente #12")
            kind = c.radio("Type", ["Dépôt", "Retrait"], horizontal=True, key=f"kind_{jar['id']}")
            if st.form_submit_button("Valider"):
                if amount <= 0:
                    st.error("Le montant doit être supérieur à 0.")
                elif kind == "Retrait" and amount > bal:
                    st.error("Solde insuffisant pour ce retrait.")
                else:
                    jar["transactions"].append(
                        {
                            "date": datetime.now().isoformat(timespec="minutes"),
                            "amount": amount if kind == "Dépôt" else -amount,
                            "note": note.strip(),
                        }
                    )
                    save()
                    st.rerun()

        with st.expander(f"Historique ({len(jar['transactions'])})"):
            if jar["transactions"]:
                st.dataframe(
                    [
                        {"Date": t["date"].replace("T", " "), "Montant": t["amount"], "Note": t["note"]}
                        for t in reversed(jar["transactions"])
                    ],
                    width="stretch",
                    hide_index=True,
                )
            else:
                st.write("Aucune opération.")
            if st.button("🗑️ Supprimer cette tirelire", key=f"del_{jar['id']}"):
                data["jars"] = [j for j in jars if j["id"] != jar["id"]]
                save()
                st.rerun()

# ---------- Sauvegarde ----------
st.divider()
st.download_button(
    "⬇️ Télécharger mes données (JSON)",
    json.dumps(data, ensure_ascii=False, indent=2),
    file_name="tirelire.json",
    mime="application/json",
)
