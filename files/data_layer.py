"""
data_layer.py  —  All Google Sheets read/write operations.
"""

import streamlit as st
import pandas as pd
import hashlib
import random
from datetime import datetime, timezone, timedelta
from config import (
    SHEET_TEAMS, SHEET_RANKING, SHEET_CHALLENGES,
    SHEET_MATCHES, SHEET_TRUNFOS, SHEET_PENDING,
    TEAMS_COLS, RANKING_COLS, CHALLENGES_COLS,
    MATCHES_COLS, TRUNFOS_COLS, PENDING_COLS,
    CATEGORY_SIZES, ADMIN_ID,
)


# ─── Utilities ────────────────────────────────────────────────────────────────
def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def parse_iso(s):
    if not s or str(s).strip() in ("", "nan", "None"):
        return None
    try:
        dt = datetime.fromisoformat(str(s))
        return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt
    except Exception:
        return None


def assign_categories(ranking_df: pd.DataFrame) -> pd.DataFrame:
    r = ranking_df.copy()
    r["position"] = pd.to_numeric(r["position"], errors="coerce").fillna(999).astype(int)
    r = r.sort_values("position").reset_index(drop=True)
    cursor = 1
    for cat, size in CATEGORY_SIZES.items():
        mask = (r["position"] >= cursor) & (r["position"] < cursor + size)
        r.loc[mask, "category"] = cat
        cursor += size
    r["category"] = r["category"].fillna("M5")
    return r


# ─── Connection ───────────────────────────────────────────────────────────────
def get_conn():
    from streamlit_gsheets import GSheetsConnection
    return st.connection("gsheets", type=GSheetsConnection)


# ─── Init ─────────────────────────────────────────────────────────────────────
def _get_gspread_wb():
    """Open the Spreadsheet using gspread + service account credentials directly."""
    import gspread
    from google.oauth2.service_account import Credentials

    s = st.secrets["connections"]["gsheets"]

    creds = Credentials.from_service_account_info(
        {
            "type":                        s["type"],
            "project_id":                  s["project_id"],
            "private_key_id":              s["private_key_id"],
            "private_key":                 s["private_key"],
            "client_email":                s["client_email"],
            "client_id":                   s["client_id"],
            "auth_uri":                    s["auth_uri"],
            "token_uri":                   s["token_uri"],
            "auth_provider_x509_cert_url": s["auth_provider_x509_cert_url"],
            "client_x509_cert_url":        s["client_x509_cert_url"],
        },
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ],
    )
    client = gspread.authorize(creds)

    raw_url = str(s["spreadsheet"])
    if "/spreadsheets/d/" in raw_url:
        sid = raw_url.split("/spreadsheets/d/")[1].split("/")[0].split("?")[0].strip()
    else:
        sid = raw_url.strip()
    return client.open_by_key(sid)


def _ensure_worksheet(wb, sheet_name):
    """Create worksheet tab if it doesn't already exist."""
    existing = [ws.title for ws in wb.worksheets()]
    if sheet_name not in existing:
        wb.add_worksheet(title=sheet_name, rows=1000, cols=30)
        return True
    return False


def init_all_sheets(conn):
    """Ensure all required worksheet tabs exist, then seed empty ones."""
    try:
        wb = _get_gspread_wb()
    except Exception as e:
        st.error(f"Não foi possível aceder à Spreadsheet: {e}")
        st.stop()

    sheets_config = [
        (SHEET_TEAMS,      TEAMS_COLS,      _seed_teams),
        (SHEET_RANKING,    RANKING_COLS,    None),
        (SHEET_CHALLENGES, CHALLENGES_COLS, None),
        (SHEET_MATCHES,    MATCHES_COLS,    None),
        (SHEET_TRUNFOS,    TRUNFOS_COLS,    None),
        (SHEET_PENDING,    PENDING_COLS,    None),
    ]

    for sheet, cols, seed_fn in sheets_config:
        # 1. Create the tab if missing
        _ensure_worksheet(wb, sheet)
        # 2. Check if it has data already
        try:
            df = conn.read(worksheet=sheet, ttl=0)
            has_data = (df is not None and not df.empty and len(df.columns) > 0)
        except Exception:
            has_data = False
        # 3. Seed with headers (+ default rows) if empty
        if not has_data:
            empty = pd.DataFrame(columns=cols)
            if seed_fn:
                empty = seed_fn(empty)
            try:
                conn.update(worksheet=sheet, data=empty)
            except Exception as e:
                st.warning(f"Aviso: não foi possível inicializar sheet '{sheet}': {e}")

    # 4. Always ensure admin user exists (in case teams sheet was created empty)
    _ensure_admin_exists(conn)


