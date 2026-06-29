"""
DEPRECATED — superseded by parse_pmsr.py + pmsr_to_sql.py.

parse_pmsr.py covers all 44 PMSR pages with correct page-layout detection
(extra shot-log pages, in-possession spatial data, GK aerial breakdown, etc.).
pmsr_to_sql.py emits full INSERT/UPDATE SQL for all 11 DB tables.

This file is retained for reference only. Do not use for new ingestion.
Use: python -m ingestion.pmsr_to_sql path/to/pdfs/ --out db/seeds/04_all_matches.sql
"""

import warnings
warnings.warn(
    "parse_efi_pdf is deprecated. Use parse_pmsr + pmsr_to_sql instead.",
    DeprecationWarning,
    stacklevel=2,
)

from __future__ import annotations

import argparse
import re
import sys
import warnings
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

warnings.filterwarnings("ignore")  # suppress pdfplumber font warnings

try:
    import pdfplumber
except ImportError:
    sys.exit("pdfplumber is required: pip install pdfplumber")

# ── Data classes ────────────────────────────────────────────────────────────

@dataclass
class TeamSpatial:
    block_type: str          # 'high' | 'mid' | 'low'
    defensive_line_height: float
    team_length: float


@dataclass
class LineBreak:
    line_type: str           # 'defensive' | 'midfield' | 'attacking'
    attempted: int
    completed: int


@dataclass
class Phase:
    phase_name: str
    phase_group: str         # 'in' | 'out'
    pct: float


@dataclass
class MatchData:
    match_no: int
    group_letter: str
    venue: str
    match_date: str          # YYYY-MM-DD
    team_a_slug: str
    team_b_slug: str
    score_a: int
    score_b: int

    # Key stats (team_a / team_b perspective)
    possession_a: float = 0.0
    possession_contest: float = 0.0
    possession_b: float = 0.0
    xg_a: float = 0.0
    xg_b: float = 0.0
    goals_a: int = 0
    goals_b: int = 0
    ball_recovery_a: float = 0.0
    ball_recovery_b: float = 0.0

    phases_a: list[Phase] = field(default_factory=list)
    phases_b: list[Phase] = field(default_factory=list)

    # Defensive (out-of-possession) spatial: pages 28-29
    spatial_def_a: list[TeamSpatial] = field(default_factory=list)
    spatial_def_b: list[TeamSpatial] = field(default_factory=list)

    line_breaks_a: list[LineBreak] = field(default_factory=list)
    line_breaks_b: list[LineBreak] = field(default_factory=list)

    forced_turnovers_a: int = 0
    forced_turnovers_b: int = 0


# ── Month lookup ─────────────────────────────────────────────────────────────

_MONTHS = {
    "January": 1, "February": 2, "March": 3, "April": 4,
    "May": 5, "June": 6, "July": 7, "August": 8,
    "September": 9, "October": 10, "November": 11, "December": 12,
}


def _parse_date(text: str) -> str:
    """Convert '14 June 2026' → '2026-06-14'."""
    m = re.search(r"(\d{1,2})\s+(\w+)\s+(\d{4})", text)
    if not m:
        return "2026-01-01"
    day, mon, year = int(m.group(1)), _MONTHS.get(m.group(2), 1), int(m.group(3))
    return f"{year:04d}-{mon:02d}-{day:02d}"


# ── Team slug mapping ─────────────────────────────────────────────────────────

