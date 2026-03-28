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

    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "➕ Nova Equipa",
        "📊 Editar Ranking",
        "🃏 Trunfos & Stats",
        "✏️ Edits Pendentes",
        "⚖️ Contestações",
        "🗃️ Dados Raw",
        "🌱 Seed Torneio",
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
            ok = st.form_submit_button("✅ Criar Equipa", width='stretch')
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
                apply    = st.form_submit_button("💾 Guardar", width='stretch')

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
                          for _, r in teams.iterrows()}
            with st.form("rst_pw_f"):
                p_sel  = st.selectbox("Equipa", list(teams_list.keys()), key="adm_pw_sel")
                new_pw = st.text_input("Nova Password", type="password")
                rst_ok = st.form_submit_button("Resetar Password", width='stretch')
            if rst_ok and new_pw:
                import hashlib
                ph   = hashlib.sha256(new_pw.encode()).hexdigest()
                tdf  = teams.copy()
                pid  = teams_list[p_sel]
                tdf.loc[tdf["team_id"] == pid, "password_hash"] = ph
                save_teams(conn, tdf)
                st.success("Password actualizada!")


    # ── 3. Trunfos & Stats manual edit ──────────────────────────────────────
    with tab3:
        section_header("Editar Trunfos & Estatísticas", "🃏")
        trunfos = data["trunfos"]
        teams_t = data["teams"]

        team_opts = {f"{r['team_id']} — {r['team_name']}": r["team_id"]
                     for _, r in teams_t.iterrows() if r["team_id"] != "admin"}
        if not team_opts:
            st.info("Sem equipas.")
        else:
            sel_lbl = st.selectbox("Equipa", list(team_opts.keys()), key="adm_tr2_sel")
            sel_id  = team_opts[sel_lbl]

            # Current trunfos
            tr_row  = trunfos[trunfos["team_id"] == sel_id]
            d0 = int(float(tr_row["desforra_qty"].values[0])) if not tr_row.empty else 0
            s0 = int(float(tr_row["salto_qty"].values[0]))    if not tr_row.empty else 0
            e0 = int(float(tr_row["escudo_qty"].values[0]))   if not tr_row.empty else 0

            # Current stats
            t_row = teams_t[teams_t["team_id"] == sel_id]
            w0  = int(float(t_row["wins"].values[0]))          if not t_row.empty else 0
            l0  = int(float(t_row["losses"].values[0]))        if not t_row.empty else 0
            s0s = int(float(t_row["streak"].values[0]))        if not t_row.empty else 0
            tm0 = int(float(t_row["total_matches"].values[0])) if not t_row.empty else 0

            col_tr, col_st = st.columns(2)
            with col_tr:
                st.markdown("**🃏 Trunfos**")
                with st.form("adm_tr_form"):
                    new_d = st.number_input("🔄 Desforra",       0, 99, d0)
                    new_s = st.number_input("🦅 Salto de Fé",    0, 99, s0)
                    new_e = st.number_input("🛡️ Escudo Platina", 0, 99, e0)
                    rst_month = st.checkbox("Reset uso mensal (permitir usar este mês)")
                    tr_ok = st.form_submit_button("💾 Guardar Trunfos")
                if tr_ok:
                    trf = trunfos.copy()
                    mask = trf["team_id"] == sel_id
                    if mask.any():
                        trf.loc[mask, "desforra_qty"] = new_d
                        trf.loc[mask, "salto_qty"]    = new_s
                        trf.loc[mask, "escudo_qty"]   = new_e
                        if rst_month:
                            trf.loc[mask, "last_trunfo_month"] = ""
                    else:
                        trf = pd.concat([trf, pd.DataFrame([{
                            "team_id": sel_id, "desforra_qty": new_d,
                            "salto_qty": new_s, "escudo_qty": new_e,
                            "last_trunfo_month": "",
                        }])], ignore_index=True)
                    save_trunfos(conn, trf)
                    st.success("✅ Trunfos actualizados!")
                    st.rerun()

            with col_st:
                st.markdown("**📊 Estatísticas**")
                with st.form("adm_st_form"):
                    new_w  = st.number_input("Vitórias",     0, 999, w0)
                    new_l  = st.number_input("Derrotas",     0, 999, l0)
                    new_str= st.number_input("Streak atual", 0, 999, s0s)
                    new_tm = st.number_input("Total Jogos",  0, 999, tm0)
                    st_ok  = st.form_submit_button("💾 Guardar Stats")
                if st_ok:
                    tms = teams_t.copy()
                    mask = tms["team_id"] == sel_id
                    tms.loc[mask, "wins"]          = new_w
                    tms.loc[mask, "losses"]        = new_l
                    tms.loc[mask, "streak"]        = new_str
                    tms.loc[mask, "total_matches"] = new_tm
                    save_teams(conn, tms)
                    st.success("✅ Estatísticas actualizadas!")
                    st.rerun()

        # ── Manual result entry ───────────────────────────────────────────────
        st.markdown("---")
        section_header("Lançar Resultado Manual", "📝")
        st.caption("Para corrigir ou inserir resultados sem passar pelo fluxo normal.")
        ranking_a = assign_categories(data["ranking"].copy())
        team_list = {f"{r['team_id']} — {r['team_name']}": r["team_id"]
                     for _, r in ranking_a.iterrows() if r["team_id"] != "admin"}
        if len(team_list) >= 2:
            with st.form("adm_manual_result"):
                mc1, mc2 = st.columns(2)
                with mc1:
                    team_a_lbl = st.selectbox("Desafiante", list(team_list.keys()), key="mr_a")
                with mc2:
                    team_b_lbl = st.selectbox("Defensor",   list(team_list.keys()), key="mr_b",
                                               index=min(1, len(team_list)-1))
                sc1, sc2 = st.columns(2)
                with sc1:
                    score_a = st.number_input("Sets ganhos Desafiante", 0, 3, 2)
                with sc2:
                    score_b = st.number_input("Sets ganhos Defensor", 0, 3, 0)
                suplente = st.checkbox("Uso de suplente")
                note     = st.text_input("Nota (opcional)")
                mr_ok    = st.form_submit_button("✅ Registar Resultado Manual")

            if mr_ok:
                from logic import calc_points
                from data_layer import save_ranking, save_matches
                from datetime import datetime, timezone
                def _now_iso(): return datetime.now(timezone.utc).isoformat()
                a_id   = team_list[team_a_lbl]
                b_id   = team_list[team_b_lbl]
                a_name = team_a_lbl.split(" — ",1)[1]
                b_name = team_b_lbl.split(" — ",1)[1]

                if a_id == b_id:
                    st.error("Desafiante e defensor têm de ser diferentes.")
                else:
                    winner_id = a_id if score_a > score_b else b_id
                    loser_id  = b_id if score_a > score_b else a_id
                    is_ch     = (winner_id == a_id)
                    pts_w, pts_l = calc_points(is_challenger=is_ch, suplente=suplente)

                    # Save match
                    matches = data["matches"].copy()
                    mid = f"M{len(matches)+1:04d}"
                    from config import MATCHES_COLS
                    row = {c: "" for c in MATCHES_COLS}
                    row.update({
                        "match_id": mid, "timestamp": _now_iso(),
                        "team_a_id": a_id, "team_a_name": a_name,
                        "team_b_id": b_id, "team_b_name": b_name,
                        "score_a": score_a, "score_b": score_b,
                        "winner_id": winner_id, "loser_id": loser_id,
                        "pts_winner": pts_w, "pts_loser": pts_l,
                        "suplente_used": str(suplente),
                        "validation_status": "admin_override",
                        "submitted_by": "admin", "confirmed_by": "admin",
                    })
                    matches = pd.concat([matches, pd.DataFrame([row])], ignore_index=True)
                    save_matches(conn, matches)

                    # Update ranking points + swap if challenger won
                    ranking_u = data["ranking"].copy()
                    for tid, pts in [(winner_id, pts_w),(loser_id, pts_l)]:
                        mask = ranking_u["team_id"] == tid
                        cur  = int(float(ranking_u.loc[mask,"points"].values[0] or 0))
                        ranking_u.loc[mask, "points"] = max(0, cur + pts)
                        ranking_u.loc[mask, "prev_position"] = ranking_u.loc[mask,"position"]
                    if winner_id == a_id:
                        ch_m  = ranking_u["team_id"] == a_id
                        def_m = ranking_u["team_id"] == b_id
                        if ch_m.any() and def_m.any():
                            cp = int(float(ranking_u.loc[ch_m,"position"].values[0]))
                            dp = int(float(ranking_u.loc[def_m,"position"].values[0]))
                            if cp > dp:
                                ranking_u.loc[ch_m,  "position"] = dp
                                ranking_u.loc[def_m, "position"] = cp
                    save_ranking(conn, ranking_u)
                    st.success(f"✅ Resultado manual registado! Vencedor: {a_name if winner_id==a_id else b_name}")
                    st.balloons()
                    st.rerun()

    # ── 4. Pending edits ──────────────────────────────────────────────────────
    with tab4:
        section_header("Edições Pendentes", "✏️")
        pending_df = data["pending"].copy()
        pend_open = pending_df[pending_df["status"] == "pending"] if not pending_df.empty else pd.DataFrame()
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
                                 width='stretch'):
                        approve_edit(conn, data, e["edit_id"])
                        st.rerun()
                with cb:
                    if st.button("❌ Rejeitar", key=f"rej_e_{e['edit_id']}",
                                 width='stretch'):
                        reject_edit(conn, data, e["edit_id"])
                        st.rerun()

    # ── 4. Contests ───────────────────────────────────────────────────────────
    with tab5:
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
                             width='stretch'):
                    admin_override_match(conn, data, m["match_id"])
                    st.success("Resultado aceite pelo Admin.")
                    st.balloons()
                    st.rerun()

    # ── 5. Raw data ───────────────────────────────────────────────────────────
    with tab6:
        section_header("Dados Raw (Read-Only)", "🗃️")
        for name, df in data.items():
            with st.expander(f"📄 {name} ({len(df)} linhas)"):
                st.dataframe(df, use_container_width=True, hide_index=True)

    # ── 6. Seed torneio de abertura ───────────────────────────────────────────
    with tab7:
        _render_seed_tab(conn)