def _ensure_admin_exists(conn):
    """Guarantee the admin row is always present in the teams sheet."""
    try:
        df = conn.read(worksheet=SHEET_TEAMS, ttl=0)
        if df is None:
            df = pd.DataFrame(columns=TEAMS_COLS)
        for c in TEAMS_COLS:
            if c not in df.columns:
                df[c] = ""
        if ADMIN_ID not in df["team_id"].astype(str).values:
            admin_hash = hashlib.sha256("admin2024".encode()).hexdigest()
            row = {c: "" for c in TEAMS_COLS}
            row.update({
                "team_id": ADMIN_ID, "team_name": "Administrador",
                "player1": "Admin", "player2": "",
                "password_hash": admin_hash, "is_admin": "TRUE",
                "photo_url": "", "wins": 0, "losses": 0,
                "streak": 0, "total_matches": 0,
                "last_match_date": "", "created_at": _now_iso(),
            })
            df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
            conn.update(worksheet=SHEET_TEAMS, data=df)
    except Exception:
        pass  # will retry on next boot


def _seed_teams(df):
    admin_hash = hashlib.sha256("admin2024".encode()).hexdigest()
    row = {c: "" for c in TEAMS_COLS}
    row.update({
        "team_id": ADMIN_ID, "team_name": "Administrador",
        "player1": "Admin", "player2": "",
        "password_hash": admin_hash, "is_admin": "TRUE",
        "photo_url": "", "wins": 0, "losses": 0,
        "streak": 0, "total_matches": 0,
        "last_match_date": "", "created_at": _now_iso(),
    })
    return pd.concat([df, pd.DataFrame([row])], ignore_index=True)


# ─── Read helpers ──────────────────────────────────────────────────────────────
def load_all(conn) -> dict:
    return {
        "teams":      _read(conn, SHEET_TEAMS,      TEAMS_COLS),
        "ranking":    _read(conn, SHEET_RANKING,    RANKING_COLS),
        "challenges": _read(conn, SHEET_CHALLENGES, CHALLENGES_COLS),
        "matches":    _read(conn, SHEET_MATCHES,    MATCHES_COLS),
        "trunfos":    _read(conn, SHEET_TRUNFOS,    TRUNFOS_COLS),
        "pending":    _read(conn, SHEET_PENDING,    PENDING_COLS),
    }


def _read(conn, sheet, cols):
    try:
        df = conn.read(worksheet=sheet, ttl=5)
        if df is None or df.empty:
            return pd.DataFrame(columns=cols)
        for c in cols:
            if c not in df.columns:
                df[c] = ""
        return df[cols].copy()
    except Exception:
        return pd.DataFrame(columns=cols)


# ─── Write helpers ────────────────────────────────────────────────────────────
def _save(conn, sheet, df):
    conn.update(worksheet=sheet, data=df)
    st.cache_data.clear()


def save_teams(conn, df):      _save(conn, SHEET_TEAMS,      df)
def save_ranking(conn, df):    _save(conn, SHEET_RANKING,    df)
def save_challenges(conn, df): _save(conn, SHEET_CHALLENGES, df)
def save_matches(conn, df):    _save(conn, SHEET_MATCHES,    df)
def save_trunfos(conn, df):    _save(conn, SHEET_TRUNFOS,    df)
def save_pending(conn, df):    _save(conn, SHEET_PENDING,    df)


# ─── Auth ─────────────────────────────────────────────────────────────────────
def verify_login(teams_df, team_id: str, password: str):
    ph  = hashlib.sha256(password.encode()).hexdigest()
    row = teams_df[teams_df["team_id"] == team_id]
    if row.empty:
        return None
    r = row.iloc[0]
    if str(r["password_hash"]) != ph:
        return None
    return r.to_dict()


