from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.deps import get_db
from sqlalchemy import func
from app.models import Match, Team, MatchStats, MatchPhase, TeamSpatialStat, LineBreak
from app.models import FinalThirdEntry, DefensiveAction, Player, PlayerStat, MatchGkStat, MatchSetPlayStat
from app.models import ShotEvent, PassingConnection, CrossStat, MatchOfferingStat, MatchMovementStat, MatchPressureStat
from app.schemas.match_stats import MatchStatsSchema
from app.schemas.phase import PhaseSchema
from app.schemas.spatial import TeamSpatialSchema
from app.schemas.line_break import LineBreakSchema
from app.schemas.final_third import FinalThirdEntrySchema
from app.schemas.defensive import DefensiveActionSchema
from app.schemas.dashboard import MatchMeta
from app.schemas.team import TeamSchema
from app.schemas.shot_events import ShotEventSchema, ShotLogSchema
from app.schemas.passing_connections import PassingConnectionSchema, PassingNetworkSchema
from app.schemas.cross_stats import CrossStatSchema, CrossStatsMatchSchema
from app.schemas.offering_stats import OfferingStatSchema, OfferingStatsMatchSchema
from app.schemas.movement_stats import MovementStatSchema, MovementStatsMatchSchema
from app.schemas.pressure_stats import PressureStatSchema, PressureStatsMatchSchema

router = APIRouter(prefix="/api/v1/matches", tags=["matches"])


async def _get_match_or_404(db: AsyncSession, match_id: int) -> Match:
    result = await db.execute(select(Match).where(Match.id == match_id))
    match = result.scalar_one_or_none()
    if match is None:
        raise HTTPException(status_code=404, detail=f"Match {match_id} not found")
    return match


@router.get("/", response_model=list[MatchMeta])
async def list_matches(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Match).order_by(Match.match_no)
    )
    matches = result.scalars().all()
    out = []
    for match in matches:
        team_a = (await db.execute(select(Team).where(Team.id == match.team_a_id))).scalar_one()
        team_b = (await db.execute(select(Team).where(Team.id == match.team_b_id))).scalar_one()
        match_date_str = match.match_date.isoformat() if match.match_date else ""
        out.append(MatchMeta(
            id=match.id, match_no=match.match_no,
            score_a=match.score_a, score_b=match.score_b,
            venue=match.venue or "", match_date=match_date_str,
            group_letter=match.group_letter or "",
            team_a=TeamSchema.model_validate(team_a),
            team_b=TeamSchema.model_validate(team_b),
            formation_a=match.formation_a,
            formation_b=match.formation_b,
        ))
    return out


@router.get("/{match_id}", response_model=MatchMeta)
async def get_match(match_id: int, db: AsyncSession = Depends(get_db)):
    match = await _get_match_or_404(db, match_id)
    team_a = (await db.execute(select(Team).where(Team.id == match.team_a_id))).scalar_one()
    team_b = (await db.execute(select(Team).where(Team.id == match.team_b_id))).scalar_one()
    match_date_str = match.match_date.isoformat() if match.match_date else ""
    return MatchMeta(
        id=match.id, match_no=match.match_no,
        score_a=match.score_a, score_b=match.score_b,
        venue=match.venue or "", match_date=match_date_str,
        group_letter=match.group_letter or "",
        team_a=TeamSchema.model_validate(team_a),
        team_b=TeamSchema.model_validate(team_b),
        formation_a=match.formation_a,
        formation_b=match.formation_b,
    )


@router.get("/{match_id}/possession", response_model=MatchStatsSchema)
async def get_possession(match_id: int, db: AsyncSession = Depends(get_db)):
    match = await _get_match_or_404(db, match_id)
    result = await db.execute(
        select(MatchStats).where(
            MatchStats.match_id == match_id,
            MatchStats.team_id == match.team_a_id,
            MatchStats.scope == "match",
        )
    )
    stats = result.scalar_one_or_none()
    if stats is None:
        raise HTTPException(status_code=404, detail="Possession data not found")
    return MatchStatsSchema.model_validate(stats)


