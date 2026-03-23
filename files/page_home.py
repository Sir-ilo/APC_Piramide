"""
page_home.py  —  Tab 1: Dashboard / Home
"""

import streamlit as st
import pandas as pd
from data_layer import assign_categories
from logic import is_immune, guardian_remaining, team_badges, level_pill_html
from components import rank_card_html, nav_to, section_header
from config import LEVEL_COLORS


def render_home(data: dict, conn):
    ranking = assign_categories(data["ranking"].copy())
    teams   = data["teams"]

    if ranking.empty:
        st.info("Sem equipas no ranking. O administrador deve adicionar equipas.")
        return

    # ── Rei da Montanha (M1) ─────────────────────────────────────────────────
    m1 = ranking[ranking["category"] == "M1"]
    if not m1.empty:
        king = m1.iloc[0]
        # Merge team info
        t_row = teams[teams["team_id"] == king["team_id"]]
        p1 = t_row["player1"].values[0] if not t_row.empty else ""
        p2 = t_row["player2"].values[0] if not t_row.empty else ""
        pts = int(king["points"] or 0)
        w   = int(t_row["wins"].values[0]   if not t_row.empty else 0)
        l   = int(t_row["losses"].values[0] if not t_row.empty else 0)

        st.markdown(f"""
        <div class="card-king animate-slide">
          <div class="king-title">👑 Rei da Montanha · M1</div>
          <div class="king-name">{king['team_name']}</div>
          <div class="king-players">{p1}{' &amp; ' + p2 if p2 else ''}</div>
          <div class="king-pts">🏅 {pts} pts &nbsp;·&nbsp; {w}V {l}D</div>
        </div>
        """, unsafe_allow_html=True)
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
        st.markdown('<div class="card"><span style="color:var(--text-muted);">Sem equipas em M2.</span></div>',
                    unsafe_allow_html=True)
    else:
        for _, row in m2.iterrows():
            t_row  = teams[teams["team_id"] == row["team_id"]]
            streak = int(t_row["streak"].values[0] if not t_row.empty else 0)
            is_me  = (row["team_id"] == st.session_state.team_id)
            if not t_row.empty:
                row = row.to_dict()
                row["player1"] = t_row["player1"].values[0]
                row["player2"] = t_row["player2"].values[0]
                row["photo_url"] = t_row["photo_url"].values[0]
            st.markdown(rank_card_html(row, streak, is_me), unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🏅 Ver Ranking Completo", use_container_width=True, key="home_ranking"):
            nav_to("ranking")
    with col2:
        pass

    # ── Pending confirmations alert ───────────────────────────────────────────
    matches = data["matches"]
    my_id   = st.session_state.team_id
    if not matches.empty:
        pend = matches[
            (matches["team_b_id"] == my_id) &
            (matches["validation_status"] == "pending")
        ]
        if not pend.empty:
            st.warning(
                f"⚠️ **{len(pend)} resultado(s) aguarda(m) a tua confirmação!**"
            )
            if st.button("⚔️ Ver Desafios Pendentes", key="home_pend"):
                nav_to("challenges")

    # ── Ações rápidas ─────────────────────────────────────────────────────────
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    section_header("Acções Rápidas", "⚡")
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("⚔️ Novo Desafio", use_container_width=True, key="home_challenge"):
            nav_to("challenges")
    with c2:
        if st.button("📝 Registar Resultado", use_container_width=True, key="home_result"):
            nav_to("results")
    with c3:
        if st.button("👥 Gerir Equipa", use_container_width=True, key="home_team"):
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
        m1c.metric("Posição", f"#{int(r['position'])}")
        m2c.metric("Nível",   str(r["category"]))
        m3c.metric("Pontos",  int(r["points"] or 0))
        m4c.metric("Streak",  f"🔥{int(t['streak'] or 0)}")