# ─── Team mutations ───────────────────────────────────────────────────────────
def add_team(conn, data, team_id, team_name, player1, player2, password, category="M5"):
    teams   = data["teams"].copy()
    ranking = data["ranking"].copy()
    trunfos = data["trunfos"].copy()

    ph = hashlib.sha256(password.encode()).hexdigest()
    team_row = {c: "" for c in TEAMS_COLS}
    team_row.update({
        "team_id": team_id, "team_name": team_name,
        "player1": player1, "player2": player2,
        "password_hash": ph, "is_admin": "FALSE",
        "photo_url": "", "wins": 0, "losses": 0,
        "streak": 0, "total_matches": 0,
        "last_match_date": "", "created_at": _now_iso(),
    })
    teams = pd.concat([teams, pd.DataFrame([team_row])], ignore_index=True)
    save_teams(conn, teams)

    if not ranking.empty:
        pos = int(pd.to_numeric(ranking["position"], errors="coerce").max() or 0) + 1
    else:
        pos = 1
    rank_row = {c: "" for c in RANKING_COLS}
    rank_row.update({
        "team_id": team_id, "team_name": team_name,
        "position": pos, "category": category,
        "points": 0, "prev_position": pos,
        "guardian_since": "", "immune_until": "",
        "ready_to_climb": "FALSE", "trunfo_salto_active": "FALSE",
    })
    ranking = pd.concat([ranking, pd.DataFrame([rank_row])], ignore_index=True)
    save_ranking(conn, ranking)

    tr_row = {
        "team_id": team_id, "desforra_qty": 1,
        "salto_qty": 1, "escudo_qty": 1, "last_trunfo_month": "",
    }
    trunfos = pd.concat([trunfos, pd.DataFrame([tr_row])], ignore_index=True)
    save_trunfos(conn, trunfos)


# ─── Challenge mutations ──────────────────────────────────────────────────────
def create_challenge(conn, data, challenger_id, challenger_name,
                     defender_id, defender_name, trunfo=""):
    challenges = data["challenges"].copy()
    cid = f"C{len(challenges)+1:04d}"
    row = {c: "" for c in CHALLENGES_COLS}
    row.update({
        "challenge_id": cid, "timestamp": _now_iso(),
        "challenger_id": challenger_id, "challenger_name": challenger_name,
        "defender_id": defender_id, "defender_name": defender_name,
        "status": "pending", "trunfo_used": trunfo, "scheduled_date": "",
    })
    challenges = pd.concat([challenges, pd.DataFrame([row])], ignore_index=True)
    save_challenges(conn, challenges)
    return cid


def update_challenge_status(conn, data, challenge_id, status):
    ch = data["challenges"].copy()
    ch.loc[ch["challenge_id"] == challenge_id, "status"] = status
    save_challenges(conn, ch)


# ─── Match mutations ──────────────────────────────────────────────────────────
def submit_match(conn, data, team_a_id, team_a_name, team_b_id, team_b_name,
                 score_a, score_b, set1_a, set1_b, set2_a, set2_b,
                 set3_a, set3_b, suplente, challenge_id, submitted_by):
    matches = data["matches"].copy()
    mid = f"M{len(matches)+1:04d}"
    row = {c: "" for c in MATCHES_COLS}
    row.update({
        "match_id": mid, "timestamp": _now_iso(),
        "team_a_id": team_a_id, "team_a_name": team_a_name,
        "team_b_id": team_b_id, "team_b_name": team_b_name,
        "score_a": score_a, "score_b": score_b,
        "set1_a": set1_a, "set1_b": set1_b,
        "set2_a": set2_a, "set2_b": set2_b,
        "set3_a": set3_a or "", "set3_b": set3_b or "",
        "winner_id": "", "loser_id": "",
        "pts_winner": "", "pts_loser": "",
        "suplente_used": str(suplente),
        "validation_status": "pending",
        "submitted_by": submitted_by, "confirmed_by": "",
        "challenge_id": challenge_id,
    })
    matches = pd.concat([matches, pd.DataFrame([row])], ignore_index=True)
    save_matches(conn, matches)
    return mid


