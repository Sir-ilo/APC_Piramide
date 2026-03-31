# components.py v6
import streamlit as st
import streamlit.components.v1 as components
from config import NAV_ITEMS, LEVEL_COLORS

DRAGON_B64 = "/9j/4AAQSkZJRgABAQAAAQABAAD/4gHYSUNDX1BST0ZJTEUAAQEAAAHIAAAAAAQwAABtbnRyUkdCIFhZWiAH4AABAAEAAAAAAABhY3NwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQAA9tYAAQAAAADTLQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAlkZXNjAAAA8AAAACRyWFlaAAABFAAAABRnWFlaAAABKAAAABRiWFlaAAABPAAAABR3dHB0AAABUAAAABRyVFJDAAABZAAAAChnVFJDAAABZAAAAChiVFJDAAABZAAAAChjcHJ0AAABjAAAADxtbHVjAAAAAAAAAAEAAAAMZW5VUwAAAAgAAAAcAHMAUgBHAEJYWVogAAAAAAAAb6IAADj1AAADkFhZWiAAAAAAAABimQAAt4UAABjaWFlaIAAAAAAAACSgAAAPhAAAts9YWVogAAAAAAAA9tYAAQAAAADTLXBhcmEAAAAAAAQAAAACZmYAAPKnAAANWQAAE9AAAApbAAAAAAAAAABtbHVjAAAAAAAAAAEAAAAMZW5VUwAAACAAAAAcAEcAbwBvAGcAbABlACAASQBuAGMALgAgADIAMAAxADb/2wBDAAUDBAQEAwUEBAQFBQUGBwwIBwcHBw8LCwkMEQ8SEhEPERETFhwXExQaFRERGCEYGh0dHx8fExciJCIeJBweHx7/2wBDAQUFBQcGBw4ICA4eFBEUHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh7/wAARCAA6ADcDASIAAhEBAxEB/8QAGQABAAMBAQAAAAAAAAAAAAAAAAEDBAUI/8QAJhAAAgICAAUEAwEAAAAAAAAAAQIAAwQRBRITIUEUMVGBInHR4f/EABcBAQEBAQAAAAAAAAAAAAAAAAABAgP/xAAZEQEBAQEBAQAAAAAAAAAAAAAAARECIVH/2gAMAwEAAhEDEQA/APGURJUFmCqCSewA8wIlzYuSuMuS1FgpY6DkdjNmNh4FnB777M4V51TbWhgdOvnv8zXkcT4w3Dj1ax6GxOmtfKOVR4I/v+TNvxzvd3xwonS4lh4FGJiejzfU5Tru9FU6Un2A+ZzZZdb56nU2EREqksxrnx8iu+vXPWwZdjY2JXEDVnXnOz78sotZtcuVX2XfgS+zL4g2L+bt0GXk5fAHzqYz00vZUctUToMRokfqdW26psU1nQXWpmuVyZ4xcMzH4ZnjJStLGVWChh22VI39b3MZJJJPuZZWK7LG6thRQpIOt7IHYfZ0JVK3JN0iIlaIiICTzNrWzqREBERAREQEREBERAREQERED//Z"

def _safe_int(val, default=0):
    try: return int(float(str(val).strip() or default))
    except: return 0


