"""
components.py  —  Shared UI components.
"""

import streamlit as st
from config import NAV_ITEMS, LEVEL_COLORS
from logic import level_pill_html, position_arrow, team_badges, level_divider_html

def _safe_int(val, default=0):
    """Safely convert a value that may be NaN, None or empty string to int."""
    try:
        return int(float(val or default))
    except (ValueError, TypeError):
        return default




# ─── Bottom nav bar ───────────────────────────────────────────────────────────
def render_navbar():
    active = st.session_state.get("active_page", "home")
    is_adm = st.session_state.get("is_admin", False)

    items = list(NAV_ITEMS)
    if is_adm:
        items.append(("admin", "🔑", "Admin"))

    st.markdown("---")
    cols = st.columns(len(items))
    for i, (page_id, icon, label) in enumerate(items):
        with cols[i]:
            is_act = (page_id == active)
            # Highlight active tab with different styling via markdown
            if is_act:
                st.markdown(
                    f"<div style='text-align:center;padding:4px 0;border-bottom:2px solid var(--cyan,#00E5FF);'>"
                    f"<span style='font-size:1.4rem;'>{icon}</span><br>"
                    f"<span style='font-size:0.62rem;color:#00E5FF;font-weight:700;"
                    f"letter-spacing:.08em;text-transform:uppercase;'>{label}</span></div>",
                    unsafe_allow_html=True,
                )
            else:
                if st.button(
                    f"{icon}",
                    key=f"nav_{page_id}",
                    help=label,
                    width='stretch',
                ):
                    st.session_state["active_page"]  = page_id
                    st.session_state["view_team_id"] = None
                    st.rerun()
                st.markdown(
                    f"<div style='text-align:center;margin-top:-12px;"
                    f"font-size:0.62rem;color:#6B7A99;letter-spacing:.08em;"
                    f"text-transform:uppercase;'>{label}</div>",
                    unsafe_allow_html=True,
                )


# ─── Help modal ───────────────────────────────────────────────────────────────
def render_help_modal():
    if st.session_state.get("show_help", False):
        with st.expander("📖 Regulamento Completo", expanded=True):
            st.markdown(REGULAMENTO_MD)
            if st.button("✕ Fechar", key="close_help"):
                st.session_state.show_help = False
                st.rerun()

    if st.button("?", key="help_fab", help="Regulamento"):
        st.session_state.show_help = not st.session_state.get("show_help", False)
        st.rerun()


# ─── Rank card HTML ───────────────────────────────────────────────────────────
def rank_card_html(row: dict, streak: int = 0, is_mine: bool = False,
                   trunfos: dict = None) -> str:
    cat    = str(row.get("category", "M5"))
    color  = LEVEL_COLORS.get(cat, "#aaa")
    pos    = _safe_int(row.get("position", 0))
    prev   = _safe_int(row.get("prev_position", pos))
    name   = str(row.get("team_name", "—") or "—")
    p1     = str(row.get("player1", "") or "")
    p2     = str(row.get("player2", "") or "")
    pts    = _safe_int(row.get("points", 0))
    photo  = str(row.get("photo_url", "") or "")

    avatar = (f'<img src="{photo}" class="rank-avatar" style="border-color:{color};">'
              if photo else
              f'<div class="rank-avatar" style="border-color:{color};">🎾</div>')
    arrow   = position_arrow(prev, pos)
    badges  = team_badges(row, streak)
    pill    = level_pill_html(cat)
    mine_cls = " mine" if is_mine else ""

    # Streak badge
    streak_html = ""
    if streak > 0:
        sc = "#FF9800" if streak >= 5 else "#8b949e"
        streak_html = f'<span style="color:{sc};font-size:0.75rem;font-weight:700;">🔥{streak}</span>'

    # Trunfos mini icons — build safe HTML
    trunfo_html = ""
    if trunfos is not None:
        def _safe_qty(v):
            try: return int(float(v or 0))
            except: return 0
        d = _safe_qty(trunfos.get("desforra_qty", 0))
        s = _safe_qty(trunfos.get("salto_qty", 0))
        e = _safe_qty(trunfos.get("escudo_qty", 0))
        def _dot(n, icon):
            return icon if n > 0 else "&#183;"
        trunfo_html = (
            f'<span style="font-size:.78rem;opacity:.9;letter-spacing:1px;">' +
            _dot(d,"&#x1F504;") + _dot(s,"&#x1F985;") + _dot(e,"&#x1F6E1;") +
            '</span>'
        )

    return f"""
<div class="rank-card{mine_cls}" style="--card-accent:{color};cursor:pointer;"
     title="Clica para ver detalhes">
  <div class="rank-num" style="color:{color}aa;">{pos}</div>
  {avatar}
  <div class="rank-info">
    <div class="rank-team-name">{name} {badges}</div>
    <div class="rank-players">{p1}{' &amp; ' + p2 if p2 else ''}</div>
    <div style="display:flex;gap:8px;align-items:center;margin-top:3px;">
      {streak_html}
      {trunfo_html}
    </div>
  </div>
  <div style="display:flex;flex-direction:column;align-items:flex-end;gap:4px;">
    {pill}
    <div>{arrow}</div>
  </div>
  <div class="rank-pts">{pts}<br><span style="font-size:0.65rem;color:var(--text-dim);">pts</span></div>
</div>"""


