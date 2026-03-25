"""
page_team_detail.py
Ecrã de detalhe de uma equipa — histórico, estatísticas, trunfos, streak.
Acessível ao clicar em qualquer cartão de equipa.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timezone
from data_layer import assign_categories, create_challenge, use_trunfo
from logic import (
    can_challenge, can_challenge_level_up, is_immune,
    guardian_remaining, format_guardian_timer, CHALLENGE_WINDOW
)
from config import LEVEL_COLORS, CHALLENGE_WINDOW


def _safe_int(val, default=0):
    try:
        return int(float(str(val).strip() or default))
    except (ValueError, TypeError):
        return default


def render_team_detail(data: dict, conn, target_id: str):
    """Full-screen team detail. Call from any page after setting
    st.session_state.view_team_id."""

    teams   = data["teams"]
    ranking = assign_categories(data["ranking"].copy())
    matches = data["matches"]
    trunfos = data["trunfos"]
    my_id   = st.session_state.team_id

    t_row = teams[teams["team_id"] == target_id]
    r_row = ranking[ranking["team_id"] == target_id]

    if t_row.empty or r_row.empty:
        st.error("Equipa não encontrada.")
        if st.button("← Voltar"):
            st.session_state.pop("view_team_id", None)
            st.rerun()
        return

    t = t_row.iloc[0]
    r = r_row.iloc[0]

    cat   = str(r["category"])
    color = LEVEL_COLORS.get(cat, "#aaa")
    pos   = _safe_int(r["position"])
    pts   = _safe_int(r["points"])
    wins  = _safe_int(t.get("wins", 0))
    losses= _safe_int(t.get("losses", 0))
    streak= _safe_int(t.get("streak", 0))
    total = _safe_int(t.get("total_matches", 0))
    photo = str(t.get("photo_url", "") or "")
    is_me = (target_id == my_id)

    # ── Back button ───────────────────────────────────────────────────────────
    if st.button("← Voltar", key="team_detail_back"):
        st.session_state.pop("view_team_id", None)
        st.rerun()

    # ── Hero card ─────────────────────────────────────────────────────────────
    avatar = (
        f'<img src="{photo}" style="width:80px;height:80px;border-radius:50%;"'
        f' class="profile-avatar" />'
        if photo else
        f'<div style="width:80px;height:80px;border-radius:50%;background:var(--bg3);'
        f'display:flex;align-items:center;justify-content:center;font-size:2.2rem;'
        f'border:2px solid {color};box-shadow:0 0 18px {color}55;">🎾</div>'
    )

    # Guardian / immune status
    status_html = ""
    rem = guardian_remaining(r.to_dict())
    if rem:
        status_html = (f'<div style="color:var(--orange);font-size:0.82rem;margin-top:6px;">'
                       f'⏳ Guardião: {format_guardian_timer(rem)}</div>')
    elif is_immune(r.to_dict()):
        status_html = '<div style="color:var(--cyan);font-size:0.82rem;margin-top:6px;">🛡️ Imune</div>'

    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#0E1A2A,#0A1520);
         border:1px solid {color}44;border-radius:18px;padding:24px;margin-bottom:16px;
         box-shadow:0 0 40px {color}11;">
      <div style="display:flex;align-items:center;gap:20px;margin-bottom:16px;">
        {avatar}
        <div>
          <div style="font-family:var(--font-display,monospace);font-size:1.8rem;
               font-weight:800;color:{color};text-shadow:0 0 20px {color}88;">
            {t['team_name']}
          </div>
          <div style="color:var(--text-muted);font-size:0.88rem;margin-top:2px;">
            {t.get('player1','')} &amp; {t.get('player2','')}
          </div>
          <div style="display:flex;gap:8px;margin-top:8px;align-items:center;">
            <span style="background:{color}22;border:1px solid {color}55;color:{color};
              border-radius:99px;padding:2px 12px;font-size:0.72rem;font-weight:700;">
              {cat}
            </span>
            <span style="color:var(--text-muted);font-size:0.82rem;">#{pos} global</span>
          </div>
          {status_html}
        </div>
      </div>
      <div style="display:flex;gap:10px;flex-wrap:wrap;">
        <div class="stat-chip">Pts <span class="val" style="color:{color};">{pts}</span></div>
        <div class="stat-chip">V <span class="val" style="color:#3fb950;">{wins}</span></div>
        <div class="stat-chip">D <span class="val" style="color:#f85149;">{losses}</span></div>
        <div class="stat-chip">Jogos <span class="val">{total}</span></div>
        <div class="stat-chip">🔥 Streak <span class="val" style="color:var(--orange);">{streak}</span></div>
        <div class="stat-chip">W% <span class="val">{round(wins/total*100) if total>0 else 0}%</span></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Trunfos ───────────────────────────────────────────────────────────────
    st.markdown("### 🃏 Trunfos")
    tr_row = trunfos[trunfos["team_id"] == target_id]
    if not tr_row.empty:
        tr = tr_row.iloc[0]
        d_qty = _safe_int(tr.get("desforra_qty", 0))
        s_qty = _safe_int(tr.get("salto_qty", 0))
        e_qty = _safe_int(tr.get("escudo_qty", 0))
    else:
        d_qty = s_qty = e_qty = 0

    tc1, tc2, tc3 = st.columns(3)
    for col, icon, name, qty, clr in [
        (tc1, "🔄", "Desforra",       d_qty, "#CE93D8"),
        (tc2, "🦅", "Salto de Fé",    s_qty, "#00E5FF"),
        (tc3, "🛡️", "Escudo Platina", e_qty, "#FFD700"),
    ]:
        with col:
            if qty > 0:
                st.markdown(f"""
                <div class="trunfo-card" style="border-color:{clr}44;">
                  <div class="trunfo-icon">{icon}</div>
                  <div class="trunfo-name" style="color:{clr};">{name}</div>
                  <div class="trunfo-qty" style="color:{clr};">{qty}×</div>
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="trunfo-card" style="opacity:0.35;border-color:#333;">
                  <div class="trunfo-icon" style="filter:grayscale(1);">🈳</div>
                  <div class="trunfo-name" style="color:var(--text-dim);">{name}</div>
                  <div class="trunfo-qty" style="color:var(--text-dim);">0×</div>
                </div>""", unsafe_allow_html=True)

    # ── Challenge button (if not my team) ─────────────────────────────────────
    if not is_me:
        st.markdown("---")
        st.markdown("### ⚔️ Desafiar")

        my_r_row = ranking[ranking["team_id"] == my_id]
        if my_r_row.empty:
            st.warning("A tua equipa não está no ranking.")
        else:
            my_r = my_r_row.iloc[0]
            ok, reason = can_challenge(my_r.to_dict(), r.to_dict())

            # Check salto trunfo availability
            my_tr = trunfos[trunfos["team_id"] == my_id]
            salto_qty  = _safe_int(my_tr["salto_qty"].values[0]) if not my_tr.empty else 0
            last_month = str(my_tr["last_trunfo_month"].values[0]) if not my_tr.empty else ""
            this_month = datetime.now(timezone.utc).strftime("%Y-%m")
            can_trunfo = (last_month != this_month)

            if not ok:
                # Maybe ok with Salto de Fé?
                ok_salto, _ = can_challenge(my_r.to_dict(), r.to_dict(), use_salto=True)
                if ok_salto and salto_qty > 0 and can_trunfo:
                    st.info(f"⚠️ {reason}")
                    if st.button(f"🦅 Desafiar com Salto de Fé ({salto_qty}×)",
                                 key="detail_ch_salto"):
                        if use_trunfo(conn, data, my_id, "salto"):
                            cid = create_challenge(
                                conn, data, my_id,
                                str(my_r["team_name"]),
                                target_id, str(r["team_name"]),
                                trunfo="salto"
                            )
                            st.success(f"🦅 Desafio com Salto de Fé enviado para {r['team_name']}!")
                            st.session_state.pop("view_team_id", None)
                            st.rerun()
                else:
                    st.warning(f"🚫 {reason}")
            else:
                col_ch, col_salto = st.columns(2)
                with col_ch:
                    if st.button(f"⚔️ Enviar Desafio a {r['team_name']}",
                                 key="detail_ch_normal"):
                        create_challenge(
                            conn, data, my_id,
                            str(my_r["team_name"]),
                            target_id, str(r["team_name"])
                        )
                        st.success(f"Desafio enviado para {r['team_name']}! ⚔️")
                        st.session_state.pop("view_team_id", None)
                        st.rerun()
                with col_salto:
                    if salto_qty > 0 and can_trunfo:
                        if st.button(f"🦅 Desafiar c/ Salto de Fé",
                                     key="detail_ch_salto2"):
                            if use_trunfo(conn, data, my_id, "salto"):
                                create_challenge(
                                    conn, data, my_id,
                                    str(my_r["team_name"]),
                                    target_id, str(r["team_name"]),
                                    trunfo="salto"
                                )
                                st.success("🦅 Desafio com Salto de Fé enviado!")
                                st.session_state.pop("view_team_id", None)
                                st.rerun()

    # ── Match history ─────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 📜 Histórico de Jogos")

    if matches.empty:
        st.info("Sem jogos registados.")
        return

    my_matches = matches[
        ((matches["team_a_id"] == target_id) | (matches["team_b_id"] == target_id)) &
        (matches["validation_status"].isin(["confirmed", "admin_override"]))
    ].copy()

    if my_matches.empty:
        st.info("Esta equipa ainda não tem jogos confirmados.")
        return

    my_matches["ts"] = pd.to_datetime(my_matches["timestamp"], errors="coerce", utc=True)
    my_matches = my_matches.sort_values("ts", ascending=False)

    for _, m in my_matches.iterrows():
        sa = _safe_int(m.get("score_a", 0))
        sb = _safe_int(m.get("score_b", 0))
        date_str = str(m["timestamp"])[:10]
        winner_id = str(m.get("winner_id", ""))
        won = (winner_id == target_id)
        role = "Desafiante" if m["team_a_id"] == target_id else "Defesa"
        result_color = "#3fb950" if won else "#f85149"
        result_label = "VITÓRIA" if won else "DERROTA"

        # Sets
        sets_html = ""
        for si in [("set1_a","set1_b"),("set2_a","set2_b"),("set3_a","set3_b")]:
            va = str(m.get(si[0], "")).strip()
            vb = str(m.get(si[1], "")).strip()
            if va and vb and va not in ("", "nan") and vb not in ("", "nan"):
                sets_html += f'<span style="color:var(--text-muted);font-size:0.78rem;margin-right:6px;">{va}–{vb}</span>'

        opp_name = str(m["team_b_name"] if m["team_a_id"] == target_id else m["team_a_name"])
        pts_earned = str(m.get("pts_winner" if won else "pts_loser", ""))

        st.markdown(f"""
        <div class="match-card" style="border-left:3px solid {result_color};
             background:linear-gradient(90deg,{result_color}08,var(--card));">
          <div style="display:flex;justify-content:space-between;align-items:center;">
            <div>
              <span style="color:{result_color};font-weight:700;font-size:0.82rem;">
                {result_label}
              </span>
              <span style="color:var(--text-muted);font-size:0.78rem;margin-left:8px;">
                {role}
              </span>
              <div style="font-family:var(--font-display,monospace);font-size:1.05rem;
                   font-weight:700;margin-top:2px;">
                vs {opp_name}
              </div>
              <div style="margin-top:4px;">{sets_html}</div>
            </div>
            <div style="text-align:right;">
              <div style="color:var(--text-muted);font-size:0.75rem;">{date_str}</div>
              <div style="color:{result_color};font-size:0.85rem;font-weight:600;margin-top:4px;">
                {'+' if won else ''}{pts_earned} pts
              </div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)
