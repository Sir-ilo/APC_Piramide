"""
page_challenges.py  —  Tab 3: Send, receive, confirm, contest challenges.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timezone
from data_layer import (
    assign_categories, create_challenge, update_challenge_status,
    confirm_match, contest_match, use_trunfo, apply_escudo,
)
from logic import can_challenge, is_immune, guardian_remaining
from components import section_header
from config import LEVEL_COLORS, CHALLENGE_WINDOW


def render_challenges(data: dict, conn):
    my_id   = st.session_state.team_id
    ranking = assign_categories(data["ranking"].copy())
    teams   = data["teams"]
    challenges = data["challenges"]
    matches    = data["matches"]
    trunfos    = data["trunfos"]

    # ── Pending result confirmations (priority alert) ──────────────────────────
    if not matches.empty:
        pend_m = matches[
            (matches["team_b_id"] == my_id) &
            (matches["validation_status"] == "pending")
        ]
        if not pend_m.empty:
            st.markdown(
                '<div style="background:rgba(255,152,0,0.1);border:1px solid rgba(255,152,0,0.4);'
                'border-radius:12px;padding:14px 18px;margin-bottom:16px;">'
                f'⚠️ <strong>{len(pend_m)} resultado(s) aguarda(m) confirmação tua!</strong>'
                '</div>',
                unsafe_allow_html=True,
            )
            for _, m in pend_m.iterrows():
                sa = int(m["score_a"] or 0)
                sb = int(m["score_b"] or 0)
                st.markdown(f"""
                <div class="challenge-card incoming">
                  <strong>Resultado submetido por {m['team_a_name']}</strong><br>
                  <span style="color:var(--text-muted);font-size:0.85rem;">{m['team_a_name']} {sa} – {sb} {m['team_b_name']}</span>
                </div>
                """, unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                with c1:
                    if st.button(f"✅ Confirmar", key=f"conf_{m['match_id']}",
                                 width='stretch'):
                        if confirm_match(conn, data, m["match_id"], my_id):
                            st.success("Resultado confirmado! Ranking actualizado.")
                            st.balloons()
                            st.rerun()
                with c2:
                    if st.button(f"❌ Contestar", key=f"cont_{m['match_id']}",
                                 width='stretch'):
                        contest_match(conn, data, m["match_id"])
                        st.warning("Resultado contestado. Admin será notificado.")
                        st.rerun()
            st.markdown("---")

    # ── Send new challenge ────────────────────────────────────────────────────
    section_header("Enviar Desafio", "⚔️")

    my_row = ranking[ranking["team_id"] == my_id]
    if my_row.empty:
        st.warning("A tua equipa não está no ranking.")
        return

    my_r   = my_row.iloc[0]
    my_pos = int(my_r["position"])
    my_cat = str(my_r["category"])

    # My trunfos
    my_tr  = trunfos[trunfos["team_id"] == my_id]
    salto_qty = int(my_tr["salto_qty"].values[0]) if not my_tr.empty else 0
    escudo_qty= int(my_tr["escudo_qty"].values[0]) if not my_tr.empty else 0
    last_month= str(my_tr["last_trunfo_month"].values[0]) if not my_tr.empty else ""
    this_month= datetime.now(timezone.utc).strftime("%Y-%m")
    can_trunfo = (last_month != this_month)

    # Guardian info
    rem = guardian_remaining(my_r.to_dict())
    if rem:
        from logic import format_guardian_timer
        st.markdown(
            f'<div style="background:rgba(255,152,0,0.08);border:1px solid rgba(255,152,0,0.3);'
            f'border-radius:12px;padding:14px;margin-bottom:12px;">'
            f'⏳ <strong>Modo Guardião activo</strong> — '
            f'<span class="guardian-timer">{format_guardian_timer(rem)}</span> restantes<br>'
            f'<span style="color:var(--text-muted);font-size:0.82rem;">'
            f'Deves defender a posição antes de subir de nível.</span></div>',
            unsafe_allow_html=True,
        )

    # Eligible targets
    use_salto = st.checkbox(
        f"🦅 Usar Salto de Fé (tenho {salto_qty}x)",
        disabled=(salto_qty == 0 or not can_trunfo),
        key="use_salto_cb"
    )
    window = 99 if use_salto else CHALLENGE_WINDOW

    # Filter teams above within window
    eligible = ranking[
        (ranking["position"] < my_pos) &
        (ranking["position"] >= my_pos - window) &
        (ranking["team_id"] != my_id)
    ]

    if eligible.empty:
        st.info("Sem adversários elegíveis no teu alcance.")
    else:
        options = {
            f"#{int(r['position'])} — {r['team_name']} ({r['category']}) · {int(r['points'] or 0)} pts": r["team_id"]
            for _, r in eligible.iterrows()
        }
        chosen_label = st.selectbox("Seleccionar adversário", list(options.keys()), key="ch_target")
        chosen_id    = options[chosen_label]
        chosen_row   = eligible[eligible["team_id"] == chosen_id].iloc[0]

        ok, reason = can_challenge(my_r.to_dict(), chosen_row.to_dict(), use_salto)
        if not ok:
            st.error(reason)
        else:
            if st.button("⚔️ Enviar Desafio", key="send_ch", width='stretch'):
                trunfo_used = "salto" if use_salto else ""
                if use_salto:
                    if not use_trunfo(conn, data, my_id, "salto"):
                        st.error("Não foi possível usar o Salto de Fé.")
                        return
                create_challenge(
                    conn, data, my_id, my_r["team_name"],
                    chosen_id, chosen_row["team_name"], trunfo_used
                )
                st.success(f"Desafio enviado para {chosen_row['team_name']}! ⚔️")
                st.rerun()

    # ── Trunfo — Escudo ───────────────────────────────────────────────────────
    st.markdown("---")
    section_header("Trunfos", "🃏")
    if not can_trunfo:
        st.info("⏳ Já usaste um trunfo este mês.")
    else:
        if escudo_qty > 0:
            if st.button(f"🛡️ Activar Escudo de Platina ({escudo_qty}x) — 10 dias imunidade",
                         key="use_escudo"):
                if use_trunfo(conn, data, my_id, "escudo"):
                    apply_escudo(conn, data, my_id)
                    st.success("🛡️ Escudo activado! Imune por 10 dias.")
                    st.rerun()
        else:
            st.markdown(
                '<div class="card" style="opacity:.5;">🛡️ Sem Escudos disponíveis</div>',
                unsafe_allow_html=True,
            )

    # ── Outgoing challenges ───────────────────────────────────────────────────
    st.markdown("---")
    section_header("Desafios Enviados", "📤")
    if not challenges.empty:
        out = challenges[challenges["challenger_id"] == my_id].sort_values(
            "timestamp", ascending=False
        ).head(10)
        if out.empty:
            st.markdown(
                '<div class="card"><span style="color:var(--text-muted);">Sem desafios enviados.</span></div>',
                unsafe_allow_html=True,
            )
        else:
            for _, c in out.iterrows():
                status_map = {
                    "pending": ("🟡", "Pendente"),
                    "accepted": ("🟢", "Aceite"),
                    "rejected": ("🔴", "Recusado"),
                    "played": ("✅", "Jogado"),
                    "cancelled": ("⚫", "Cancelado"),
                }
                ico, lbl = status_map.get(c["status"], ("⚪", c["status"]))
                ts = str(c["timestamp"])[:10]
                st.markdown(f"""
                <div class="challenge-card outgoing">
                  <strong>{ico} vs {c['defender_name']}</strong>
                  <span style="float:right;color:var(--text-muted);font-size:0.8rem;">{ts}</span><br>
                  <span style="color:var(--text-muted);font-size:0.82rem;">{lbl}
                  {' · 🦅 Salto' if c['trunfo_used'] == 'salto' else ''}
                  </span>
                </div>
                """, unsafe_allow_html=True)
                if c["status"] == "pending":
                    if st.button("Cancelar", key=f"cancel_{c['challenge_id']}"):
                        update_challenge_status(conn, data, c["challenge_id"], "cancelled")
                        st.rerun()
    else:
        st.markdown(
            '<div class="card"><span style="color:var(--text-muted);">Sem desafios.</span></div>',
            unsafe_allow_html=True,
        )

    # ── Incoming challenges ───────────────────────────────────────────────────
    section_header("Desafios Recebidos", "📥")
    if not challenges.empty:
        inc = challenges[
            (challenges["defender_id"] == my_id) &
            (challenges["status"] == "pending")
        ].sort_values("timestamp", ascending=False)
        if inc.empty:
            st.markdown(
                '<div class="card"><span style="color:var(--text-muted);">Sem desafios recebidos.</span></div>',
                unsafe_allow_html=True,
            )
        else:
            for _, c in inc.iterrows():
                st.markdown(f"""
                <div class="challenge-card incoming">
                  <strong>⚔️ Desafio de {c['challenger_name']}</strong><br>
                  <span style="color:var(--text-muted);font-size:0.82rem;">{str(c['timestamp'])[:10]}</span>
                </div>
                """, unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("✅ Aceitar", key=f"acc_{c['challenge_id']}",
                                 width='stretch'):
                        update_challenge_status(conn, data, c["challenge_id"], "accepted")
                        st.rerun()
                with c2:
                    if st.button("❌ Recusar", key=f"rej_{c['challenge_id']}",
                                 width='stretch'):
                        update_challenge_status(conn, data, c["challenge_id"], "rejected")
                        st.rerun()
    else:
        st.markdown(
            '<div class="card"><span style="color:var(--text-muted);">Sem desafios.</span></div>',
            unsafe_allow_html=True,
        )
