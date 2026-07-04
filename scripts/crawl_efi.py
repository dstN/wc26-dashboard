#!/usr/bin/env python3
"""Crawl efidatareference.com and generate db/seeds/03_team_aggregates.sql.

Run from repo root:
    python3 scripts/crawl_efi.py
"""
import json
import re
import sys
import time
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError

from bs4 import BeautifulSoup

BASE = "https://efidatareference.com"

TEAM_SLUGS = [
    "algeria", "argentina", "australia", "austria",
    "belgium", "bosnia-herzegovina", "brazil", "cabo-verde",
    "canada", "colombia", "congo-dr", "cote-divoire",
    "croatia", "curacao", "czechia", "ecuador",
    "egypt", "england", "france", "germany",
    "ghana", "haiti", "ir-iran", "iraq",
    "japan", "jordan", "korea-republic", "mexico",
    "morocco", "netherlands", "new-zealand", "norway",
    "panama", "paraguay", "portugal", "qatar",
    "saudi-arabia", "scotland", "senegal", "south-africa",
    "spain", "sweden", "switzerland", "tunisia",
    "turkiye", "uruguay", "usa", "uzbekistan",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; wc26-dashboard-crawler/1.0)"
}


def fetch(url: str) -> bytes:
    req = Request(url, headers=HEADERS)
    for attempt in range(3):
        try:
            with urlopen(req, timeout=20) as resp:
                return resp.read()
        except URLError as e:
            print(f"  !! {url} attempt {attempt+1}: {e}", file=sys.stderr)
            time.sleep(2 ** attempt)
    return b""


def tables_from_html(html: bytes) -> list[dict]:
    """Return list of {headers, rows} dicts for all tables in HTML."""
    soup = BeautifulSoup(html, "lxml")
    result = []
    for tbl in soup.find_all("table"):
        headers = [th.get_text(strip=True) for th in tbl.find_all("th")]
        rows = []
        for tr in tbl.find_all("tr"):
            cells = [td.get_text(strip=True) for td in tr.find_all("td")]
            if cells:
                rows.append(dict(zip(headers, cells)) if headers else cells)
        if rows:
            result.append({"headers": headers, "rows": rows})
    return result


def _f(val: str | None) -> str:
    """SQL float literal or NULL."""
    if not val or val.strip() in ("", "-", "N/A"):
        return "NULL"
    try:
        float(val)
        return val.strip()
    except ValueError:
        return "NULL"


def _i(val: str | None) -> str:
    """SQL int literal or NULL."""
    if not val or val.strip() in ("", "-", "N/A"):
        return "NULL"
    try:
        return str(int(float(val.strip())))
    except ValueError:
        return "NULL"


def _s(val: str | None) -> str:
    """SQL string literal."""
    if not val:
        return "NULL"
    return "'" + val.replace("'", "''") + "'"


# Canonical display name → DB team name override
DISPLAY_OVERRIDES = {
    "Côte d'Ivoire": "Côte d'Ivoire",
    "IR Iran": "IR Iran",
    "Korea Republic": "Korea Republic",
    "Bosnia-Herzegovina": "Bosnia and Herzegovina",
}