# Maps PDF team name → DB slug.  Extend as new PDFs are processed.
_TEAM_SLUGS: dict[str, str] = {
    "Germany": "ger",
    "Curaçao": "cur", "Curacao": "cur",
    "Algeria": "alg", "Argentina": "arg", "Australia": "aus",
    "Austria": "aut", "Belgium": "bel", "Bosnia and Herzegovina": "bih",
    "Brazil": "bra", "Cape Verde": "cpv", "Canada": "can",
    "Colombia": "col", "DR Congo": "cod", "Ivory Coast": "civ",
    "Croatia": "cro", "Czech Republic": "cze", "Ecuador": "ecu",
    "Egypt": "egy", "England": "eng", "France": "fra",
    "Ghana": "gha", "Haiti": "hai", "Iran": "irn", "Iraq": "irq",
    "Japan": "jpn", "Jordan": "jor", "South Korea": "kor",
    "Korea Republic": "kor", "Mexico": "mex", "Morocco": "mar",
    "Netherlands": "ned", "New Zealand": "nzl", "Norway": "nor",
    "Panama": "pan", "Paraguay": "par", "Portugal": "por",
    "Qatar": "qat", "Saudi Arabia": "ksa", "Scotland": "sco",
    "Senegal": "sen", "South Africa": "rsa", "Spain": "esp",
    "Sweden": "swe", "Switzerland": "sui", "Tunisia": "tun",
    "Turkey": "tur", "Turkey (Türkiye)": "tur", "Türkiye": "tur",
    "Uruguay": "uru", "USA": "usa", "United States": "usa",
    "Uzbekistan": "uzb",
}


def _slug(name: str) -> str:
    return _TEAM_SLUGS.get(name.strip(), name.strip().lower()[:3])


# ── Page parsers ─────────────────────────────────────────────────────────────

def _parse_page1(text: str) -> tuple[str, str, int, int, int, str, str, str]:
    """Return (team_a, team_b, score_a, score_b, match_no, group_letter, venue, match_date)."""
    lines = [l.strip() for l in text.splitlines() if l.strip()]

    team_a, team_b, score_a, score_b = "", "", 0, 0
    # First line: "Germany 7 - 1 Curaçao"
    m = re.match(r"^(.+?)\s+(\d+)\s*[-–]\s*(\d+)\s+(.+)$", lines[0])
    if m:
        team_a, score_a, score_b, team_b = (
            m.group(1).strip(), int(m.group(2)), int(m.group(3)), m.group(4).strip()
        )

    match_no, group_letter = 1, "A"
    for line in lines:
        mg = re.search(r"Group\s+([A-Z])\s*[-–]\s*Match\s+(\d+)", line)
        if mg:
            group_letter, match_no = mg.group(1), int(mg.group(2))
            break

    match_date = _parse_date(text)

    venue = ""
    for line in lines:
        if "Stadium" in line or "Arena" in line or "Field" in line:
            if not re.search(r"POST MATCH|MATCH SUMMARY", line, re.I):
                venue = line
                break

    return team_a, team_b, score_a, score_b, match_no, group_letter, venue, match_date


def _parse_page3(text: str) -> dict:
    """Extract key stats from the Key Statistics page."""
    stats: dict = {}

    # Possession: "Total 57.8% 6.9% 35.3% Total"
    m = re.search(r"Total\s+([\d.]+)%\s+([\d.]+)%\s+([\d.]+)%\s+Total", text)
    if m:
        stats["possession_a"] = float(m.group(1))
        stats["possession_contest"] = float(m.group(2))
        stats["possession_b"] = float(m.group(3))

    # Goals: "7 Goals 1"
    m = re.search(r"(\d+)\s+Goals\s+(\d+)", text)
    if m:
        stats["goals_a"], stats["goals_b"] = int(m.group(1)), int(m.group(2))

    # xG: "4.17 xG (Expected Goals) 0.4"
    m = re.search(r"([\d.]+)\s+xG.*?([\d.]+)", text)
    if m:
        stats["xg_a"], stats["xg_b"] = float(m.group(1)), float(m.group(2))

    return stats


