"""
page_results.py — Registar resultados em formato padel (sets/games)
"""
import streamlit as st
import pandas as pd
from data_layer import assign_categories, submit_match, update_challenge_status
from components import section_header
from config import LEVEL_COLORS


def _safe_int(val, default=0):
    try: return int(float(str(val).strip() or default))
    except: return 0


def _padel_winner(s1a, s1b, s2a, s2b, s3a=None, s3b=None):
    """Returns 'A', 'B' or None. Padel: first to 2 sets."""
    sets_a = (1 if s1a > s1b else 0) + (1 if s2a > s2b else 0)
    sets_b = (1 if s1b > s1a else 0) + (1 if s2b > s2a else 0)
    if sets_a == 2: return "A"
    if sets_b == 2: return "B"
    if s3a is not None and s3b is not None and s3a != s3b:
        return "A" if s3a > s3b else "B"
    return None


def render_results(data: dict, conn):
    my_id     = st.session_state.team_id
    teams     = data["teams"]
    ranking   = assign_categories(data["ranking"].copy())
    matches   = data["matches"]
    challenges = data["challenges"]

    # ── Submit new result ────────────────────────────────────────────────────
    section_header("Registar Resultado", "📝")

    my_ch = pd.DataFrame()
    if not challenges.empty:
        my_ch = challenges[
            ((challenges["challenger_id"] == my_id) | (challenges["defender_id"] == my_id)) &
            (challenges["status"] == "accepted")
        ]

    if my_ch.empty:
        st.info("Sem desafios aceites. Envia ou aceita um desafio primeiro.")
    else:
        ch_opts = {
            f"{r['challenger_name']} vs {r['defender_name']} ({str(r['timestamp'])[:10]})": r["challenge_id"]
            for _, r in my_ch.iterrows()
        }
        sel_label = st.selectbox("Seleccionar jogo", list(ch_opts.keys()), key="match_ch")
        sel_id    = ch_opts[sel_label]
        sel_ch    = my_ch[my_ch["challenge_id"] == sel_id].iloc[0]

        a_id, a_name = sel_ch["challenger_id"], sel_ch["challenger_name"]
        b_id, b_name = sel_ch["defender_id"],   sel_ch["defender_name"]

        st.markdown(f"""
        <div style="background:linear-gradient(90deg,#0E1A2A,#0A1520);
             border:1px solid rgba(0,229,255,0.2);border-radius:14px;padding:16px 20px;margin-bottom:16px;">
          <div style="display:flex;justify-content:space-between;align-items:center;">
            <div>
              <div style="font-size:.7rem;color:#00E5FF;letter-spacing:.15em;text-transform:uppercase;">⚔️ Desafiante</div>
              <div style="font-family:\'Barlow Condensed\',sans-serif;font-size:1.4rem;font-weight:800;color:#fff;">{a_name}</div>
            </div>
            <div style="font-size:2rem;color:#30363d;font-weight:900;">VS</div>
            <div style="text-align:right;">
              <div style="font-size:.7rem;color:#CE93D8;letter-spacing:.15em;text-transform:uppercase;">🛡️ Defesa</div>
              <div style="font-family:\'Barlow Condensed\',sans-serif;font-size:1.4rem;font-weight:800;color:#fff;">{b_name}</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        suplente = st.checkbox("⚠️ Uso de Suplente (vitória vale apenas 2 pts)")

        st.markdown("##### 🎾 Resultado por sets")

        # Set 1
        st.markdown(f"**Set 1**")
        c1, c2, c3 = st.columns([2, 1, 2])
        with c1: s1a = st.number_input(f"{a_name}", 0, 99, 0, key="s1a", label_visibility="visible")
        with c2: st.markdown("<div style='text-align:center;padding-top:28px;color:#30363d;font-weight:900;'>—</div>", unsafe_allow_html=True)
        with c3: s1b = st.number_input(f"{b_name}", 0, 99, 0, key="s1b", label_visibility="visible")

        # Set 2
        st.markdown(f"**Set 2**")
        c1, c2, c3 = st.columns([2, 1, 2])
        with c1: s2a = st.number_input(f"{a_name} ", 0, 99, 0, key="s2a", label_visibility="visible")
        with c2: st.markdown("<div style='text-align:center;padding-top:28px;color:#30363d;font-weight:900;'>—</div>", unsafe_allow_html=True)
        with c3: s2b = st.number_input(f"{b_name} ", 0, 99, 0, key="s2b", label_visibility="visible")

        # Check if set 3 needed
        sets_a = (1 if s1a > s1b else 0) + (1 if s2a > s2b else 0)
        sets_b = (1 if s1b > s1a else 0) + (1 if s2b > s2a else 0)
        need_s3 = (sets_a == 1 and sets_b == 1)
        s3a = s3b = None

        if need_s3:
            st.markdown("**Set 3 (decisivo)**")
            c1, c2, c3 = st.columns([2, 1, 2])
            with c1: s3a = st.number_input(f"{a_name}  ", 0, 99, 0, key="s3a", label_visibility="visible")
            with c2: st.markdown("<div style='text-align:center;padding-top:28px;color:#30363d;font-weight:900;'>—</div>", unsafe_allow_html=True)
            with c3: s3b = st.number_input(f"{b_name}  ", 0, 99, 0, key="s3b", label_visibility="visible")

        # Preview score string
        if s1a or s1b or s2a or s2b:
            score_str = f"{s1a}-{s1b}; {s2a}-{s2b}"
            if s3a is not None: score_str += f"; {s3a}-{s3b}"
            winner = _padel_winner(s1a, s1b, s2a, s2b, s3a, s3b)
            wname  = a_name if winner == "A" else (b_name if winner == "B" else "?")
            role   = "Desafiante" if winner == "A" else ("Defesa" if winner == "B" else "")
            clr    = "#3fb950" if winner else "#f85149"
            st.markdown(f"""
            <div style="background:#0d1117;border:1px solid #30363d;border-radius:10px;
                 padding:12px 16px;margin:8px 0;font-family:\'Barlow Condensed\',sans-serif;">
              <span style="font-size:1.3rem;font-weight:800;color:#fff;">{score_str}</span>
              &nbsp;&nbsp;
              <span style="color:{clr};font-weight:700;">
                {'🏆 ' + wname + ' (' + role + ')' if winner else '⏳ incompleto'}
              </span>
            </div>
            """, unsafe_allow_html=True)

        # W.O. buttons
        st.markdown("---")
        wo1, wo2 = st.columns(2)
        with wo1:
            if st.button(f"❌ W.O. de {a_name}", key="wo_a"):
                _submit(conn, data, a_id, a_name, b_id, b_name,
                        0, 0, 0, 0, 0, 0, None, None, False, sel_id, my_id, wo="A")
                return
        with wo2:
            if st.button(f"❌ W.O. de {b_name}", key="wo_b"):
                _submit(conn, data, a_id, a_name, b_id, b_name,
                        0, 0, 0, 0, 0, 0, None, None, False, sel_id, my_id, wo="B")
                return

        if st.button("✅ Submeter Resultado", key="submit_res"):
            winner = _padel_winner(s1a, s1b, s2a, s2b, s3a, s3b)
            if winner is None:
                st.error("Resultado inválido — completa todos os sets necessários.")
            else:
                _submit(conn, data, a_id, a_name, b_id, b_name,
                        s1a, s1b, s2a, s2b, s3a or 0, s3b or 0,
                        s3a, s3b, suplente, sel_id, my_id)

    # ── Timeline ─────────────────────────────────────────────────────────────
    st.markdown("---")
    section_header("Histórico de Resultados", "📋")

    if matches.empty:
        st.info("Sem resultados registados.")
        return

    confirmed = matches[matches["validation_status"].isin(["confirmed","admin_override"])]
    confirmed = confirmed.sort_values("timestamp", ascending=False)

    if confirmed.empty:
        st.info("Sem resultados confirmados.")
        return

    for _, m in confirmed.head(25).iterrows():
        sa = _safe_int(m.get("score_a", 0))
        sb = _safe_int(m.get("score_b", 0))
        s1a_ = str(m.get("set1_a","")).strip()
        s1b_ = str(m.get("set1_b","")).strip()
        s2a_ = str(m.get("set2_a","")).strip()
        s2b_ = str(m.get("set2_b","")).strip()
        s3a_ = str(m.get("set3_a","")).strip()
        s3b_ = str(m.get("set3_b","")).strip()

        sets_str = ""
        for ga, gb in [(s1a_,s1b_),(s2a_,s2b_)]:
            if ga and gb and ga not in ("0","nan","") and gb not in ("0","nan",""):
                sets_str += f"  {ga}–{gb}"
        if s3a_ and s3b_ and s3a_ not in ("0","nan","") and s3b_ not in ("0","nan",""):
            sets_str += f"  {s3a_}–{s3b_}"

        winner_id  = str(m.get("winner_id",""))
        winner_name = str(m["team_a_name"] if winner_id == m["team_a_id"] else m["team_b_name"])
        loser_name  = str(m["team_b_name"] if winner_id == m["team_a_id"] else m["team_a_name"])
        role_w = "Desafiante" if winner_id == m["team_a_id"] else "Defesa"
        date_str = str(m["timestamp"])[:10]
        pts = str(m.get("pts_winner",""))
        sup_tag = " 🔄suplente" if str(m.get("suplente_used","")).upper()=="TRUE" else ""

        st.markdown(f"""
        <div style="background:#0d1117;border:1px solid #21262d;border-left:3px solid #3fb950;
             border-radius:10px;padding:12px 16px;margin-bottom:8px;">
          <div style="display:flex;justify-content:space-between;align-items:flex-start;">
            <div>
              <div style="color:#8b949e;font-size:.72rem;text-transform:uppercase;letter-spacing:.08em;">{date_str}</div>
              <div style="font-family:\'Barlow Condensed\',sans-serif;font-size:1.1rem;font-weight:700;color:#fff;margin-top:2px;">
                ⚔️ {m['team_a_name']} <span style="color:#30363d;">vs</span> {m['team_b_name']}
              </div>
              <div style="font-size:.85rem;color:#27C878;margin-top:4px;font-weight:700;">{sets_str}{sup_tag}</div>
            </div>
            <div style="text-align:right;">
              <div style="color:#3fb950;font-size:.8rem;font-weight:700;">🏆 {winner_name}</div>
              <div style="color:#8b949e;font-size:.72rem;">{role_w} · +{pts}pts</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)


