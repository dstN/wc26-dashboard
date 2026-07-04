from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.deps import get_db
from app.models import Player, PlayerStat, Team, Match, PlayerLineBreak

router = APIRouter(prefix="/api/v1/players", tags=["players"])


def _i(v):
    return int(v) if v is not None else None


def _f(v, d=1):
    return round(float(v), d) if v is not None else None


@router.get("/", response_model=list[dict])
async def list_players(
    db: AsyncSession = Depends(get_db),
    team_id: Optional[int] = Query(None),
):
    query = select(Player, Team).join(Team, Player.team_id == Team.id)
    if team_id is not None:
        query = query.where(Player.team_id == team_id)
    query = query.order_by(Player.jersey_number)
    result = await db.execute(query)
    rows = result.all()
    return [
        {
            "id": player.id,
            "name": player.name,
            "position": player.position,
            "jersey_number": player.jersey_number,
            "team": {
                "id": team.id,
                "name": team.name,
                "short_code": team.short_code,
                "color": team.color,
                "slug": team.slug,
            },
        }
        for player, team in rows
    ]


@router.get("/{player_id}")
async def get_player(player_id: int, db: AsyncSession = Depends(get_db)):
    """Return full player profile: info, team, career totals, per-match breakdown."""
    player_result = await db.execute(
        select(Player, Team).join(Team, Player.team_id == Team.id).where(Player.id == player_id)
    )
    row = player_result.first()
    if row is None:
        raise HTTPException(status_code=404, detail=f"Player {player_id} not found")
    player, team = row

    # Per-match stats (joined with match for context)
    match_stats_result = await db.execute(
        select(PlayerStat, Match)
        .outerjoin(Match, PlayerStat.match_id == Match.id)
        .where(PlayerStat.player_id == player_id, PlayerStat.scope == "match")
        .order_by(Match.match_no)
    )
    match_rows = match_stats_result.all()

    # Opponent team info per match
    opp_ids = []
    for _, match in match_rows:
        if match:
            opp_id = match.team_b_id if match.team_a_id == team.id else match.team_a_id
            opp_ids.append(opp_id)
    opp_ids = list(set(opp_ids))
    opp_map = {}
    if opp_ids:
        opp_result = await db.execute(select(Team).where(Team.id.in_(opp_ids)))
        for t in opp_result.scalars().all():
            opp_map[t.id] = {"id": t.id, "name": t.name, "short_code": t.short_code, "color": t.color}

    per_match = []
    for stat, match in match_rows:
        opp_id = None
        if match:
            opp_id = match.team_b_id if match.team_a_id == team.id else match.team_a_id
        per_match.append({
            "match_no": match.match_no if match else None,
            "match_date": match.match_date.isoformat() if match and match.match_date else None,
            "opponent": opp_map.get(opp_id),
            "started": stat.started,
            "minutes_played": stat.minutes_played,
            # Match summary
            "goals": _i(stat.goals),
            "yellow_cards": _i(stat.yellow_cards),
            "red_cards": _i(stat.red_cards),
            # Possession
            "passes_attempted": _i(stat.passes_attempted),
            "passes_completed": _i(stat.passes_completed),
            "pass_completion_pct": _i(stat.pass_completion_pct),
            "crosses_attempted": _i(stat.crosses_attempted),
            "crosses_completed": _i(stat.crosses_completed),
            "take_ons": _i(stat.take_ons),
            "ball_progressions": _i(stat.ball_progressions),
            "attempts_at_goal": _i(stat.attempts_at_goal),
            "total_offers": _i(stat.total_offers),
            "offers_received": _i(stat.offers_received),
            # Defensive
            "tackles_made": _i(stat.tackles_made),
            "tackles_won": _i(stat.tackles_won),
            "blocks": _i(stat.blocks),
            "interceptions": _i(stat.interceptions),
            "pressing_direct": _i(stat.pressing_direct),
            "pressing_indirect": _i(stat.pressing_indirect),
            "duels_won_aerial": _i(stat.duels_won_aerial),
            "duels_won_physical": _i(stat.duels_won_physical),
            "possession_contests_won": _i(stat.possession_contests_won),
            "clearances": _i(stat.clearances),
            "possession_regains": _i(stat.possession_regains),
            # Passing detail
            "switches_of_play": _i(stat.switches_of_play),
            "step_ins": _i(stat.step_ins),
            "lb_attempted": _i(stat.lb_attempted),
            "lb_completed": _i(stat.lb_completed),
            # Offer breakdown
            "offers_in_front": _i(stat.offers_in_front),
            "offers_in_between": _i(stat.offers_in_between),
            "offers_out_to_in": _i(stat.offers_out_to_in),
            "offers_in_to_out": _i(stat.offers_in_to_out),
            "offers_in_behind": _i(stat.offers_in_behind),
            "offers_no_movement": _i(stat.offers_no_movement),
            # OOP detail
            "loose_ball_receptions": _i(stat.loose_ball_receptions),
            "pushing_on": _i(stat.pushing_on),
            "pushing_on_into_pressing": _i(stat.pushing_on_into_pressing),
            "possession_interrupted": _i(stat.possession_interrupted),
            # Physical
            "total_distance_m": _f(stat.total_distance_m, 1),
            "high_speed_runs": _i(stat.high_speed_runs),
            "sprints": _i(stat.sprints),
            "top_speed_kmh": _f(stat.top_speed_kmh, 1),
            "dist_zone1_m": _f(stat.dist_zone1_m, 1),
            "dist_zone2_m": _f(stat.dist_zone2_m, 1),
            "dist_zone3_m": _f(stat.dist_zone3_m, 1),
            "dist_zone4_m": _f(stat.dist_zone4_m, 1),
            "dist_zone5_m": _f(stat.dist_zone5_m, 1),
            # Cross breakdown
            "crosses_inswing": _i(stat.crosses_inswing),
            "crosses_outswing": _i(stat.crosses_outswing),
            "crosses_driven": _i(stat.crosses_driven),
            "crosses_lofted": _i(stat.crosses_lofted),
            "crosses_cutback": _i(stat.crosses_cutback),
            "crosses_push_cross": _i(stat.crosses_push_cross),
        })

    # Career totals
    totals_result = await db.execute(
        select(
            func.count(PlayerStat.id).label("apps"),
            func.sum(PlayerStat.goals).label("goals"),
            func.sum(PlayerStat.minutes_played).label("minutes"),
            func.sum(PlayerStat.yellow_cards).label("yellows"),
            func.sum(PlayerStat.red_cards).label("reds"),
            func.sum(PlayerStat.passes_attempted).label("passes_att"),
            func.sum(PlayerStat.passes_completed).label("passes_comp"),
            func.sum(PlayerStat.take_ons).label("take_ons"),
            func.sum(PlayerStat.attempts_at_goal).label("shots"),
            func.sum(PlayerStat.tackles_made).label("tackles_made"),
            func.sum(PlayerStat.tackles_won).label("tackles_won"),
            func.sum(PlayerStat.interceptions).label("interceptions"),
            func.sum(PlayerStat.blocks).label("blocks"),
            func.sum(PlayerStat.clearances).label("clearances"),
            func.sum(PlayerStat.possession_regains).label("regains"),
            func.sum(PlayerStat.duels_won_aerial).label("duels_aerial"),
            func.sum(PlayerStat.duels_won_physical).label("duels_physical"),
            func.sum(PlayerStat.pressing_direct).label("pressing_direct"),
            func.sum(PlayerStat.total_distance_m).label("distance_m"),
            func.sum(PlayerStat.high_speed_runs).label("hsr"),
            func.sum(PlayerStat.sprints).label("sprints"),
            func.max(PlayerStat.top_speed_kmh).label("top_speed"),
            func.sum(PlayerStat.total_offers).label("offers"),
            func.sum(PlayerStat.offers_received).label("offers_recv"),
            func.sum(PlayerStat.pressing_indirect).label("pressing_indirect"),
            func.sum(PlayerStat.possession_contests_won).label("possession_contests_won"),
            func.sum(PlayerStat.crosses_attempted).label("crosses_att"),
            func.sum(PlayerStat.crosses_completed).label("crosses_comp"),
            func.sum(PlayerStat.ball_progressions).label("ball_progressions"),
            func.sum(PlayerStat.switches_of_play).label("switches_of_play"),
            func.sum(PlayerStat.step_ins).label("step_ins"),
            func.sum(PlayerStat.lb_attempted).label("lb_attempted"),
            func.sum(PlayerStat.lb_completed).label("lb_completed"),
            func.sum(PlayerStat.offers_in_front).label("offers_in_front"),
            func.sum(PlayerStat.offers_in_between).label("offers_in_between"),
            func.sum(PlayerStat.offers_out_to_in).label("offers_out_to_in"),
            func.sum(PlayerStat.offers_in_to_out).label("offers_in_to_out"),
            func.sum(PlayerStat.offers_in_behind).label("offers_in_behind"),
            func.sum(PlayerStat.offers_no_movement).label("offers_no_movement"),
            func.sum(PlayerStat.loose_ball_receptions).label("loose_ball_receptions"),
            func.sum(PlayerStat.pushing_on).label("pushing_on"),
            func.sum(PlayerStat.pushing_on_into_pressing).label("pushing_on_into_pressing"),
            func.sum(PlayerStat.possession_interrupted).label("possession_interrupted"),
            func.sum(PlayerStat.dist_zone1_m).label("dist_zone1_m"),
            func.sum(PlayerStat.dist_zone2_m).label("dist_zone2_m"),
            func.sum(PlayerStat.dist_zone3_m).label("dist_zone3_m"),
            func.sum(PlayerStat.dist_zone4_m).label("dist_zone4_m"),
            func.sum(PlayerStat.dist_zone5_m).label("dist_zone5_m"),
            func.sum(PlayerStat.crosses_inswing).label("crosses_inswing"),
            func.sum(PlayerStat.crosses_outswing).label("crosses_outswing"),
            func.sum(PlayerStat.crosses_driven).label("crosses_driven"),
            func.sum(PlayerStat.crosses_lofted).label("crosses_lofted"),
            func.sum(PlayerStat.crosses_cutback).label("crosses_cutback"),
            func.sum(PlayerStat.crosses_push_cross).label("crosses_push_cross"),
        )
        .where(PlayerStat.player_id == player_id, PlayerStat.scope == "match")
    )
    t = totals_result.first()

    pass_pct = None
    if t and t.passes_att and t.passes_comp:
        pass_pct = round(t.passes_comp / t.passes_att * 100)

    totals = {
        "appearances": _i(t.apps) if t else 0,
        "goals": _i(t.goals) if t else 0,
        "minutes_played": _i(t.minutes) if t else 0,
        "yellow_cards": _i(t.yellows) if t else 0,
        "red_cards": _i(t.reds) if t else 0,
        "passes_attempted": _i(t.passes_att) if t else None,
        "passes_completed": _i(t.passes_comp) if t else None,
        "pass_completion_pct": pass_pct,
        "take_ons": _i(t.take_ons) if t else None,
        "attempts_at_goal": _i(t.shots) if t else None,
        "tackles_made": _i(t.tackles_made) if t else None,
        "tackles_won": _i(t.tackles_won) if t else None,
        "interceptions": _i(t.interceptions) if t else None,
        "blocks": _i(t.blocks) if t else None,
        "clearances": _i(t.clearances) if t else None,
        "possession_regains": _i(t.regains) if t else None,
        "duels_won_aerial": _i(t.duels_aerial) if t else None,
        "duels_won_physical": _i(t.duels_physical) if t else None,
        "pressing_direct": _i(t.pressing_direct) if t else None,
        "total_distance_m": _f(t.distance_m, 1) if t else None,
        "high_speed_runs": _i(t.hsr) if t else None,
        "sprints": _i(t.sprints) if t else None,
        "top_speed_kmh": _f(t.top_speed, 1) if t else None,
        "total_offers": _i(t.offers) if t else None,
        "offers_received": _i(t.offers_recv) if t else None,
        "pressing_indirect": _i(t.pressing_indirect) if t else None,
        "possession_contests_won": _i(t.possession_contests_won) if t else None,
        "crosses_attempted": _i(t.crosses_att) if t else None,
        "crosses_completed": _i(t.crosses_comp) if t else None,
        "ball_progressions": _i(t.ball_progressions) if t else None,
        "switches_of_play": _i(t.switches_of_play) if t else None,
        "step_ins": _i(t.step_ins) if t else None,
        "lb_attempted": _i(t.lb_attempted) if t else None,
        "lb_completed": _i(t.lb_completed) if t else None,
        "offers_in_front": _i(t.offers_in_front) if t else None,
        "offers_in_between": _i(t.offers_in_between) if t else None,
        "offers_out_to_in": _i(t.offers_out_to_in) if t else None,
        "offers_in_to_out": _i(t.offers_in_to_out) if t else None,
        "offers_in_behind": _i(t.offers_in_behind) if t else None,
        "offers_no_movement": _i(t.offers_no_movement) if t else None,
        "loose_ball_receptions": _i(t.loose_ball_receptions) if t else None,
        "pushing_on": _i(t.pushing_on) if t else None,
        "pushing_on_into_pressing": _i(t.pushing_on_into_pressing) if t else None,
        "possession_interrupted": _i(t.possession_interrupted) if t else None,
        "dist_zone1_m": _f(t.dist_zone1_m, 1) if t else None,
        "dist_zone2_m": _f(t.dist_zone2_m, 1) if t else None,
        "dist_zone3_m": _f(t.dist_zone3_m, 1) if t else None,
        "dist_zone4_m": _f(t.dist_zone4_m, 1) if t else None,
        "dist_zone5_m": _f(t.dist_zone5_m, 1) if t else None,
        "crosses_inswing": _i(t.crosses_inswing) if t else None,
        "crosses_outswing": _i(t.crosses_outswing) if t else None,
        "crosses_driven": _i(t.crosses_driven) if t else None,
        "crosses_lofted": _i(t.crosses_lofted) if t else None,
        "crosses_cutback": _i(t.crosses_cutback) if t else None,
        "crosses_push_cross": _i(t.crosses_push_cross) if t else None,
    }

    return {
        "player": {
            "id": player.id,
            "name": player.name,
            "position": player.position,
            "jersey_number": player.jersey_number,
        },
        "team": {
            "id": team.id,
            "name": team.name,
            "short_code": team.short_code,
            "color": team.color,
            "slug": team.slug,
        },
        "totals": totals,
        "per_match": per_match,
    }