def _parse_page4(text: str) -> tuple[list[Phase], list[Phase]]:
    """Parse phases of play page (both teams, in + out of possession)."""
    phases_a: list[Phase] = []
    phases_b: list[Phase] = []

    group = "in"
    for line in text.splitlines():
        line = line.strip()
        if "OUT OF POSSESSION" in line:
            group = "out"
            continue
        if "IN POSSESSION" in line:
            group = "in"
            continue

        # "35% Build Up Unopposed 25%" or "9% High Press 2%"
        m = re.match(r"(\d+)%\s+(.+?)\s+(\d+)%\s*$", line)
        if m:
            pct_a, name, pct_b = int(m.group(1)), m.group(2).strip(), int(m.group(3))
            phases_a.append(Phase(phase_name=name, phase_group=group, pct=float(pct_a)))
            phases_b.append(Phase(phase_name=name, phase_group=group, pct=float(pct_b)))

    return phases_a, phases_b


def _spatial_from_words(page) -> list[TeamSpatial]:
    """
    Extract 3 spatial blocks (high/mid/low) from a spatial page.

    The page has 3 mini-pitch columns left-to-right:
      Col1 (x < 350): first block listed in the header
      Col2 (x 350-640): second block
      Col3 (x > 640): third block

    For In Possession pages (p6-7): header order is Build Up Low, Build Up Mid, Final Third.
    Maps these to block_type: low, mid, high.

    For Defensive pages (p28-29): header order is High Block/Press, Mid Block, Low Block.
    Maps to block_type: high, mid, low.

    Within each column we take the first two numeric-meter values (by top position):
      first  = defensive_line_height
      second = team_length
    """
    words = page.extract_words(x_tolerance=5, y_tolerance=5)

    cols: dict[int, list[tuple[float, float]]] = {0: [], 1: [], 2: []}
    for w in words:
        if not (re.fullmatch(r"\d+m", w["text"])):
            continue
        val = float(w["text"][:-1])
        x = w["x0"]
        col = 0 if x < 350 else (1 if x < 640 else 2)
        cols[col].append((w["top"], val))

    result: list[TeamSpatial] = []
    # Detect header text to determine column→block mapping
    full_text = page.extract_text() or ""
    if "High Block" in full_text or "High Press" in full_text:
        col_blocks = ["high", "mid", "low"]
    else:
        # In Possession: Build Up Low (col0), Build Up Mid (col1), Final Third (col2)
        col_blocks = ["low", "mid", "high"]

    for col_idx in range(3):
        vals = sorted(cols[col_idx])  # sort by y (top)
        if len(vals) >= 2:
            def_line = vals[0][1]
            team_len = vals[1][1]
        elif len(vals) == 1:
            def_line = vals[0][1]
            team_len = 0.0
        else:
            def_line = team_len = 0.0
        result.append(TeamSpatial(
            block_type=col_blocks[col_idx],
            defensive_line_height=def_line,
            team_length=team_len,
        ))

    return result


def _parse_linebreaks_page(text: str) -> list[LineBreak]:
    """
    Parse a Line Breaks page.

    Page header: "Attempted Line Breaks\n<Team> <total>\n<att> <comp> <att> <comp> <att> <comp>"
    4 Units = defensive, 3 Units = midfield, 2 Units = attacking.
    """
    lines = [l.strip() for l in text.splitlines() if l.strip()]

    # Find the summary line: "47 33 81 73 30 19"  (6 numbers)
    for line in lines:
        nums = re.findall(r"\d+", line)
        if len(nums) == 6:
            att_def, comp_def = int(nums[0]), int(nums[1])
            att_mid, comp_mid = int(nums[2]), int(nums[3])
            att_att, comp_att = int(nums[4]), int(nums[5])
            return [
                LineBreak("defensive", att_def, comp_def),
                LineBreak("midfield", att_mid, comp_mid),
                LineBreak("attacking", att_att, comp_att),
            ]

    return []


def _parse_defensive_page(text: str) -> int:
    """Extract forced turnovers count from a Defensive Actions page."""
    m = re.search(r"^(\d+)\s+\d+\s+\d+\s+\d+\s+[\d.]+\s+Regains", text, re.M)
    if m:
        return int(m.group(1))
    # Fallback: look for "46 41 8 41" at start of a line
    m = re.search(r"^(\d{2,3})\s+\d+", text, re.M)
    if m:
        return int(m.group(1))
    return 0


