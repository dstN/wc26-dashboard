from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func

from app.deps import get_db
from app.models import Team, Match, MatchStats, MatchPhase, Player, PlayerStat, LineBreak, DefensiveAction, MatchGkStat, MatchSetPlayStat
from app.schemas.team import TeamSchema
from app.schemas.match_stats import MatchStatsSchema
from app.schemas.dashboard import MatchMeta
from app.schemas.phase import PhaseSchema

router = APIRouter(prefix="/api/v1/teams", tags=["teams"])


@router.get("/", response_model=list[dict])
async def list_teams(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Team).order_by(Team.name))
    teams = result.scalars().all()

    # One query for all aggregate stats (was one per team)
    stats_result = await db.execute(
        select(MatchStats).where(MatchStats.scope == "team_aggregate")
    )
    stats_by_team = {s.team_id: s for s in stats_result.scalars().all()}

    # Actual goals per team from real match results, in two grouped queries
    goals_by_team: dict[int, int] = {}
    for team_col, score_col in ((Match.team_a_id, Match.score_a), (Match.team_b_id, Match.score_b)):
        rows = await db.execute(
            select(team_col, func.sum(score_col))
            .where(score_col.is_not(None))
            .group_by(team_col)
        )
        for team_id, goals in rows.all():
            # SUM() returns Decimal on MySQL — coerce so JSON gets a number
            goals_by_team[team_id] = goals_by_team.get(team_id, 0) + int(goals or 0)

    out = []
    for team in teams:
        stats = stats_by_team.get(team.id)
        stats_dict = MatchStatsSchema.model_validate(stats).model_dump() if stats else None
        if stats_dict is not None:
            stats_dict["goals_a"] = goals_by_team.get(team.id, 0)
        out.append({
            "team": TeamSchema.model_validate(team).model_dump(),
            "stats": stats_dict,
        })
    return out


@router.get("/{team_id}/players")
async def get_team_players(team_id: int, db: AsyncSession = Depends(get_db)):
    team_result = await db.execute(select(Team).where(Team.id == team_id))
    team = team_result.scalar_one_or_none()
    if team is None:
        raise HTTPException(status_code=404, detail=f"Team {team_id} not found")

    result = await db.execute(
        select(Player).where(Player.team_id == team_id).order_by(Player.jersey_number)
    )
    players = result.scalars().all()
    return [
        {"id": p.id, "name": p.name, "position": p.position, "jersey_number": p.jersey_number}
        for p in players
    ]


@router.get("/{team_id}/phases")
async def get_team_phases(team_id: int, db: AsyncSession = Depends(get_db)):
    """Average phase distribution across all team's matches."""
    team_result = await db.execute(select(Team).where(Team.id == team_id))
    if team_result.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail=f"Team {team_id} not found")

    result = await db.execute(
        select(MatchPhase.phase_name, MatchPhase.phase_group, func.avg(MatchPhase.pct).label("avg_pct"))
        .where(MatchPhase.team_id == team_id, MatchPhase.scope == "match")
        .group_by(MatchPhase.phase_name, MatchPhase.phase_group)
        .order_by(MatchPhase.phase_group, func.avg(MatchPhase.pct).desc())
    )
    rows = result.all()
    return [
        {"phase_name": r.phase_name, "phase_group": r.phase_group, "pct": round(float(r.avg_pct), 1)}
        for r in rows
    ]


@router.get("/{team_id}/general")
async def get_team_general(team_id: int, db: AsyncSession = Depends(get_db)):
    team_result = await db.execute(select(Team).where(Team.id == team_id))
    team = team_result.scalar_one_or_none()
    if team is None:
        raise HTTPException(status_code=404, detail=f"Team {team_id} not found")

    stats_result = await db.execute(
        select(MatchStats).where(
            MatchStats.team_id == team_id,
            MatchStats.scope == "team_aggregate",
        )
    )
    stats = stats_result.scalar_one_or_none()

    return {
        "team": TeamSchema.model_validate(team),
        "stats": MatchStatsSchema.model_validate(stats) if stats else None,
    }


