"""
Liga de Duplas — app.py
Entry point. Handles page config, session init, auth gate, and tab routing.
"""

import streamlit as st

st.set_page_config(
    page_title="APC Champions League",
    page_icon="🎾",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Local modules ──────────────────────────────────────────────────────────────
from styles import inject_all_styles
from auth import render_login, ensure_session_defaults
from data_layer import get_conn, init_all_sheets, load_all
from page_home import render_home
from page_ranking import render_ranking
from page_challenges import render_challenges
from page_teams import render_teams
from page_results import render_results
from page_admin import render_admin
from page_team_detail import render_team_detail
from components import render_navbar, render_help_modal

# ── Styles ─────────────────────────────────────────────────────────────────────
inject_all_styles()

# ── Session defaults ───────────────────────────────────────────────────────────
ensure_session_defaults()
# Ensure view_team_id always exists in session
if "view_team_id" not in st.session_state:
    st.session_state["view_team_id"] = None

# ── Google Sheets connection + one-time init ───────────────────────────────────
@st.cache_resource(show_spinner=False)
def _conn():
    import time
    c = get_conn()
    time.sleep(2)
    init_all_sheets(c)
    return c

conn = _conn()

# ── Auth gate ──────────────────────────────────────────────────────────────────
if not st.session_state.get("authenticated"):
    render_login(conn)
    st.stop()

# ── Load data ──────────────────────────────────────────────────────────────────
@st.cache_data(ttl=8, show_spinner=False)
def _load():
    return load_all(conn)

# Force reload when navigating
if st.session_state.get("_last_page") != st.session_state.get("active_page"):
    st.cache_data.clear()
    st.session_state["_last_page"] = st.session_state.get("active_page")

data = _load()

# ── Top bar ────────────────────────────────────────────────────────────────────
top_left, top_right = st.columns([6, 1])
with top_left:
    st.markdown(
        f"<div class='topbar-greeting'>{'Olá meu Mestre 👑' if st.session_state.get('is_admin') else f'Olá, <span>{st.session_state.team_name}</span> 👋'}</div>",
        unsafe_allow_html=True,
    )
with top_right:
    if st.button("🚪", help="Logout", key="logout_btn"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()

# ── Routing ────────────────────────────────────────────────────────────────────
active      = st.session_state.get("active_page", "home")
view_team   = st.session_state.get("view_team_id")  # None or a team_id string

if view_team:
    # Show back button prominently so user can always escape
    render_team_detail(data, conn, view_team)
elif active == "home":
    render_home(data, conn)
elif active == "ranking":
    render_ranking(data, conn)
elif active == "challenges":
    render_challenges(data, conn)
elif active == "teams":
    render_teams(data, conn)
elif active == "results":
    render_results(data, conn)
elif active == "admin" and st.session_state.get("is_admin"):
    render_admin(data, conn)
else:
    render_home(data, conn)

# ── Footer Sir-ILO with dragon egg (all screens) ──────────────────────────────
from auth import _render_dragon_egg
_render_dragon_egg()

# ── Bottom nav bar ─────────────────────────────────────────────────────────────
render_navbar()