# ─── Easter Egg Dragon (renders on every page) ────────────────────────────────
def render_dragon_egg():
    """Call once per page render to inject the dragon easter egg JS/CSS."""
    img_src = f"data:image/png;base64,{DRAGON_B64}"
    css = """<style>
#dr-ov{display:none;position:fixed;inset:0;z-index:99999;background:#020f02;
  flex-direction:column;align-items:center;justify-content:center;cursor:pointer;}
#dr-ov.show{display:flex;}
#dr-img{width:180px;animation:dr-br 3s ease-in-out infinite;margin-bottom:16px;}
.dr-lbl{color:#27C878;font-size:.9rem;letter-spacing:.2em;opacity:.7;}
#dr-zzz{font-size:2.2rem;opacity:0;margin-top:10px;transition:opacity .6s;}
#dr-zzz.show{opacity:1;}
@keyframes dr-br{0%,100%{transform:scale(1);}50%{transform:scale(1.06);}}
.sir-lnk{text-align:center;padding:4px 0 68px;color:#2a3545;font-size:.65rem;
  cursor:pointer;user-select:none;letter-spacing:.05em;}
</style>"""
    body = (
        f'<div id="dr-ov" onclick="drTouch()">'
        f'<img id="dr-img" src="{img_src}">'
        f'<div class="dr-lbl">Powered by Sir-ILO &copy; 2026</div>'
        f'<div id="dr-zzz">&#128164; Zzz...</div>'
        f'</div>'
        f'<div class="sir-lnk" onclick="sirClick()">Powered by Sir-ILO &copy; 2026</div>'
    )
    js = """<script>
(function(){
  var sc=0,st=null,dt=null;
  window.sirClick=function(){
    sc++;clearTimeout(st);
    st=setTimeout(function(){sc=0;},2500);
    if(sc===3){showMsg("Don't wake the Dragon");}
    if(sc>=7){sc=0;openDr();}
  };
  window.drTouch=function(){if(dt)resetDt();};
  function showMsg(t){
    var d=document.createElement('div');
    d.style.cssText='position:fixed;bottom:88px;left:50%;transform:translateX(-50%);'
      +'background:#27C878;color:#000;padding:9px 22px;border-radius:99px;'
      +'font-weight:800;z-index:99998;font-size:.9rem;pointer-events:none;';
    d.innerText=t;document.body.appendChild(d);
    setTimeout(function(){d.remove();},2500);
  }
  function openDr(){
    document.getElementById('dr-ov').classList.add('show');
    resetDt();
  }
  function resetDt(){
    var z=document.getElementById('dr-zzz');
    if(z)z.classList.remove('show');
    clearTimeout(dt);
    dt=setTimeout(function(){
      var z2=document.getElementById('dr-zzz');
      if(z2)z2.classList.add('show');
      setTimeout(function(){
        document.getElementById('dr-ov').classList.remove('show');
        sc=0;
      },4000);
    },3000);
  }
})();
</script>"""
    st.markdown(css + body + js, unsafe_allow_html=True)

# ─── Build rows_data from dataframes ─────────────────────────────────────────
def build_rows_data(ranking_df, teams_df, trunfos_df, matches_df, my_id):
    """Merge all data into a list of dicts for render_expandable_cards."""
    rows = []
    for _, r in ranking_df.iterrows():
        tid = str(r["team_id"])
        t   = teams_df[teams_df["team_id"]==tid]
        tr  = trunfos_df[trunfos_df["team_id"]==tid]
        
        row = r.to_dict()
        if not t.empty:
            row["player1"]  = str(t.iloc[0].get("player1","") or "")
            row["player2"]  = str(t.iloc[0].get("player2","") or "")
            row["photo_url"]= str(t.iloc[0].get("photo_url","") or "")
            row["wins"]     = t.iloc[0].get("wins",0)
            row["losses"]   = t.iloc[0].get("losses",0)
            row["streak"]   = t.iloc[0].get("streak",0)
        row["trunfos"] = tr.iloc[0].to_dict() if not tr.empty else {}

        # Recent matches
        if not matches_df.empty:
            my_m = matches_df[
                ((matches_df["team_a_id"]==tid)|(matches_df["team_b_id"]==tid)) &
                (matches_df["validation_status"].isin(["confirmed","admin_override"]))
            ].sort_values("timestamp", ascending=False).head(5)
            mlist = []
            for _, m in my_m.iterrows():
                won = str(m.get("winner_id","")) == tid
                is_a = m["team_a_id"] == tid
                opp  = m["team_b_name"] if is_a else m["team_a_name"]
                role = "Desaf." if is_a else "Defesa"
                s1a,s1b = str(m.get("set1_a","")).strip(),str(m.get("set1_b","")).strip()
                s2a,s2b = str(m.get("set2_a","")).strip(),str(m.get("set2_b","")).strip()
                s3a,s3b = str(m.get("set3_a","")).strip(),str(m.get("set3_b","")).strip()
                parts = []
                for a,b in [(s1a,s1b),(s2a,s2b)]:
                    if a and b and a not in ("0","nan","") : parts.append(f"{a}-{b}")
                if s3a and s3b and s3a not in ("0","nan",""): parts.append(f"{s3a}-{s3b}")
                mlist.append({"winner_id":str(m.get("winner_id","")),"opp_name":opp,
                              "role":role,"sets_str":"; ".join(parts)})
            row["matches"] = mlist
        else:
            row["matches"] = []
        rows.append(row)
    return rows