# ─── Quick navigation helper ──────────────────────────────────────────────────
def nav_to(page: str):
    st.session_state["active_page"]  = page
    st.session_state["view_team_id"] = None
    st.rerun()


# ─── Render a rank card — clicking opens team detail ──────────────────────────
def rank_card_with_button(row: dict, streak: int = 0, is_mine: bool = False,
                          trunfos_row: dict = None, key_prefix: str = "rc"):
    """Uses st.button styled to look like the card itself."""
    team_id   = str(row.get("team_id", ""))
    team_name = str(row.get("team_name", ""))
    cat       = str(row.get("category", "M5"))
    color     = LEVEL_COLORS.get(cat, "#aaa")
    pos       = _safe_int(row.get("position", 0))
    pts       = _safe_int(row.get("points", 0))
    p1        = str(row.get("player1", "") or "")
    p2        = str(row.get("player2", "") or "")
    photo     = str(row.get("photo_url", "") or "")
    streak_i  = int(streak or 0)
    mine_border = f"border:2px solid {color};" if is_mine else f"border:1px solid #21262d;"

    # Trunfos
    tr_html = ""
    if trunfos_row:
        def _q(v):
            try: return int(float(v or 0))
            except: return 0
        d = _q(trunfos_row.get("desforra_qty",0))
        s = _q(trunfos_row.get("salto_qty",0))
        e = _q(trunfos_row.get("escudo_qty",0))
        tr_html = (
            ("🔄" if d>0 else "◌") +
            ("🦅" if s>0 else "◌") +
            ("🛡️" if e>0 else "◌")
        )

    streak_html = f"🔥{streak_i}" if streak_i >= 1 else ""
    avatar_html = f'<img src="{photo}" style="width:38px;height:38px;border-radius:50%;object-fit:cover;border:2px solid {color};">' if photo else f'<div style="width:38px;height:38px;border-radius:50%;background:#1c2128;border:2px solid {color};display:flex;align-items:center;justify-content:center;font-size:1.1rem;">🎾</div>'

    # Badge for level
    pill = f'<span style="background:{color}22;border:1px solid {color}66;color:{color};border-radius:99px;padding:1px 8px;font-size:.65rem;font-weight:700;">{cat}</span>'

    card_html = f"""
<div style="{mine_border}border-radius:12px;background:#0d1117;padding:10px 14px;
     margin-bottom:6px;display:flex;align-items:center;gap:10px;
     box-shadow: 0 2px 8px rgba(0,0,0,.4);">
  <div style="font-family:'Barlow Condensed',monospace;font-size:1.4rem;font-weight:800;
       color:{color}55;min-width:28px;text-align:center;">#{pos}</div>
  {avatar_html}
  <div style="flex:1;min-width:0;">
    <div style="font-weight:700;font-size:.95rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{team_name}</div>
    <div style="font-size:.72rem;color:#6B7A99;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{p1}{" &amp; "+p2 if p2 else ""}</div>
    <div style="font-size:.75rem;margin-top:2px;">{streak_html} {tr_html}</div>
  </div>
  <div style="text-align:right;flex-shrink:0;">
    {pill}
    <div style="font-family:'Barlow Condensed',monospace;font-size:1.1rem;font-weight:700;color:#8b949e;margin-top:2px;">{pts}<span style="font-size:.6rem;color:#3D4A60;"> pts</span></div>
  </div>
</div>"""

    # Use button with card label for accessibility, hide default styling
    uid = f"{key_prefix}_{team_id}"
    st.markdown(f"""
<style>
div[data-testid="stButton"] > button[kind="secondary"]#card_{uid} {{
    display:none;
}}
</style>""", unsafe_allow_html=True)

    st.markdown(card_html, unsafe_allow_html=True)
    if st.button(f"#{pos} {team_name}", key=f"card_{uid}",
                 help=f"Ver perfil de {team_name}",
                 use_container_width=True):
        st.session_state["view_team_id"] = team_id
        st.rerun()
    # Hide the button visually with CSS
    st.markdown(f"""
<style>
[data-testid="stButton"]:has(button[title="Ver perfil de {team_name}"]) button {{
    margin-top: -8px;
    height: 4px;
    opacity: 0;
    pointer-events: auto;
    cursor: pointer;
}}
</style>""", unsafe_allow_html=True)


