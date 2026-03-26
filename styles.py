"""
styles.py  —  All CSS injected into Streamlit.
Premium dark mode, Playtomic-inspired, with neon glow and fluid nav.
Font: Barlow Condensed (display) + Outfit (body) — powerful and sporty.
"""

import streamlit as st


def inject_all_styles():
    st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@400;600;700;800&family=Outfit:wght@300;400;500;600;700&display=swap" rel="stylesheet">

<style>
/* ═══════════════════════════════════════════════════════
   ROOT VARIABLES
═══════════════════════════════════════════════════════ */
:root {
  --bg:          #0E1117;
  --bg2:         #13181F;
  --bg3:         #1A2130;
  --card:        #151C27;
  --card-hover:  #1E2A3A;
  --border:      rgba(255,255,255,0.07);
  --border-lit:  rgba(255,255,255,0.15);

  --text:        #E8EDF5;
  --text-muted:  #6B7A99;
  --text-dim:    #3D4A60;

  --gold:    #FFD700;
  --cyan:    #00E5FF;
  --purple:  #CE93D8;
  --orange:  #FF9800;
  --green:   #66BB6A;
  --red:     #FF5252;
  --neon:    #00E5FF;

  --glow-gold:   0 0 20px rgba(255,215,0,0.5),   0 0 40px rgba(255,215,0,0.2);
  --glow-cyan:   0 0 20px rgba(0,229,255,0.4),   0 0 40px rgba(0,229,255,0.15);
  --glow-purple: 0 0 20px rgba(206,147,216,0.4), 0 0 40px rgba(206,147,216,0.15);
  --glow-green:  0 0 20px rgba(102,187,106,0.4), 0 0 40px rgba(102,187,106,0.15);

  --font-display: 'Barlow Condensed', sans-serif;
  --font-body:    'Outfit', sans-serif;

  --radius:  12px;
  --radius-lg: 20px;
  --nav-h:   70px;
  --transition: all 0.22s cubic-bezier(.4,0,.2,1);
}

/* ═══════════════════════════════════════════════════════
   GLOBAL RESET
═══════════════════════════════════════════════════════ */
*, *::before, *::after { box-sizing: border-box; }

.stApp {
  background: var(--bg) !important;
  font-family: var(--font-body) !important;
  color: var(--text) !important;
  /* bottom padding for fixed nav */
  padding-bottom: var(--nav-h) !important;
}

/* remove Streamlit chrome */
#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"] { display: none !important; }

/* scrollbar */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: var(--bg2); }
::-webkit-scrollbar-thumb { background: var(--bg3); border-radius: 99px; }

/* ═══════════════════════════════════════════════════════
   TYPOGRAPHY
═══════════════════════════════════════════════════════ */
h1,h2,h3 {
  font-family: var(--font-display) !important;
  letter-spacing: 0.02em;
  color: var(--text) !important;
}
.stMarkdown p { color: var(--text); }

/* ═══════════════════════════════════════════════════════
   TOP BAR
═══════════════════════════════════════════════════════ */
.topbar-greeting {
  font-family: var(--font-display);
  font-size: 1.15rem;
  font-weight: 600;
  color: var(--text-muted);
  padding: 14px 0 6px;
  letter-spacing: 0.05em;
}
.topbar-greeting span {
  color: var(--cyan);
  text-shadow: var(--glow-cyan);
}

/* ═══════════════════════════════════════════════════════
   BOTTOM NAV BAR
═══════════════════════════════════════════════════════ */
.navbar-fixed {
  position: fixed;
  bottom: 0; left: 0; right: 0;
  height: var(--nav-h);
  background: rgba(19,24,31,0.96);
  backdrop-filter: blur(20px) saturate(1.4);
  -webkit-backdrop-filter: blur(20px) saturate(1.4);
  border-top: 1px solid var(--border-lit);
  display: flex;
  align-items: center;
  justify-content: space-around;
  z-index: 9999;
  padding: 0 8px;
}
.nav-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 3px;
  cursor: pointer;
  padding: 8px 14px;
  border-radius: 10px;
  border: none;
  background: transparent;
  transition: var(--transition);
  min-width: 56px;
  text-decoration: none;
}
.nav-btn:hover { background: rgba(0,229,255,0.08); }
.nav-btn.active { background: rgba(0,229,255,0.12); }
.nav-icon {
  font-size: 1.35rem;
  line-height: 1;
}
.nav-label {
  font-family: var(--font-body);
  font-size: 0.62rem;
  font-weight: 500;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--text-muted);
  transition: var(--transition);
}
.nav-btn.active .nav-label,
.nav-btn.active .nav-icon { color: var(--cyan) !important; }
.nav-dot {
  width: 4px; height: 4px;
  border-radius: 50%;
  background: var(--cyan);
  box-shadow: var(--glow-cyan);
  margin-top: 2px;
}

