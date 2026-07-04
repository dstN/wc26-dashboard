#!/usr/bin/env python3
"""
pmsr_to_sql.py — Convert FIFA Post Match Summary Report PDFs to SQL seed files.

Usage:
  python pmsr_to_sql.py <pdf>              Print SQL for one PDF to stdout
  python pmsr_to_sql.py --batch            Process all PDFs in .claude/data/
                                           → db/seeds/04_all_matches.sql
                                           → moves processed PDFs to .claude/data/done/
"""

import sys
import os
import re
import json
import argparse
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))
from parse_pmsr import extract  # type: ignore

# ── Team name (as it appears in PDF) → FIFA 3-letter short code ──────────────
TEAM_NAME_TO_CODE: dict[str, str] = {
    "Germany":                    "GER",
    "Curaçao":                    "CUR",
    "Argentina":                  "ARG",
    "Algeria":                    "ALG",
    "Australia":                  "AUS",
    "Türkiye":                    "TUR",
    "Austria":                    "AUT",
    "Jordan":                     "JOR",
    "Belgium":                    "BEL",
    "Egypt":                      "EGY",
    "Brazil":                     "BRA",
    "Haiti":                      "HAI",
    "Morocco":                    "MAR",
    "Canada":                     "CAN",
    "Bosnia and Herzegovina":     "BIH",
    "Qatar":                      "QAT",
    "Côte d'Ivoire":              "CIV",
    "Ecuador":                    "ECU",
    "Czechia":                    "CZE",
    "South Africa":               "RSA",
    "England":                    "ENG",
    "Croatia":                    "CRO",
    "France":                     "FRA",
    "Senegal":                    "SEN",
    "Ghana":                      "GHA",
    "Panama":                     "PAN",
    "Scotland":                   "SCO",
    "IR Iran":                    "IRN",
    "New Zealand":                "NZL",
    "Iraq":                       "IRQ",
    "Norway":                     "NOR",
    "Mexico":                     "MEX",
    "Korea Republic":             "KOR",
    "Netherlands":                "NED",
    "Japan":                      "JPN",
    "Sweden":                     "SWE",
    "Portugal":                   "POR",
    "Congo DR":                   "COD",
    "Switzerland":                "SUI",
    "Saudi Arabia":               "KSA",
    "Uruguay":                    "URU",
    "Spain":                      "ESP",
    "Cabo Verde":                 "CPV",
    "Tunisia":                    "TUN",
    "Paraguay":                   "PAR",
    "USA":                        "USA",
    "Uzbekistan":                 "UZB",
    "Colombia":                   "COL",
}


def _code(name: str) -> str:
    code = TEAM_NAME_TO_CODE.get(name)
    if not code:
        raise ValueError(f"Unknown team name {name!r} — add to TEAM_NAME_TO_CODE")
    return code


def _q(v: object) -> str:
    """Quote a value for SQL (handles None → NULL, strings → escaped)."""
    if v is None:
        return "NULL"
    return "'{}'".format(str(v).replace("'", "''"))


def _n(v: object) -> str:
    """Return NULL or numeric string for SQL."""
    return "NULL" if v is None else str(v)


def _team(code: str) -> str:
    return f"(SELECT id FROM teams WHERE short_code = '{code}')"


def _match(match_no: int) -> str:
    return f"(SELECT id FROM matches WHERE match_no = {match_no})"


def _pressure(avg_duration_s: float | None) -> str:
    """Derive pressure_on_ball ENUM from avg pressure duration (seconds)."""
    if avg_duration_s and avg_duration_s > 1.5:
        return "heavy"
    return "moderate"


def _aggregate_line_breaks(by_units: dict) -> dict[str, tuple[int, int]]:
    """
    Aggregate attempted/completed per semantic line type across all unit groups.

    The EFI framework tracks which specific line (defensive/midfield/attacking)
    was broken, regardless of how many total units were available. We sum these
    across all unit-count groups to get the per-line totals.

    'advanced midfield' is merged into 'midfield'.
    """
    totals: dict[str, list[int]] = {
        "defensive": [0, 0],
        "midfield":  [0, 0],
        "attacking": [0, 0],
    }
    for unit_data in by_units.values():
        for line_info in unit_data.get("lines", []):
            line = line_info.get("line", "")
            att  = int(line_info.get("attempted",  0) or 0)
            comp = int(line_info.get("completed",  0) or 0)
            if line == "defensive":
                totals["defensive"][0] += att
                totals["defensive"][1] += comp
            elif line in ("midfield", "advanced midfield"):
                totals["midfield"][0] += att
                totals["midfield"][1] += comp
            elif line == "attacking":
                totals["attacking"][0] += att
                totals["attacking"][1] += comp
    return {k: (v[0], v[1]) for k, v in totals.items()}


# ─────────────────────────────────────────────────────────────────────────────

