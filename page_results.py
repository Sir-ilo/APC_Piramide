"""
page_results.py  —  Tab 5: Submit match result + timeline of validated matches.
"""

import streamlit as st
import pandas as pd
from data_layer import assign_categories, submit_match
from logic import determine_winner_sets
from components import section_header
from config import LEVEL_COLORS


def render_results(data: dict, conn):
    my_id  = st.session_state.team_id
    teams  = data["teams"]
    ranking= assign_categories(data["ranking"].copy())
    matches= data["matches"]
    challenges = data["challenges"]

    # ── Submit new result ─────────────────────────────────────────────────────
    section_header("Registar Resultado", "📝")

    # Find accepted challenges involving me
    my_ch = pd.DataFrame()
    if not challenges.empty:
        my_ch = challenges[
            ((challenges["challenger_id"] == my_id) | (challenges["defender_id"] == my_id)) &
            (challenges["status"] == "accepted")
        ]

    if my_ch.empty:
        st.info("Sem desafios aceites para registar. Envia ou aceita um desafio primeiro.")
    else:
        ch_options = {
            f"{r['challenger_name']} vs {r['defender_name']} ({str(r['timestamp'])[:10]})": r["challenge_id"]
            for _, r in my_ch.iterrows()
        }
        sel_label = st.selectbox("Seleccionar jogo", list(ch_options.keys()), key="match_ch")
        sel_id    = ch_options[sel_label]
        sel_ch    = my_ch[my_ch["challenge_id"] == sel_id].iloc[0]

        a_id   = sel_ch["challenger_id"]
        a_name = sel_ch["challenger_name"]
        b_id   = sel_ch["defender_id"]
        b_name = sel_ch["defender_name"]

        st.markdown(f"""
        <div class="card" style="--card-accent:var(--cyan);">
          <div style="display:flex;justify-content:space-between;align-items:center;">
            <div>
              <div style="font-size:0.7rem;color:var(--text-muted);text-transform:uppercase;letter-spacing:.1em;">Desafiante</div>
              <div style="font-family:var(--font-display);font-size:1.2rem;font-weight:700;">{a_name}</div>
            </div>
            <div style="font-family:var(--font-display);font-size:1.8rem;color:var(--text-dim);">VS</div>
            <div style="text-align:right;">
              <div style="font-size:0.7rem;color:var(--text-muted);text-transform:uppercase;letter-spacing:.1em;">Defesa</div>
              <div style="font-family:var(--font-display);font-size:1.2rem;font-weight:700;">{b_name}</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        with st.form("result_form"):
            suplente = st.checkbox("⚠️ Uso de Suplente (vitória vale apenas 2 pts)")

            st.markdown("**Sets**")
            cols1 = st.columns([2,1,2])
            with cols1[0]: s1a = st.number_input(f"Set 1 — {a_name}", 0, 99, 0, key="s1a")
            with cols1[1]: st.markdown("<div style='text-align:center;padding-top:26px;color:var(--text-dim);'>–</div>", unsafe_allow_html=True)
            with cols1[2]: s1b = st.number_input(f"Set 1 — {b_name}", 0, 99, 0, key="s1b")

            cols2 = st.columns([2,1,2])
            with cols2[0]: s2a = st.number_input(f"Set 2 — {a_name}", 0, 99, 0, key="s2a")
            with cols2[1]: st.markdown("<div style='text-align:center;padding-top:26px;color:var(--text-dim);'>–</div>", unsafe_allow_html=True)
            with cols2[2]: s2b = st.number_input(f"Set 2 — {b_name}", 0, 99, 0, key="s2b")

            need_s3 = (
                (1 if s1a > s1b else 0) + (1 if s2a > s2b else 0) == 1 and
                (1 if s1b > s1a else 0) + (1 if s2b > s2a else 0) == 1
            )
            s3a = s3b = None
            if need_s3:
                cols3 = st.columns([2,1,2])
                with cols3[0]: s3a = st.number_input(f"Set 3 — {a_name}", 0, 99, 0, key="s3a")
                with cols3[1]: st.markdown("<div style='text-align:center;padding-top:26px;color:var(--text-dim);'>–</div>", unsafe_allow_html=True)
                with cols3[2]: s3b = st.number_input(f"Set 3 — {b_name}", 0, 99, 0, key="s3b")

            wo_col1, wo_col2 = st.columns(2)
            wo_a = wo_col1.form_submit_button(f"❌ W.O. {a_name}")
            wo_b = wo_col2.form_submit_button(f"❌ W.O. {b_name}")
            submitted = st.form_submit_button("✅ Submeter Resultado", width='stretch')

        if wo_a or wo_b:
            score_a = 0 if wo_a else 99
            score_b = 99 if wo_a else 0
            submit_match(
                conn, data, a_id, a_name, b_id, b_name,
                score_a, score_b, 0,0,0,0,None,None,
                suplente=False, challenge_id=sel_id, submitted_by=my_id
            )
            from data_layer import update_challenge_status
            update_challenge_status(conn, data, sel_id, "played")
            st.warning("W.O. registado. Aguarda confirmação.")
            st.rerun()

        if submitted:
            winner = determine_winner_sets(s1a, s1b, s2a, s2b, s3a, s3b)
            if winner is None:
                st.error("Resultado inválido. Verifica os sets.")
            else:
                score_a = (1 if s1a > s1b else 0) + (1 if s2a > s2b else 0)
                score_b = (1 if s1b > s1a else 0) + (1 if s2b > s2a else 0)
                if s3a: score_a += (1 if s3a > s3b else 0)
                if s3b: score_b += (1 if s3b > s3a else 0)
                mid = submit_match(
                    conn, data, a_id, a_name, b_id, b_name,
                    score_a, score_b,
                    s1a, s1b, s2a, s2b, s3a, s3b,
                    suplente=suplente, challenge_id=sel_id,
                    submitted_by=my_id
                )
                from data_layer import update_challenge_status
                update_challenge_status(conn, data, sel_id, "played")
                st.success(f"Resultado submetido! Aguarda confirmação de {b_name}.")
                st.rerun()

    # ── Timeline ──────────────────────────────────────────────────────────────
    st.markdown("---")
    section_header("Timeline de Resultados", "📋")

    if matches.empty:
        st.info("Sem resultados registados.")
        return

    confirmed = matches[matches["validation_status"].isin(["confirmed","admin_override"])]
    confirmed = confirmed.sort_values("timestamp", ascending=False)

    if confirmed.empty:
        st.info("Sem resultados confirmados ainda.")
        return

    for _, m in confirmed.head(20).iterrows():
        sa = int(m["score_a"] or 0)
        sb = int(m["score_b"] or 0)
        winner_name = m["team_a_name"] if sa > sb else m["team_b_name"]
        sup_tag = ' <span style="color:var(--orange);font-size:0.75rem;">·suplente</span>' if str(m.get("suplente_used","")).upper() == "TRUE" else ""
        date_str = str(m["timestamp"])[:10]
        st.markdown(f"""
        <div class="match-card animate-slide">
          <div style="display:flex;justify-content:space-between;align-items:flex-start;">
            <div>
              <span style="color:var(--text-muted);font-size:0.72rem;text-transform:uppercase;letter-spacing:.1em;">{date_str}</span>
              <div style="margin-top:4px;">
                <span style="font-family:var(--font-display);font-weight:700;">{m['team_a_name']}</span>
                <span class="score-big" style="padding:0 8px;color:var(--cyan);">{sa}</span>
                <span style="color:var(--text-dim);">–</span>
                <span class="score-big" style="padding:0 8px;color:var(--purple);">{sb}</span>
                <span style="font-family:var(--font-display);font-weight:700;">{m['team_b_name']}</span>
                {sup_tag}
              </div>
            </div>
            <div style="text-align:right;">
              <div style="color:var(--green);font-size:0.8rem;font-weight:600;">🏆 {winner_name}</div>
              <div style="color:var(--text-dim);font-size:0.72rem;">+{m.get('pts_winner',0)} pts</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)