@router.get("/{player_id}/stats")
async def get_player_stats(player_id: int, db: AsyncSession = Depends(get_db)):
    player_result = await db.execute(select(Player).where(Player.id == player_id))
    player = player_result.scalar_one_or_none()
    if player is None:
        raise HTTPException(status_code=404, detail=f"Player {player_id} not found")

    stats_result = await db.execute(
        select(PlayerStat).where(PlayerStat.player_id == player_id)
    )
    stats = stats_result.scalars().all()

    return {
        "player": {"id": player.id, "name": player.name, "position": player.position},
        "stats": [
            {
                "goals": s.goals, "yellow_cards": s.yellow_cards, "red_cards": s.red_cards,
                "minutes_played": s.minutes_played, "started": s.started,
                "passes_attempted": s.passes_attempted, "passes_completed": s.passes_completed,
                "tackles_made": s.tackles_made, "interceptions": s.interceptions,
                "total_distance_m": float(s.total_distance_m or 0),
                "top_speed_kmh": float(s.top_speed_kmh or 0),
            }
            for s in stats
        ],
    }


@router.get("/{player_id}/line-breaks")
async def get_player_line_breaks(player_id: int, db: AsyncSession = Depends(get_db)):
    player_result = await db.execute(select(Player).where(Player.id == player_id))
    player = player_result.scalar_one_or_none()
    if player is None:
        raise HTTPException(status_code=404, detail=f"Player {player_id} not found")

    result = await db.execute(
        select(PlayerLineBreak, Match)
        .outerjoin(Match, PlayerLineBreak.match_id == Match.id)
        .where(PlayerLineBreak.player_id == player_id, PlayerLineBreak.scope == "match")
        .order_by(Match.match_no)
    )
    rows = result.all()

    def _row(lb, match):
        return {
            "match_no": match.match_no if match else None,
            "match_date": match.match_date.isoformat() if match and match.match_date else None,
            "attempted": lb.attempted,
            "completed": lb.completed,
            "dir_through": lb.dir_through,
            "dir_around": lb.dir_around,
            "dir_over": lb.dir_over,
            "dist_pass": lb.dist_pass,
            "dist_cross": lb.dist_cross,
            "dist_ball_prog": lb.dist_ball_prog,
            "unit_4u_attacking": lb.unit_4u_attacking,
            "unit_4u_attacking_mid": lb.unit_4u_attacking_mid,
            "unit_4u_midfield": lb.unit_4u_midfield,
            "unit_4u_defensive": lb.unit_4u_defensive,
            "unit_3u_attacking": lb.unit_3u_attacking,
            "unit_3u_midfield": lb.unit_3u_midfield,
            "unit_3u_defensive": lb.unit_3u_defensive,
            "unit_2u_midfield": lb.unit_2u_midfield,
            "unit_2u_defensive": lb.unit_2u_defensive,
        }

    return {"player_id": player_id, "line_breaks": [_row(lb, m) for lb, m in rows]}
