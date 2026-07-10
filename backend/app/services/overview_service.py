from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models import Match, MatchStats

# matches.group_letter is 'A'-'L' for group stage, one of these short codes
# for knockout rounds (see ingestion/pmsr_to_sql.py). Fixed bracket sizes.
KNOCKOUT_STAGE_SIZES = {"R32": 16, "R16": 8, "QF": 4, "SF": 2, "3RD": 1, "FIN": 1}
GROUP_STAGE_SIZE = 72


async def get_overview(db: AsyncSession) -> dict:
    # Count matches with a score (fully processed)
    match_count_row = await db.execute(
        select(func.count()).where(Match.score_a.is_not(None))
    )
    matches_played = match_count_row.scalar_one() or 0

    # Played-count per stage, so the frontend can show real group-stage vs.
    # knockout-round progress instead of one global count against thresholds
    # (which broke as soon as group and knockout matches were ingested
    # together — a knockout match was indistinguishable from a group match).
    stage_rows = await db.execute(
        select(Match.group_letter, func.count())
        .where(Match.score_a.is_not(None))
        .group_by(Match.group_letter)
    )
    played_by_letter: dict[str | None, int] = dict(stage_rows.all())
    stage_counts = {
        "group": sum(
            n for letter, n in played_by_letter.items()
            if letter is not None and letter not in KNOCKOUT_STAGE_SIZES
        ),
        **{k: played_by_letter.get(k, 0) for k in KNOCKOUT_STAGE_SIZES},
    }

    # Sum goals from matches table
    goals_row = await db.execute(
        select(func.sum(Match.score_a + Match.score_b)).where(Match.score_a.is_not(None))
    )
    goals_total = goals_row.scalar_one() or 0

    # Average in-contest % from match stats (scope='match', one row per team per match)
    # in-contest is the same for both teams, so just average across team_a rows
    ic_row = await db.execute(
        select(func.avg(MatchStats.possession_in_contest)).where(
            MatchStats.scope == "match",
            MatchStats.possession_in_contest.is_not(None),
        )
    )
    avg_in_contest = float(ic_row.scalar_one() or 0)

    return {
        "matches_played": matches_played,
        "goals_total": int(goals_total),
        "avg_in_contest_pct": round(avg_in_contest, 2),
        "stage_counts": stage_counts,
    }