SLUG_TO_DISPLAY = {
    "algeria": "Algeria",
    "argentina": "Argentina",
    "australia": "Australia",
    "austria": "Austria",
    "belgium": "Belgium",
    "bosnia-herzegovina": "Bosnia and Herzegovina",
    "brazil": "Brazil",
    "cabo-verde": "Cabo Verde",
    "canada": "Canada",
    "colombia": "Colombia",
    "congo-dr": "Congo DR",
    "cote-divoire": "Côte d'Ivoire",
    "croatia": "Croatia",
    "curacao": "Curaçao",
    "czechia": "Czechia",
    "ecuador": "Ecuador",
    "egypt": "Egypt",
    "england": "England",
    "france": "France",
    "germany": "Germany",
    "ghana": "Ghana",
    "haiti": "Haiti",
    "ir-iran": "IR Iran",
    "iraq": "Iraq",
    "japan": "Japan",
    "jordan": "Jordan",
    "korea-republic": "Korea Republic",
    "mexico": "Mexico",
    "morocco": "Morocco",
    "netherlands": "Netherlands",
    "new-zealand": "New Zealand",
    "norway": "Norway",
    "panama": "Panama",
    "paraguay": "Paraguay",
    "portugal": "Portugal",
    "qatar": "Qatar",
    "saudi-arabia": "Saudi Arabia",
    "scotland": "Scotland",
    "senegal": "Senegal",
    "south-africa": "South Africa",
    "spain": "Spain",
    "sweden": "Sweden",
    "switzerland": "Switzerland",
    "tunisia": "Tunisia",
    "turkiye": "Türkiye",
    "uruguay": "Uruguay",
    "usa": "USA",
    "uzbekistan": "Uzbekistan",
}


def crawl_team(slug: str) -> dict:
    display = SLUG_TO_DISPLAY[slug]
    print(f"  {slug} …", end=" ", flush=True)

    # General + physical data
    gen_url = f"{BASE}/{slug}-2026-general-and-physical-data/"
    gen_html = fetch(gen_url)
    gen_tables = tables_from_html(gen_html)

    team_row = {}
    opp_row = {}
    for tbl in gen_tables:
        hdrs = tbl["headers"]
        if "Possession" in hdrs and "Goals" in hdrs:
            data_rows = [r for r in tbl["rows"] if r.get("Team", "") != "Team"]
            for row in data_rows:
                name = row.get("Team", "").strip()
                is_opp = name.lower() in ("opponents", "opponent")
                if is_opp:
                    opp_row = row
                elif not team_row:
                    team_row = row
            # Fallback: if team name was blank, use first row
            if not team_row and data_rows:
                team_row = data_rows[0]
                if len(data_rows) > 1:
                    opp_row = data_rows[1]
            break

    # Phases of play
    phases_url = f"{BASE}/{slug}-2026-phases-of-play-and-shapes/"
    phases_html = fetch(phases_url)
    phases_tables = tables_from_html(phases_html)

    phase_team_row = {}
    shape_team_row = {}
    for tbl in phases_tables:
        hdrs = tbl["headers"]
        if "In/Pos-Build Up Unopposed" in hdrs and not phase_team_row:
            data_rows = [r for r in tbl["rows"] if r.get("Team", "") not in ("Team", "Opponents", "Opponent")]
            for row in data_rows:
                name = row.get("Team", "").strip()
                if name.lower() not in ("opponents", "opponent"):
                    phase_team_row = row
                    break
            if not phase_team_row and data_rows:
                phase_team_row = data_rows[0]
        if "Bld Up-Distance From Own Endline (m)" in hdrs and not shape_team_row:
            data_rows = [r for r in tbl["rows"] if r.get("Team", "") not in ("Team", "Opponents", "Opponent")]
            for row in data_rows:
                name = row.get("Team", "").strip()
                if name.lower() not in ("opponents", "opponent"):
                    shape_team_row = row
                    break
            if not shape_team_row and data_rows:
                shape_team_row = data_rows[0]

    # Line breaks
    lb_url = f"{BASE}/{slug}-2026-line-breaks/"
    lb_html = fetch(lb_url)
    lb_tables = tables_from_html(lb_html)

    lb_team_row = {}
    for tbl in lb_tables:
        hdrs = tbl["headers"]
        if "Ttl-Attempted Line Breaks" in hdrs and "Ttl-Completed Line Breaks" in hdrs:
            data_rows = [r for r in tbl["rows"] if r.get("Team", "") not in ("Team", "Opponents", "Opponent")]
            for row in data_rows:
                name = row.get("Team", "").strip()
                if name.lower() not in ("opponents", "opponent"):
                    lb_team_row = row
                    break
            if not lb_team_row and data_rows:
                lb_team_row = data_rows[0]
            break

    time.sleep(0.4)  # polite crawl delay

    print("ok")
    return {
        "slug": slug,
        "display": display,
        "general": {"team": team_row, "opponents": opp_row},
        "phases": phase_team_row,
        "shapes": shape_team_row,
        "line_breaks": lb_team_row,
    }


