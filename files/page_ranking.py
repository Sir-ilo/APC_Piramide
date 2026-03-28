"""page_ranking.py — Pirâmide com gatekeepers e cartões expansíveis"""
import streamlit as st
import pandas as pd
from datetime import datetime, timezone, timedelta
from data_layer import assign_categories, save_ranking
from logic import guardian_remaining, format_guardian_timer
from config import CATEGORY_ORDER
from components import section_header, build_rows_data, render_expandable_cards
from config import LEVEL_COLORS, CATEGORY_SIZES

def _safe_int(val, default=0):
    try: return int(float(str(val).strip() or default))
    except: return 0

def render_ranking(data: dict, conn):
    section_header("Pirâmide de Ranking", "🏅")
    ranking = assign_categories(data["ranking"].copy())
    teams   = data["teams"]
    trunfos = data["trunfos"]
    matches = data["matches"]
    my_id   = st.session_state.team_id

    if ranking.empty:
        st.info("Ranking vazio.")
        return

    for col in ["wins","losses","streak"]:
        if col not in ranking.columns:
            ranking[col] = 0

    ranking = ranking.merge(
        teams[["team_id","player1","player2","photo_url","streak","wins","losses"]],
        on="team_id", how="left", suffixes=("","_t")
    )
    for col in ["player1","player2","photo_url"]:
        ranking[col] = ranking[col].fillna("")
    for col in ["streak","wins","losses"]:
        ranking[col] = pd.to_numeric(ranking.get(col, 0), errors="coerce").fillna(0).astype(int)
    ranking["points"]   = pd.to_numeric(ranking["points"],   errors="coerce").fillna(0).astype(int)
    ranking["position"] = pd.to_numeric(ranking["position"], errors="coerce").fillna(999).astype(int)
    ranking = ranking.sort_values("position")

    # Stats
    c1,c2,c3 = st.columns(3)
    c1.metric("Total Equipas", len(ranking))
    my_r = ranking[ranking["team_id"]==my_id]
    if not my_r.empty:
        c2.metric("Minha Posição", f"#{int(my_r.iloc[0]['position'])}")
        c3.metric("Meu Nível", my_r.iloc[0]["category"])

    cats_present = [c for c in CATEGORY_SIZES if c in ranking["category"].values]
    selected = st.multiselect("Filtrar nível", cats_present, default=cats_present, key="rank_filter")
    st.markdown("---")

    for cat in ["M1","M2","M3","M4","M5"]:
        if cat not in selected: continue
        cat_df = ranking[ranking["category"]==cat]
        if cat_df.empty: continue

        color = LEVEL_COLORS.get(cat,"#aaa")

        # ── Gatekeeper banner ─────────────────────────────────────────────────
        top_team = cat_df[cat_df["position"]==cat_df["position"].min()].iloc[0] if not cat_df.empty else None
        _render_gatekeeper_banner(cat, color, top_team, ranking)

        # ── Level divider ─────────────────────────────────────────────────────
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:12px;margin:16px 0 10px;">
          <span style="background:{color}18;border:1px solid {color}44;color:{color};
            border-radius:99px;padding:3px 14px;font-size:.75rem;font-weight:800;
            letter-spacing:.2em;white-space:nowrap;">{cat}</span>
          <div style="flex:1;height:1px;background:linear-gradient(90deg,{color}55,transparent);"></div>
        </div>""", unsafe_allow_html=True)

        rows_data = build_rows_data(cat_df, teams, trunfos, matches, my_id)
        render_expandable_cards(rows_data, my_id, conn, data)


def _render_gatekeeper_banner(cat, color, top_team, ranking):
    if top_team is None or cat == "M1": return

    from logic import guardian_remaining, format_guardian_timer
    from config import CATEGORY_ORDER
    rem = guardian_remaining(top_team.to_dict())
    ready = str(top_team.get("ready_to_climb","")).upper()=="TRUE"

    cat_idx = CATEGORY_ORDER.index(cat) if cat in CATEGORY_ORDER else -1
    upper_cat = CATEGORY_ORDER[cat_idx-1] if cat_idx > 0 else None

    if rem:
        # Guardian active — show countdown
        h = int(rem.total_seconds()//3600)
        m = int((rem.total_seconds()%3600)//60)
        pct = max(0, min(100, int((1 - rem.total_seconds()/(168*3600))*100)))
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#1a1200,#0d0900);
             border:1px solid {color}33;border-radius:12px;padding:12px 16px;margin-bottom:4px;">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
            <div style="font-size:.7rem;color:{color};letter-spacing:.15em;text-transform:uppercase;font-weight:700;">
              ⏳ Guardião · {top_team['team_name']}
            </div>
            <div style="font-family:monospace;font-size:1rem;font-weight:800;color:{color};">
              {h:02d}h {m:02d}m
            </div>
          </div>
          <div style="background:#21262d;border-radius:99px;height:6px;overflow:hidden;">
            <div style="background:linear-gradient(90deg,{color},{color}88);height:100%;
                 width:{pct}%;border-radius:99px;transition:width .5s;"></div>
          </div>
          <div style="font-size:.65rem;color:#6B7A99;margin-top:4px;">
            A guardar o portão para {upper_cat or "nível acima"} · {pct}% do período cumprido
          </div>
        </div>""", unsafe_allow_html=True)

    elif ready and upper_cat:
        # Gatekeeper — show open gate visual
        upper_df = ranking[ranking["category"]==upper_cat]
        last_upper = upper_df[upper_df["position"]==upper_df["position"].max()] if not upper_df.empty else None
        last_name = last_upper.iloc[0]["team_name"] if last_upper is not None and not last_upper.empty else "?"

        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#001a00,#000d00);
             border:2px solid {color};border-radius:12px;padding:14px 16px;margin-bottom:4px;
             box-shadow:0 0 20px {color}33;">
          <div style="text-align:center;margin-bottom:8px;">
            <span style="font-size:.7rem;color:{color};letter-spacing:.2em;text-transform:uppercase;font-weight:800;">
              ⚔️ PORTÃO ABERTO · CONFRONTO GARANTIDO
            </span>
          </div>
          <div style="display:flex;align-items:center;justify-content:center;gap:12px;">
            <div style="text-align:center;background:{color}11;border:1px solid {color}44;
                 border-radius:10px;padding:8px 14px;">
              <div style="font-size:.65rem;color:#6B7A99;">Desafiante (sobe)</div>
              <div style="font-weight:800;color:{color};">{top_team['team_name']}</div>
              <div style="font-size:.7rem;color:#6B7A99;">{cat} · #{int(top_team['position'])}</div>
            </div>
            <div style="font-size:1.8rem;animation:pulse 1s infinite;">⚔️</div>
            <div style="text-align:center;background:#21262d;border:1px solid #30363d;
                 border-radius:10px;padding:8px 14px;">
              <div style="font-size:.65rem;color:#6B7A99;">Defensor (desce se perder)</div>
              <div style="font-weight:800;color:#fff;">{last_name}</div>
              <div style="font-size:.7rem;color:#6B7A99;">{upper_cat} · último lugar</div>
            </div>
          </div>
          <div style="text-align:center;margin-top:8px;font-size:.68rem;color:#6B7A99;">
            🏆 Vencedor sobe de nível · Derrotado desce e defende nova posição
          </div>
        </div>
        <style>@keyframes pulse{{0%,100%{{opacity:1;}}50%{{opacity:.5;}}}}</style>
        """, unsafe_allow_html=True)
