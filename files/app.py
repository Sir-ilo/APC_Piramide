"""
Liga de Duplas — app.py
Entry point. Handles page config, session init, auth gate, and tab routing.
"""

import streamlit as st

st.set_page_config(
    page_title="Liga de Duplas",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Local modules ──────────────────────────────────────────────────────────────
from config import NAV_ITEMS
from styles import inject_all_styles
from auth import render_login, ensure_session_defaults
from data_layer import get_conn, init_all_sheets, load_all
from page_home import render_home
from page_ranking import render_ranking
from page_challenges import render_challenges
from page_teams import render_teams
from page_results import render_results
from page_admin import render_admin
from components import render_navbar, render_help_modal

# ── Styles (must come before any st.markdown) ──────────────────────────────────
inject_all_styles()

# ── Session defaults ───────────────────────────────────────────────────────────
ensure_session_defaults()

# ── Google Sheets connection (cached resource) ─────────────────────────────────
@st.cache_resource(show_spinner=False)
def _conn():
    return get_conn()

conn = _conn()
init_all_sheets(conn)

# ── Auth gate ──────────────────────────────────────────────────────────────────
if not st.session_state.get("authenticated"):
    render_login(conn)
    st.stop()

# ── Load data (short TTL cache so edits propagate quickly) ─────────────────────
@st.cache_data(ttl=8, show_spinner=False)
def _load():
    return load_all(conn)

data = _load()

# ── Help modal (floating '?' button) ──────────────────────────────────────────
render_help_modal()

# ── Top bar ────────────────────────────────────────────────────────────────────
top_left, top_right = st.columns([6, 1])
with top_left:
    st.markdown(
        f"<div class='topbar-greeting'>Olá, <span>{st.session_state.team_name}</span> 👋</div>",
        unsafe_allow_html=True,
    )
with top_right:
    if st.button("🚪", help="Logout", key="logout_btn"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()

# ── Active page routing ────────────────────────────────────────────────────────
active = st.session_state.get("active_page", "home")

if active == "home":
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

# ── Bottom nav bar ─────────────────────────────────────────────────────────────
render_navbar()
