"""
seed_data.py
─────────────────────────────────────────────────────────────────────────────
Run ONCE to populate the Google Sheets with 20 test teams for the
Torneio de Abertura.

Usage:
    streamlit run seed_data.py

Or from command line (set GOOGLE_APPLICATION_CREDENTIALS or use secrets):
    python seed_data.py
─────────────────────────────────────────────────────────────────────────────
"""

import streamlit as st
import pandas as pd
import hashlib
from datetime import datetime, timezone

st.set_page_config(page_title="Seed Data", page_icon="🌱")
st.title("🌱 Seed — Torneio de Abertura")
st.warning("Este script popula as sheets com 20 equipas de teste. Executa apenas uma vez!")

def now_iso():
    return datetime.now(timezone.utc).isoformat()

def h(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

# ── 20 equipas ────────────────────────────────────────────────────────────────
TEAMS = [
    ("EQ001", "Os Trovões",       "João Silva",      "Pedro Costa"),
    ("EQ002", "Ace Masters",      "Miguel Santos",   "Rui Ferreira"),
    ("EQ003", "Net Ninjas",       "André Oliveira",  "Tiago Sousa"),
    ("EQ004", "Smash Bros",       "Carlos Mendes",   "Paulo Rodrigues"),
    ("EQ005", "Drop Shot Kings",  "Nuno Pereira",    "Filipe Carvalho"),
    ("EQ006", "Lob Stars",        "Ricardo Gomes",   "Sérgio Martins"),
    ("EQ007", "Volley Boys",      "António Lima",    "Luís Pinto"),
    ("EQ008", "Court Jesters",    "Hugo Fernandes",  "Bruno Alves"),
    ("EQ009", "Padel Sharks",     "Marco Correia",   "David Lopes"),
    ("EQ010", "Wild Cards",       "Gonçalo Dias",    "Rafael Mota"),
    ("EQ011", "Deuce Devils",     "Vítor Cunha",     "Fábio Neves"),
    ("EQ012", "Power Serves",     "Diogo Teixeira",  "Leandro Reis"),
    ("EQ013", "Baseline Kings",   "Rodrigo Freitas", "Hélder Castro"),
    ("EQ014", "Net Breakers",     "Eduardo Moreira", "Bernardo Fonseca"),
    ("EQ015", "Spin Masters",     "Tomás Azevedo",   "Samuel Barros"),
    ("EQ016", "Slice & Dice",     "Mário Pires",     "Valter Soares"),
    ("EQ017", "The Returners",    "Álvaro Brito",    "Cláudio Campos"),
    ("EQ018", "Rally Cats",       "Nelson Henriques", "Osvaldo Cruz"),
    ("EQ019", "Topspin Tigers",   "Armindo Rocha",   "Celestino Serra"),
    ("EQ020", "Game Set Match",   "Florindo Nunes",  "Januário Vaz"),
]

# Resultados simulados do Torneio de Abertura (W, L, streak, total)
STATS = [
    (8,2,3,10),(7,3,4,10),(9,1,5,10),(6,4,2,10),(5,5,0,10),
    (7,3,3,10),(6,4,2,10),(5,5,1,10),(4,6,0,10),(8,2,4,10),
    (6,4,2,10),(5,5,1,10),(7,3,3,10),(4,6,0,10),(6,4,2,10),
    (5,5,0,10),(3,7,0,10),(4,6,1,10),(3,7,0,10),(2,8,0,10),
]

def get_cat(pos):
    if pos == 1:  return "M1"
    if pos <= 5:  return "M2"
    if pos <= 11: return "M3"
    if pos <= 17: return "M4"
    return "M5"

def build_dataframes():
    # Sort by wins desc → ranking order
    combined = sorted(zip(TEAMS, STATS), key=lambda x: (-x[1][0], x[1][1]))

    team_rows    = []
    ranking_rows = []
    trunfo_rows  = []

    for pos, ((tid, name, p1, p2), (w, l, streak, tm)) in enumerate(combined, 1):
        pts = w * 5 + l
        cat = get_cat(pos)

        team_rows.append({
            "team_id": tid, "team_name": name,
            "player1": p1, "player2": p2,
            "password_hash": h("padel2024"),
            "is_admin": "FALSE", "photo_url": "",
            "wins": w, "losses": l, "streak": streak,
            "total_matches": tm, "last_match_date": now_iso(),
            "created_at": now_iso(),
        })
        ranking_rows.append({
            "team_id": tid, "team_name": name,
            "position": pos, "category": cat,
            "points": pts, "prev_position": pos,
            "guardian_since": "", "immune_until": "",
            "ready_to_climb": "FALSE", "trunfo_salto_active": "FALSE",
        })
        trunfo_rows.append({
            "team_id": tid,
            "desforra_qty": 1, "salto_qty": 1, "escudo_qty": 1,
            "last_trunfo_month": "",
        })

    return (
        pd.DataFrame(team_rows),
        pd.DataFrame(ranking_rows),
        pd.DataFrame(trunfo_rows),
    )

# ── Preview ───────────────────────────────────────────────────────────────────
teams_df, ranking_df, trunfos_df = build_dataframes()

st.markdown("### 🏆 Ranking resultante do Torneio de Abertura")
st.dataframe(
    ranking_df[["position","team_name","category","points"]],
    hide_index=True, use_container_width=True
)
st.markdown("### 👥 Equipas (password: `padel2024`)")
st.dataframe(
    teams_df[["team_id","team_name","player1","player2","wins","losses"]],
    hide_index=True, use_container_width=True
)

st.markdown("---")
st.info("Clica em **Executar Seed** para escrever estes dados na Google Sheets.")

if st.button("🌱 Executar Seed", type="primary"):
    try:
        import gspread
        import time
        from google.oauth2.service_account import Credentials

        s = st.secrets["connections"]["gsheets"]
        creds = Credentials.from_service_account_info(
            {k: s[k] for k in [
                "type","project_id","private_key_id","private_key",
                "client_email","client_id","auth_uri","token_uri",
                "auth_provider_x509_cert_url","client_x509_cert_url"
            ]},
            scopes=[
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive",
            ],
        )
        gc  = gspread.authorize(creds)
        raw = str(s["spreadsheet"])
        sid = raw.split("/spreadsheets/d/")[1].split("/")[0].split("?")[0].strip() \
              if "/spreadsheets/d/" in raw else raw.strip()
        wb  = gc.open_by_key(sid)

        def write_sheet(wb, sheet_name, df):
            try:
                ws = wb.worksheet(sheet_name)
            except Exception:
                ws = wb.add_worksheet(title=sheet_name, rows=200, cols=30)
            ws.clear()
            rows = [df.columns.tolist()] + df.astype(str).values.tolist()
            ws.update(rows, value_input_option="RAW")
            time.sleep(2)  # respect rate limits

        with st.spinner("A escrever teams..."):
            # Preserve admin row — read existing teams first
            try:
                existing = wb.worksheet("teams").get_all_values()
                if existing and len(existing) > 1:
                    existing_df = pd.DataFrame(existing[1:], columns=existing[0])
                    admin_rows  = existing_df[existing_df["team_id"] == "admin"]
                    teams_final = pd.concat([admin_rows, teams_df], ignore_index=True)
                else:
                    # Create admin row
                    admin_row = pd.DataFrame([{
                        "team_id": "admin", "team_name": "Administrador",
                        "player1": "Admin", "player2": "",
                        "password_hash": h("admin2024"),
                        "is_admin": "TRUE", "photo_url": "",
                        "wins": 0, "losses": 0, "streak": 0,
                        "total_matches": 0, "last_match_date": "",
                        "created_at": now_iso(),
                    }])
                    teams_final = pd.concat([admin_row, teams_df], ignore_index=True)
            except Exception:
                teams_final = teams_df

            write_sheet(wb, "teams", teams_final)
            st.success(f"✅ teams — {len(teams_final)} linhas")

        with st.spinner("A escrever ranking..."):
            write_sheet(wb, "ranking", ranking_df)
            st.success(f"✅ ranking — {len(ranking_df)} linhas")

        with st.spinner("A escrever trunfos..."):
            write_sheet(wb, "trunfos", trunfos_df)
            st.success(f"✅ trunfos — {len(trunfos_df)} linhas")

        with st.spinner("A limpar challenges e matches..."):
            for sheet in ["challenges", "matches", "pending_edits"]:
                try:
                    ws = wb.worksheet(sheet)
                    ws.clear()
                    time.sleep(1)
                    st.success(f"✅ {sheet} — limpo")
                except Exception:
                    pass

        st.success("🎉 **Seed completo!** Vai para a app principal e faz login.")
        st.balloons()

    except Exception as e:
        st.error(f"Erro: {e}")