def _submit(conn, data, a_id, a_name, b_id, b_name,
            s1a, s1b, s2a, s2b, s3a, s3b, s3a_raw, s3b_raw,
            suplente, challenge_id, submitted_by, wo=None):
    from logic import calc_points
    if wo == "A":
        score_a, score_b = 0, 2
        winner_id, loser_id = b_id, a_id
        pts_w, pts_l = calc_points(is_challenger=False, suplente=False)
    elif wo == "B":
        score_a, score_b = 2, 0
        winner_id, loser_id = a_id, b_id
        pts_w, pts_l = calc_points(is_challenger=True, suplente=False)
    else:
        score_a = (1 if s1a>s1b else 0)+(1 if s2a>s2b else 0)+(1 if (s3a or 0)>(s3b or 0) and s3a_raw else 0)
        score_b = (1 if s1b>s1a else 0)+(1 if s2b>s2a else 0)+(1 if (s3b or 0)>(s3a or 0) and s3b_raw else 0)
        winner_id = a_id if score_a > score_b else b_id
        loser_id  = b_id if score_a > score_b else a_id
        pts_w, pts_l = calc_points(is_challenger=(winner_id==a_id), suplente=suplente)

    submit_match(conn, data, a_id, a_name, b_id, b_name,
                 score_a, score_b, s1a, s1b, s2a, s2b,
                 s3a_raw, s3b_raw, suplente, challenge_id, submitted_by)
    update_challenge_status(conn, data, challenge_id, "played")
    st.success(f"✅ Resultado submetido! Aguarda confirmação.")
    st.rerun()
