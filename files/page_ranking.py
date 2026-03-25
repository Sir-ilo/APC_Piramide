"""
page_ranking.py  —  Tab 2: Full pyramid ranking view.
"""

import streamlit as st
import pandas as pd
from data_layer import assign_categories
from logic import level_divider_html
from components import rank_card_with_button, section_header
from config import CATEGORY_SIZES


def render_ranking(data: dict, conn):
    section_header("Pirâmide de Ranking", "🏅")

    ranking = assign_categories(data["ranking"].copy())
    teams   = data["teams"]
    trunfos = data["trunfos"]

    if ranking.empty:
        st.info("Ranking vazio. O administrador deve adicionar equipas.")
        return

    # Merge team info
    ranking = ranking.merge(
        teams[["team_id","player1","player2","photo_url","streak","wins","losses"]],
        on="team_id", how="left"
    )
    for col in ["streak","wins","losses"]:
        ranking[col] = pd.to_numeric(ranking[col], errors="coerce").fillna(0).astype(int)
    for col in ["player1","player2","photo_url"]:
        ranking[col] = ranking[col].fillna("")
    ranking["points"]   = pd.to_numeric(ranking["points"],   errors="coerce").fillna(0).astype(int)
    ranking["position"] = pd.to_numeric(ranking["position"], errors="coerce").fillna(999).astype(int)
    ranking = ranking.sort_values("position")

    my_id = st.session_state.team_id

    # Stats
    m1c, m2c, m3c = st.columns(3)
    m1c.metric("Total Equipas", len(ranking))
    my_row = ranking[ranking["team_id"] == my_id]
    if not my_row.empty:
        m2c.metric("Minha Posição", f"#{int(my_row.iloc[0]['position'])}")
        m3c.metric("Meu Nível",     my_row.iloc[0]["category"])

    # Level filter
    cats_present = [c for c in CATEGORY_SIZES if c in ranking["category"].values]
    selected = st.multiselect("Filtrar nível", cats_present,
                               default=cats_present, key="rank_filter")
    st.markdown("---")

    # Build trunfos lookup dict: team_id -> row dict
    tr_map = {}
    if not trunfos.empty:
        for _, tr in trunfos.iterrows():
            tr_map[str(tr["team_id"])] = tr.to_dict()

    # Render by level
    for cat in ["M1","M2","M3","M4","M5"]:
        if cat not in selected:
            continue
        cat_df = ranking[ranking["category"] == cat]
        if cat_df.empty:
            continue
        st.markdown(level_divider_html(cat), unsafe_allow_html=True)
        for _, row in cat_df.iterrows():
            row_dict = row.to_dict()
            is_mine  = (row_dict["team_id"] == my_id)
            tr_row   = tr_map.get(str(row_dict["team_id"]))
            rank_card_with_button(
                row_dict,
                streak=int(row_dict.get("streak", 0)),
                is_mine=is_mine,
                trunfos_row=tr_row,
                key_prefix="rk",
            )
