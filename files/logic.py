"""
logic.py  —  Pure business-logic. No Streamlit, no I/O.
"""

from datetime import datetime, timezone, timedelta
import pandas as pd
from config import (
    GUARDIAN_HOURS, IMMUNE_DAYS, CHALLENGE_WINDOW,
    PTS_WIN_CHALLENGER, PTS_WIN_DEFENDER, PTS_LOSS, PTS_WO, PTS_WIN_SUPLENTE,
    LEVEL_COLORS, LEVEL_GLOW,
)


# ─── Time helpers ─────────────────────────────────────────────────────────────
def now_utc():
    return datetime.now(timezone.utc)


def parse_iso(s):
    if not s or str(s).strip() in ("", "nan", "None"):
        return None
    try:
        dt = datetime.fromisoformat(str(s))
        return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt
    except Exception:
        return None


def immune_until_iso() -> str:
    return (now_utc() + timedelta(days=IMMUNE_DAYS)).isoformat()


def is_immune(row) -> bool:
    dt = parse_iso(str(row.get("immune_until", "")))
    return dt is not None and now_utc() < dt


def guardian_remaining(row) -> timedelta | None:
    dt = parse_iso(str(row.get("guardian_since", "")))
    if dt is None:
        return None
    elapsed   = now_utc() - dt
    remaining = timedelta(hours=GUARDIAN_HOURS) - elapsed
    return remaining if remaining.total_seconds() > 0 else None


def is_ready_to_climb(row) -> bool:
    return str(row.get("ready_to_climb", "FALSE")).upper() == "TRUE"


# ─── Challenge eligibility ────────────────────────────────────────────────────
def can_challenge(my_row: dict, target_row: dict, use_salto=False) -> tuple[bool, str]:
    """Return (allowed, reason)."""
    if is_immune(target_row):
        return False, "🛡️ Equipa alvo está imune."
    my_pos  = int(my_row.get("position", 9999))
    tgt_pos = int(target_row.get("position", 9999))
    if tgt_pos >= my_pos:
        return False, "Só podes desafiar equipas acima de ti."
    window = 99 if use_salto else CHALLENGE_WINDOW
    if (my_pos - tgt_pos) > window:
        return False, f"Fora do alcance (máx {CHALLENGE_WINDOW} posições, usa Salto de Fé para mais)."
    return True, "OK"


def can_challenge_level_up(my_row: dict) -> tuple[bool, str]:
    """Check if a team that hit #1 in its level may now challenge the level above."""
    remaining = guardian_remaining(my_row)
    if remaining is not None:
        h = int(remaining.total_seconds() // 3600)
        m = int((remaining.total_seconds() % 3600) // 60)
        return False, f"⏳ Guardião: {h}h {m}m restantes"
    if not is_ready_to_climb(my_row):
        return False, "Ainda não atingiste o 1.º lugar do teu nível."
    return True, "OK"


# ─── Score + points ───────────────────────────────────────────────────────────
def calc_points(is_challenger: bool, suplente: bool) -> tuple[int, int]:
    """Return (pts_winner, pts_loser)."""
    if is_challenger:
        pts_w = PTS_WIN_SUPLENTE if suplente else PTS_WIN_CHALLENGER
    else:
        pts_w = PTS_WIN_DEFENDER
    return pts_w, PTS_LOSS


def calc_wo_points(wo_team_is_challenger: bool) -> tuple[int, int]:
    """Return (pts_team_a, pts_team_b). team_a = challenger."""
    if wo_team_is_challenger:
        return PTS_WO, PTS_WIN_DEFENDER
    return PTS_WIN_CHALLENGER, PTS_WO


def determine_winner_sets(s1a, s1b, s2a, s2b, s3a=None, s3b=None) -> str | None:
    """'A' | 'B' | None if invalid."""
    try:
        sets_a = (1 if int(s1a) > int(s1b) else 0) + (1 if int(s2a) > int(s2b) else 0)
        sets_b = (1 if int(s1b) > int(s1a) else 0) + (1 if int(s2b) > int(s2a) else 0)
        if sets_a == 2:
            return "A"
        if sets_b == 2:
            return "B"
        if s3a is not None and s3b is not None:
            return "A" if int(s3a) > int(s3b) else "B"
        return None
    except Exception:
        return None


# ─── Ranking display helpers ──────────────────────────────────────────────────
def position_arrow(prev_pos, curr_pos) -> str:
    try:
        d = int(prev_pos) - int(curr_pos)
        if d > 0:
            return f'<span class="arrow-up">🔼 +{d}</span>'
        if d < 0:
            return f'<span class="arrow-down">🔽 {d}</span>'
        return '<span class="arrow-same">—</span>'
    except Exception:
        return ""


def team_badges(row: dict, streak: int = 0) -> str:
    badges = []
    if is_immune(row):
        badges.append('<span class="rank-badge" title="Imune">🛡️</span>')
    rem = guardian_remaining(row)
    if rem:
        badges.append('<span class="rank-badge" title="Guardião activo">⏳</span>')
    elif is_ready_to_climb(row):
        badges.append('<span class="rank-badge" title="Pronto a subir">⚔️</span>')
    if streak >= 5:
        badges.append('<span class="rank-badge" title="Streak 5+">🔥</span>')
    return "".join(badges)


def level_pill_html(cat: str) -> str:
    color = LEVEL_COLORS.get(cat, "#aaa")
    return (
        f'<span class="cat-pill" style="color:{color}; border-color:{color}; '
        f'background:{color}18;">{cat}</span>'
    )


def level_divider_html(cat: str) -> str:
    color = LEVEL_COLORS.get(cat, "#aaa")
    glow  = LEVEL_GLOW.get(cat, "rgba(255,255,255,0.1)")
    return f"""
<div class="level-divider">
  <span class="level-label" style="color:{color}; background:{color}18; border:1px solid {color}44;">
    {cat}
  </span>
  <div class="level-line" style="background:linear-gradient(90deg,{color}55,transparent);"></div>
</div>"""


def format_guardian_timer(remaining: timedelta) -> str:
    total_s = int(remaining.total_seconds())
    h = total_s // 3600
    m = (total_s % 3600) // 60
    s = total_s % 60
    return f"{h:02d}:{m:02d}:{s:02d}"
