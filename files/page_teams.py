"""
page_teams.py  —  Tab 4: My team profile + list of other teams.
"""

import streamlit as st
import pandas as pd
from data_layer import assign_categories, save_teams, submit_edit_request
from logic import is_immune, guardian_remaining, format_guardian_timer
from components import section_header, build_rows_data, render_expandable_cards
from config import LEVEL_COLORS


def _safe_int(val, default=0):
    try:
        return int(float(str(val).strip() or default))
    except (ValueError, TypeError):
        return default


def render_teams(data: dict, conn):
    my_id   = st.session_state.team_id
    ranking = assign_categories(data["ranking"].copy())
    teams   = data["teams"]
    trunfos = data["trunfos"]

    # Trunfos lookup
    tr_map = {}
    if not trunfos.empty:
        for _, tr in trunfos.iterrows():
            tr_map[str(tr["team_id"])] = tr.to_dict()

    my_team = teams[teams["team_id"] == my_id]
    my_rank = ranking[ranking["team_id"] == my_id]

    # ── My Profile Card ───────────────────────────────────────────────────────
    section_header("Minha Equipa", "👤")

    if my_team.empty:
        st.warning("Equipa não encontrada.")
    else:
        t = my_team.iloc[0]
        r = my_rank.iloc[0] if not my_rank.empty else None
        cat   = str(r["category"]) if r is not None else "—"
        color = LEVEL_COLORS.get(cat, "#aaa")
        pos   = _safe_int(r["position"] if r is not None else 0)
        pts   = _safe_int(r["points"]   if r is not None else 0)
        photo = str(t.get("photo_url","") or "")
        wins  = _safe_int(t.get("wins",   0))
        losses= _safe_int(t.get("losses", 0))
        streak= _safe_int(t.get("streak", 0))
        total = _safe_int(t.get("total_matches", 0))

        guard_html = ""
        if r is not None:
            rem = guardian_remaining(r.to_dict())
            if rem:
                guard_html = (f'<div style="margin-top:8px;color:var(--orange);font-size:0.82rem;">'
                              f'⏳ Guardião: {format_guardian_timer(rem)}</div>')
            elif is_immune(r.to_dict()):
                guard_html = ('<div style="margin-top:8px;color:var(--cyan);font-size:0.82rem;">'
                              '🛡️ Imune</div>')

        avatar = (
            f'<img src="{photo}" class="profile-avatar" style="border-color:{color};">'
            if photo else
            f'<div class="profile-avatar" style="border-color:{color};'
            f'box-shadow:0 0 20px {color}55;">🎾</div>'
        )

        st.markdown(f"""
        <div class="profile-card animate-slide">
          <div style="display:flex;align-items:center;gap:16px;margin-bottom:14px;">
            {avatar}
            <div style="flex:1;">
              <div class="profile-name">{t['team_name']}</div>
              <div style="color:var(--text-muted);font-size:0.82rem;margin-top:2px;">
                {t.get('player1','')}{' &amp; ' + str(t.get('player2','')) if t.get('player2') else ''}
              </div>
              {guard_html}
            </div>
          </div>
          <div style="display:flex;gap:10px;flex-wrap:wrap;">
            <div class="stat-chip">Pos <span class="val">#{pos}</span></div>
            <div class="stat-chip">Nível <span class="val" style="color:{color};">{cat}</span></div>
            <div class="stat-chip">Pts <span class="val">{pts}</span></div>
            <div class="stat-chip">V <span class="val" style="color:#3fb950;">{wins}</span></div>
            <div class="stat-chip">D <span class="val" style="color:#f85149;">{losses}</span></div>
            <div class="stat-chip">🔥 <span class="val">{streak}</span></div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("📋 Ver Histórico Completo", key="my_history_btn"):
            st.session_state["view_team_id"] = my_id
            st.rerun()

        # ── Trunfos inventory ─────────────────────────────────────────────────
        my_tr = trunfos[trunfos["team_id"] == my_id]
        if not my_tr.empty:
            tr = my_tr.iloc[0]
            d_qty = _safe_int(tr.get("desforra_qty", 0))
            s_qty = _safe_int(tr.get("salto_qty",    0))
            e_qty = _safe_int(tr.get("escudo_qty",   0))
            t1, t2, t3 = st.columns(3)
            for col, icon, name, qty, clr in [
                (t1, "🔄", "Desforra",       d_qty, "var(--purple)"),
                (t2, "🦅", "Salto de Fé",    s_qty, "var(--cyan)"),
                (t3, "🛡️", "Escudo Platina", e_qty, "var(--gold)"),
            ]:
                with col:
                    if qty > 0:
                        st.markdown(f"""
                        <div class="trunfo-card">
                          <div class="trunfo-icon">{icon}</div>
                          <div class="trunfo-name">{name}</div>
                          <div class="trunfo-qty" style="color:{clr};">{qty}×</div>
                        </div>""", unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class="trunfo-card" style="opacity:0.35;">
                          <div class="trunfo-icon" style="filter:grayscale(1);">🈳</div>
                          <div class="trunfo-name" style="color:var(--text-dim);">{name}</div>
                          <div class="trunfo-qty" style="color:var(--text-dim);">0×</div>
                        </div>""", unsafe_allow_html=True)

        # ── Photo upload ──────────────────────────────────────────────────────
        st.markdown("---")
        section_header("Actualizar Foto", "📷")
        uploaded = st.file_uploader("Carregar foto de perfil",
                                     type=["png","jpg","jpeg"], key="photo_upload")
        if uploaded:
            import base64
            b64      = base64.b64encode(uploaded.read()).decode()
            data_url = f"data:{uploaded.type};base64,{b64}"
            teams_upd = teams.copy()
            teams_upd.loc[teams_upd["team_id"] == my_id, "photo_url"] = data_url
            save_teams(conn, teams_upd)
            st.success("Foto actualizada!")
            st.rerun()

        # ── Edit request ──────────────────────────────────────────────────────
        st.markdown("---")
        section_header("Editar Perfil (Pendente Aprovação)", "✏️")
        with st.expander("Pedir alteração de nome / jogadores"):
            field = st.selectbox("Campo", ["team_name","player1","player2"],
                                  key="edit_field")
            old_v = str(t.get(field, ""))
            new_v = st.text_input("Novo valor", value=old_v, key="edit_val")
            if st.button("Enviar Pedido de Alteração", key="submit_edit"):
                if new_v and new_v != old_v:
                    submit_edit_request(conn, data, my_id, field, old_v, new_v)
                    st.success("Pedido enviado. Aguarda aprovação do Admin.")

    # ── Other teams ───────────────────────────────────────────────────────────
    st.markdown("---")
    section_header("Todas as Equipas", "🏆")
    search = st.text_input("🔍 Pesquisar", placeholder="Nome da equipa...",
                            key="team_search")

    ranking_full = ranking.merge(
        teams[["team_id","player1","player2","photo_url","streak","wins","losses"]],
        on="team_id", how="left"
    )
    for col in ["player1","player2","photo_url"]:
        ranking_full[col] = ranking_full[col].fillna("")

    if search:
        ranking_full = ranking_full[
            ranking_full["team_name"].str.contains(search, case=False, na=False)
        ]

    other_teams = ranking_full[ranking_full["team_id"] != my_id]
    matches_df = data.get("matches", pd.DataFrame())
    rows_data = build_rows_data(other_teams, teams, trunfos, matches_df, my_id)
    render_expandable_cards(rows_data, my_id, conn, data)
