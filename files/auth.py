"""
auth.py  —  Login form, logout, session state defaults.
"""

import streamlit as st
from data_layer import verify_login, load_all
from config import ADMIN_ID


def ensure_session_defaults():
    defaults = {
        "authenticated": False,
        "team_id":       None,
        "team_name":     None,
        "is_admin":      False,
        "active_page":   "home",
        "show_help":     False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def render_login(conn):
    # Logo / club image — place your logo at files/logo.png in the repo
    import os, base64
    logo_path = os.path.join(os.path.dirname(__file__), "logo.png")
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            logo_b64 = base64.b64encode(f.read()).decode()
        logo_html = (f'<img src="data:image/png;base64,{logo_b64}" '                     f'style="width:110px;border-radius:16px;margin-bottom:10px;">')
    else:
        logo_html = '<div style="font-size:3rem;margin-bottom:10px;">🏆</div>'

    st.markdown(f"""
    <div class="login-container">
      {logo_html}
      <div class="login-logo">APC<br>Champions League</div>
      <div class="login-sub">Padel · Ranking Ladder</div>
    </div>
    """, unsafe_allow_html=True)

    _, col, _ = st.columns([1, 2, 1])
    with col:
        with st.container():
            st.markdown(
                "<div style='background:var(--card);border:1px solid var(--border);"
                "border-radius:16px;padding:28px 24px;'>",
                unsafe_allow_html=True,
            )
            tid = st.text_input("ID da Equipa", placeholder="ex: EQ001 ou admin",
                                key="login_tid").strip()
            pw  = st.text_input("Password", type="password", key="login_pw")

            if st.button("▶  Entrar", width='stretch', key="login_btn"):
                data = load_all(conn)
                user = verify_login(data["teams"], tid, pw)
                if user:
                    st.session_state.authenticated = True
                    st.session_state.team_id       = tid
                    st.session_state.team_name     = user.get("team_name", tid)
                    st.session_state.is_admin      = (tid == ADMIN_ID or
                                                      str(user.get("is_admin","")).upper() == "TRUE")
                    # Check for pending confirmations → go to challenges
                    my_matches = data["matches"]
                    if not my_matches.empty:
                        pend = my_matches[
                            (my_matches["team_b_id"] == tid) &
                            (my_matches["validation_status"] == "pending")
                        ]
                        if not pend.empty:
                            st.session_state.active_page = "challenges"
                    st.rerun()
                else:
                    st.error("Credenciais inválidas.")
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        "<div style='text-align:center;margin-top:16px;color:var(--text-dim);"
        "font-size:0.75rem;'>Liga de Duplas © 2024</div>",
        unsafe_allow_html=True,
    )
