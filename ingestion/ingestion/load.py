"""Upsert extracted DataFrames into MySQL via SQLAlchemy core."""
import logging
from typing import Optional

import pandas as pd
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


async def upsert_team_stats(
    session: AsyncSession,
    df: pd.DataFrame,
    team_id: int,
    match_id: Optional[int],
    scope: str,
) -> int:
    """Insert or update rows in match_stats. Returns rows affected."""
    if df is None or df.empty:
        return 0

    rows = df.to_dict(orient="records")
    affected = 0
    for row in rows:
        cols = list(row.keys())
        placeholders = ", ".join(f":{c}" for c in cols)
        updates = ", ".join(f"{c} = VALUES({c})" for c in cols if c != "team_name")
        sql = text(
            f"INSERT INTO match_stats (team_id, match_id, scope, {', '.join(cols)}) "
            f"VALUES (:_team_id, :_match_id, :_scope, {placeholders}) "
            f"ON DUPLICATE KEY UPDATE {updates}"
        )
        params = {**row, "_team_id": team_id, "_match_id": match_id, "_scope": scope}
        result = await session.execute(sql, params)
        affected += result.rowcount
    return affected


async def upsert_phases(
    session: AsyncSession,
    df: pd.DataFrame,
    team_id: int,
    match_id: Optional[int],
) -> int:
    if df is None or df.empty:
        return 0
    affected = 0
    for row in df.to_dict(orient="records"):
        sql = text(
            "INSERT INTO phases (team_id, match_id, phase_name, phase_group, in_poss_pct, out_poss_pct) "
            "VALUES (:team_id, :match_id, :phase_name, :phase_group, :in_poss_pct, :out_poss_pct) "
            "ON DUPLICATE KEY UPDATE in_poss_pct=VALUES(in_poss_pct), out_poss_pct=VALUES(out_poss_pct)"
        )
        result = await session.execute(
            sql,
            {**row, "team_id": team_id, "match_id": match_id},
        )
        affected += result.rowcount
    return affected


async def upsert_line_breaks(
    session: AsyncSession,
    df: pd.DataFrame,
    team_id: int,
    match_id: Optional[int],
) -> int:
    if df is None or df.empty:
        return 0
    affected = 0
    for row in df.to_dict(orient="records"):
        sql = text(
            "INSERT INTO line_breaks (team_id, match_id, line_type, breaks_for, breaks_against) "
            "VALUES (:team_id, :match_id, :line_type, :breaks_for, :breaks_against) "
            "ON DUPLICATE KEY UPDATE breaks_for=VALUES(breaks_for), breaks_against=VALUES(breaks_against)"
        )
        result = await session.execute(
            sql,
            {**row, "team_id": team_id, "match_id": match_id},
        )
        affected += result.rowcount
    return affected


async def upsert_spatial(
    session: AsyncSession,
    df: pd.DataFrame,
    team_id: int,
    match_id: Optional[int],
) -> int:
    if df is None or df.empty:
        return 0
    affected = 0
    for row in df.to_dict(orient="records"):
        sql = text(
            "INSERT INTO spatial_stats (team_id, match_id, spatial_zone, def_line_height_pct, "
            "pressure_high_pct, pressure_mid_pct, pressure_low_pct) "
            "VALUES (:team_id, :match_id, :spatial_zone, :def_line_height_pct, "
            ":pressure_high_pct, :pressure_mid_pct, :pressure_low_pct) "
            "ON DUPLICATE KEY UPDATE def_line_height_pct=VALUES(def_line_height_pct), "
            "pressure_high_pct=VALUES(pressure_high_pct), pressure_mid_pct=VALUES(pressure_mid_pct), "
            "pressure_low_pct=VALUES(pressure_low_pct)"
        )
        result = await session.execute(
            sql,
            {**row, "team_id": team_id, "match_id": match_id},
        )
        affected += result.rowcount
    return affected


async def upsert_final_third(
    session: AsyncSession,
    df: pd.DataFrame,
    team_id: int,
    match_id: Optional[int],
) -> int:
    if df is None or df.empty:
        return 0
    affected = 0
    for row in df.to_dict(orient="records"):
        sql = text(
            "INSERT INTO final_third_entries (team_id, match_id, zone_name, entry_count, xg) "
            "VALUES (:team_id, :match_id, :zone_name, :entry_count, :xg) "
            "ON DUPLICATE KEY UPDATE entry_count=VALUES(entry_count), xg=VALUES(xg)"
        )
        result = await session.execute(
            sql,
            {**row, "team_id": team_id, "match_id": match_id},
        )
        affected += result.rowcount
    return affected


async def upsert_defensive(
    session: AsyncSession,
    df: pd.DataFrame,
    team_id: int,
    match_id: Optional[int],
) -> int:
    if df is None or df.empty:
        return 0
    affected = 0
    for row in df.to_dict(orient="records"):
        sql = text(
            "INSERT INTO defensive_actions (team_id, match_id, action_type, action_count, success_pct, zone) "
            "VALUES (:team_id, :match_id, :action_type, :action_count, :success_pct, :zone) "
            "ON DUPLICATE KEY UPDATE action_count=VALUES(action_count), success_pct=VALUES(success_pct)"
        )
        result = await session.execute(
            sql,
            {**row, "team_id": team_id, "match_id": match_id},
        )
        affected += result.rowcount
    return affected