def _parse_pressure_page(text: str) -> tuple[float, float]:
    """Extract ball recovery times from the Defensive Pressure page."""
    m = re.search(r"([\d.]+)s\s+Ball Recovery Time\s+([\d.]+)s", text)
    if m:
        return float(m.group(1)), float(m.group(2))
    return 0.0, 0.0


# ── Main extraction ──────────────────────────────────────────────────────────

def extract(pdf_path: Path) -> MatchData:
    with pdfplumber.open(pdf_path) as pdf:
        n = len(pdf.pages)

        def text(page_no: int) -> str:
            if page_no > n:
                return ""
            return pdf.pages[page_no - 1].extract_text() or ""

        # Page 1 — match header
        team_a_name, team_b_name, score_a, score_b, match_no, group_letter, venue, match_date = (
            _parse_page1(text(1))
        )

        data = MatchData(
            match_no=match_no,
            group_letter=group_letter,
            venue=venue,
            match_date=match_date,
            team_a_slug=_slug(team_a_name),
            team_b_slug=_slug(team_b_name),
            score_a=score_a,
            score_b=score_b,
        )

        # Page 3 — key stats
        stats = _parse_page3(text(3))
        data.possession_a = stats.get("possession_a", 0.0)
        data.possession_contest = stats.get("possession_contest", 0.0)
        data.possession_b = stats.get("possession_b", 0.0)
        data.xg_a = stats.get("xg_a", 0.0)
        data.xg_b = stats.get("xg_b", 0.0)
        data.goals_a = stats.get("goals_a", score_a)
        data.goals_b = stats.get("goals_b", score_b)

        # Page 4 — phases of play
        data.phases_a, data.phases_b = _parse_page4(text(4))

        # Pages 6-7 — In Possession spatial (not used for DB currently, stored as 'low','mid','high')
        # Pages 28-29 — Defensive spatial (used as block_type high/mid/low)
        if n >= 28:
            data.spatial_def_a = _spatial_from_words(pdf.pages[27])  # page 28
        if n >= 29:
            data.spatial_def_b = _spatial_from_words(pdf.pages[28])  # page 29

        # Pages 8-9 — Line breaks
        data.line_breaks_a = _parse_linebreaks_page(text(8))
        data.line_breaks_b = _parse_linebreaks_page(text(9))

        # Pages 26-27 — Defensive actions (forced turnovers)
        data.forced_turnovers_a = _parse_defensive_page(text(26))
        data.forced_turnovers_b = _parse_defensive_page(text(27))

        # Page 30 — Ball recovery time
        if n >= 30:
            data.ball_recovery_a, data.ball_recovery_b = _parse_pressure_page(text(30))

    return data


# ── SQL generation ───────────────────────────────────────────────────────────

def _team_id(slug: str) -> str:
    return f"(SELECT id FROM teams WHERE slug = '{slug}')"