@router.get("/{match_id}/phases", response_model=dict)
async def get_phases(match_id: int, db: AsyncSession = Depends(get_db)):
    match = await _get_match_or_404(db, match_id)
    phases_a = (await db.execute(
        select(MatchPhase).where(MatchPhase.match_id == match_id, MatchPhase.team_id == match.team_a_id, MatchPhase.scope == "match")
    )).scalars().all()
    phases_b = (await db.execute(
        select(MatchPhase).where(MatchPhase.match_id == match_id, MatchPhase.team_id == match.team_b_id, MatchPhase.scope == "match")
    )).scalars().all()
    return {
        "team_a": [PhaseSchema.model_validate(p) for p in phases_a],
        "team_b": [PhaseSchema.model_validate(p) for p in phases_b],
    }


@router.get("/{match_id}/spatial", response_model=dict)
async def get_spatial(match_id: int, db: AsyncSession = Depends(get_db)):
    from app.schemas.spatial import DEFENSIVE_BLOCKS, POSSESSION_BLOCKS
    match = await _get_match_or_404(db, match_id)
    spatial_a = (await db.execute(
        select(TeamSpatialStat).where(TeamSpatialStat.match_id == match_id, TeamSpatialStat.team_id == match.team_a_id, TeamSpatialStat.scope == "match")
    )).scalars().all()
    spatial_b = (await db.execute(
        select(TeamSpatialStat).where(TeamSpatialStat.match_id == match_id, TeamSpatialStat.team_id == match.team_b_id, TeamSpatialStat.scope == "match")
    )).scalars().all()

    def split(rows):
        validated = [TeamSpatialSchema.model_validate(s) for s in rows]
        return {
            "defensive": [r for r in validated if r.block in DEFENSIVE_BLOCKS],
            "possession": [r for r in validated if r.block in POSSESSION_BLOCKS],
        }

    return {
        "team_a": split(spatial_a),
        "team_b": split(spatial_b),
    }


@router.get("/{match_id}/line-breaks", response_model=dict)
async def get_line_breaks(match_id: int, db: AsyncSession = Depends(get_db)):
    match = await _get_match_or_404(db, match_id)
    lb_a = (await db.execute(
        select(LineBreak).where(LineBreak.match_id == match_id, LineBreak.team_id == match.team_a_id, LineBreak.scope == "match")
    )).scalars().all()
    lb_b = (await db.execute(
        select(LineBreak).where(LineBreak.match_id == match_id, LineBreak.team_id == match.team_b_id, LineBreak.scope == "match")
    )).scalars().all()
    return {
        "team_a": [LineBreakSchema.model_validate(lb) for lb in lb_a],
        "team_b": [LineBreakSchema.model_validate(lb) for lb in lb_b],
    }


@router.get("/{match_id}/final-third", response_model=dict)
async def get_final_third(match_id: int, db: AsyncSession = Depends(get_db)):
    match = await _get_match_or_404(db, match_id)
    ft_a = (await db.execute(
        select(FinalThirdEntry).where(FinalThirdEntry.match_id == match_id, FinalThirdEntry.team_id == match.team_a_id, FinalThirdEntry.scope == "match")
    )).scalars().all()
    ft_b = (await db.execute(
        select(FinalThirdEntry).where(FinalThirdEntry.match_id == match_id, FinalThirdEntry.team_id == match.team_b_id, FinalThirdEntry.scope == "match")
    )).scalars().all()
    return {
        "team_a": [FinalThirdEntrySchema.model_validate(ft) for ft in ft_a],
        "team_b": [FinalThirdEntrySchema.model_validate(ft) for ft in ft_b],
    }


