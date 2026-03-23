"""
page_admin.py  —  Admin tab: full manual control + pending approvals.
"""

import streamlit as st
import pandas as pd
from data_layer import (
    assign_categories, save_ranking, save_teams, save_trunfos,
    add_team, approve_edit, reject_edit, admin_override_match,
)
from components import section_header
from config import CATEGORY_SIZES


def render_admin(data: dict, conn):
    st.markdown("## 🔑 Super Admin Panel")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "➕ Nova Equipa",
        "📊 Editar Ranking",
        "✏️ Edits Pendentes",
        "⚖️ Contestações",
        "🗃️ Dados Raw",
    ])

    # ── 1. Add team ───────────────────────────────────────────────────────────
    with tab1:
        section_header("Adicionar Equipa", "➕")
        with st.form("add_team_f"):
            c1, c2 = st.columns(2)
            with c1:
                tid  = st.text_input("ID (ex: EQ001)").strip().upper()
                name = st.text_input("Nome da Equipa")
                cat  = st.selectbox("Categoria Inicial", list(CATEGORY_SIZES.keys()))
            with c2:
                p1 = st.text_input("Jogador 1")
                p2 = st.text_input("Jogador 2")
                pw = st.text_input("Password", type="password")
            ok = st.form_submit_button("✅ Criar Equipa", use_container_width=True)
        if ok:
            errs = []
            if not tid: errs.append("ID vazio")
            if tid in data["teams"]["team_id"].values: errs.append("ID já existe")
            if not name: errs.append("Nome vazio")
            if not pw: errs.append("Password vazia")
            if errs:
                for e in errs: st.error(e)
            else:
                add_team(conn, data, tid, name, p1, p2, pw, cat)
                st.success(f"Equipa '{name}' criada em {cat}!")
                st.rerun()

    # ── 2. Edit ranking ───────────────────────────────────────────────────────
    with tab2:
        section_header("Editar Ranking / Pontos / Guardião", "📊")
        ranking = assign_categories(data["ranking"].copy())
        teams   = data["teams"]

        if ranking.empty:
            st.info("Ranking vazio.")
        else:
            opts = {f"#{int(r['position'])} — {r['team_name']} ({r['category']})": r["team_id"]
                    for _, r in ranking.iterrows()}
            sel_lbl = st.selectbox("Equipa", list(opts.keys()), key="adm_rk_sel")
            sel_id  = opts[sel_lbl]
            r_row   = ranking[ranking["team_id"] == sel_id].iloc[0]

            with st.form("edit_rank_f"):
                new_pos  = st.number_input("Posição", 1, 999, int(r_row["position"]))
                new_pts  = st.number_input("Pontos",  0, 99999, int(r_row["points"] or 0))
                new_cat  = st.selectbox("Categoria", list(CATEGORY_SIZES.keys()),
                                         index=list(CATEGORY_SIZES.keys()).index(r_row["category"]))
                rst_grd  = st.checkbox("Reset Guardião (Lider_Desde)")
                rst_imm  = st.checkbox("Reset Imunidade")
                clmb     = st.checkbox("Marcar como Pronto a Subir ⚔️")
                apply    = st.form_submit_button("💾 Guardar", use_container_width=True)

            if apply:
                rk = data["ranking"].copy()
                mask = rk["team_id"] == sel_id
                rk.loc[mask, "position"]  = new_pos
                rk.loc[mask, "points"]    = new_pts
                rk.loc[mask, "category"]  = new_cat
                if rst_grd: rk.loc[mask, "guardian_since"]    = ""
                if rst_imm: rk.loc[mask, "immune_until"]      = ""
                if clmb:    rk.loc[mask, "ready_to_climb"]    = "TRUE"
                save_ranking(conn, rk)
                st.success("Ranking actualizado!")
                st.rerun()

            # Reset password
            st.markdown("---")
            section_header("Reset de Password", "🔑")
            teams_list = {f"{r['team_id']} — {r['team_name']}": r["team_id"]
                          for _, r in teams.iterrows() if r["team_id"] != "admin"}
            with st.form("rst_pw_f"):
                p_sel  = st.selectbox("Equipa", list(teams_list.keys()), key="adm_pw_sel")
                new_pw = st.text_input("Nova Password", type="password")
                rst_ok = st.form_submit_button("Resetar Password", use_container_width=True)
            if rst_ok and new_pw:
                import hashlib
                ph   = hashlib.sha256(new_pw.encode()).hexdigest()
                tdf  = teams.copy()
                pid  = teams_list[p_sel]
                tdf.loc[tdf["team_id"] == pid, "password_hash"] = ph
                save_teams(conn, tdf)
                st.success("Password actualizada!")

            # Trunfo adjustment
            st.markdown("---")
            section_header("Ajustar Trunfos", "🃏")
            trunfos = data["trunfos"]
            tr_opts = {r["team_id"]: r["team_id"] for _, r in trunfos.iterrows()}
            with st.form("truf_f"):
                tr_sel = st.selectbox("Equipa", list(tr_opts.keys()), key="adm_tr_sel")
                tr_row = trunfos[trunfos["team_id"] == tr_sel]
                d0 = int(tr_row["desforra_qty"].values[0]) if not tr_row.empty else 0
                s0 = int(tr_row["salto_qty"].values[0])    if not tr_row.empty else 0
                e0 = int(tr_row["escudo_qty"].values[0])   if not tr_row.empty else 0
                tc1, tc2, tc3 = st.columns(3)
                new_d = tc1.number_input("Desforra", 0, 99, d0)
                new_s = tc2.number_input("Salto",    0, 99, s0)
                new_e = tc3.number_input("Escudo",   0, 99, e0)
                tr_ok = st.form_submit_button("Guardar Trunfos", use_container_width=True)
            if tr_ok:
                trf = trunfos.copy()
                mask = trf["team_id"] == tr_sel
                if mask.any():
                    trf.loc[mask, "desforra_qty"] = new_d
                    trf.loc[mask, "salto_qty"]    = new_s
                    trf.loc[mask, "escudo_qty"]   = new_e
                else:
                    trf = pd.concat([trf, pd.DataFrame([{
                        "team_id": tr_sel, "desforra_qty": new_d,
                        "salto_qty": new_s, "escudo_qty": new_e,
                        "last_trunfo_month": "",
                    }])], ignore_index=True)
                save_trunfos(conn, trf)
                st.success("Trunfos actualizados!")

    # ── 3. Pending edits ──────────────────────────────────────────────────────
    with tab3:
        section_header("Edições Pendentes", "✏️")
        pending = data["pending"]
        pend_open = pending[pending["status"] == "pending"] if not pending.empty else pd.DataFrame()
        if pend_open.empty:
            st.info("Sem pedidos pendentes.")
        else:
            for _, e in pend_open.iterrows():
                st.markdown(f"""
                <div class="card">
                  <strong>{e['team_id']}</strong> quer alterar <code>{e['field']}</code><br>
                  <span style="color:var(--red);">{e['old_value']}</span>
                  → <span style="color:var(--green);">{e['new_value']}</span>
                </div>
                """, unsafe_allow_html=True)
                ca, cb = st.columns(2)
                with ca:
                    if st.button("✅ Aprovar", key=f"apr_{e['edit_id']}",
                                 use_container_width=True):
                        approve_edit(conn, data, e["edit_id"])
                        st.rerun()
                with cb:
                    if st.button("❌ Rejeitar", key=f"rej_e_{e['edit_id']}",
                                 use_container_width=True):
                        reject_edit(conn, data, e["edit_id"])
                        st.rerun()

    # ── 4. Contests ───────────────────────────────────────────────────────────
    with tab4:
        section_header("Resultados Contestados", "⚖️")
        matches = data["matches"]
        contested = matches[matches["validation_status"] == "contested"] if not matches.empty else pd.DataFrame()
        if contested.empty:
            st.info("Sem contestações pendentes.")
        else:
            for _, m in contested.iterrows():
                sa = int(m["score_a"] or 0)
                sb = int(m["score_b"] or 0)
                st.markdown(f"""
                <div class="card" style="--card-accent:var(--orange);">
                  <strong>{m['team_a_name']} {sa}–{sb} {m['team_b_name']}</strong><br>
                  <span style="color:var(--text-muted);font-size:0.8rem;">
                    Submetido por {m['submitted_by']} · {str(m['timestamp'])[:10]}
                  </span>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"✅ Override Aceitar ({m['match_id']})", key=f"ov_{m['match_id']}",
                             use_container_width=True):
                    admin_override_match(conn, data, m["match_id"])
                    st.success("Resultado aceite pelo Admin.")
                    st.balloons()
                    st.rerun()

    # ── 5. Raw data ───────────────────────────────────────────────────────────
    with tab5:
        section_header("Dados Raw (Read-Only)", "🗃️")
        for name, df in data.items():
            with st.expander(f"📄 {name} ({len(df)} linhas)"):
                st.dataframe(df, use_container_width=True, hide_index=True)