/* ═══════════════════════════════════════════════════════
   CARDS
═══════════════════════════════════════════════════════ */
.card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 18px 20px;
  margin-bottom: 10px;
  transition: var(--transition);
  position: relative;
  overflow: hidden;
}
.card:hover {
  background: var(--card-hover);
  border-color: var(--border-lit);
  transform: translateY(-2px);
  box-shadow: 0 8px 32px rgba(0,0,0,0.4);
}
/* Glowing stripe on left */
.card::before {
  content: '';
  position: absolute;
  top: 0; left: 0;
  width: 3px; height: 100%;
  border-radius: 3px 0 0 3px;
  background: var(--card-accent, var(--cyan));
}

/* ── King card (M1) ────────────────────────────────── */
.card-king {
  background: linear-gradient(135deg, #1A160A 0%, #201A06 60%, #1A160A 100%);
  border: 1px solid rgba(255,215,0,0.3);
  box-shadow: 0 0 40px rgba(255,215,0,0.12), inset 0 0 60px rgba(255,215,0,0.03);
  border-radius: var(--radius-lg);
  padding: 24px;
  position: relative;
  overflow: hidden;
}
.card-king::after {
  content: '👑';
  position: absolute;
  right: 20px; top: 20px;
  font-size: 2.5rem;
  opacity: 0.15;
  transform: rotate(15deg);
}
.king-title {
  font-family: var(--font-display);
  font-size: 0.7rem;
  letter-spacing: 0.25em;
  text-transform: uppercase;
  color: var(--gold);
  font-weight: 700;
  margin-bottom: 6px;
}
.king-name {
  font-family: var(--font-display);
  font-size: 2.2rem;
  font-weight: 800;
  color: var(--gold);
  text-shadow: var(--glow-gold);
  line-height: 1.1;
}
.king-players {
  font-size: 0.82rem;
  color: rgba(255,215,0,0.6);
  margin-top: 4px;
}
.king-pts {
  font-family: var(--font-display);
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--gold);
  margin-top: 10px;
}

/* ── Ranking card ──────────────────────────────────── */
.rank-card {
  display: flex;
  align-items: center;
  gap: 12px;
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 12px 16px;
  margin-bottom: 8px;
  transition: var(--transition);
  position: relative;
  overflow: hidden;
}
.rank-card:hover {
  background: var(--card-hover);
  border-color: var(--border-lit);
  transform: translateX(4px);
}
.rank-card.mine {
  border-color: rgba(0,229,255,0.35);
  box-shadow: 0 0 20px rgba(0,229,255,0.1);
}
.rank-num {
  font-family: var(--font-display);
  font-size: 1.5rem;
  font-weight: 800;
  color: var(--text-dim);
  min-width: 32px;
  text-align: center;
}
.rank-avatar {
  width: 42px; height: 42px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid var(--border-lit);
  background: var(--bg3);
  flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
  font-size: 1.3rem;
}
.rank-info { flex: 1; min-width: 0; }
.rank-team-name {
  font-family: var(--font-display);
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.rank-players {
  font-size: 0.72rem;
  color: var(--text-muted);
  margin-top: 1px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.rank-badges { display: flex; gap: 5px; align-items: center; }
.rank-badge {
  font-size: 1.0rem;
  line-height: 1;
  filter: drop-shadow(0 0 4px rgba(0,229,255,0.6));
}
.rank-pts {
  font-family: var(--font-display);
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--text-muted);
  text-align: right;
  min-width: 52px;
}
.cat-pill {
  font-size: 0.6rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  padding: 2px 7px;
  border-radius: 99px;
  border: 1px solid;
  flex-shrink: 0;
}

/* ── Challenge card ─────────────────────────────────── */
.challenge-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 16px;
  margin-bottom: 8px;
  transition: var(--transition);
}
.challenge-card.incoming {
  border-left: 3px solid var(--orange);
  background: linear-gradient(90deg, rgba(255,152,0,0.06) 0%, var(--card) 30%);
}
.challenge-card.outgoing {
  border-left: 3px solid var(--cyan);
  background: linear-gradient(90deg, rgba(0,229,255,0.05) 0%, var(--card) 30%);
}

/* ── Match / result card ─────────────────────────────── */
.match-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 14px 18px;
  margin-bottom: 8px;
}
.score-big {
  font-family: var(--font-display);
  font-size: 2.4rem;
  font-weight: 800;
  letter-spacing: 0.05em;
}
.score-sep { color: var(--text-dim); padding: 0 8px; }

/* ─── Section headers ───────────────────────────────── */
.section-header {
  font-family: var(--font-display);
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--text-muted);
  padding: 18px 0 8px;
  border-bottom: 1px solid var(--border);
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.section-header .line {
  flex: 1;
  height: 1px;
  background: linear-gradient(90deg, var(--border-lit), transparent);
}

