from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models import Match, MatchStats


async def get_overview(db: AsyncSession) -> dict:
    # Count matches with a score (fully processed)
    match_count_row = await db.execute(
        select(func.count()).where(Match.score_a.is_not(None))
    )
    matches_played = match_count_row.scalar_one() or 0

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
    }