# ─── Section header ───────────────────────────────────────────────────────────
def section_header(title: str, icon: str = ""):
    st.markdown(
        f'<div class="section-header">{icon} {title}<span class="line"></span></div>',
        unsafe_allow_html=True,
    )


# ─── Regulamento ─────────────────────────────────────────────────────────────
REGULAMENTO_MD = """
## 📖 Regulamento — Liga de Duplas

### 1. Estrutura da Liga
- O ranking é uma **escada única**, do 1.º ao último lugar.
- **M1** (Topo): apenas o 1.º lugar — o Campeão 👑
- **M2, M3, M4, M5**: categorias que agrupam os restantes, conforme posição.
- O ranking inicial é definido por um **Torneio de Abertura** para cada categoria.

### 2. Desafios
- Só é permitido **desafiar equipas até 3 posições acima** (regra +3).
- O desafiante envia o pedido; o defensor recebe aviso no próximo login.

### 3. O Guardião (7 dias)
- Ao atingir o 1.º lugar do seu nível (M2–M5), a equipa entra em **Modo Guardião** por **168 horas (7 dias)**.
- Durante esse período, deve defender a posição antes de poder desafiar o nível acima.
- Após as 168h (ou defesa bem-sucedida), o ícone muda para ⚔️ e pode **desafiar a última equipa do nível acima**.

### 4. Pontuação
| Situação | Pontos |
|---|---|
| Vitória Desafiante | +5 |
| Vitória Defesa | +3 |
| Derrota | +1 |
| W.O. | -10 |
| Vitória c/ Suplente | +2 |
| Inatividade 15 dias | -5 e desce 2 posições |

### 5. Validação de Resultados
1. A Equipa A submete o resultado.
2. A Equipa B recebe aviso no login e deve **Confirmar** ou **Contestar**.
3. O ranking **só mexe após confirmação**.
4. Contestações ficam pendentes para o Admin resolver.

### 6. Trunfos (máx. 1 por mês)
| Trunfo | Efeito |
|---|---|
| 🔄 Desforra | Anula derrota e força repetição (prazo 72h) |
| 🦅 Salto de Fé | Ignora a regra +3 dentro do mesmo nível M |
| 🛡️ Escudo de Platina | 10 dias de imunidade total |

- **Recarga**: streak de 5 vitórias ou 10 jogos realizados = +1 carta aleatória.
- Máximo **1 trunfo por mês**.

### 7. Inatividade
- 15 dias sem jogar: **−5 pontos** e **desce 2 posições**.

### 8. Administração
- O Super Admin pode editar qualquer dado manualmente e resolver contestações.
- Edições de nome de equipa/jogadores ficam pendentes de aprovação.
"""
