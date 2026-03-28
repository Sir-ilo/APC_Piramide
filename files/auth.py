# v4
import streamlit as st
from data_layer import verify_login, load_all
from config import ADMIN_ID

LOGO_B64   = "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"
DRAGON_B64 = "/9j/4AAQSkZJRgABAQAAAQABAAD/4gHYSUNDX1BST0ZJTEUAAQEAAAHIAAAAAAQwAABtbnRyUkdCIFhZWiAH4AABAAEAAAAAAABhY3NwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQAA9tYAAQAAAADTLQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAlkZXNjAAAA8AAAACRyWFlaAAABFAAAABRnWFlaAAABKAAAABRiWFlaAAABPAAAABR3dHB0AAABUAAAABRyVFJDAAABZAAAAChnVFJDAAABZAAAAChiVFJDAAABZAAAAChjcHJ0AAABjAAAADxtbHVjAAAAAAAAAAEAAAAMZW5VUwAAAAgAAAAcAHMAUgBHAEJYWVogAAAAAAAAb6IAADj1AAADkFhZWiAAAAAAAABimQAAt4UAABjaWFlaIAAAAAAAACSgAAAPhAAAts9YWVogAAAAAAAA9tYAAQAAAADTLXBhcmEAAAAAAAQAAAACZmYAAPKnAAANWQAAE9AAAApbAAAAAAAAAABtbHVjAAAAAAAAAAEAAAAMZW5VUwAAACAAAAAcAEcAbwBvAGcAbABlACAASQBuAGMALgAgADIAMAAxADb/2wBDAAUDBAQEAwUEBAQFBQUGBwwIBwcHBw8LCwkMEQ8SEhEPERETFhwXExQaFRERGCEYGh0dHx8fExciJCIeJBweHx7/2wBDAQUFBQcGBw4ICA4eFBEUHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh7/wAARCAA6ADcDASIAAhEBAxEB/8QAGQABAAMBAQAAAAAAAAAAAAAAAAEDBAUI/8QAJhAAAgICAAUEAwEAAAAAAAAAAQIAAwQRBRITIUEUMVGBInHR4f/EABcBAQEBAQAAAAAAAAAAAAAAAAABAgP/xAAZEQEBAQEBAQAAAAAAAAAAAAAAARECIVH/2gAMAwEAAhEDEQA/APGURJUFmCqCSewA8wIlzYuSuMuS1FgpY6DkdjNmNh4FnB777M4V51TbWhgdOvnv8zXkcT4w3Dj1ax6GxOmtfKOVR4I/v+TNvxzvd3xwonS4lh4FGJiejzfU5Tru9FU6Un2A+ZzZZdb56nU2EREqksxrnx8iu+vXPWwZdjY2JXEDVnXnOz78sotZtcuVX2XfgS+zL4g2L+bt0GXk5fAHzqYz00vZUctUToMRokfqdW26psU1nQXWpmuVyZ4xcMzH4ZnjJStLGVWChh22VI39b3MZJJJPuZZWK7LG6thRQpIOt7IHYfZ0JVK3JN0iIlaIiICTzNrWzqREBERAREQEREBERAREQERED//Z"

