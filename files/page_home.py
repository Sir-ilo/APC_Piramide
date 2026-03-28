"""
page_home.py  —  Tab 1: Dashboard / Home
"""

import streamlit as st
import pandas as pd
from data_layer import assign_categories
from logic import is_immune, guardian_remaining
from components import nav_to, section_header, build_rows_data, render_expandable_cards
from config import LEVEL_COLORS


def _safe_int(val, default=0):
    try:
        return int(float(str(val).strip() or default))
    except (ValueError, TypeError):
        return default


def render_home(data: dict, conn):
    ranking = assign_categories(data["ranking"].copy())
    teams   = data["teams"]
    trunfos = data["trunfos"]

    if ranking.empty:
        st.info("Sem equipas no ranking. O administrador deve adicionar equipas.")
        return


    # ── Rei da Montanha (M1) ─────────────────────────────────────────────────
    m1 = ranking[ranking["category"] == "M1"]
    if not m1.empty:
        king  = m1.iloc[0]
        t_row = teams[teams["team_id"] == king["team_id"]]
        p1  = t_row["player1"].values[0] if not t_row.empty else ""
        p2  = t_row["player2"].values[0] if not t_row.empty else ""
        pts = _safe_int(king["points"])
        w   = _safe_int(t_row["wins"].values[0]   if not t_row.empty else 0)
        l   = _safe_int(t_row["losses"].values[0] if not t_row.empty else 0)
        st.markdown(f"""
        <div class="card-king animate-slide">
          <div class="king-title">👑 Rei da Montanha · M1</div>
          <div class="king-name">{king['team_name']}</div>
          <div class="king-players">{p1}{' &amp; ' + p2 if p2 else ''}</div>
          <div class="king-pts">🏅 {pts} pts &nbsp;·&nbsp; {w}V {l}D</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("👤 Ver Perfil do Campeão", key="king_detail"):
            st.session_state["view_team_id"] = str(king["team_id"])
            st.rerun()
    else:
        st.markdown(
            '<div class="card-king" style="opacity:.5;"><div class="king-title">Trono vazio</div>'
            '<div class="king-name" style="font-size:1.3rem;color:#666;">—</div></div>',
            unsafe_allow_html=True,
        )

    # ── Top 5 M2 ─────────────────────────────────────────────────────────────
    section_header("Top M2", "🥈")
    m2 = ranking[ranking["category"] == "M2"].head(5)

    if m2.empty:
        st.info("Sem equipas em M2.")
    else:
        rows_data = build_rows_data(m2, teams, trunfos, data.get("matches", __import__("pandas").DataFrame()), my_id)
        render_expandable_cards(rows_data, my_id, conn, data)

    col1, _ = st.columns(2)
    with col1:
        if st.button("🏅 Ver Ranking Completo", key="home_ranking"):
            nav_to("ranking")

    # ── Pending confirmations alert ───────────────────────────────────────────
    matches = data["matches"]
    my_id   = st.session_state.team_id
    if not matches.empty:
        pend = matches[
            (matches["team_b_id"] == my_id) &
            (matches["validation_status"] == "pending")
        ]
        if not pend.empty:
            st.warning(f"⚠️ **{len(pend)} resultado(s) aguarda(m) a tua confirmação!**")
            if st.button("⚔️ Ver Desafios Pendentes", key="home_pend"):
                nav_to("challenges")

    # ── Acções rápidas ────────────────────────────────────────────────────────
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    section_header("Acções Rápidas", "⚡")
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("⚔️ Novo Desafio",       key="home_challenge"):
            nav_to("challenges")
    with c2:
        if st.button("📝 Registar Resultado",  key="home_result"):
            nav_to("results")
    with c3:
        if st.button("👥 Gerir Equipa",        key="home_team"):
            st.cache_data.clear()
            nav_to("teams")

    # ── My stats mini ─────────────────────────────────────────────────────────
    my_rank = ranking[ranking["team_id"] == my_id]
    my_team = teams[teams["team_id"] == my_id]
    if not my_rank.empty and not my_team.empty:
        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
        section_header("A Minha Equipa", "📊")
        r = my_rank.iloc[0]
        t = my_team.iloc[0]
        m1c, m2c, m3c, m4c = st.columns(4)
        m1c.metric("Posição", f"#{_safe_int(r['position'])}")
        m2c.metric("Nível",   str(r["category"]))
        m3c.metric("Pontos",  _safe_int(r["points"]))
        m4c.metric("Streak",  f"🔥{_safe_int(t['streak'])}")
        if st.button("👤 Ver o Meu Perfil Completo", key="home_myprofile"):
            st.session_state["view_team_id"] = my_id
            st.rerun()