def pdf_to_sql(pdf_path: str) -> str:
    """Parse a FIFA PMSR PDF and return the corresponding SQL INSERT statements."""
    tmp = f"/tmp/pmsr_{Path(pdf_path).stem}.json"
    extract(pdf_path, tmp)
    data = json.loads(Path(tmp).read_text())

    match  = data["match"]
    pages  = data["pages"]

    # ── Sentinel: page 29 must be 'Defensive Pressure' ───────────────────────
    # If _count_extra_shot_log_pages() misfires, all pages after p17 shift and
    # page 29 will contain wrong data. Fail loudly rather than silently corrupt.
    p29_title = pages.get("29", {}).get("title", "MISSING")
    if p29_title != "Defensive Pressure":
        raise RuntimeError(
            f"{Path(pdf_path).name}: page 29 should be 'Defensive Pressure' "
            f"but got {p29_title!r}. "
            "Verify _count_extra_shot_log_pages() handles this PDF correctly."
        )

    match_no   = match["match_number"]
    home_name  = match["home_team_name"]
    away_name  = match["away_team_name"]
    home_code  = _code(home_name)
    away_code  = _code(away_name)
    score_home = match["score"]["home"]
    score_away = match["score"]["away"]
    venue      = match["venue"]
    date       = match["date"]

    group_m = re.search(r"Group\s+([A-Z])", match.get("stage", ""))
    group_letter = group_m.group(1) if group_m else None

    out: list[str] = []
    L = out.append

    L(f"-- ── {home_name} {score_home}–{score_away} {away_name}  "
      f"· Match {match_no} · {date} ────────────────────────────────────────")
    L(f"-- Generated from {Path(pdf_path).name}")
    L("")

    # ── Match ─────────────────────────────────────────────────────────────────
    formations = pages.get("2", {}).get("data", {}).get("formations", {})
    form_a = _q(formations.get("home_team") or "")
    form_b = _q(formations.get("away_team") or "")
    L("INSERT INTO matches (match_no, team_a_id, team_b_id, score_a, score_b, venue, match_date, group_letter, is_featured, formation_a, formation_b)")
    L(f"VALUES ({match_no}, {_team(home_code)}, {_team(away_code)}, "
      f"{score_home}, {score_away}, {_q(venue)}, {_q(date)}, "
      f"{_q(group_letter)}, 0, {form_a}, {form_b})")
    L("ON DUPLICATE KEY UPDATE")
    L("  score_a=VALUES(score_a), score_b=VALUES(score_b),")
    L("  venue=VALUES(venue), match_date=VALUES(match_date),")
    L("  formation_a=VALUES(formation_a), formation_b=VALUES(formation_b);")
    L("")

    # ── Match Stats ───────────────────────────────────────────────────────────
    p3    = pages.get("3", {}).get("data", {})
    poss  = p3.get("possession_pct", {})
    stats = p3.get("statistics", [])

    home_xg = away_xg = None
    for s in stats:
        if "xG" in s.get("stat", ""):
            home_xg = s["home_team"]
            away_xg = s["away_team"]

    p29_stats = pages.get("29", {}).get("data", {}).get("statistics", [])
    home_recovery = away_recovery = None
    for s in p29_stats:
        if "Ball Recovery Time" in s.get("stat", ""):
            home_recovery = s["home_team"]
            away_recovery = s["away_team"]

    poss_home = poss.get("home_team")
    poss_away = poss.get("away_team")
    poss_cont = poss.get("contested")

    for (code, pa, pb, xa, xb, ga, gb, rec) in [
        (home_code, poss_home, poss_away, home_xg, away_xg, score_home, score_away, home_recovery),
        (away_code, poss_away, poss_home, away_xg, home_xg, score_away, score_home, away_recovery),
    ]:
        def n(v: object) -> str:
            return "NULL" if v is None else str(v)
        L("INSERT INTO match_stats")
        L("  (team_id, match_id, scope, possession_team_a, possession_team_b,")
        L("   possession_in_contest, ball_recovery_time_avg, xg_a, xg_b, goals_a, goals_b)")
        L(f"VALUES ({_team(code)}, {_match(match_no)}, 'match',")
        L(f"  {n(pa)}, {n(pb)}, {n(poss_cont)}, {n(rec)}, {n(xa)}, {n(xb)}, {n(ga)}, {n(gb)})")
        L("ON DUPLICATE KEY UPDATE")
        L("  possession_team_a=VALUES(possession_team_a),")
        L("  possession_team_b=VALUES(possession_team_b),")
        L("  possession_in_contest=VALUES(possession_in_contest),")
        L("  ball_recovery_time_avg=VALUES(ball_recovery_time_avg),")
        L("  xg_a=VALUES(xg_a), xg_b=VALUES(xg_b),")
        L("  goals_a=VALUES(goals_a), goals_b=VALUES(goals_b);")
    L("")

    # ── Match Phases ──────────────────────────────────────────────────────────
    p4       = pages.get("4", {}).get("data", {})
    in_ph    = p4.get("in_possession", [])
    out_ph   = p4.get("out_of_possession", [])

    for (code, pct_key) in [(home_code, "home_team_pct"), (away_code, "away_team_pct")]:
        rows: list[str] = []
        for ph in in_ph:
            rows.append(
                f"  ({_team(code)}, {_match(match_no)}, 'match', "
                f"{_q(ph['phase'])}, 'in', {ph.get(pct_key, 0)})"
            )
        for ph in out_ph:
            rows.append(
                f"  ({_team(code)}, {_match(match_no)}, 'match', "
                f"{_q(ph['phase'])}, 'out', {ph.get(pct_key, 0)})"
            )
        if rows:
            L("INSERT INTO match_phases")
            L("  (team_id, match_id, scope, phase_name, phase_group, pct)")
            L("VALUES")
            L(",\n".join(rows))
            L("ON DUPLICATE KEY UPDATE pct=VALUES(pct);")
    L("")

    # ── Spatial Stats (Defensive) ─────────────────────────────────────────────
    for (code, pg) in [(home_code, "27"), (away_code, "28")]:
        spat = pages.get(pg, {}).get("data", {})
        block_map = {
            "high": spat.get("high_block_press", {}),
            "mid":  spat.get("mid_block",        {}),
            "low":  spat.get("low_block",         {}),
        }
        rows = []
        for btype, bd in block_map.items():
            dist = bd.get("distance_to_goal_m")
            leng = bd.get("length_m")
            wid  = bd.get("width_m")
            if dist is not None:
                rows.append(
                    f"  ({_team(code)}, {_match(match_no)}, 'match', "
                    f"'{btype}', {dist}, {leng}, {wid})"
                )
        if rows:
            L("INSERT INTO team_spatial_stats")
            L("  (team_id, match_id, scope, block_type, defensive_line_height, team_length, width_m)")
            L("VALUES")
            L(",\n".join(rows))
            L("ON DUPLICATE KEY UPDATE")
            L("  defensive_line_height=VALUES(defensive_line_height),")
            L("  team_length=VALUES(team_length),")
            L("  width_m=VALUES(width_m);")
    L("")

    # ── Spatial Stats (In Possession, pages 6/7) ──────────────────────────────
    section_map = {
        "build_up_low":       "build_up_low",
        "build_up_mid":       "build_up_mid",
        "final_third_phase":  "final_third_phase",
    }
    for (code, pg) in [(home_code, "6"), (away_code, "7")]:
        spat = pages.get(pg, {}).get("data", {})
        rows = []
        for sec_key, block_val in section_map.items():
            bd = spat.get(sec_key, {})
            dist = bd.get("distance_to_goal_m")
            leng = bd.get("length_m")
            wid  = bd.get("width_m")
            if dist is not None:
                rows.append(
                    f"  ({_team(code)}, {_match(match_no)}, 'match', "
                    f"'{block_val}', {dist}, {leng}, {wid})"
                )
        if rows:
            L("INSERT INTO team_spatial_stats")
            L("  (team_id, match_id, scope, block_type, defensive_line_height, team_length, width_m)")
            L("VALUES")
            L(",\n".join(rows))
            L("ON DUPLICATE KEY UPDATE")
            L("  defensive_line_height=VALUES(defensive_line_height),")
            L("  team_length=VALUES(team_length),")
            L("  width_m=VALUES(width_m);")
    L("")

    # ── Line Breaks (per-line aggregated across unit groups) ─────────────────
    # We aggregate by which specific line was broken (defensive/midfield/attacking)
    # across all unit-count contexts (4u/3u/2u). "advanced midfield" → "midfield".
    for (code, pg) in [(home_code, "8"), (away_code, "9")]:
        by_units = pages.get(pg, {}).get("data", {}).get("by_units", {})
        agg = _aggregate_line_breaks(by_units)
        rows = [
            f"  ({_team(code)}, {_match(match_no)}, 'match', '{lt}', {att}, {comp})"
            for lt, (att, comp) in agg.items()
        ]
        if rows:
            L("INSERT INTO line_breaks")
            L("  (team_id, match_id, scope, line_type, attempted, completed)")
            L("VALUES")
            L(",\n".join(rows))
            L("ON DUPLICATE KEY UPDATE")
            L("  attempted=VALUES(attempted), completed=VALUES(completed);")
    L("")

    # ── Defensive Actions (pages 25/26) ──────────────────────────────────────
    for (code, pg) in [(home_code, "25"), (away_code, "26")]:
        da  = pages.get(pg, {}).get("data", {})
        ft  = da.get("forced_turnovers", 0)
        avg_dur = None
        for s in p29_stats:
            if "Avg Pressure Duration" in s.get("stat", ""):
                avg_dur = s["home_team"] if code == home_code else s["away_team"]
        pressure = _pressure(avg_dur)
        def n(v):
            return "NULL" if v is None else str(v)
        blk = da.get("blocks") or {}
        con = da.get("possession_contests") or {}
        mrg = da.get("most_possession_regains") or {}
        L("INSERT INTO defensive_actions")
        L("  (team_id, match_id, scope, forced_turnovers, pressure_on_ball,")
        L("   possession_regained, interceptions, tackles, possession_actions_per_da,")
        L("   blocks_total, blocks_passes, blocks_shots, blocks_crosses, blocks_clearances,")
        L("   contests_total, contests_physical, contests_aerial, contests_duels,")
        L("   most_regains_player, most_regains_count)")
        L(f"VALUES ({_team(code)}, {_match(match_no)}, 'match', {ft}, '{pressure}',")
        L(f"  {n(da.get('possession_regained'))}, {n(da.get('interceptions'))},")
        L(f"  {n(da.get('tackles'))}, {n(da.get('possession_actions_per_defensive_action'))},")
        L(f"  {n(blk.get('total'))}, {n(blk.get('passes'))}, {n(blk.get('attempts_at_goal'))},")
        L(f"  {n(blk.get('crosses'))}, {n(blk.get('clearances'))},")
        L(f"  {n(con.get('total'))}, {n(con.get('physical_duels'))},")
        L(f"  {n(con.get('aerial_duels'))}, {n(con.get('duels'))},")
        L(f"  {_q(mrg.get('player',''))}, {n(mrg.get('count'))})")
        L("ON DUPLICATE KEY UPDATE")
        L("  forced_turnovers=VALUES(forced_turnovers), pressure_on_ball=VALUES(pressure_on_ball),")
        L("  possession_regained=VALUES(possession_regained), interceptions=VALUES(interceptions),")
        L("  tackles=VALUES(tackles), possession_actions_per_da=VALUES(possession_actions_per_da),")
        L("  blocks_total=VALUES(blocks_total), blocks_passes=VALUES(blocks_passes),")
        L("  blocks_shots=VALUES(blocks_shots), blocks_crosses=VALUES(blocks_crosses),")
        L("  blocks_clearances=VALUES(blocks_clearances),")
        L("  contests_total=VALUES(contests_total), contests_physical=VALUES(contests_physical),")
        L("  contests_aerial=VALUES(contests_aerial), contests_duels=VALUES(contests_duels),")
        L("  most_regains_player=VALUES(most_regains_player),")
        L("  most_regains_count=VALUES(most_regains_count);")
    L("")

    # ── Players + per-match player stats ─────────────────────────────────────
    p2 = pages.get("2", {}).get("data", {})
    for (code, team_key) in [(home_code, "home_team"), (away_code, "away_team")]:
        team_data  = p2.get(team_key, {})
        starting   = list(team_data.get("starting",    []))
        subs       = list(team_data.get("substitutes", []))
        for pl in starting + subs:
            name = (pl.get("name") or "").strip()
            pos  = pl.get("position") or ""
            num  = pl.get("number")
            if not name:
                continue
            L("INSERT INTO players (team_id, name, position, jersey_number)")
            L(f"VALUES ({_team(code)}, {_q(name)}, {_q(pos)}, "
              f"{'NULL' if num is None else num})")
            L("ON DUPLICATE KEY UPDATE name=VALUES(name), position=VALUES(position);")

        # Per-match player stats (goals, cards, minutes, started)
        stats_rows = []
        for is_starter, group in [(1, starting), (0, subs)]:
            for pl in group:
                name = (pl.get("name") or "").strip()
                num  = pl.get("number")
                if not name:
                    continue
                goals_count  = len(pl.get("goals", []) or [])
                cards        = pl.get("cards", []) or []
                yellow = sum(1 for c in cards if c.get("type") == "yellow")
                red    = sum(1 for c in cards if c.get("type") in ("red", "second_yellow"))
                sub_on   = pl.get("subbed_on")
                sub_off  = pl.get("subbed_off")
                if is_starter:
                    mins = int(sub_off) if sub_off is not None else 90
                else:
                    mins = (90 - int(sub_on)) if sub_on is not None else 0
                mins = max(0, min(120, mins))
                player_ref = (
                    f"(SELECT id FROM players WHERE team_id={_team(code)} "
                    f"AND jersey_number={num})"
                    if num is not None else
                    f"(SELECT id FROM players WHERE team_id={_team(code)} "
                    f"AND name={_q(name)} LIMIT 1)"
                )
                stats_rows.append(
                    f"  ({player_ref}, {_match(match_no)}, 'match', "
                    f"{goals_count}, {yellow}, {red}, {is_starter}, {mins})"
                )
        if stats_rows:
            L("INSERT INTO player_stats "
              "(player_id, match_id, scope, goals, yellow_cards, red_cards, started, minutes_played)")
            L("VALUES")
            L(",\n".join(stats_rows))
            L("ON DUPLICATE KEY UPDATE "
              "goals=VALUES(goals), yellow_cards=VALUES(yellow_cards), "
              "red_cards=VALUES(red_cards), started=VALUES(started), "
              "minutes_played=VALUES(minutes_played);")
    L("")

    # ── Shot summary (pages 14/16) ────────────────────────────────────────────
    for (code, pg) in [(home_code, "14"), (away_code, "16")]:
        shots = pages.get(pg, {}).get("data", {})
        total = shots.get("total_shots")
        on_tgt = (shots.get("outcomes") or {}).get("on_target")
        if total is not None:
            def n(v):
                return "NULL" if v is None else str(v)
            L("UPDATE match_stats")
            L(f"SET shots_total={n(total)}, shots_on_target={n(on_tgt)}")
            L(f"WHERE team_id={_team(code)} AND match_id={_match(match_no)}")
            L("  AND scope='match';")
    L("")

    # ── Shot Events (pages 15/17) ─────────────────────────────────────────────
    for (code, pg) in [(home_code, "15"), (away_code, "17")]:
        shots = pages.get(pg, {}).get("data", {}).get("shots", [])
        if shots:
            L(f"DELETE FROM shot_events WHERE team_id={_team(code)} AND match_id={_match(match_no)};")
            rows = []
            for s in shots:
                rows.append(
                    f"  ({_team(code)}, {_match(match_no)}, "
                    f"{s.get('minute', 0)}, {_n(s.get('number'))}, "
                    f"{_q(s.get('player',''))}, {_q(s.get('outcome',''))}, "
                    f"{_q(s.get('body_part',''))}, {_q(s.get('delivery_type',''))})"
                )
            L("INSERT INTO shot_events")
            L("  (team_id, match_id, minute, player_jersey, player_name,")
            L("   outcome, body_part, delivery_type)")
            L("VALUES")
            L(",\n".join(rows) + ";")
    L("")

    # ── Passing Connections (pages 12/13) ─────────────────────────────────────
    for (code, pg) in [(home_code, "12"), (away_code, "13")]:
        top5 = pages.get(pg, {}).get("data", {}).get("top5_player_to_player_passers", [])
        rows = []
        rank = 1
        for entry in top5:
            frm = entry.get("from", "")
            to  = entry.get("to", "")
            pct = entry.get("pct_of_team_passes")
            # Skip header rows parsed as data (from="% of Total")
            if not frm or "%" in frm or len(frm) < 3:
                continue
            rows.append(
                f"  ({_team(code)}, {_match(match_no)}, {rank}, "
                f"{_q(frm)}, {_q(to)}, {_n(pct)})"
            )
            rank += 1
        if rows:
            L("INSERT INTO passing_connections (team_id, match_id, rank_no, from_name, to_name, pct_of_team_passes)")
            L("VALUES")
            L(",\n".join(rows))
            L("ON DUPLICATE KEY UPDATE from_name=VALUES(from_name), to_name=VALUES(to_name),")
            L("  pct_of_team_passes=VALUES(pct_of_team_passes);")
    L("")

    # ── Cross Stats (pages 18/19) ─────────────────────────────────────────────
    for (code, pg) in [(home_code, "18"), (away_code, "19")]:
        cr = pages.get(pg, {}).get("data", {})
        if not cr:
            continue
        def n(v):
            return "NULL" if v is None else str(v)
        dt  = cr.get("delivery_type_totals") or {}
        cz  = cr.get("cross_zones") or {}
        most = cr.get("most_attempted") or {}
        L("INSERT INTO cross_stats")
        L("  (team_id, match_id, scope, attempted, completed,")
        L("   zone_left, zone_center_left, zone_center_right, zone_right,")
        L("   type_inswing, type_outswing, type_driven, type_lofted,")
        L("   type_cutback, type_push_cross, most_player, most_count)")
        L(f"VALUES ({_team(code)}, {_match(match_no)}, 'match',")
        L(f"  {n(cr.get('attempted'))}, {n(cr.get('completed'))},")
        L(f"  {n(cz.get('left'))}, {n(cz.get('center_left'))}, {n(cz.get('center_right'))}, {n(cz.get('right'))},")
        L(f"  {n(dt.get('inswing'))}, {n(dt.get('outswing'))}, {n(dt.get('driven'))}, {n(dt.get('lofted'))},")
        L(f"  {n(dt.get('cutback'))}, {n(dt.get('push_cross'))}, {_q(most.get('player',''))}, {n(most.get('count'))})")
        L("ON DUPLICATE KEY UPDATE")
        L("  attempted=VALUES(attempted), completed=VALUES(completed),")
        L("  zone_left=VALUES(zone_left), zone_center_left=VALUES(zone_center_left),")
        L("  zone_center_right=VALUES(zone_center_right), zone_right=VALUES(zone_right),")
        L("  type_inswing=VALUES(type_inswing), type_outswing=VALUES(type_outswing),")
        L("  type_driven=VALUES(type_driven), type_lofted=VALUES(type_lofted),")
        L("  type_cutback=VALUES(type_cutback), type_push_cross=VALUES(type_push_cross),")
        L("  most_player=VALUES(most_player), most_count=VALUES(most_count);")
    L("")

    # ── Offering Stats (pages 20/21) ──────────────────────────────────────────
    for (code, pg) in [(home_code, "20"), (away_code, "21")]:
        of = pages.get(pg, {}).get("data", {})
        if not of:
            continue
        def n(v):
            return "NULL" if v is None else str(v)
        byt  = of.get("offers_made_by_third") or {}
        shp  = of.get("offers_made_shape") or {}
        most = of.get("most_offers") or {}
        L("INSERT INTO match_offering_stats")
        L("  (team_id, match_id, scope, total_offers_made, total_offers_received,")
        L("   offers_final_third, offers_middle_third, offers_defensive_third,")
        L("   inside_shape, outside_shape, most_player, most_count)")
        L(f"VALUES ({_team(code)}, {_match(match_no)}, 'match',")
        L(f"  {n(of.get('total_offers_made'))}, {n(of.get('total_offers_received'))},")
        L(f"  {n(byt.get('final'))}, {n(byt.get('middle'))}, {n(byt.get('defensive'))},")
        L(f"  {n(shp.get('inside_shape'))}, {n(shp.get('outside_shape'))},")
        L(f"  {_q(most.get('player',''))}, {n(most.get('count'))})")
        L("ON DUPLICATE KEY UPDATE")
        L("  total_offers_made=VALUES(total_offers_made),")
        L("  total_offers_received=VALUES(total_offers_received),")
        L("  offers_final_third=VALUES(offers_final_third),")
        L("  offers_middle_third=VALUES(offers_middle_third),")
        L("  offers_defensive_third=VALUES(offers_defensive_third),")
        L("  inside_shape=VALUES(inside_shape), outside_shape=VALUES(outside_shape),")
        L("  most_player=VALUES(most_player), most_count=VALUES(most_count);")
    L("")

    # ── Movement Stats (pages 22/23) ──────────────────────────────────────────
    for (code, pg) in [(home_code, "22"), (away_code, "23")]:
        mv = pages.get(pg, {}).get("data", {})
        if not mv:
            continue
        def n(v):
            return "NULL" if v is None else str(v)
        amt = mv.get("all_movement_types") or {}
        bph = mv.get("by_phase_totals") or {}
        bpt = mv.get("by_pitch_third") or {}
        ft  = bpt.get("final_third") or {}
        mid = bpt.get("middle_third") or {}
        df  = bpt.get("defensive_third") or {}
        L("INSERT INTO match_movement_stats")
        L("  (team_id, match_id, scope, total_movements,")
        L("   phase_final_third, phase_progression, phase_build_up,")
        L("   type_in_front, type_in_between, type_out_to_in, type_in_to_out, type_in_behind,")
        L("   ft_in_front, ft_in_between, ft_out_to_in, ft_in_to_out, ft_in_behind,")
        L("   mid_in_front, mid_in_between, mid_out_to_in, mid_in_to_out, mid_in_behind,")
        L("   def_in_front, def_in_between, def_out_to_in, def_in_to_out, def_in_behind)")
        L(f"VALUES ({_team(code)}, {_match(match_no)}, 'match',")
        L(f"  {n(amt.get('total'))}, {n(bph.get('final_third_phase'))},")
        L(f"  {n(bph.get('progression_phase'))}, {n(bph.get('build_up_phase'))},")
        L(f"  {n(amt.get('in_front'))}, {n(amt.get('in_between'))},")
        L(f"  {n(amt.get('out_to_in'))}, {n(amt.get('in_to_out'))}, {n(amt.get('in_behind'))},")
        L(f"  {n(ft.get('in_front'))}, {n(ft.get('in_between'))}, {n(ft.get('out_to_in'))}, {n(ft.get('in_to_out'))}, {n(ft.get('in_behind'))},")
        L(f"  {n(mid.get('in_front'))}, {n(mid.get('in_between'))}, {n(mid.get('out_to_in'))}, {n(mid.get('in_to_out'))}, {n(mid.get('in_behind'))},")
        L(f"  {n(df.get('in_front'))}, {n(df.get('in_between'))}, {n(df.get('out_to_in'))}, {n(df.get('in_to_out'))}, {n(df.get('in_behind'))})")
        L("ON DUPLICATE KEY UPDATE")
        L("  total_movements=VALUES(total_movements),")
        L("  phase_final_third=VALUES(phase_final_third),")
        L("  phase_progression=VALUES(phase_progression),")
        L("  phase_build_up=VALUES(phase_build_up),")
        L("  type_in_front=VALUES(type_in_front), type_in_between=VALUES(type_in_between),")
        L("  type_out_to_in=VALUES(type_out_to_in), type_in_to_out=VALUES(type_in_to_out),")
        L("  type_in_behind=VALUES(type_in_behind),")
        L("  ft_in_front=VALUES(ft_in_front), ft_in_between=VALUES(ft_in_between),")
        L("  ft_out_to_in=VALUES(ft_out_to_in), ft_in_to_out=VALUES(ft_in_to_out), ft_in_behind=VALUES(ft_in_behind),")
        L("  mid_in_front=VALUES(mid_in_front), mid_in_between=VALUES(mid_in_between),")
        L("  mid_out_to_in=VALUES(mid_out_to_in), mid_in_to_out=VALUES(mid_in_to_out), mid_in_behind=VALUES(mid_in_behind),")
        L("  def_in_front=VALUES(def_in_front), def_in_between=VALUES(def_in_between),")
        L("  def_out_to_in=VALUES(def_out_to_in), def_in_to_out=VALUES(def_in_to_out), def_in_behind=VALUES(def_in_behind);")
    L("")

    # ── Pressure Stats (page 29) ──────────────────────────────────────────────
    p29_data = pages.get("29", {}).get("data", {})
    p29_most = p29_data.get("most_direct_pressures", {})

    def _p29_val(stat_name: str, team_key: str):
        for s in p29_stats:
            if s.get("stat", "") == stat_name:
                return s.get(team_key)
        return None

    for (code, tk) in [(home_code, "home_team"), (away_code, "away_team")]:
        def n(v):
            return "NULL" if v is None else str(v)
        most_pl = (p29_most.get(tk) or {}).get("player", "")
        most_ct = (p29_most.get(tk) or {}).get("count")
        L("INSERT INTO match_pressure_stats")
        L("  (team_id, match_id, scope, total_pressures, direct_pressures,")
        L("   avg_duration_s, forced_turnovers, ball_recovery_time_s,")
        L("   pushing_on_into_pressing, pushing_on,")
        L("   direction_inside, direction_outside, most_direct_player, most_direct_count)")
        L(f"VALUES ({_team(code)}, {_match(match_no)}, 'match',")
        L(f"  {n(_p29_val('Total Pressures', tk))},")
        L(f"  {n(_p29_val('Direct Pressures', tk))},")
        L(f"  {n(_p29_val('Avg Pressure Duration (s)', tk))},")
        L(f"  {n(_p29_val('Forced Turnovers', tk))},")
        L(f"  {n(_p29_val('Ball Recovery Time (s)', tk))},")
        L(f"  {n(_p29_val('Pushing on into Pressing', tk))},")
        L(f"  {n(_p29_val('Pushing on', tk))},")
        L(f"  {n(_p29_val('Direction - Inside', tk))},")
        L(f"  {n(_p29_val('Direction - Outside', tk))},")
        L(f"  {_q(most_pl)}, {n(most_ct)})")
        L("ON DUPLICATE KEY UPDATE")
        L("  total_pressures=VALUES(total_pressures), direct_pressures=VALUES(direct_pressures),")
        L("  avg_duration_s=VALUES(avg_duration_s), forced_turnovers=VALUES(forced_turnovers),")
        L("  ball_recovery_time_s=VALUES(ball_recovery_time_s),")
        L("  pushing_on_into_pressing=VALUES(pushing_on_into_pressing),")
        L("  pushing_on=VALUES(pushing_on),")
        L("  direction_inside=VALUES(direction_inside), direction_outside=VALUES(direction_outside),")
        L("  most_direct_player=VALUES(most_direct_player), most_direct_count=VALUES(most_direct_count);")
    L("")

    # ── GK stats (pages 31-37) ────────────────────────────────────────────────
    p31 = pages.get("31", {}).get("data", {})
    for (code, pg_inv, pg_dist, pg_prev, pg_aerial) in [
        (home_code, "31", "32", "34", "36"),
        (away_code, "31", "33", "35", "37"),
    ]:
        team_key_inv = "home_team" if code == home_code else "away_team"
        inv_data  = (p31.get(team_key_inv) or {})
        dist_data = pages.get(pg_dist,   {}).get("data", {})
        prev_data = pages.get(pg_prev,   {}).get("data", {})
        aer_data  = pages.get(pg_aerial, {}).get("data", {})

        def n(v):
            return "NULL" if v is None else str(v)

        total_inv  = inv_data.get("total_involvements")
        total_dist = dist_data.get("total_distributions")
        k_feet     = (dist_data.get("kick_from_feet") or {}).get("total")
        k_hands    = (dist_data.get("kick_from_hands") or {}).get("total")
        k_throw    = (dist_data.get("throw_distribution") or {}).get("total")
        gk_lb      = dist_data.get("goalkeeper_line_breaks")
        att_faced  = prev_data.get("total_attempts_faced")
        save_pct   = prev_data.get("save_pct")
        ib         = prev_data.get("intervention_breakdown") or {}
        goal_int   = ib.get("total_goal_interventions")
        save_ret   = ib.get("save_and_retain")
        defl_ret   = ib.get("deflect_and_retain")
        save_defl  = ib.get("save_and_deflect")
        save_att   = ib.get("save_attempt")
        no_save    = ib.get("no_save_attempt")
        aer_int    = aer_data.get("total_interventions")
        cfd        = aer_data.get("crosses_faced_delivery_types") or {}
        cr_faced   = cfd.get("total")
        cr_inswing = cfd.get("in_swing")
        cr_outswing= cfd.get("out_swing")
        cr_driven  = cfd.get("driven")
        cr_lofted  = cfd.get("lofted")
        cr_cutback = cfd.get("cutback")
        cr_push    = cfd.get("push")
        gk_name    = dist_data.get("goalkeeper")
        punches    = aer_data.get("punches") or {}
        claims     = aer_data.get("claims") or {}
        tipped     = aer_data.get("tipped_palmed") or {}

        def _qs(v):
            return "NULL" if not v else f"'{v.replace(chr(39), chr(39)+chr(39))}'"

        if total_inv is not None or total_dist is not None:
            L("INSERT INTO match_gk_stats")
            L("  (team_id, match_id, scope, total_involvements, total_distributions,")
            L("   kick_from_feet, kick_from_hands, throw_distribution, gk_line_breaks,")
            L("   total_attempts_faced, save_pct, total_goal_interventions,")
            L("   save_and_retain, deflect_and_retain, save_and_deflect, save_attempt, no_save_attempt,")
            L("   total_aerial_interventions, crosses_faced,")
            L("   crosses_faced_inswing, crosses_faced_outswing, crosses_faced_driven,")
            L("   crosses_faced_lofted, crosses_faced_cutback, crosses_faced_push,")
            L("   gk_name,")
            L("   punches_complete, punches_incomplete,")
            L("   claims_complete, claims_incomplete,")
            L("   tipped_palmed_complete, tipped_palmed_incomplete)")
            L(f"VALUES ({_team(code)}, {_match(match_no)}, 'match',")
            L(f"  {n(total_inv)}, {n(total_dist)}, {n(k_feet)}, {n(k_hands)},")
            L(f"  {n(k_throw)}, {n(gk_lb)}, {n(att_faced)}, {n(save_pct)},")
            L(f"  {n(goal_int)},")
            L(f"  {n(save_ret)}, {n(defl_ret)}, {n(save_defl)}, {n(save_att)}, {n(no_save)},")
            L(f"  {n(aer_int)}, {n(cr_faced)},")
            L(f"  {n(cr_inswing)}, {n(cr_outswing)}, {n(cr_driven)},")
            L(f"  {n(cr_lofted)}, {n(cr_cutback)}, {n(cr_push)},")
            L(f"  {_qs(gk_name)},")
            L(f"  {n(punches.get('complete'))}, {n(punches.get('incomplete'))},")
            L(f"  {n(claims.get('complete'))}, {n(claims.get('incomplete'))},")
            L(f"  {n(tipped.get('complete'))}, {n(tipped.get('incomplete'))})")
            L("ON DUPLICATE KEY UPDATE")
            L("  total_involvements=VALUES(total_involvements),")
            L("  total_distributions=VALUES(total_distributions),")
            L("  kick_from_feet=VALUES(kick_from_feet),")
            L("  kick_from_hands=VALUES(kick_from_hands),")
            L("  throw_distribution=VALUES(throw_distribution),")
            L("  gk_line_breaks=VALUES(gk_line_breaks),")
            L("  total_attempts_faced=VALUES(total_attempts_faced),")
            L("  save_pct=VALUES(save_pct),")
            L("  total_goal_interventions=VALUES(total_goal_interventions),")
            L("  save_and_retain=VALUES(save_and_retain), deflect_and_retain=VALUES(deflect_and_retain),")
            L("  save_and_deflect=VALUES(save_and_deflect), save_attempt=VALUES(save_attempt),")
            L("  no_save_attempt=VALUES(no_save_attempt),")
            L("  total_aerial_interventions=VALUES(total_aerial_interventions),")
            L("  crosses_faced=VALUES(crosses_faced),")
            L("  crosses_faced_inswing=VALUES(crosses_faced_inswing), crosses_faced_outswing=VALUES(crosses_faced_outswing),")
            L("  crosses_faced_driven=VALUES(crosses_faced_driven), crosses_faced_lofted=VALUES(crosses_faced_lofted),")
            L("  crosses_faced_cutback=VALUES(crosses_faced_cutback), crosses_faced_push=VALUES(crosses_faced_push),")
            L("  gk_name=VALUES(gk_name),")
            L("  punches_complete=VALUES(punches_complete), punches_incomplete=VALUES(punches_incomplete),")
            L("  claims_complete=VALUES(claims_complete), claims_incomplete=VALUES(claims_incomplete),")
            L("  tipped_palmed_complete=VALUES(tipped_palmed_complete),")
            L("  tipped_palmed_incomplete=VALUES(tipped_palmed_incomplete);")
    L("")

    # ── Set plays (pages 39/40) ───────────────────────────────────────────────
    for (code, pg) in [(home_code, "39"), (away_code, "40")]:
        sp = pages.get(pg, {}).get("data", {})
        totals = sp.get("totals") or {}
        fk     = sp.get("free_kicks") or {}

        def n(v):
            return "NULL" if v is None else str(v)

        set_pl  = totals.get("set_plays")
        fk_tot  = totals.get("free_kicks")
        pens    = totals.get("penalties")
        cors    = totals.get("corners")
        throws  = totals.get("throw_ins")
        fk_dir  = fk.get("direct")
        fk_ind  = fk.get("indirect")

        corners_type  = sp.get("corners_by_delivery_type") or {}
        corners_style = sp.get("corners_by_delivery_style") or {}
        c_direct = corners_type.get("direct_to_area") or {}
        c_short  = corners_type.get("short") or {}
        c_edge   = corners_type.get("edge_of_penalty_area") or {}

        if set_pl is not None:
            L("INSERT INTO match_set_play_stats")
            L("  (team_id, match_id, scope, set_plays, free_kicks,")
            L("   free_kicks_direct, free_kicks_indirect, penalties, corners, throw_ins,")
            L("   corner_direct_area_left, corner_direct_area_right, corner_direct_area_total,")
            L("   corner_short_left, corner_short_right, corner_short_total,")
            L("   corner_edge_left, corner_edge_right, corner_edge_total,")
            L("   corner_inswing, corner_outswing, corner_driven, corner_lofted)")
            L(f"VALUES ({_team(code)}, {_match(match_no)}, 'match',")
            L(f"  {n(set_pl)}, {n(fk_tot)}, {n(fk_dir)}, {n(fk_ind)},")
            L(f"  {n(pens)}, {n(cors)}, {n(throws)},")
            L(f"  {n(c_direct.get('from_left'))}, {n(c_direct.get('from_right'))}, {n(c_direct.get('total'))},")
            L(f"  {n(c_short.get('from_left'))}, {n(c_short.get('from_right'))}, {n(c_short.get('total'))},")
            L(f"  {n(c_edge.get('from_left'))}, {n(c_edge.get('from_right'))}, {n(c_edge.get('total'))},")
            L(f"  {n(corners_style.get('inswing'))}, {n(corners_style.get('outswing'))},")
            L(f"  {n(corners_style.get('driven'))}, {n(corners_style.get('lofted'))})")
            L("ON DUPLICATE KEY UPDATE")
            L("  set_plays=VALUES(set_plays), free_kicks=VALUES(free_kicks),")
            L("  free_kicks_direct=VALUES(free_kicks_direct),")
            L("  free_kicks_indirect=VALUES(free_kicks_indirect),")
            L("  penalties=VALUES(penalties), corners=VALUES(corners),")
            L("  throw_ins=VALUES(throw_ins),")
            L("  corner_direct_area_left=VALUES(corner_direct_area_left),")
            L("  corner_direct_area_right=VALUES(corner_direct_area_right),")
            L("  corner_direct_area_total=VALUES(corner_direct_area_total),")
            L("  corner_short_left=VALUES(corner_short_left),")
            L("  corner_short_right=VALUES(corner_short_right),")
            L("  corner_short_total=VALUES(corner_short_total),")
            L("  corner_edge_left=VALUES(corner_edge_left),")
            L("  corner_edge_right=VALUES(corner_edge_right),")
            L("  corner_edge_total=VALUES(corner_edge_total),")
            L("  corner_inswing=VALUES(corner_inswing), corner_outswing=VALUES(corner_outswing),")
            L("  corner_driven=VALUES(corner_driven), corner_lofted=VALUES(corner_lofted);")
    L("")

    # ── Per-player: Cross breakdown (pages 18/19) ─────────────────────────────
    for (code, pg) in [(home_code, "18"), (away_code, "19")]:
        cr = pages.get(pg, {}).get("data", {})
        if not cr:
            continue
        for pl in cr.get("players", []):
            num  = pl.get("num")
            name = pl.get("name", "")
            if num is None and not name:
                continue
            L(f"UPDATE player_stats SET")
            L(f"  crosses_inswing={_n(pl.get('inswing'))},")
            L(f"  crosses_outswing={_n(pl.get('outswing'))},")
            L(f"  crosses_driven={_n(pl.get('driven'))},")
            L(f"  crosses_lofted={_n(pl.get('lofted'))},")
            L(f"  crosses_cutback={_n(pl.get('cutback'))},")
            L(f"  crosses_push_cross={_n(pl.get('push_cross'))}")
            if num is not None:
                L(f"WHERE player_id=(SELECT id FROM players WHERE team_id={_team(code)} AND jersey_number={num})")
            else:
                L(f"WHERE player_id=(SELECT id FROM players WHERE team_id={_team(code)} AND name={_q(name)} LIMIT 1)")
            L(f"  AND match_id={_match(match_no)} AND scope='match';")
    L("")

    # ── Per-player: Line breaks (pages 10/11) ────────────────────────────────
    for (code, pg) in [(home_code, "10"), (away_code, "11")]:
        lb_data = pages.get(pg, {}).get("data", {})
        if not lb_data:
            continue
        for pl in lb_data.get("players", []):
            num  = pl.get("num")
            name = pl.get("name", "")
            if num is None and not name:
                continue
            if num is not None:
                player_id_expr = f"(SELECT id FROM players WHERE team_id={_team(code)} AND jersey_number={num})"
            else:
                player_id_expr = f"(SELECT id FROM players WHERE team_id={_team(code)} AND name={_q(name)} LIMIT 1)"
            L("INSERT INTO player_line_breaks")
            L("  (player_id, match_id, scope, attempted, completed,")
            L("   dir_through, dir_around, dir_over,")
            L("   dist_pass, dist_cross, dist_ball_prog,")
            L("   unit_4u_attacking, unit_4u_attacking_mid, unit_4u_midfield, unit_4u_defensive,")
            L("   unit_3u_attacking, unit_3u_midfield, unit_3u_defensive,")
            L("   unit_2u_midfield, unit_2u_defensive)")
            L(f"VALUES ({player_id_expr}, {_match(match_no)}, 'match',")
            L(f"  {_n(pl.get('attempted'))}, {_n(pl.get('completed'))},")
            L(f"  {_n(pl.get('dir_through'))}, {_n(pl.get('dir_around'))}, {_n(pl.get('dir_over'))},")
            L(f"  {_n(pl.get('dist_type_pass'))}, {_n(pl.get('dist_type_cross'))}, {_n(pl.get('dist_type_ball_progression'))},")
            L(f"  {_n(pl.get('4u_attacking'))}, {_n(pl.get('4u_attacking_mid'))}, {_n(pl.get('4u_midfield'))}, {_n(pl.get('4u_defensive'))},")
            L(f"  {_n(pl.get('3u_attacking'))}, {_n(pl.get('3u_midfield'))}, {_n(pl.get('3u_defensive'))},")
            L(f"  {_n(pl.get('2u_midfield'))}, {_n(pl.get('2u_defensive'))})")
            L("ON DUPLICATE KEY UPDATE")
            L("  attempted=VALUES(attempted), completed=VALUES(completed),")
            L("  dir_through=VALUES(dir_through), dir_around=VALUES(dir_around), dir_over=VALUES(dir_over),")
            L("  dist_pass=VALUES(dist_pass), dist_cross=VALUES(dist_cross), dist_ball_prog=VALUES(dist_ball_prog),")
            L("  unit_4u_attacking=VALUES(unit_4u_attacking), unit_4u_attacking_mid=VALUES(unit_4u_attacking_mid),")
            L("  unit_4u_midfield=VALUES(unit_4u_midfield), unit_4u_defensive=VALUES(unit_4u_defensive),")
            L("  unit_3u_attacking=VALUES(unit_3u_attacking), unit_3u_midfield=VALUES(unit_3u_midfield),")
            L("  unit_3u_defensive=VALUES(unit_3u_defensive),")
            L("  unit_2u_midfield=VALUES(unit_2u_midfield), unit_2u_defensive=VALUES(unit_2u_defensive);")
    L("")

    # ── Per-player stats: helper to emit UPDATE ───────────────────────────────
    def _player_ref(code: str, num, name: str) -> str:
        if num is not None:
            return (f"(SELECT ps.id FROM player_stats ps "
                    f"JOIN players pl ON pl.id=ps.player_id "
                    f"WHERE pl.team_id={_team(code)} AND pl.jersey_number={num} "
                    f"AND ps.match_id={_match(match_no)} AND ps.scope='match')")
        return (f"(SELECT ps.id FROM player_stats ps "
                f"JOIN players pl ON pl.id=ps.player_id "
                f"WHERE pl.team_id={_team(code)} AND pl.name={_q(name)} "
                f"AND ps.match_id={_match(match_no)} AND ps.scope='match' LIMIT 1)")

    # ── Per-player: Distributions (pages 42/44) ───────────────────────────────
    for (code, pg) in [(home_code, "42"), (away_code, "44")]:
        dist_players = pages.get(pg, {}).get("data", {}).get("players", [])
        for pl in dist_players:
            num  = pl.get("num")
            name = pl.get("name", "")
            L(f"UPDATE player_stats SET")
            L(f"  passes_attempted={_n(pl.get('passes_attempted'))},")
            L(f"  passes_completed={_n(pl.get('passes_completed'))},")
            L(f"  pass_completion_pct={_n(pl.get('pass_completion_pct'))},")
            L(f"  switches_of_play={_n(pl.get('switches_of_play'))},")
            L(f"  crosses_attempted={_n(pl.get('crosses_attempted'))},")
            L(f"  crosses_completed={_n(pl.get('crosses_completed'))},")
            L(f"  lb_attempted={_n(pl.get('line_breaks_attempted'))},")
            L(f"  lb_completed={_n(pl.get('line_breaks_completed'))},")
            L(f"  ball_progressions={_n(pl.get('ball_progressions'))},")
            L(f"  take_ons={_n(pl.get('take_ons'))},")
            L(f"  step_ins={_n(pl.get('step_ins'))},")
            L(f"  attempts_at_goal={_n(pl.get('attempts_at_goal'))}")
            if num is not None:
                L(f"WHERE player_id=(SELECT id FROM players WHERE team_id={_team(code)} AND jersey_number={num})")
            else:
                L(f"WHERE player_id=(SELECT id FROM players WHERE team_id={_team(code)} AND name={_q(name)} LIMIT 1)")
            L(f"  AND match_id={_match(match_no)} AND scope='match';")
    L("")

    # ── Per-player: Offers & Receptions (pages 43/45) ─────────────────────────
    for (code, pg) in [(home_code, "43"), (away_code, "45")]:
        off_players = pages.get(pg, {}).get("data", {}).get("players", [])
        for pl in off_players:
            num  = pl.get("num")
            name = pl.get("name", "")
            L(f"UPDATE player_stats SET")
            L(f"  total_offers={_n(pl.get('total_offers'))},")
            L(f"  offers_received={_n(pl.get('offers_received'))},")
            L(f"  offers_in_front={_n(pl.get('in_front'))},")
            L(f"  offers_in_between={_n(pl.get('in_between'))},")
            L(f"  offers_out_to_in={_n(pl.get('out_to_in'))},")
            L(f"  offers_in_to_out={_n(pl.get('in_to_out'))},")
            L(f"  offers_in_behind={_n(pl.get('in_behind'))},")
            L(f"  offers_no_movement={_n(pl.get('no_movement'))}")
            if num is not None:
                L(f"WHERE player_id=(SELECT id FROM players WHERE team_id={_team(code)} AND jersey_number={num})")
            else:
                L(f"WHERE player_id=(SELECT id FROM players WHERE team_id={_team(code)} AND name={_q(name)} LIMIT 1)")
            L(f"  AND match_id={_match(match_no)} AND scope='match';")
    L("")

    # ── Per-player: Out of Possession (pages 47/48) ───────────────────────────
    for (code, pg) in [(home_code, "47"), (away_code, "48")]:
        oop_players = pages.get(pg, {}).get("data", {}).get("players", [])
        for pl in oop_players:
            num  = pl.get("num")
            name = pl.get("name", "")
            L(f"UPDATE player_stats SET")
            L(f"  tackles_made={_n(pl.get('tackles_made'))},")
            L(f"  tackles_won={_n(pl.get('tackles_won'))},")
            L(f"  blocks={_n(pl.get('blocks'))},")
            L(f"  interceptions={_n(pl.get('interceptions'))},")
            L(f"  pressing_direct={_n(pl.get('pressing_direct'))},")
            L(f"  pressing_indirect={_n(pl.get('pressing_indirect'))},")
            L(f"  duels_won_aerial={_n(pl.get('duels_won_aerial'))},")
            L(f"  duels_won_physical={_n(pl.get('duels_won_physical'))},")
            L(f"  possession_contests_won={_n(pl.get('possession_contests_won'))},")
            L(f"  clearances={_n(pl.get('clearances'))},")
            L(f"  possession_regains={_n(pl.get('possession_regains'))},")
            L(f"  loose_ball_receptions={_n(pl.get('loose_ball_receptions'))},")
            L(f"  pushing_on={_n(pl.get('pushing_on'))},")
            L(f"  pushing_on_into_pressing={_n(pl.get('pushing_on_into_pressing'))},")
            L(f"  possession_interrupted={_n(pl.get('possession_interrupted'))}")
            if num is not None:
                L(f"WHERE player_id=(SELECT id FROM players WHERE team_id={_team(code)} AND jersey_number={num})")
            else:
                L(f"WHERE player_id=(SELECT id FROM players WHERE team_id={_team(code)} AND name={_q(name)} LIMIT 1)")
            L(f"  AND match_id={_match(match_no)} AND scope='match';")
    L("")

    # ── Per-player: Physical (pages 50/51) ────────────────────────────────────
    for (code, pg) in [(home_code, "50"), (away_code, "51")]:
        phys_players = pages.get(pg, {}).get("data", {}).get("players", [])
        for pl in phys_players:
            num  = pl.get("num")
            name = pl.get("name", "")
            L(f"UPDATE player_stats SET")
            L(f"  total_distance_m={_n(pl.get('total_distance_m'))},")
            L(f"  dist_zone1_m={_n(pl.get('zone1_0_7_m'))},")
            L(f"  dist_zone2_m={_n(pl.get('zone2_7_15_m'))},")
            L(f"  dist_zone3_m={_n(pl.get('zone3_15_20_m'))},")
            L(f"  dist_zone4_m={_n(pl.get('zone4_20_25_m'))},")
            L(f"  dist_zone5_m={_n(pl.get('zone5_25plus_m'))},")
            L(f"  high_speed_runs={_n(pl.get('high_speed_runs_zone3'))},")
            L(f"  sprints={_n(pl.get('sprints_zone4_5'))},")
            L(f"  top_speed_kmh={_n(pl.get('top_speed_kmh'))}")
            if num is not None:
                L(f"WHERE player_id=(SELECT id FROM players WHERE team_id={_team(code)} AND jersey_number={num})")
            else:
                L(f"WHERE player_id=(SELECT id FROM players WHERE team_id={_team(code)} AND name={_q(name)} LIMIT 1)")
            L(f"  AND match_id={_match(match_no)} AND scope='match';")
    L("")

    return "\n".join(out)


