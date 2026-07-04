from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import Match, Team, MatchStats, MatchPhase, TeamSpatialStat, LineBreak
from app.models import FinalThirdEntry, DefensiveAction
from sqlalchemy import func
from app.schemas.dashboard import (
    DashboardResponse, MatchMeta, KpiCard, TournamentOverviewSchema,
)
from app.schemas.team import TeamSchema
from app.schemas.match_stats import MatchStatsSchema
from app.schemas.phase import PhaseSchema
from app.schemas.spatial import TeamSpatialSchema, DEFENSIVE_BLOCKS, POSSESSION_BLOCKS
from app.schemas.line_break import LineBreakSchema
from app.schemas.final_third import FinalThirdEntrySchema
from app.schemas.defensive import DefensiveActionSchema


def _split_spatial(rows):
    validated = [TeamSpatialSchema.model_validate(s) for s in rows]
    return {
        "defensive": [r for r in validated if r.block in DEFENSIVE_BLOCKS],
        "possession": [r for r in validated if r.block in POSSESSION_BLOCKS],
    }


async def get_featured_match_id(db: AsyncSession) -> int:
    result = await db.execute(select(Match.id).order_by(Match.id.desc()).limit(1))
    row = result.scalar_one_or_none()
    if row is None:
        raise ValueError("No matches found")
    return row


async def get_match_dashboard(db: AsyncSession, match_id: int) -> DashboardResponse:
    # Fetch match + teams
    match_result = await db.execute(
        select(Match).where(Match.id == match_id)
    )
    match = match_result.scalar_one_or_none()
    if match is None:
        raise ValueError(f"Match {match_id} not found")

    team_a_result = await db.execute(select(Team).where(Team.id == match.team_a_id))
    team_b_result = await db.execute(select(Team).where(Team.id == match.team_b_id))
    team_a = team_a_result.scalar_one()
    team_b = team_b_result.scalar_one()

    # Match stats (use team_a perspective)
    stats_result = await db.execute(
        select(MatchStats).where(
            MatchStats.match_id == match_id,
            MatchStats.team_id == match.team_a_id,
            MatchStats.scope == "match",
        )
    )
    stats = stats_result.scalar_one()

    # Phases for both teams
    phases_a_result = await db.execute(
        select(MatchPhase).where(
            MatchPhase.match_id == match_id,
            MatchPhase.team_id == match.team_a_id,
            MatchPhase.scope == "match",
        )
    )
    phases_b_result = await db.execute(
        select(MatchPhase).where(
            MatchPhase.match_id == match_id,
            MatchPhase.team_id == match.team_b_id,
            MatchPhase.scope == "match",
        )
    )
    phases_a = phases_a_result.scalars().all()
    phases_b = phases_b_result.scalars().all()

    # Spatial for both teams
    spatial_a_result = await db.execute(
        select(TeamSpatialStat).where(
            TeamSpatialStat.match_id == match_id,
            TeamSpatialStat.team_id == match.team_a_id,
            TeamSpatialStat.scope == "match",
        )
    )
    spatial_b_result = await db.execute(
        select(TeamSpatialStat).where(
            TeamSpatialStat.match_id == match_id,
            TeamSpatialStat.team_id == match.team_b_id,
            TeamSpatialStat.scope == "match",
        )
    )

    # Line breaks for both teams
    lb_a_result = await db.execute(
        select(LineBreak).where(
            LineBreak.match_id == match_id,
            LineBreak.team_id == match.team_a_id,
            LineBreak.scope == "match",
        )
    )
    lb_b_result = await db.execute(
        select(LineBreak).where(
            LineBreak.match_id == match_id,
            LineBreak.team_id == match.team_b_id,
            LineBreak.scope == "match",
        )
    )

    # Final third entries for both teams
    ft_a_result = await db.execute(
        select(FinalThirdEntry).where(
            FinalThirdEntry.match_id == match_id,
            FinalThirdEntry.team_id == match.team_a_id,
            FinalThirdEntry.scope == "match",
        )
    )
    ft_b_result = await db.execute(
        select(FinalThirdEntry).where(
            FinalThirdEntry.match_id == match_id,
            FinalThirdEntry.team_id == match.team_b_id,
            FinalThirdEntry.scope == "match",
        )
    )

    # Defensive actions for both teams
    da_a_result = await db.execute(
        select(DefensiveAction).where(
            DefensiveAction.match_id == match_id,
            DefensiveAction.team_id == match.team_a_id,
            DefensiveAction.scope == "match",
        )
    )
    da_b_result = await db.execute(
        select(DefensiveAction).where(
            DefensiveAction.match_id == match_id,
            DefensiveAction.team_id == match.team_b_id,
            DefensiveAction.scope == "match",
        )
    )

    # Tournament overview — computed dynamically (not from stale cache table)
    matches_played = (await db.execute(
        select(func.count()).where(Match.score_a.is_not(None))
    )).scalar_one() or 0
    goals_total = (await db.execute(
        select(func.sum(Match.score_a + Match.score_b)).where(Match.score_a.is_not(None))
    )).scalar_one() or 0
    avg_in_contest = float((await db.execute(
        select(func.avg(MatchStats.possession_in_contest)).where(
            MatchStats.scope == "match",
            MatchStats.possession_in_contest.is_not(None),
        )
    )).scalar_one() or 0)

    team_a_schema = TeamSchema.model_validate(team_a)
    team_b_schema = TeamSchema.model_validate(team_b)

    match_date_str = match.match_date.isoformat() if match.match_date else ""

    return DashboardResponse(
        overview=TournamentOverviewSchema(
            matches_played=matches_played,
            goals_total=int(goals_total),
            avg_in_contest_pct=round(avg_in_contest, 2),
        ),
        featured=MatchMeta(
            id=match.id,
            match_no=match.match_no,
            score_a=match.score_a,
            score_b=match.score_b,
            venue=match.venue or "",
            match_date=match_date_str,
            group_letter=match.group_letter or "",
            team_a=team_a_schema,
            team_b=team_b_schema,
        ),
        possession=MatchStatsSchema.model_validate(stats),
        head_to_head=MatchStatsSchema.model_validate(stats),
        phases={
            "team_a": [PhaseSchema.model_validate(p) for p in phases_a],
            "team_b": [PhaseSchema.model_validate(p) for p in phases_b],
        },
        spatial={
            "team_a": _split_spatial(spatial_a_result.scalars().all()),
            "team_b": _split_spatial(spatial_b_result.scalars().all()),
        },
        line_breaks={
            "team_a": [LineBreakSchema.model_validate(lb) for lb in lb_a_result.scalars().all()],
            "team_b": [LineBreakSchema.model_validate(lb) for lb in lb_b_result.scalars().all()],
        },
        final_third={
            "team_a": [FinalThirdEntrySchema.model_validate(ft) for ft in ft_a_result.scalars().all()],
            "team_b": [FinalThirdEntrySchema.model_validate(ft) for ft in ft_b_result.scalars().all()],
        },
        defensive={
            "team_a": DefensiveActionSchema.model_validate(da_a_result.scalar_one()),
            "team_b": DefensiveActionSchema.model_validate(da_b_result.scalar_one()),
        },
        kpi_cards=[
            KpiCard(label="Matches Played", value=str(matches_played)),
            KpiCard(label="Goals Scored", value=str(int(goals_total))),
            KpiCard(label="Avg In-Contest", value=str(round(avg_in_contest, 2)), unit="%"),
        ],
    )
