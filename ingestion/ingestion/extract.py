import logging
from typing import Optional

import pandas as pd

from ingestion.fetch import fetch_tables
from ingestion.render import render_tables

logger = logging.getLogger(__name__)

# Column aliases the site uses for each subpage table
_GENERAL_COLS = {
    "Team": "team_name",
    "Poss %": "possession_pct",
    "In Contest %": "in_contest_pct",
    "Out of Poss %": "out_of_possession_pct",
    "xG": "xg",
    "Goals": "goals",
    "Shots": "shots",
    "Tackles Won %": "tackles_won_pct",
    "Press Success %": "press_success_pct",
    "Forced Turnover %": "forced_turnover_pct",
    "Recovery Speed": "recovery_speed",
    "Pressure (Ball Heavy) %": "pressure_ball_heavy_pct",
    "Pressure (Moderate) %": "pressure_moderate_pct",
}

_PHASES_COLS = {
    "Team": "team_name",
    "Phase": "phase_name",
    "Group": "phase_group",
    "In-Possession %": "in_poss_pct",
    "Out-of-Possession %": "out_poss_pct",
}

_LINE_BREAKS_COLS = {
    "Team": "team_name",
    "Line Type": "line_type",
    "For": "breaks_for",
    "Against": "breaks_against",
}

_SPATIAL_COLS = {
    "Team": "team_name",
    "Zone": "spatial_zone",
    "Defensive Line Height %": "def_line_height_pct",
    "Pressure High %": "pressure_high_pct",
    "Pressure Mid %": "pressure_mid_pct",
    "Pressure Low %": "pressure_low_pct",
}

_FINAL_THIRD_COLS = {
    "Team": "team_name",
    "Zone": "zone_name",
    "Count": "entry_count",
    "xG": "xg",
}

_DEFENSIVE_COLS = {
    "Team": "team_name",
    "Action": "action_type",
    "Count": "action_count",
    "Success %": "success_pct",
    "Zone": "zone",
}

_SUBPAGE_MAP = {
    "general": _GENERAL_COLS,
    "phases": _PHASES_COLS,
    "line-breaks": _LINE_BREAKS_COLS,
    "spatial": _SPATIAL_COLS,
    "final-third": _FINAL_THIRD_COLS,
    "defensive": _DEFENSIVE_COLS,
}


def _first_matching(tables: list[pd.DataFrame], col_map: dict) -> Optional[pd.DataFrame]:
    required = set(col_map.keys())
    for df in tables:
        if required.issubset(set(df.columns)):
            return df.rename(columns=col_map)[list(col_map.values())]
    # Fuzzy: at least half the cols present
    for df in tables:
        overlap = required & set(df.columns)
        if len(overlap) >= len(required) // 2:
            partial_map = {k: v for k, v in col_map.items() if k in df.columns}
            return df.rename(columns=partial_map)[list(partial_map.values())]
    return None


async def extract(url: str, subpage: str) -> Optional[pd.DataFrame]:
    col_map = _SUBPAGE_MAP.get(subpage)
    if col_map is None:
        raise ValueError(f"Unknown subpage: {subpage!r}")

    tables = await fetch_tables(url)
    if not tables:
        logger.info("Fast path failed, trying Playwright for %s", url)
        tables = await render_tables(url)
    if not tables:
        logger.error("No tables found at %s", url)
        return None

    df = _first_matching(tables, col_map)
    if df is None:
        logger.warning("No matching table for subpage %r at %s", subpage, url)
    return df