# ── Seed function ─────────────────────────────────────────────────────────────
def _render_seed_tab(conn):
    import hashlib, time
    from datetime import datetime, timezone

    section_header("Seed — Torneio de Abertura", "🌱")

    st.warning(
        "⚠️ **Atenção:** isto apaga os dados actuais de ranking, equipas e trunfos "
        "e substitui por 20 equipas de teste. Usa apenas uma vez no arranque."
    )

    def _now():
        return datetime.now(timezone.utc).isoformat()
    def _h(pw):
        return hashlib.sha256(pw.encode()).hexdigest()

    TEAMS = [
        ("EQ001","Os Trovões",      "João Silva",      "Pedro Costa"),
        ("EQ002","Ace Masters",     "Miguel Santos",   "Rui Ferreira"),
        ("EQ003","Net Ninjas",      "André Oliveira",  "Tiago Sousa"),
        ("EQ004","Smash Bros",      "Carlos Mendes",   "Paulo Rodrigues"),
        ("EQ005","Drop Shot Kings", "Nuno Pereira",    "Filipe Carvalho"),
        ("EQ006","Lob Stars",       "Ricardo Gomes",   "Sérgio Martins"),
        ("EQ007","Volley Boys",     "António Lima",    "Luís Pinto"),
        ("EQ008","Court Jesters",   "Hugo Fernandes",  "Bruno Alves"),
        ("EQ009","Padel Sharks",    "Marco Correia",   "David Lopes"),
        ("EQ010","Wild Cards",      "Gonçalo Dias",    "Rafael Mota"),
        ("EQ011","Deuce Devils",    "Vítor Cunha",     "Fábio Neves"),
        ("EQ012","Power Serves",    "Diogo Teixeira",  "Leandro Reis"),
        ("EQ013","Baseline Kings",  "Rodrigo Freitas", "Hélder Castro"),
        ("EQ014","Net Breakers",    "Eduardo Moreira", "Bernardo Fonseca"),
        ("EQ015","Spin Masters",    "Tomás Azevedo",   "Samuel Barros"),
        ("EQ016","Slice & Dice",    "Mário Pires",     "Valter Soares"),
        ("EQ017","The Returners",   "Álvaro Brito",    "Cláudio Campos"),
        ("EQ018","Rally Cats",      "Nelson Henriques","Osvaldo Cruz"),
        ("EQ019","Topspin Tigers",  "Armindo Rocha",   "Celestino Serra"),
        ("EQ020","Game Set Match",  "Florindo Nunes",  "Januário Vaz"),
    ]
    STATS = [
        (8,2,3,10),(7,3,4,10),(9,1,5,10),(6,4,2,10),(5,5,0,10),
        (7,3,3,10),(6,4,2,10),(5,5,1,10),(4,6,0,10),(8,2,4,10),
        (6,4,2,10),(5,5,1,10),(7,3,3,10),(4,6,0,10),(6,4,2,10),
        (5,5,0,10),(3,7,0,10),(4,6,1,10),(3,7,0,10),(2,8,0,10),
    ]

    def _cat(pos):
        if pos == 1:  return "M1"
        if pos <= 5:  return "M2"
        if pos <= 11: return "M3"
        if pos <= 17: return "M4"
        return "M5"

    # Build preview
    combined = sorted(zip(TEAMS, STATS), key=lambda x: (-x[1][0], x[1][1]))
    preview = [{"#": i+1, "Equipa": t[1], "Nível": _cat(i+1),
                "Pontos": w*5+l, "V": w, "D": l}
               for i, ((tid,*t),(w,l,*_)) in enumerate(combined)]
    st.dataframe(pd.DataFrame(preview), hide_index=True, use_container_width=True)
    st.caption("Password de todas as equipas: **padel2024**")

    if st.button("🌱 EXECUTAR SEED AGORA", key="run_seed"):
        try:
            import gspread
            from google.oauth2.service_account import Credentials

            s = st.secrets["connections"]["gsheets"]
            creds = Credentials.from_service_account_info(
                {k: s[k] for k in ["type","project_id","private_key_id","private_key",
                                    "client_email","client_id","auth_uri","token_uri",
                                    "auth_provider_x509_cert_url","client_x509_cert_url"]},
                scopes=["https://www.googleapis.com/auth/spreadsheets",
                        "https://www.googleapis.com/auth/drive"],
            )
            gc  = gspread.authorize(creds)
            raw = str(s["spreadsheet"])
            sid = raw.split("/spreadsheets/d/")[1].split("/")[0].split("?")[0].strip() \
                  if "/spreadsheets/d/" in raw else raw.strip()
            wb  = gc.open_by_key(sid)

            def _write(sheet_name, df):
                try:
                    ws = wb.worksheet(sheet_name)
                except Exception:
                    ws = wb.add_worksheet(title=sheet_name, rows=200, cols=30)
                ws.clear()
                rows = [df.columns.tolist()] + df.astype(str).values.tolist()
                ws.update(rows, value_input_option="RAW")
                time.sleep(2)

            # Teams — keep admin row
            team_rows, ranking_rows, trunfo_rows = [], [], []
            for i, ((tid,name,p1,p2),(w,l,streak,tm)) in enumerate(combined):
                pos = i + 1
                team_rows.append({
                    "team_id":tid,"team_name":name,"player1":p1,"player2":p2,
                    "password_hash":_h("padel2024"),"is_admin":"FALSE","photo_url":"",
                    "wins":w,"losses":l,"streak":streak,"total_matches":tm,
                    "last_match_date":_now(),"created_at":_now(),
                })
                ranking_rows.append({
                    "team_id":tid,"team_name":name,"position":pos,"category":_cat(pos),
                    "points":w*5+l,"prev_position":pos,
                    "guardian_since":"","immune_until":"",
                    "ready_to_climb":"FALSE","trunfo_salto_active":"FALSE",
                })
                trunfo_rows.append({
                    "team_id":tid,"desforra_qty":1,"salto_qty":1,
                    "escudo_qty":1,"last_trunfo_month":"",
                })

            # Prepend admin row to teams
            admin_row = {
                "team_id":"admin","team_name":"Administrador","player1":"Admin",
                "player2":"","password_hash":_h("admin2024"),"is_admin":"TRUE",
                "photo_url":"","wins":0,"losses":0,"streak":0,"total_matches":0,
                "last_match_date":"","created_at":_now(),
            }
            teams_df   = pd.concat([pd.DataFrame([admin_row]),
                                    pd.DataFrame(team_rows)], ignore_index=True)
            ranking_df = pd.DataFrame(ranking_rows)
            trunfos_df = pd.DataFrame(trunfo_rows)

            with st.spinner("A escrever teams..."):
                _write("teams", teams_df)
            st.success(f"✅ teams — {len(teams_df)} linhas")

            with st.spinner("A escrever ranking..."):
                _write("ranking", ranking_df)
            st.success(f"✅ ranking — {len(ranking_df)} linhas")

            with st.spinner("A escrever trunfos..."):
                _write("trunfos", trunfos_df)
            st.success(f"✅ trunfos — {len(trunfos_df)} linhas")

            for sheet in ["challenges","matches","pending_edits"]:
                try:
                    wb.worksheet(sheet).clear()
                    time.sleep(1)
                except Exception:
                    pass
            st.success("✅ challenges / matches / pending_edits — limpos")

            st.success("🎉 **Seed completo!** Faz logout e volta a entrar.")
            st.balloons()
            st.cache_data.clear()

        except Exception as e:
            st.error(f"Erro durante seed: {e}")