# ─────────────────────────────────────────────────────────────────────────────

def process_all(
    data_dir:  str = ".claude/data",
    seeds_dir: str = "db/seeds",
    done_dir:  str = ".claude/data/done",
    out_file:  str = "db/seeds/04_all_matches.sql",
) -> None:
    """Process every PDF in data_dir, write combined SQL to out_file,
    then move each successfully processed PDF to done_dir."""
    pdfs = sorted(Path(data_dir).glob("*.pdf"))
    if not pdfs:
        print(f"No PDFs found in {data_dir}", file=sys.stderr)
        return

    Path(done_dir).mkdir(parents=True, exist_ok=True)
    Path(out_file).parent.mkdir(parents=True, exist_ok=True)

    all_sql: list[str] = [
        "-- ── All Match Data (auto-generated from PDF parser) ──────────────────────",
        "-- Run after 01_schema.sql, 02_teams_ger_cur.sql, 03_team_aggregates.sql",
        "USE wc26;",
        "",
    ]
    errors: list[str] = []
    processed = 0

    for pdf in pdfs:
        print(f"  Parsing {pdf.name}…", end=" ", flush=True)
        try:
            sql = pdf_to_sql(str(pdf))
            all_sql.append(sql)
            processed += 1
            pdf.rename(Path(done_dir) / pdf.name)
            print("✓")
        except Exception as exc:
            print(f"✗ {exc}", file=sys.stderr)
            errors.append(f"{pdf.name}: {exc}")

    Path(out_file).write_text("\n".join(all_sql))
    print(f"\nWrote {out_file} ({processed}/{len(pdfs)} matches)")

    if errors:
        print("\nFailed PDFs:")
        for e in errors:
            print(f"  ✗ {e}")


# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    ap = argparse.ArgumentParser(description="Convert FIFA PMSR PDFs to SQL")
    ap.add_argument("pdf", nargs="?",       help="Path to a single PDF")
    ap.add_argument("--batch", action="store_true", help="Process all PDFs in .claude/data/")
    ap.add_argument("--data-dir",  default=".claude/data",        help="PDF input directory")
    ap.add_argument("--seeds-dir", default="db/seeds",            help="SQL output directory")
    ap.add_argument("--done-dir",  default=".claude/data/done",   help="Processed PDF destination")
    ap.add_argument("--out",       default="db/seeds/04_all_matches.sql", help="Output SQL file (batch)")
    args = ap.parse_args()

    if args.batch:
        process_all(args.data_dir, args.seeds_dir, args.done_dir, args.out)
    elif args.pdf:
        print(pdf_to_sql(args.pdf))
    else:
        ap.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