@router.get("/{match_id}/key-stats", response_model=dict)
async def get_key_stats(match_id: int, db: AsyncSession = Depends(get_db)):
    """Return all aggregated key stats for a match (both teams), computed from multiple tables."""
    match = await _get_match_or_404(db, match_id)

    def _i(v):
        return int(v) if v is not None else None

    def _f(v, d=2):
        return round(float(v), d) if v is not None else None

    result = {}
    for prefix, team_id in [("a", match.team_a_id), ("b", match.team_b_id)]:
        # match_stats row
        ms = (await db.execute(
            select(MatchStats).where(MatchStats.match_id == match_id, MatchStats.team_id == team_id, MatchStats.scope == "match")
        )).scalar_one_or_none()

        # line_breaks aggregated
        lb_rows = (await db.execute(
            select(LineBreak).where(LineBreak.match_id == match_id, LineBreak.team_id == team_id, LineBreak.scope == "match")
        )).scalars().all()
        lb_total = sum(r.completed or 0 for r in lb_rows)
        lb_def = next((r.completed for r in lb_rows if r.line_type == "defensive"), 0)

        # defensive_actions
        da = (await db.execute(
            select(DefensiveAction).where(DefensiveAction.match_id == match_id, DefensiveAction.team_id == team_id, DefensiveAction.scope == "match")
        )).scalar_one_or_none()

        # Player-stat aggregates for this match+team
        pl_agg = (await db.execute(
            select(
                func.sum(PlayerStat.crosses_completed).label("crosses"),
                func.sum(PlayerStat.ball_progressions).label("ball_prog"),
                func.sum(PlayerStat.total_distance_m).label("distance_m"),
                func.sum(PlayerStat.passes_attempted).label("passes_att"),
                func.sum(PlayerStat.passes_completed).label("passes_comp"),
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
            )
            .join(Player, Player.id == PlayerStat.player_id)
            .where(
                PlayerStat.match_id == match_id,
                Player.team_id == team_id,
                PlayerStat.scope == "match",
            )
        )).first()

        # GK stats
        gk = (await db.execute(
            select(MatchGkStat).where(MatchGkStat.match_id == match_id, MatchGkStat.team_id == team_id, MatchGkStat.scope == "match")
        )).scalar_one_or_none()

        # Set play stats
        sp = (await db.execute(
            select(MatchSetPlayStat).where(MatchSetPlayStat.match_id == match_id, MatchSetPlayStat.team_id == team_id, MatchSetPlayStat.scope == "match")
        )).scalar_one_or_none()

        pass_pct = None
        if pl_agg and pl_agg.passes_att and pl_agg.passes_comp:
            pass_pct = round(pl_agg.passes_comp / pl_agg.passes_att * 100)

        result[prefix] = {
            "goals": ms.goals_a if ms else None,
            "xg": _f(ms.xg_a) if ms else None,
            "possession_pct": _f(ms.possession_team_a, 1) if ms else None,
            "in_contest_pct": _f(ms.possession_in_contest, 1) if ms else None,
            "ball_recovery_time_avg": _f(ms.ball_recovery_time_avg, 2) if ms else None,
            "shots_total": _i(ms.shots_total) if ms else None,
            "shots_on_target": _i(ms.shots_on_target) if ms else None,
            "passes_attempted": _i(pl_agg.passes_att) if pl_agg else None,
            "passes_completed": _i(pl_agg.passes_comp) if pl_agg else None,
            "pass_completion_pct": pass_pct,
            "completed_line_breaks": lb_total,
            "defensive_line_breaks": _i(lb_def),
            "crosses": _i(pl_agg.crosses) if pl_agg else None,
            "ball_progressions": _i(pl_agg.ball_prog) if pl_agg else None,
            "take_ons": _i(pl_agg.take_ons) if pl_agg else None,
            "forced_turnovers": _i(da.forced_turnovers) if da else None,
            "tackles_made": _i(pl_agg.tackles_made) if pl_agg else None,
            "tackles_won": _i(pl_agg.tackles_won) if pl_agg else None,
            "interceptions": _i(pl_agg.interceptions) if pl_agg else None,
            "blocks": _i(pl_agg.blocks) if pl_agg else None,
            "clearances": _i(pl_agg.clearances) if pl_agg else None,
            "possession_regains": _i(pl_agg.regains) if pl_agg else None,
            "pressing_direct": _i(pl_agg.pressing_direct) if pl_agg else None,
            "duels_won_aerial": _i(pl_agg.duels_aerial) if pl_agg else None,
            "duels_won_physical": _i(pl_agg.duels_physical) if pl_agg else None,
            "total_distance_km": round(float(pl_agg.distance_m or 0) / 1000, 1) if pl_agg else None,
            # GK
            "gk_name": gk.gk_name if gk else None,
            "gk_involvements": _i(gk.total_involvements) if gk else None,
            "gk_distributions": _i(gk.total_distributions) if gk else None,
            "gk_line_breaks": _i(gk.gk_line_breaks) if gk else None,
            "gk_attempts_faced": _i(gk.total_attempts_faced) if gk else None,
            "gk_save_pct": _f(gk.save_pct, 1) if gk else None,
            "gk_goal_interventions": _i(gk.total_goal_interventions) if gk else None,
            "gk_save_retain": _i(gk.save_and_retain) if gk else None,
            "gk_deflect_retain": _i(gk.deflect_and_retain) if gk else None,
            "gk_save_deflect": _i(gk.save_and_deflect) if gk else None,
            "gk_save_attempt": _i(gk.save_attempt) if gk else None,
            "gk_no_save_attempt": _i(gk.no_save_attempt) if gk else None,
            "gk_crosses_faced": _i(gk.crosses_faced) if gk else None,
            "gk_crosses_inswing": _i(gk.crosses_faced_inswing) if gk else None,
            "gk_crosses_outswing": _i(gk.crosses_faced_outswing) if gk else None,
            "gk_crosses_driven": _i(gk.crosses_faced_driven) if gk else None,
            "gk_crosses_lofted": _i(gk.crosses_faced_lofted) if gk else None,
            "gk_crosses_cutback": _i(gk.crosses_faced_cutback) if gk else None,
            "gk_crosses_push": _i(gk.crosses_faced_push) if gk else None,
            "gk_kick_from_feet": _i(gk.kick_from_feet) if gk else None,
            "gk_kick_from_hands": _i(gk.kick_from_hands) if gk else None,
            "gk_throw_distribution": _i(gk.throw_distribution) if gk else None,
            "gk_aerial_interventions": _i(gk.total_aerial_interventions) if gk else None,
            "gk_punches_complete": _i(gk.punches_complete) if gk else None,
            "gk_punches_incomplete": _i(gk.punches_incomplete) if gk else None,
            "gk_claims_complete": _i(gk.claims_complete) if gk else None,
            "gk_claims_incomplete": _i(gk.claims_incomplete) if gk else None,
            "gk_tipped_complete": _i(gk.tipped_palmed_complete) if gk else None,
            "gk_tipped_incomplete": _i(gk.tipped_palmed_incomplete) if gk else None,
            # Set plays
            "set_plays": _i(sp.set_plays) if sp else None,
            "free_kicks": _i(sp.free_kicks) if sp else None,
            "free_kicks_direct": _i(sp.free_kicks_direct) if sp else None,
            "free_kicks_indirect": _i(sp.free_kicks_indirect) if sp else None,
            "corners": _i(sp.corners) if sp else None,
            "throw_ins": _i(sp.throw_ins) if sp else None,
            "penalties": _i(sp.penalties) if sp else None,
            "corner_direct_area_left": _i(sp.corner_direct_area_left) if sp else None,
            "corner_direct_area_right": _i(sp.corner_direct_area_right) if sp else None,
            "corner_direct_area_total": _i(sp.corner_direct_area_total) if sp else None,
            "corner_short_left": _i(sp.corner_short_left) if sp else None,
            "corner_short_right": _i(sp.corner_short_right) if sp else None,
            "corner_short_total": _i(sp.corner_short_total) if sp else None,
            "corner_edge_left": _i(sp.corner_edge_left) if sp else None,
            "corner_edge_right": _i(sp.corner_edge_right) if sp else None,
            "corner_edge_total": _i(sp.corner_edge_total) if sp else None,
            "corner_inswing": _i(sp.corner_inswing) if sp else None,
            "corner_outswing": _i(sp.corner_outswing) if sp else None,
            "corner_driven": _i(sp.corner_driven) if sp else None,
            "corner_lofted": _i(sp.corner_lofted) if sp else None,
        }

    return result