def confirm_match(conn, data, match_id, confirmed_by):
    from logic import calc_points
    matches = data["matches"].copy()
    row_idx = matches[matches["match_id"] == match_id].index
    if row_idx.empty:
        return False
    idx = row_idx[0]
    m = matches.loc[idx]

    sa = int(m["score_a"] or 0)
    sb = int(m["score_b"] or 0)
    suplente = str(m["suplente_used"]).upper() == "TRUE"
    winner_id = m["team_a_id"] if sa > sb else m["team_b_id"]
    loser_id  = m["team_b_id"] if sa > sb else m["team_a_id"]
    is_ch     = (winner_id == m["team_a_id"])
    pts_w, pts_l = calc_points(is_challenger=is_ch, suplente=suplente)

    matches.loc[idx, "winner_id"]         = winner_id
    matches.loc[idx, "loser_id"]          = loser_id
    matches.loc[idx, "pts_winner"]        = pts_w
    matches.loc[idx, "pts_loser"]         = pts_l
    matches.loc[idx, "validation_status"] = "confirmed"
    matches.loc[idx, "confirmed_by"]      = confirmed_by
    save_matches(conn, matches)

    _apply_match_to_ranking(conn, data, m, winner_id, loser_id, pts_w, pts_l)
    _update_team_stats(conn, data, winner_id, loser_id)
    return True


def contest_match(conn, data, match_id):
    matches = data["matches"].copy()
    idx = matches[matches["match_id"] == match_id].index
    if not idx.empty:
        matches.loc[idx, "validation_status"] = "contested"
        save_matches(conn, matches)


def admin_override_match(conn, data, match_id):
    matches = data["matches"].copy()
    idx = matches[matches["match_id"] == match_id].index
    if idx.empty:
        return
    matches.loc[idx, "validation_status"] = "admin_override"
    save_matches(conn, matches)
    confirm_match(conn, data, match_id, "admin")


def _apply_match_to_ranking(conn, data, match_row, winner_id, loser_id, pts_w, pts_l):
    ranking = data["ranking"].copy()
    ch_id   = str(match_row["team_a_id"])
    def_id  = str(match_row["team_b_id"])

    for tid, pts in [(winner_id, pts_w), (loser_id, pts_l)]:
        mask = ranking["team_id"] == tid
        if mask.any():
            ranking.loc[mask, "prev_position"] = ranking.loc[mask, "position"]
            cur = int(pd.to_numeric(ranking.loc[mask, "points"], errors="coerce").values[0] or 0)
            ranking.loc[mask, "points"] = max(0, cur + pts)

    # Swap positions if challenger won and was below
    if winner_id == ch_id:
        ch_mask  = ranking["team_id"] == ch_id
        def_mask = ranking["team_id"] == def_id
        if ch_mask.any() and def_mask.any():
            ch_pos  = int(pd.to_numeric(ranking.loc[ch_mask,  "position"], errors="coerce").values[0])
            def_pos = int(pd.to_numeric(ranking.loc[def_mask, "position"], errors="coerce").values[0])
            if ch_pos > def_pos:
                ranking.loc[ch_mask,  "position"] = def_pos
                ranking.loc[def_mask, "position"] = ch_pos
                _check_guardian(ranking, ch_id)

    save_ranking(conn, ranking)


def _check_guardian(ranking, team_id):
    ranking = assign_categories(ranking)
    row = ranking[ranking["team_id"] == team_id]
    if row.empty:
        return
    r   = row.iloc[0]
    cat = r["category"]
    if cat == "M1":
        return
    cat_rows = ranking[ranking["category"] == cat]
    min_pos  = int(cat_rows["position"].min())
    if int(r["position"]) == min_pos:
        mask = ranking["team_id"] == team_id
        gs   = str(ranking.loc[mask, "guardian_since"].values[0])
        if gs.strip() in ("", "nan", "None"):
            ranking.loc[mask, "guardian_since"] = _now_iso()
            ranking.loc[mask, "ready_to_climb"]  = "FALSE"