/* ─── Level divider ─────────────────────────────────── */
.level-divider {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 20px 0 10px;
}
.level-label {
  font-family: var(--font-display);
  font-size: 0.75rem;
  font-weight: 800;
  letter-spacing: 0.25em;
  text-transform: uppercase;
  white-space: nowrap;
  padding: 3px 12px;
  border-radius: 99px;
}
.level-line {
  flex: 1;
  height: 1px;
}

/* ─── Trunfo cards ──────────────────────────────────── */
.trunfo-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 16px;
  text-align: center;
  transition: var(--transition);
}
.trunfo-card:hover { border-color: var(--border-lit); }
.trunfo-icon { font-size: 2.2rem; margin-bottom: 6px; }
.trunfo-name {
  font-family: var(--font-display);
  font-size: 1rem;
  font-weight: 700;
  color: var(--text);
}
.trunfo-desc {
  font-size: 0.73rem;
  color: var(--text-muted);
  margin-top: 4px;
  line-height: 1.4;
}
.trunfo-qty {
  font-family: var(--font-display);
  font-size: 1.6rem;
  font-weight: 800;
  margin-top: 8px;
}

/* ─── Stat chips ─────────────────────────────────────── */
.stat-chip {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  background: var(--bg3);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 5px 10px;
  font-size: 0.78rem;
  color: var(--text-muted);
}
.stat-chip .val {
  font-family: var(--font-display);
  font-size: 1rem;
  font-weight: 700;
  color: var(--text);
}

/* ─── Action buttons ─────────────────────────────────── */
.stButton > button {
  font-family: var(--font-body) !important;
  font-weight: 600 !important;
  border-radius: 10px !important;
  border: 1px solid rgba(0,229,255,0.25) !important;
  background: rgba(0,229,255,0.08) !important;
  color: var(--cyan) !important;
  transition: var(--transition) !important;
  letter-spacing: 0.02em !important;
}
.stButton > button:hover {
  background: rgba(0,229,255,0.18) !important;
  border-color: var(--cyan) !important;
  box-shadow: 0 0 16px rgba(0,229,255,0.25) !important;
  transform: translateY(-1px) !important;
}
.stButton > button:active {
  transform: translateY(0) !important;
}

/* Primary / accent button variant */
button[data-testid*="primary"],
.btn-primary > button {
  background: linear-gradient(135deg, #0077AA, #00E5FF) !important;
  color: #000 !important;
  border: none !important;
  font-weight: 700 !important;
  box-shadow: 0 0 20px rgba(0,229,255,0.3) !important;
}

/* Danger button */
.btn-danger > button {
  background: rgba(255,82,82,0.1) !important;
  color: var(--red) !important;
  border-color: rgba(255,82,82,0.3) !important;
}

/* ─── Forms ──────────────────────────────────────────── */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stSelectbox > div > div,
.stTextArea textarea {
  background: var(--bg2) !important;
  border: 1px solid var(--border) !important;
  border-radius: 10px !important;
  color: var(--text) !important;
  font-family: var(--font-body) !important;
}
.stTextInput > div > div > input:focus,
.stTextArea textarea:focus {
  border-color: var(--cyan) !important;
  box-shadow: 0 0 0 2px rgba(0,229,255,0.15) !important;
}
.stCheckbox > label { color: var(--text-muted) !important; }
.stSelectbox label,
.stTextInput label,
.stNumberInput label { color: var(--text-muted) !important; font-size: 0.82rem !important; }

/* ─── Expander ────────────────────────────────────────── */
.streamlit-expanderHeader {
  background: var(--card) !important;
  border-radius: var(--radius) !important;
  color: var(--text) !important;
  font-family: var(--font-body) !important;
}

/* ─── Tabs (fallback for non-nav tabs) ───────────────── */
.stTabs [data-baseweb="tab-list"] {
  background: var(--bg2) !important;
  border-radius: 10px !important;
  padding: 4px !important;
  gap: 4px !important;
  border-bottom: none !important;
}
.stTabs [data-baseweb="tab"] {
  border-radius: 8px !important;
  color: var(--text-muted) !important;
  font-family: var(--font-body) !important;
  font-weight: 500 !important;
  padding: 6px 16px !important;
}
.stTabs [aria-selected="true"] {
  background: rgba(0,229,255,0.12) !important;
  color: var(--cyan) !important;
}

/* ─── Alert / info boxes ─────────────────────────────── */
.stAlert { border-radius: var(--radius) !important; }
[data-testid="stNotification"] { border-radius: var(--radius) !important; }

/* ─── Sidebar (collapsed) ────────────────────────────── */
[data-testid="stSidebar"] {
  background: var(--bg2) !important;
  border-right: 1px solid var(--border) !important;
}

/* ─── Metrics ─────────────────────────────────────────── */
[data-testid="stMetric"] {
  background: var(--card) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius) !important;
  padding: 14px 18px !important;
}
[data-testid="stMetricValue"] {
  font-family: var(--font-display) !important;
  font-size: 2rem !important;
  color: var(--cyan) !important;
}
[data-testid="stMetricLabel"] {
  color: var(--text-muted) !important;
  font-size: 0.75rem !important;
  letter-spacing: 0.1em !important;
  text-transform: uppercase !important;
}