def build_sql(teams_data: list[dict]) -> str:
    lines = [
        "-- Auto-generated by scripts/crawl_efi.py",
        "-- EFI team aggregate stats for all 48 WC26 teams",
        "-- Source: https://efidatareference.com",
        "",
        "SET NAMES utf8mb4;",
        "",
    ]

    # Teams table
    lines += [
        "-- ── Teams ──────────────────────────────────────────────────────────",
        "INSERT INTO teams (team_slug, team_name, group_name, color_primary)",
        "VALUES",
    ]
    team_vals = []
    for td in teams_data:
        slug = td["slug"]
        name = td["display"].replace("'", "\\'")
        team_vals.append(f"  ({_s(slug)}, '{name}', '', '#888888')")
    lines.append(",\n".join(team_vals))
    lines += [
        "ON DUPLICATE KEY UPDATE team_name=VALUES(team_name);",
        "",
    ]

    # match_stats (team_aggregate scope, match_id=NULL)
    lines += [
        "-- ── Team aggregate match_stats ────────────────────────────────────",
    ]
    for td in teams_data:
        slug = td["slug"]
        g = td["general"]["team"]
        o = td["general"]["opponents"]
        if not g:
            continue

        poss = _f(g.get("Possession"))
        opp_poss = _f(o.get("Possession")) if o else "NULL"
        in_contest = "NULL"
        if poss != "NULL" and opp_poss != "NULL":
            try:
                ic = 100.0 - float(poss) - float(opp_poss)
                in_contest = f"{ic:.1f}"
            except ValueError:
                pass

        goals = _i(g.get("Goals"))
        shots = _i(g.get("Attempts at Goal"))
        passes_total = _i(g.get("Total Passes"))
        passes_completed = _i(g.get("Completed Passes"))
        pass_pct = _f(g.get("Pass Completion %"))
        line_breaks_for = _i(g.get("Completed Line Breaks"))
        line_breaks_against = _i(g.get("Defensive Line Breaks"))
        crosses = _i(g.get("Crosses"))
        ball_progressions = _i(g.get("Ball Progressions"))
        def_pressures = _i(g.get("Defensive Pressures Applied"))
        direct_pressures = _i(g.get("Direct Pressures"))
        forced_turnovers = _i(g.get("Forced Turnovers"))
        second_balls = _i(g.get("Second Balls"))
        dist_total = _f(g.get("Total Distance Covered"))
        dist_high_speed = _f(g.get("High Speed Distance Covered"))

        lines.append(
            f"INSERT INTO match_stats (team_id, match_id, scope, "
            f"possession_pct, in_contest_pct, out_of_possession_pct, "
            f"goals, shots, passes_total, passes_completed, pass_completion_pct, "
            f"line_breaks_for, line_breaks_against, crosses, ball_progressions, "
            f"def_pressures_applied, direct_pressures, forced_turnovers, second_balls, "
            f"distance_total_km, distance_high_speed_km)"
            f"\nSELECT t.team_id, NULL, 'team_aggregate', "
            f"{poss}, {in_contest}, {opp_poss}, "
            f"{goals}, {shots}, {passes_total}, {passes_completed}, {pass_pct}, "
            f"{line_breaks_for}, {line_breaks_against}, {crosses}, {ball_progressions}, "
            f"{def_pressures}, {direct_pressures}, {forced_turnovers}, {second_balls}, "
            f"{dist_total}, {dist_high_speed}"
            f"\nFROM teams t WHERE t.team_slug = {_s(slug)}"
            f"\nON DUPLICATE KEY UPDATE possession_pct=VALUES(possession_pct), goals=VALUES(goals);"
        )

    lines.append("")

    # Phases
    lines += [
        "-- ── Team aggregate phases ──────────────────────────────────────────",
    ]
    phase_col_map = {
        "Build Up Unopposed": "In/Pos-Build Up Unopposed",
        "Build Up Opposed": "In/Pos-Build Up Opposed",
        "Progression": "In/Pos-Progression",
        "Final Third": "In/Pos-Final Third",
        "Long Ball": "In/Pos-Long Ball",
        "Attacking Transition": "In/Pos-Attacking Transition",
        "Counter Attack": "In/Pos-Counter Attack",
        "Set Piece": "In/Pos-Set Piece",
        "High Press": "Out/Pos-High Press",
        "Mid Press": "Out/Pos-Mid Press",
        "Low Press": "Out/Pos-Low Press",
        "High Block": "Out/Pos-High Block",
        "Mid Block": "Out/Pos-Mid Block",
        "Low Block": "Out/Pos-Low Block",
    }
    for td in teams_data:
        slug = td["slug"]
        p = td["phases"]
        if not p:
            continue
        for phase_name, col in phase_col_map.items():
            val = _i(p.get(col))
            group = "in_possession" if col.startswith("In/Pos") else "out_of_possession"
            lines.append(
                f"INSERT INTO phases (team_id, match_id, phase_name, phase_group, phase_count)"
                f"\nSELECT t.team_id, NULL, {_s(phase_name)}, {_s(group)}, {val}"
                f"\nFROM teams t WHERE t.team_slug = {_s(slug)}"
                f"\nON DUPLICATE KEY UPDATE phase_count=VALUES(phase_count);"
            )

    lines.append("")

    # Line breaks
    lines += [
        "-- ── Team aggregate line breaks ────────────────────────────────────",
    ]
    lb_map = {
        "Through": ("Thrgh-Attempted Line Breaks", "Thrgh-Completed Line Breaks"),
        "Around": ("Arnd-Attempted Line Breaks", "Arnd-Completed Line Breaks"),
        "Over": ("Ovr-Attempted Line Breaks", "Ovr-Completed Line Breaks"),
        "Total": ("Ttl-Attempted Line Breaks", "Ttl-Completed Line Breaks"),
    }
    for td in teams_data:
        slug = td["slug"]
        lb = td["line_breaks"]
        if not lb:
            continue
        for line_type, (att_col, comp_col) in lb_map.items():
            att = _i(lb.get(att_col))
            comp = _i(lb.get(comp_col))
            lines.append(
                f"INSERT INTO line_breaks (team_id, match_id, line_type, breaks_attempted, breaks_completed)"
                f"\nSELECT t.team_id, NULL, {_s(line_type)}, {att}, {comp}"
                f"\nFROM teams t WHERE t.team_slug = {_s(slug)}"
                f"\nON DUPLICATE KEY UPDATE breaks_attempted=VALUES(breaks_attempted), breaks_completed=VALUES(breaks_completed);"
            )

    lines.append("")
    return "\n".join(lines)


def main():
    out_dir = Path(__file__).parent.parent / "db" / "seeds"
    json_out = out_dir / "team_aggregates.json"
    sql_out = out_dir / "03_team_aggregates.sql"

    all_data = []
    print(f"Crawling {len(TEAM_SLUGS)} teams from efidatareference.com …")
    for slug in TEAM_SLUGS:
        try:
            data = crawl_team(slug)
            all_data.append(data)
        except Exception as e:
            print(f"  ERROR {slug}: {e}", file=sys.stderr)
            all_data.append({"slug": slug, "display": SLUG_TO_DISPLAY[slug],
                             "general": {}, "phases": {}, "shapes": {}, "line_breaks": {}})

    # Save raw JSON
    json_out.write_text(json.dumps(all_data, indent=2, ensure_ascii=False))
    print(f"\nRaw JSON → {json_out}")

    # Generate SQL
    sql = build_sql(all_data)
    sql_out.write_text(sql)
    print(f"SQL seed → {sql_out}")
    print(f"Done — {len(all_data)} teams processed.")


if __name__ == "__main__":
    main()