def ensure_session_defaults():
    defaults = {
        "authenticated": False,
        "team_id": None,
        "team_name": None,
        "is_admin": False,
        "active_page": "home",
        "show_help": False,
        "view_team_id": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def render_login(conn):
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:ital,wght@0,700;0,900;1,900&display=swap');
    .lcwrap {{ max-width:400px; margin:30px auto 0; text-align:center; font-family:'Barlow Condensed',sans-serif; }}
    .lc-apc {{
        font-size:1.1rem; font-weight:900; color:#27C878;
        letter-spacing:.5em; font-style:italic;
        display:flex; align-items:center; justify-content:center; gap:8px;
        margin:10px 0 0;
    }}
    .lc-apc .bar {{ color:#27C878; font-size:1.4rem; font-style:normal; }}
    .lc-cl {{
        font-size:2.6rem; font-weight:900; color:#fff;
        letter-spacing:.08em; font-style:italic;
        line-height:1; margin:0 0 4px;
    }}
    .lc-league {{
        font-size:1.6rem; font-weight:700; color:#fff;
        letter-spacing:.2em; margin-bottom:28px;
    }}
    .sirl {{ text-align:center; margin-top:18px; color:#3D4A60; font-size:.72rem; cursor:pointer; user-select:none; }}
    </style>
    <div class="lcwrap">
      <img src="data:image/png;base64,{LOGO_B64}"
           style="width:180px;filter:drop-shadow(0 0 18px rgba(39,200,120,.5));">
      <div class="lc-apc"><span class="bar">⌇</span>APC<span class="bar">⌇</span></div>
      <div class="lc-cl">CHAMPIONS</div>
      <div class="lc-league">LEAGUE</div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        tid = st.text_input("ID da Equipa", placeholder="ex: EQ001", key="login_tid").strip()
        pw  = st.text_input("Password", type="password", key="login_pw")
        if st.button("Vamos!", key="login_btn"):
            data = load_all(conn)
            user = verify_login(data["teams"], tid, pw)
            if user:
                st.session_state.authenticated = True
                st.session_state.team_id       = tid
                st.session_state.team_name     = user.get("team_name", tid)
                st.session_state.is_admin      = (
                    tid == ADMIN_ID or
                    str(user.get("is_admin", "")).upper() == "TRUE"
                )
                my_matches = data["matches"]
                if not my_matches.empty:
                    pend = my_matches[
                        (my_matches["team_b_id"] == tid) &
                        (my_matches["validation_status"] == "pending")
                    ]
                    if not pend.empty:
                        st.session_state.active_page = "challenges"
                st.rerun()
            else:
                st.error("Credenciais inválidas.")

    # Secret Dragon Easter Egg
    _render_dragon_egg()


def _render_dragon_egg():
    st.markdown(f"""
    <style>
    #dragon-overlay {{
        display:none; position:fixed; inset:0; z-index:99999;
        background:#0a1a0a;
        flex-direction:column; align-items:center; justify-content:center;
    }}
    #dragon-overlay.show {{ display:flex; }}
    #dragon-img {{ width:200px; opacity:.9; margin-bottom:20px; animation: breathe 3s ease-in-out infinite; }}
    #dragon-msg {{ color:#27C878; font-family:'Barlow Condensed',sans-serif;
                   font-size:1.1rem; letter-spacing:.15em; opacity:.7; }}
    #zzz {{ font-size:2rem; color:#27C878; opacity:0; margin-top:10px;
            animation: none; }}
    #zzz.show {{ animation: fadeInOut 1s ease-in-out infinite; }}
    @keyframes breathe {{ 0%,100% {{ transform:scale(1); }} 50% {{ transform:scale(1.04); }} }}
    @keyframes fadeInOut {{ 0%,100% {{ opacity:0; }} 50% {{ opacity:1; }} }}
    </style>

    <div id="dragon-overlay" onclick="dragonTouch()">
      <img id="dragon-img" src="data:image/png;base64,{DRAGON_B64}">
      <div id="dragon-msg">Powered by Sir-ILO &copy; 2026</div>
      <div id="zzz">💤 Zzz...</div>
    </div>

    <div class="sirl" id="siril-txt" onclick="sirilClick()">Powered by Sir-ILO &copy; 2026</div>

    <script>
    var _sc = 0, _st = null, _dt = null, _sleeping = false;

    function sirilClick() {{
        _sc++;
        clearTimeout(_st);
        _st = setTimeout(function(){{ _sc = 0; }}, 2000);
        if (_sc === 3) {{
            var o = document.getElementById('dragon-overlay');
            o.innerHTML += '';
            o.classList.remove('show');
            // show message first
            showMsg("Don't wake the Dragon 🐉");
        }}
        if (_sc === 7) {{
            _sc = 0;
            openDragon();
        }}
    }}

    function showMsg(txt) {{
        var d = document.createElement('div');
        d.style.cssText = 'position:fixed;bottom:80px;left:50%;transform:translateX(-50%);'
            + 'background:#27C878;color:#000;padding:10px 22px;border-radius:99px;'
            + 'font-family:Barlow Condensed,sans-serif;font-size:1rem;font-weight:700;'
            + 'z-index:99998;letter-spacing:.05em;';
        d.innerText = txt;
        document.body.appendChild(d);
        setTimeout(function(){{ d.remove(); }}, 2500);
    }}

    function openDragon() {{
        document.getElementById('dragon-overlay').classList.add('show');
        _sleeping = false;
        resetDragonTimer();
    }}

    function dragonTouch() {{
        if (!_sleeping) resetDragonTimer();
    }}

    function resetDragonTimer() {{
        _sleeping = false;
        var z = document.getElementById('zzz');
        if (z) z.classList.remove('show');
        clearTimeout(_dt);
        // show zzz after 3s of no touch
        _dt = setTimeout(function() {{
            _sleeping = true;
            var z2 = document.getElementById('zzz');
            if (z2) z2.classList.add('show');
            // close after 4s
            setTimeout(function() {{
                document.getElementById('dragon-overlay').classList.remove('show');
                _sleeping = false;
                _sc = 0;
            }}, 4000);
        }}, 3000);
    }}
    </script>
    """, unsafe_allow_html=True)