# ─── Bottom nav bar ───────────────────────────────────────────────────────────
def render_navbar():
    active = st.session_state.get("active_page","home")
    is_adm = st.session_state.get("is_admin",False)
    items  = list(NAV_ITEMS)
    if is_adm: items.append(("admin","🔑","Admin"))

    st.markdown("---")
    cols = st.columns(len(items))
    for i,(page_id,icon,label) in enumerate(items):
        with cols[i]:
            is_act = (page_id==active) and not st.session_state.get("view_team_id")
            if is_act:
                st.markdown(
                    f"<div style='text-align:center;padding:4px 0;border-bottom:2px solid #00E5FF;'>"
                    f"<span style='font-size:1.4rem;'>{icon}</span><br>"
                    f"<span style='font-size:.62rem;color:#00E5FF;font-weight:700;"
                    f"letter-spacing:.08em;text-transform:uppercase;'>{label}</span></div>",
                    unsafe_allow_html=True,
                )
            else:
                if st.button(f"{icon}", key=f"nav_{page_id}", help=label,
                             use_container_width=True):
                    st.session_state["active_page"]  = page_id
                    st.session_state["view_team_id"] = None
                    st.rerun()
                st.markdown(
                    f"<div style='text-align:center;margin-top:-12px;"
                    f"font-size:.62rem;color:#6B7A99;letter-spacing:.08em;"
                    f"text-transform:uppercase;'>{label}</div>",
                    unsafe_allow_html=True,
                )


# ─── Section header ───────────────────────────────────────────────────────────
def section_header(title:str, icon:str=""):
    st.markdown(
        f'<div style="font-family:monospace;font-size:.72rem;font-weight:700;'
        f'letter-spacing:.2em;text-transform:uppercase;color:#6B7A99;'
        f'padding:18px 0 8px;border-bottom:1px solid #21262d;margin-bottom:12px;">' 
        f'{icon} {title}</div>',
        unsafe_allow_html=True,
    )


def nav_to(page:str):
    st.session_state["active_page"]  = page
    st.session_state["view_team_id"] = None
    st.rerun()


# ─── Regulamento ─────────────────────────────────────────────────────────────
REGULAMENTO_MD = """
## Regulamento — APC Champions League

### 1. Estrutura
- Ranking único do 1.º ao último. M1=Campeão, M2-M5 por posição.

### 2. Desafios
- Só podes desafiar até 3 posições acima (regra +3).

### 3. Guardião (7 dias)
- Ao atingir o 1.º lugar do teu nível, entras em Modo Guardião por 168h.
- Após esse período, podes desafiar o último do nível acima.

### 4. Pontuação
| Situação | Pontos |
|---|---|
| Vitória Desafiante | +5 |
| Vitória Defesa | +3 |
| Derrota | +1 |
| W.O. | -10 |
| Vitória c/ Suplente | +2 |

### 5. Trunfos (máx. 1/mês)
- 🔄 Desforra — revanche obrigatória (72h)
- 🦅 Salto de Fé — ignora +3 mas só no mesmo nível M
- 🛡️ Escudo de Platina — 10 dias de imunidade

### 6. Inatividade
- 15 dias sem jogar: -5 pts e desce 2 posições.
"""


def render_help_modal():
    if st.session_state.get("show_help",False):
        with st.expander("📖 Regulamento", expanded=True):
            st.markdown(REGULAMENTO_MD)
            if st.button("✕ Fechar", key="close_help"):
                st.session_state.show_help=False
                st.rerun()
    if st.button("?", key="help_fab", help="Regulamento"):
        st.session_state.show_help = not st.session_state.get("show_help",False)
        st.rerun()


# ─── Legacy rank_card_html (kept for team_detail page) ───────────────────────
def rank_card_html(row:dict, streak:int=0, is_mine:bool=False, trunfos:dict=None)->str:
    return ""  # replaced by expandable cards

def rank_card_with_button(row:dict, streak:int=0, is_mine:bool=False,
                           trunfos_row:dict=None, key_prefix:str="rc"):
    """Kept for compatibility — expandable cards now used instead."""
    pass