def generate_sql(data: MatchData) -> str:
    lines: list[str] = [
        "-- Auto-generated by ingestion/parse_efi_pdf.py",
        f"-- Match {data.match_no}: {data.team_a_slug.upper()} vs {data.team_b_slug.upper()}",
        "",
    ]

    ta = _team_id(data.team_a_slug)
    tb = _team_id(data.team_b_slug)

    # ── Match row ──────────────────────────────────────────────────────────
    lines += [
        "-- Match",
        f"INSERT INTO matches (match_no, team_a_id, team_b_id, score_a, score_b, venue, match_date, group_letter)",
        f"VALUES (",
        f"  {data.match_no}, {ta}, {tb},",
        f"  {data.score_a}, {data.score_b},",
        f"  '{data.venue}', '{data.match_date}', '{data.group_letter}'",
        f")",
        f"ON DUPLICATE KEY UPDATE",
        f"  score_a={data.score_a}, score_b={data.score_b},",
        f"  venue=VALUES(venue), match_date=VALUES(match_date);",
        "",
    ]

    # Inline match_id lookup
    mid = f"(SELECT id FROM matches WHERE match_no = {data.match_no})"

    # ── match_stats ────────────────────────────────────────────────────────
    lines.append("-- Match stats (team A)")
    lines.append(
        f"INSERT INTO match_stats "
        f"(team_id, match_id, scope, possession_team_a, possession_in_contest, possession_team_b, "
        f"xg_a, xg_b, goals_a, goals_b, ball_recovery_time_avg)"
    )
    lines.append(
        f"VALUES ({ta}, {mid}, 'match', "
        f"{data.possession_a}, {data.possession_contest}, {data.possession_b}, "
        f"{data.xg_a}, {data.xg_b}, {data.goals_a}, {data.goals_b}, {data.ball_recovery_a})"
    )
    lines.append(
        "ON DUPLICATE KEY UPDATE "
        "possession_team_a=VALUES(possession_team_a), possession_in_contest=VALUES(possession_in_contest), "
        "possession_team_b=VALUES(possession_team_b), xg_a=VALUES(xg_a), xg_b=VALUES(xg_b), "
        "goals_a=VALUES(goals_a), goals_b=VALUES(goals_b), "
        "ball_recovery_time_avg=VALUES(ball_recovery_time_avg);"
    )
    lines.append("")

    lines.append("-- Match stats (team B)")
    lines.append(
        f"INSERT INTO match_stats "
        f"(team_id, match_id, scope, possession_team_a, possession_in_contest, possession_team_b, "
        f"xg_a, xg_b, goals_a, goals_b, ball_recovery_time_avg)"
    )
    lines.append(
        f"VALUES ({tb}, {mid}, 'match', "
        f"{data.possession_b}, {data.possession_contest}, {data.possession_a}, "
        f"{data.xg_b}, {data.xg_a}, {data.score_b}, {data.score_a}, {data.ball_recovery_b})"
    )
    lines.append(
        "ON DUPLICATE KEY UPDATE "
        "possession_team_a=VALUES(possession_team_a), possession_in_contest=VALUES(possession_in_contest), "
        "possession_team_b=VALUES(possession_team_b), xg_a=VALUES(xg_a), xg_b=VALUES(xg_b), "
        "goals_a=VALUES(goals_a), goals_b=VALUES(goals_b), "
        "ball_recovery_time_avg=VALUES(ball_recovery_time_avg);"
    )
    lines.append("")

    # ── Phases ─────────────────────────────────────────────────────────────
    for slug, team_id_expr, phases in [
        (data.team_a_slug, ta, data.phases_a),
        (data.team_b_slug, tb, data.phases_b),
    ]:
        if not phases:
            continue
        lines.append(f"-- Phases ({slug.upper()})")
        for ph in phases:
            lines.append(
                f"INSERT INTO match_phases (team_id, match_id, scope, phase_name, phase_group, pct) "
                f"VALUES ({team_id_expr}, {mid}, 'match', '{ph.phase_name}', '{ph.phase_group}', {ph.pct}) "
                f"ON DUPLICATE KEY UPDATE pct=VALUES(pct);"
            )
        lines.append("")

    # ── Spatial stats (defensive) ──────────────────────────────────────────
    for slug, team_id_expr, spatials in [
        (data.team_a_slug, ta, data.spatial_def_a),
        (data.team_b_slug, tb, data.spatial_def_b),
    ]:
        if not spatials:
            continue
        lines.append(f"-- Spatial (defensive) ({slug.upper()})")
        for s in spatials:
            lines.append(
                f"INSERT INTO team_spatial_stats "
                f"(team_id, match_id, scope, block_type, defensive_line_height, team_length) "
                f"VALUES ({team_id_expr}, {mid}, 'match', '{s.block_type}', "
                f"{s.defensive_line_height}, {s.team_length}) "
                f"ON DUPLICATE KEY UPDATE "
                f"defensive_line_height=VALUES(defensive_line_height), team_length=VALUES(team_length);"
            )
        lines.append("")

    # ── Line breaks ────────────────────────────────────────────────────────
    for slug, team_id_expr, breaks in [
        (data.team_a_slug, ta, data.line_breaks_a),
        (data.team_b_slug, tb, data.line_breaks_b),
    ]:
        if not breaks:
            continue
        lines.append(f"-- Line breaks ({slug.upper()})")
        for lb in breaks:
            lines.append(
                f"INSERT INTO line_breaks (team_id, match_id, scope, line_type, attempted, completed) "
                f"VALUES ({team_id_expr}, {mid}, 'match', '{lb.line_type}', {lb.attempted}, {lb.completed}) "
                f"ON DUPLICATE KEY UPDATE attempted=VALUES(attempted), completed=VALUES(completed);"
            )
        lines.append("")

    # ── Defensive actions ──────────────────────────────────────────────────
    for slug, team_id_expr, forced in [
        (data.team_a_slug, ta, data.forced_turnovers_a),
        (data.team_b_slug, tb, data.forced_turnovers_b),
    ]:
        lines.append(f"-- Defensive actions ({slug.upper()})")
        lines.append(
            f"INSERT INTO defensive_actions (team_id, match_id, scope, forced_turnovers) "
            f"VALUES ({team_id_expr}, {mid}, 'match', {forced}) "
            f"ON DUPLICATE KEY UPDATE forced_turnovers=VALUES(forced_turnovers);"
        )
        lines.append("")

    return "\n".join(lines)