@router.get("/{team_id}/avg-stats")
async def get_team_avg_stats(team_id: int, db: AsyncSession = Depends(get_db)):
    """Averaged key stats across all parsed matches for a team."""
    team_result = await db.execute(select(Team).where(Team.id == team_id))
    if team_result.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail=f"Team {team_id} not found")

    match_ids_result = await db.execute(
        select(Match.id).where(or_(Match.team_a_id == team_id, Match.team_b_id == team_id))
    )
    match_ids = [r[0] for r in match_ids_result.all()]
    if not match_ids:
        return {"match_count": 0, "totals": {}, "averages": {}}

    def _f(v, d=2): return round(float(v), d) if v is not None else None
    def _i(v): return int(v) if v is not None else None

    totals: dict = {}
    counts: dict = {}

    def _add(key, val):
        if val is None:
            return
        totals[key] = totals.get(key, 0) + val
        counts[key] = counts.get(key, 0) + 1

    for mid in match_ids:
        ms = (await db.execute(
            select(MatchStats).where(MatchStats.match_id == mid, MatchStats.team_id == team_id, MatchStats.scope == "match")
        )).scalar_one_or_none()

        lb_rows = (await db.execute(
            select(LineBreak).where(LineBreak.match_id == mid, LineBreak.team_id == team_id, LineBreak.scope == "match")
        )).scalars().all()

        da = (await db.execute(
            select(DefensiveAction).where(DefensiveAction.match_id == mid, DefensiveAction.team_id == team_id, DefensiveAction.scope == "match")
        )).scalar_one_or_none()

        pl = (await db.execute(
            select(
                func.sum(PlayerStat.passes_attempted).label("passes_att"),
                func.sum(PlayerStat.passes_completed).label("passes_comp"),
                func.sum(PlayerStat.crosses_completed).label("crosses"),
                func.sum(PlayerStat.ball_progressions).label("ball_prog"),
                func.sum(PlayerStat.take_ons).label("take_ons"),
                func.sum(PlayerStat.tackles_made).label("tackles_made"),
                func.sum(PlayerStat.tackles_won).label("tackles_won"),
                func.sum(PlayerStat.interceptions).label("interceptions"),
                func.sum(PlayerStat.blocks).label("blocks"),
                func.sum(PlayerStat.clearances).label("clearances"),
                func.sum(PlayerStat.possession_regains).label("regains"),
                func.sum(PlayerStat.pressing_direct).label("pressing_direct"),
                func.sum(PlayerStat.duels_won_aerial).label("duels_aerial"),
                func.sum(PlayerStat.duels_won_physical).label("duels_physical"),
                func.sum(PlayerStat.total_distance_m).label("distance_m"),
            )
            .join(Player, Player.id == PlayerStat.player_id)
            .where(PlayerStat.match_id == mid, Player.team_id == team_id, PlayerStat.scope == "match")
        )).first()

        gk = (await db.execute(
            select(MatchGkStat).where(MatchGkStat.match_id == mid, MatchGkStat.team_id == team_id, MatchGkStat.scope == "match")
        )).scalar_one_or_none()

        sp = (await db.execute(
            select(MatchSetPlayStat).where(MatchSetPlayStat.match_id == mid, MatchSetPlayStat.team_id == team_id, MatchSetPlayStat.scope == "match")
        )).scalar_one_or_none()

        if ms:
            _add("xg", _f(ms.xg_a))
            _add("xg_conceded", _f(ms.xg_b))
            _add("possession_pct", _f(ms.possession_team_a, 1))
            _add("in_contest_pct", _f(ms.possession_in_contest, 1))
            _add("shots_total", _i(ms.shots_total))
            _add("shots_on_target", _i(ms.shots_on_target))
            _add("goals", _i(ms.goals_a))
            _add("goals_conceded", _i(ms.goals_b))

        lb_total = sum(r.completed or 0 for r in lb_rows)
        lb_def = next((r.completed for r in lb_rows if r.line_type == "defensive"), None)
        if lb_rows:
            _add("completed_line_breaks", lb_total)
            _add("defensive_line_breaks", _i(lb_def))

        if da:
            _add("forced_turnovers", _i(da.forced_turnovers))

        if pl:
            _add("passes_attempted", _i(pl.passes_att))
            _add("passes_completed", _i(pl.passes_comp))
            _add("crosses", _i(pl.crosses))
            _add("ball_progressions", _i(pl.ball_prog))
            _add("take_ons", _i(pl.take_ons))
            _add("tackles_made", _i(pl.tackles_made))
            _add("tackles_won", _i(pl.tackles_won))
            _add("interceptions", _i(pl.interceptions))
            _add("blocks", _i(pl.blocks))
            _add("clearances", _i(pl.clearances))
            _add("possession_regains", _i(pl.regains))
            _add("pressing_direct", _i(pl.pressing_direct))
            _add("duels_won_aerial", _i(pl.duels_aerial))
            _add("duels_won_physical", _i(pl.duels_physical))
            dist = round(float(pl.distance_m or 0) / 1000, 1)
            _add("total_distance_km", dist)

        if gk:
            _add("gk_involvements", _i(gk.total_involvements))
            _add("gk_distributions", _i(gk.total_distributions))
            _add("gk_attempts_faced", _i(gk.total_attempts_faced))
            _add("gk_save_pct", _f(gk.save_pct, 1))
            _add("gk_crosses_faced", _i(gk.crosses_faced))

        if sp:
            _add("set_plays", _i(sp.set_plays))
            _add("corners", _i(sp.corners))
            _add("free_kicks", _i(sp.free_kicks))

    averages = {
        k: round(totals[k] / counts[k], 2) if counts.get(k, 0) > 0 else None
        for k in totals
    }

    return {"match_count": len(match_ids), "totals": totals, "averages": averages}


@router.get("/{team_id}/matches")
async def get_team_matches(team_id: int, db: AsyncSession = Depends(get_db)):
    team_result = await db.execute(select(Team).where(Team.id == team_id))
    team = team_result.scalar_one_or_none()
    if team is None:
        raise HTTPException(status_code=404, detail=f"Team {team_id} not found")

    result = await db.execute(
        select(Match)
        .where(or_(Match.team_a_id == team_id, Match.team_b_id == team_id))
        .order_by(Match.match_no)
    )
    matches = result.scalars().all()
    out = []
    for match in matches:
        team_a = (await db.execute(select(Team).where(Team.id == match.team_a_id))).scalar_one()
        team_b = (await db.execute(select(Team).where(Team.id == match.team_b_id))).scalar_one()
        stats_result = await db.execute(
            select(MatchStats).where(
                MatchStats.match_id == match.id,
                MatchStats.team_id == team_id,
                MatchStats.scope == "match",
            )
        )
        stats = stats_result.scalar_one_or_none()
        out.append({
            "match": MatchMeta(
                id=match.id, match_no=match.match_no,
                score_a=match.score_a, score_b=match.score_b,
                venue=match.venue or "", match_date=match.match_date.isoformat() if match.match_date else "",
                group_letter=match.group_letter or "",
                team_a=TeamSchema.model_validate(team_a),
                team_b=TeamSchema.model_validate(team_b),
                went_to_extra_time=match.went_to_extra_time,
                penalty_score_a=match.penalty_score_a,
                penalty_score_b=match.penalty_score_b,
            ).model_dump(),
            "stats": MatchStatsSchema.model_validate(stats).model_dump() if stats else None,
        })
    return out
