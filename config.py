"""
config.py  —  Global constants and configuration.
"""

# ── Sheet names ────────────────────────────────────────────────────────────────
SHEET_TEAMS     = "teams"
SHEET_RANKING   = "ranking"
SHEET_CHALLENGES = "challenges"
SHEET_MATCHES   = "matches"
SHEET_TRUNFOS   = "trunfos"
SHEET_PENDING   = "pending_edits"

# ── Column schemas ─────────────────────────────────────────────────────────────
TEAMS_COLS = [
    "team_id", "team_name", "player1", "player2",
    "password_hash", "is_admin", "photo_url",
    "wins", "losses", "streak", "total_matches",
    "last_match_date", "created_at",
]

RANKING_COLS = [
    "team_id", "team_name", "position", "category",
    "points", "prev_position",
    "guardian_since",   # ISO or ""
    "immune_until",     # ISO or ""
    "ready_to_climb",   # TRUE/FALSE
    "trunfo_salto_active",  # TRUE/FALSE  — Salto de Fé active this match
]

CHALLENGES_COLS = [
    "challenge_id", "timestamp",
    "challenger_id", "challenger_name",
    "defender_id",   "defender_name",
    "status",   # pending | accepted | rejected | played | cancelled
    "trunfo_used",   # "" | desforra | salto | escudo
    "scheduled_date",
]

MATCHES_COLS = [
    "match_id", "timestamp",
    "team_a_id", "team_a_name",
    "team_b_id", "team_b_name",
    "score_a", "score_b",
    "set1_a", "set1_b", "set2_a", "set2_b", "set3_a", "set3_b",
    "winner_id", "loser_id",
    "pts_winner", "pts_loser",
    "suplente_used",   # TRUE/FALSE
    "validation_status",  # pending | confirmed | contested | admin_override
    "submitted_by", "confirmed_by",
    "challenge_id",
]

TRUNFOS_COLS = [
    "team_id",
    "desforra_qty", "salto_qty", "escudo_qty",
    "last_trunfo_month",  # YYYY-MM or ""
]

PENDING_COLS = [
    "edit_id", "timestamp", "team_id",
    "field", "old_value", "new_value",
    "status",  # pending | approved | rejected
]

# ── Category boundaries (by position in unified ladder) ───────────────────────
# Adjust sizes to taste; M1 is always position 1 only.
CATEGORY_SIZES = {
    "M1": 1,
    "M2": 4,
    "M3": 6,
    "M4": 8,
    "M5": 999,  # everyone else
}

# ── Level colours (used in CSS and Python) ────────────────────────────────────
LEVEL_COLORS = {
    "M1": "#FFD700",
    "M2": "#00E5FF",
    "M3": "#CE93D8",
    "M4": "#FF9800",
    "M5": "#66BB6A",
}
LEVEL_GLOW = {
    "M1": "rgba(255,215,0,0.45)",
    "M2": "rgba(0,229,255,0.35)",
    "M3": "rgba(206,147,216,0.35)",
    "M4": "rgba(255,152,0,0.35)",
    "M5": "rgba(102,187,106,0.35)",
}

# ── Scoring ────────────────────────────────────────────────────────────────────
PTS_WIN_CHALLENGER  = 5
PTS_WIN_DEFENDER    = 3
PTS_LOSS            = 1
PTS_WO              = -10
PTS_WIN_SUPLENTE    = 2
PTS_INACTIVITY      = -5
INACTIVITY_DAYS     = 15

# ── Guardian / Trunfos ────────────────────────────────────────────────────────
GUARDIAN_HOURS      = 168   # 7 days
IMMUNE_DAYS         = 10
DESFORRA_HOURS      = 72
CHALLENGE_WINDOW    = 3     # positions above allowed without trunfo
STREAK_BONUS_AT     = 5
MATCHES_BONUS_AT    = 10

# ── Navigation items ──────────────────────────────────────────────────────────
NAV_ITEMS = [
    ("home",       "🏠", "Home"),
    ("ranking",    "🏅", "Ranking"),
    ("challenges", "⚔️",  "Desafios"),
    ("teams",      "👥", "Equipas"),
    ("results",    "📋", "Resultados"),
]

ADMIN_ID = "admin"