/* ─── Progress bar ────────────────────────────────────── */
.stProgress > div > div > div {
  background: linear-gradient(90deg, var(--cyan), var(--purple)) !important;
  border-radius: 99px !important;
}

/* ─── Divider ─────────────────────────────────────────── */
hr { border-color: var(--border) !important; }

/* ─── Toast notification ─────────────────────────────── */
.toast-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: var(--red);
  color: #fff;
  font-size: 0.6rem;
  font-weight: 800;
  width: 16px; height: 16px;
  border-radius: 50%;
  position: absolute;
  top: 4px; right: 8px;
}

/* ─── Animations ──────────────────────────────────────── */
@keyframes pulse-glow {
  0%,100% { box-shadow: 0 0 8px rgba(0,229,255,0.3); }
  50%      { box-shadow: 0 0 24px rgba(0,229,255,0.6); }
}
@keyframes slide-up {
  from { opacity:0; transform: translateY(14px); }
  to   { opacity:1; transform: translateY(0); }
}
@keyframes shimmer {
  0%   { background-position: -200% 0; }
  100% { background-position:  200% 0; }
}
.animate-slide { animation: slide-up 0.35s ease forwards; }
.animate-pulse { animation: pulse-glow 2s infinite; }

/* ─── Help modal ─────────────────────────────────────── */
.help-fab {
  position: fixed;
  top: 16px; right: 16px;
  width: 36px; height: 36px;
  border-radius: 50%;
  background: rgba(0,229,255,0.12);
  border: 1px solid rgba(0,229,255,0.3);
  color: var(--cyan);
  font-weight: 700;
  font-size: 0.9rem;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer;
  z-index: 10000;
  transition: var(--transition);
}
.help-fab:hover {
  background: rgba(0,229,255,0.25);
  box-shadow: var(--glow-cyan);
}

/* ─── Guardian timer ─────────────────────────────────── */
.guardian-timer {
  font-family: var(--font-display);
  font-size: 2rem;
  font-weight: 800;
  color: var(--orange);
  text-shadow: 0 0 20px rgba(255,152,0,0.5);
  letter-spacing: 0.1em;
}

/* ─── Login screen ────────────────────────────────────── */
.login-container {
  max-width: 420px;
  margin: 60px auto 0;
  text-align: center;
}
.login-logo {
  font-family: var(--font-display);
  font-size: 3.5rem;
  font-weight: 800;
  letter-spacing: -0.02em;
  background: linear-gradient(135deg, var(--cyan), var(--purple));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 6px;
}
.login-sub {
  font-size: 0.85rem;
  color: var(--text-muted);
  letter-spacing: 0.15em;
  text-transform: uppercase;
  margin-bottom: 32px;
}

/* ─── Team profile card ───────────────────────────────── */
.profile-card {
  background: linear-gradient(135deg, #0E1A2A 0%, #0A1520 100%);
  border: 1px solid rgba(0,229,255,0.2);
  border-radius: var(--radius-lg);
  padding: 24px;
  margin-bottom: 16px;
  box-shadow: 0 0 40px rgba(0,229,255,0.07);
}
.profile-avatar {
  width: 72px; height: 72px;
  border-radius: 50%;
  border: 2px solid var(--cyan);
  box-shadow: var(--glow-cyan);
  object-fit: cover;
  background: var(--bg3);
  font-size: 2rem;
  display: flex; align-items: center; justify-content: center;
}
.profile-name {
  font-family: var(--font-display);
  font-size: 1.6rem;
  font-weight: 800;
  color: var(--cyan);
  text-shadow: var(--glow-cyan);
}

/* ─── Position change arrow ───────────────────────────── */
.arrow-up   { color: var(--green); font-size: 1rem; }
.arrow-down { color: var(--red);   font-size: 1rem; }
.arrow-same { color: var(--text-dim); font-size: 0.8rem; }

/* Pending badge in nav */
.pending-badge {
  background: var(--orange);
  color: #000;
  border-radius: 99px;
  font-size: 0.55rem;
  font-weight: 800;
  padding: 1px 5px;
  margin-left: 3px;
  vertical-align: super;
}
</style>
""", unsafe_allow_html=True)
