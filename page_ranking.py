"""
page_ranking.py  —  Tab 2: Full pyramid ranking view.
"""

import streamlit as st
import pandas as pd
from data_layer import assign_categories
from logic import level_divider_html, team_badges
from components import rank_card_html, section_header
from config import CATEGORY_SIZES, LEVEL_COLORS

def _safe_int(val, default=0):
    """Safely convert a value that may be NaN, None or empty string to int."""
    try:
        return int(float(val or default))
    except (ValueError, TypeError):
        return default




def render_ranking(data: dict, conn):
    section_header("Pirâmide de Ranking", "🏅")

    ranking = assign_categories(data["ranking"].copy())
    teams   = data["teams"]

    if ranking.empty:
        st.info("Ranking vazio. O administrador deve adicionar equipas.")
        return

    # Merge team info once
    ranking = ranking.merge(
        teams[["team_id","player1","player2","photo_url","streak","wins","losses"]],
        on="team_id", how="left"
    )
    ranking["streak"]  = pd.to_numeric(ranking["streak"],  errors="coerce").fillna(0).astype(int)
    ranking["player1"] = ranking["player1"].fillna("")
    ranking["player2"] = ranking["player2"].fillna("")
    ranking["photo_url"] = ranking["photo_url"].fillna("")
    ranking["points"]  = pd.to_numeric(ranking["points"],  errors="coerce").fillna(0).astype(int)
    ranking["position"]= pd.to_numeric(ranking["position"],errors="coerce").fillna(999).astype(int)
    ranking = ranking.sort_values("position")

    my_id = st.session_state.team_id

    # Level filter
    cats_present = [c for c in CATEGORY_SIZES if c in ranking["category"].values]
    selected_cats = st.multiselect(
        "Filtrar nível", cats_present,
        default=cats_present, key="rank_filter"
    )

    # Stats
    total = len(ranking)
    m1c, m2c, m3c = st.columns(3)
    m1c.metric("Total Equipas",  total)
    my_row = ranking[ranking["team_id"] == my_id]
    if not my_row.empty:
        m2c.metric("Minha Posição", f"#{int(my_row.iloc[0]['position'])}")
        m3c.metric("Meu Nível",     my_row.iloc[0]["category"])

    st.markdown("---")

    # Render by level
    for cat in ["M1","M2","M3","M4","M5"]:
        if cat not in selected_cats:
            continue
        cat_df = ranking[ranking["category"] == cat]
        if cat_df.empty:
            continue
        st.markdown(level_divider_html(cat), unsafe_allow_html=True)
        for _, row in cat_df.iterrows():
            row_dict = row.to_dict()
            is_mine  = (row_dict["team_id"] == my_id)
            st.markdown(
                rank_card_html(row_dict, _safe_int(row_dict.get("streak", 0)), is_mine),
                unsafe_allow_html=True,
            )