@router.get("/{match_id}/gk-stats", response_model=dict)
async def get_gk_stats(match_id: int, db: AsyncSession = Depends(get_db)):
    """Return full GK stats for both teams in a match."""
    match = await _get_match_or_404(db, match_id)

    def _i(v):
        return int(v) if v is not None else None

    def _f(v, d=2):
        return round(float(v), d) if v is not None else None

    def gk_dict(gk):
        if gk is None:
            return None
        return {
            "gk_name": gk.gk_name,
            "total_involvements": _i(gk.total_involvements),
            "total_distributions": _i(gk.total_distributions),
            "kick_from_feet": _i(gk.kick_from_feet),
            "kick_from_hands": _i(gk.kick_from_hands),
            "throw_distribution": _i(gk.throw_distribution),
            "gk_line_breaks": _i(gk.gk_line_breaks),
            "total_attempts_faced": _i(gk.total_attempts_faced),
            "save_pct": _f(gk.save_pct, 1),
            "total_goal_interventions": _i(gk.total_goal_interventions),
            "save_and_retain": _i(gk.save_and_retain),
            "deflect_and_retain": _i(gk.deflect_and_retain),
            "save_and_deflect": _i(gk.save_and_deflect),
            "save_attempt": _i(gk.save_attempt),
            "no_save_attempt": _i(gk.no_save_attempt),
            "total_aerial_interventions": _i(gk.total_aerial_interventions),
            "punches_complete": _i(gk.punches_complete),
            "punches_incomplete": _i(gk.punches_incomplete),
            "claims_complete": _i(gk.claims_complete),
            "claims_incomplete": _i(gk.claims_incomplete),
            "tipped_palmed_complete": _i(gk.tipped_palmed_complete),
            "tipped_palmed_incomplete": _i(gk.tipped_palmed_incomplete),
            "crosses_faced": _i(gk.crosses_faced),
            "crosses_faced_inswing": _i(gk.crosses_faced_inswing),
            "crosses_faced_outswing": _i(gk.crosses_faced_outswing),
            "crosses_faced_driven": _i(gk.crosses_faced_driven),
            "crosses_faced_lofted": _i(gk.crosses_faced_lofted),
            "crosses_faced_cutback": _i(gk.crosses_faced_cutback),
            "crosses_faced_push": _i(gk.crosses_faced_push),
        }

    gk_a = (await db.execute(
        select(MatchGkStat).where(MatchGkStat.match_id == match_id, MatchGkStat.team_id == match.team_a_id, MatchGkStat.scope == "match")
    )).scalar_one_or_none()
    gk_b = (await db.execute(
        select(MatchGkStat).where(MatchGkStat.match_id == match_id, MatchGkStat.team_id == match.team_b_id, MatchGkStat.scope == "match")
    )).scalar_one_or_none()

    return {"team_a": gk_dict(gk_a), "team_b": gk_dict(gk_b)}


