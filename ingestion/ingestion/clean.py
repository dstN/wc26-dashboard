import re
from typing import Optional

import pandas as pd


def _pct_to_float(val) -> Optional[float]:
    if pd.isna(val):
        return None
    s = str(val).replace("%", "").strip()
    try:
        return float(s)
    except ValueError:
        return None


def _to_int(val) -> Optional[int]:
    if pd.isna(val):
        return None
    try:
        return int(val)
    except (ValueError, TypeError):
        return None


def _to_float(val) -> Optional[float]:
    if pd.isna(val):
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


_PCT_COLS = {
    "possession_pct", "in_contest_pct", "out_of_possession_pct",
    "tackles_won_pct", "press_success_pct", "forced_turnover_pct",
    "pressure_ball_heavy_pct", "pressure_moderate_pct",
    "in_poss_pct", "out_poss_pct",
    "def_line_height_pct", "pressure_high_pct", "pressure_mid_pct", "pressure_low_pct",
    "success_pct",
}
_FLOAT_COLS = {"xg", "recovery_speed"}
_INT_COLS = {"goals", "shots", "breaks_for", "breaks_against", "entry_count", "action_count"}


def clean(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for col in df.columns:
        if col in _PCT_COLS:
            df[col] = df[col].apply(_pct_to_float)
        elif col in _FLOAT_COLS:
            df[col] = df[col].apply(_to_float)
        elif col in _INT_COLS:
            df[col] = df[col].apply(_to_int)
        elif col == "team_name":
            df[col] = df[col].apply(lambda v: re.sub(r"\s+", " ", str(v).strip()) if not pd.isna(v) else v)
    return df.dropna(how="all")