def _update_team_stats(conn, data, winner_id, loser_id):
    teams = data["teams"].copy()
    now   = _now_iso()
    for tid, won in [(winner_id, True), (loser_id, False)]:
        mask = teams["team_id"] == tid
        if not mask.any():
            continue
        w  = int(pd.to_numeric(teams.loc[mask, "wins"],         errors="coerce").values[0] or 0)
        l  = int(pd.to_numeric(teams.loc[mask, "losses"],       errors="coerce").values[0] or 0)
        s  = int(pd.to_numeric(teams.loc[mask, "streak"],       errors="coerce").values[0] or 0)
        tm = int(pd.to_numeric(teams.loc[mask, "total_matches"],errors="coerce").values[0] or 0)
        teams.loc[mask, "total_matches"]   = tm + 1
        teams.loc[mask, "last_match_date"] = now
        if won:
            teams.loc[mask, "wins"]   = w + 1
            teams.loc[mask, "streak"] = s + 1
        else:
            teams.loc[mask, "losses"] = l + 1
            teams.loc[mask, "streak"] = 0
    save_teams(conn, teams)
    _check_trunfo_bonus(conn, data, winner_id, loser_id, teams)


def _check_trunfo_bonus(conn, data, winner_id, loser_id, teams_df):
    trunfos   = data["trunfos"].copy()
    bonus_cols = ["desforra_qty", "salto_qty", "escudo_qty"]
    changed   = False
    for tid in [winner_id, loser_id]:
        tmask = teams_df["team_id"] == tid
        if not tmask.any():
            continue
        streak = int(pd.to_numeric(teams_df.loc[tmask, "streak"],        errors="coerce").values[0] or 0)
        total  = int(pd.to_numeric(teams_df.loc[tmask, "total_matches"],  errors="coerce").values[0] or 0)
        bonus  = (streak > 0 and streak % 5 == 0) or (total > 0 and total % 10 == 0)
        if bonus:
            fmask = trunfos["team_id"] == tid
            if fmask.any():
                col = random.choice(bonus_cols)
                cur = int(pd.to_numeric(trunfos.loc[fmask, col], errors="coerce").values[0] or 0)
                trunfos.loc[fmask, col] = cur + 1
                changed = True
    if changed:
        save_trunfos(conn, trunfos)


# ─── Trunfo use ───────────────────────────────────────────────────────────────
def use_trunfo(conn, data, team_id, trunfo_type):
    trunfos    = data["trunfos"].copy()
    mask       = trunfos["team_id"] == team_id
    if not mask.any():
        return False
    last_month = str(trunfos.loc[mask, "last_trunfo_month"].values[0]).strip()
    this_month = datetime.now(timezone.utc).strftime("%Y-%m")
    if last_month == this_month:
        return False
    col_map = {"desforra": "desforra_qty", "salto": "salto_qty", "escudo": "escudo_qty"}
    col = col_map.get(trunfo_type)
    if not col:
        return False
    qty = int(pd.to_numeric(trunfos.loc[mask, col], errors="coerce").values[0] or 0)
    if qty <= 0:
        return False
    trunfos.loc[mask, col]                 = qty - 1
    trunfos.loc[mask, "last_trunfo_month"] = this_month
    save_trunfos(conn, trunfos)
    return True


def apply_escudo(conn, data, team_id):
    from logic import immune_until_iso
    ranking = data["ranking"].copy()
    mask    = ranking["team_id"] == team_id
    ranking.loc[mask, "immune_until"] = immune_until_iso()
    save_ranking(conn, ranking)


# ─── Pending edits ────────────────────────────────────────────────────────────
def submit_edit_request(conn, data, team_id, field, old_val, new_val):
    pending = data["pending"].copy()
    eid  = f"E{len(pending)+1:04d}"
    row  = {
        "edit_id": eid, "timestamp": _now_iso(),
        "team_id": team_id, "field": field,
        "old_value": str(old_val), "new_value": str(new_val),
        "status": "pending",
    }
    pending = pd.concat([pending, pd.DataFrame([row])], ignore_index=True)
    save_pending(conn, pending)


def approve_edit(conn, data, edit_id):
    pending = data["pending"].copy()
    idx     = pending[pending["edit_id"] == edit_id].index
    if idx.empty:
        return
    edit = pending.loc[idx[0]]
    pending.loc[idx, "status"] = "approved"
    save_pending(conn, pending)
    teams = data["teams"].copy()
    mask  = teams["team_id"] == edit["team_id"]
    teams.loc[mask, edit["field"]] = edit["new_value"]
    save_teams(conn, teams)


def reject_edit(conn, data, edit_id):
    pending = data["pending"].copy()
    idx     = pending[pending["edit_id"] == edit_id].index
    if not idx.empty:
        pending.loc[idx, "status"] = "rejected"
        save_pending(conn, pending)