@router.get("/{match_id}/defensive", response_model=dict)
async def get_defensive(match_id: int, db: AsyncSession = Depends(get_db)):
    match = await _get_match_or_404(db, match_id)
    da_a = (await db.execute(
        select(DefensiveAction).where(DefensiveAction.match_id == match_id, DefensiveAction.team_id == match.team_a_id, DefensiveAction.scope == "match")
    )).scalar_one_or_none()
    da_b = (await db.execute(
        select(DefensiveAction).where(DefensiveAction.match_id == match_id, DefensiveAction.team_id == match.team_b_id, DefensiveAction.scope == "match")
    )).scalar_one_or_none()
    return {
        "team_a": DefensiveActionSchema.model_validate(da_a) if da_a else None,
        "team_b": DefensiveActionSchema.model_validate(da_b) if da_b else None,
    }


@router.get("/{match_id}/shots", response_model=ShotLogSchema)
async def get_shots(match_id: int, db: AsyncSession = Depends(get_db)):
    match = await _get_match_or_404(db, match_id)
    shots_a = (await db.execute(
        select(ShotEvent)
        .where(ShotEvent.match_id == match_id, ShotEvent.team_id == match.team_a_id)
        .order_by(ShotEvent.minute)
    )).scalars().all()
    shots_b = (await db.execute(
        select(ShotEvent)
        .where(ShotEvent.match_id == match_id, ShotEvent.team_id == match.team_b_id)
        .order_by(ShotEvent.minute)
    )).scalars().all()
    return ShotLogSchema(
        team_a=[ShotEventSchema.model_validate(s) for s in shots_a],
        team_b=[ShotEventSchema.model_validate(s) for s in shots_b],
    )


@router.get("/{match_id}/passing-network", response_model=PassingNetworkSchema)
async def get_passing_network(match_id: int, db: AsyncSession = Depends(get_db)):
    match = await _get_match_or_404(db, match_id)
    conns_a = (await db.execute(
        select(PassingConnection)
        .where(PassingConnection.match_id == match_id, PassingConnection.team_id == match.team_a_id)
        .order_by(PassingConnection.rank_no)
    )).scalars().all()
    conns_b = (await db.execute(
        select(PassingConnection)
        .where(PassingConnection.match_id == match_id, PassingConnection.team_id == match.team_b_id)
        .order_by(PassingConnection.rank_no)
    )).scalars().all()
    return PassingNetworkSchema(
        team_a=[PassingConnectionSchema.model_validate(c) for c in conns_a],
        team_b=[PassingConnectionSchema.model_validate(c) for c in conns_b],
    )