# ── CLI ──────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Parse EFI PDF match reports to SQL")
    parser.add_argument("pdfs", nargs="+", type=Path, help="One or more PDF files")
    parser.add_argument("--out", type=Path, default=None, help="Write SQL to file (default: stdout)")
    parser.add_argument("--dry-run", action="store_true", help="Print extracted data without SQL")
    args = parser.parse_args()

    all_sql: list[str] = []

    for pdf_path in args.pdfs:
        if not pdf_path.exists():
            print(f"[WARN] {pdf_path} not found, skipping", file=sys.stderr)
            continue
        print(f"[INFO] Parsing {pdf_path.name} …", file=sys.stderr)
        try:
            data = extract(pdf_path)
        except Exception as exc:
            print(f"[ERROR] {pdf_path.name}: {exc}", file=sys.stderr)
            continue

        if args.dry_run:
            print(f"\n{'='*60}")
            print(f"Match {data.match_no}: {data.team_a_slug.upper()} {data.score_a}"
                  f"–{data.score_b} {data.team_b_slug.upper()}")
            print(f"  Date: {data.match_date}  Venue: {data.venue}")
            print(f"  Possession: {data.possession_a}% / {data.possession_contest}% / {data.possession_b}%")
            print(f"  xG: {data.xg_a} / {data.xg_b}   Goals: {data.goals_a}/{data.goals_b}")
            print(f"  Phases A: {len(data.phases_a)}  Phases B: {len(data.phases_b)}")
            print(f"  Spatial A: {[(s.block_type, s.defensive_line_height, s.team_length) for s in data.spatial_def_a]}")
            print(f"  Spatial B: {[(s.block_type, s.defensive_line_height, s.team_length) for s in data.spatial_def_b]}")
            print(f"  LineBreaks A: {[(lb.line_type, lb.attempted, lb.completed) for lb in data.line_breaks_a]}")
            print(f"  LineBreaks B: {[(lb.line_type, lb.attempted, lb.completed) for lb in data.line_breaks_b]}")
            print(f"  ForcedTurnovers: A={data.forced_turnovers_a} B={data.forced_turnovers_b}")
            print(f"  BallRecovery: A={data.ball_recovery_a}s B={data.ball_recovery_b}s")
        else:
            all_sql.append(generate_sql(data))

    if not args.dry_run:
        sql_output = "\n\n".join(all_sql)
        if args.out:
            args.out.write_text(sql_output, encoding="utf-8")
            print(f"[INFO] Wrote {args.out}", file=sys.stderr)
        else:
            print(sql_output)


if __name__ == "__main__":
    main()