@router.get("/{match_id}/crosses", response_model=CrossStatsMatchSchema)
async def get_crosses(match_id: int, db: AsyncSession = Depends(get_db)):
    match = await _get_match_or_404(db, match_id)
    cr_a = (await db.execute(
        select(CrossStat).where(CrossStat.match_id == match_id, CrossStat.team_id == match.team_a_id, CrossStat.scope == "match")
    )).scalar_one_or_none()
    cr_b = (await db.execute(
        select(CrossStat).where(CrossStat.match_id == match_id, CrossStat.team_id == match.team_b_id, CrossStat.scope == "match")
    )).scalar_one_or_none()
    return CrossStatsMatchSchema(
        team_a=CrossStatSchema.model_validate(cr_a) if cr_a else None,
        team_b=CrossStatSchema.model_validate(cr_b) if cr_b else None,
    )


@router.get("/{match_id}/offerings", response_model=OfferingStatsMatchSchema)
async def get_offerings(match_id: int, db: AsyncSession = Depends(get_db)):
    match = await _get_match_or_404(db, match_id)
    of_a = (await db.execute(
        select(MatchOfferingStat).where(MatchOfferingStat.match_id == match_id, MatchOfferingStat.team_id == match.team_a_id, MatchOfferingStat.scope == "match")
    )).scalar_one_or_none()
    of_b = (await db.execute(
        select(MatchOfferingStat).where(MatchOfferingStat.match_id == match_id, MatchOfferingStat.team_id == match.team_b_id, MatchOfferingStat.scope == "match")
    )).scalar_one_or_none()
    return OfferingStatsMatchSchema(
        team_a=OfferingStatSchema.model_validate(of_a) if of_a else None,
        team_b=OfferingStatSchema.model_validate(of_b) if of_b else None,
    )


@router.get("/{match_id}/movement", response_model=MovementStatsMatchSchema)
async def get_movement(match_id: int, db: AsyncSession = Depends(get_db)):
    match = await _get_match_or_404(db, match_id)
    mv_a = (await db.execute(
        select(MatchMovementStat).where(MatchMovementStat.match_id == match_id, MatchMovementStat.team_id == match.team_a_id, MatchMovementStat.scope == "match")
    )).scalar_one_or_none()
    mv_b = (await db.execute(
        select(MatchMovementStat).where(MatchMovementStat.match_id == match_id, MatchMovementStat.team_id == match.team_b_id, MatchMovementStat.scope == "match")
    )).scalar_one_or_none()
    return MovementStatsMatchSchema(
        team_a=MovementStatSchema.model_validate(mv_a) if mv_a else None,
        team_b=MovementStatSchema.model_validate(mv_b) if mv_b else None,
    )


@router.get("/{match_id}/pressure", response_model=PressureStatsMatchSchema)
async def get_pressure(match_id: int, db: AsyncSession = Depends(get_db)):
    match = await _get_match_or_404(db, match_id)
    pr_a = (await db.execute(
        select(MatchPressureStat).where(MatchPressureStat.match_id == match_id, MatchPressureStat.team_id == match.team_a_id, MatchPressureStat.scope == "match")
    )).scalar_one_or_none()
    pr_b = (await db.execute(
        select(MatchPressureStat).where(MatchPressureStat.match_id == match_id, MatchPressureStat.team_id == match.team_b_id, MatchPressureStat.scope == "match")
    )).scalar_one_or_none()
    return PressureStatsMatchSchema(
        team_a=PressureStatSchema.model_validate(pr_a) if pr_a else None,
        team_b=PressureStatSchema.model_validate(pr_b) if pr_b else None,
    )


@router.get("/{match_id}/player-name-map", response_model=dict[str, int])
async def get_player_name_map(match_id: int, db: AsyncSession = Depends(get_db)):
    """Return {player_name: player_id} for all players with stats in this match."""
    await _get_match_or_404(db, match_id)
    rows = (await db.execute(
        select(Player.name, Player.id)
        .join(PlayerStat, PlayerStat.player_id == Player.id)
        .where(PlayerStat.match_id == match_id)
    )).all()
    return {name: pid for name, pid in rows}
