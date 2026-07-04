from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, case

from app.deps import get_db
from app.models import Team, Match, MatchStats, Player, PlayerStat, MatchGkStat, MatchSetPlayStat

router = APIRouter(prefix="/api/v1/stats", tags=["stats"])


def _int(v):
    return int(v) if v is not None else None


def _float(v, decimals=2):
    return round(float(v), decimals) if v is not None else None


@router.get("/player-stats-summary")
async def get_player_stats_summary(
    db: AsyncSession = Depends(get_db),
    team_id: Optional[int] = Query(None),
):
    """Return aggregated stats for all players with at least 1 match appearance. Optionally filter by team_id."""
    query = (
        select(
            PlayerStat.player_id,
            func.count(PlayerStat.id).label("appearances"),
            func.sum(PlayerStat.goals).label("goals"),
            func.sum(PlayerStat.yellow_cards).label("yellow_cards"),
            func.sum(PlayerStat.red_cards).label("red_cards"),
            func.sum(PlayerStat.minutes_played).label("minutes_played"),
            func.sum(PlayerStat.passes_attempted).label("passes_attempted"),
            func.sum(PlayerStat.passes_completed).label("passes_completed"),
            func.sum(PlayerStat.crosses_attempted).label("crosses_attempted"),
            func.sum(PlayerStat.crosses_completed).label("crosses_completed"),
            func.sum(PlayerStat.take_ons).label("take_ons"),
            func.sum(PlayerStat.ball_progressions).label("ball_progressions"),
            func.sum(PlayerStat.attempts_at_goal).label("attempts_at_goal"),
            func.sum(PlayerStat.total_offers).label("total_offers"),
            func.sum(PlayerStat.offers_received).label("offers_received"),
            func.sum(PlayerStat.tackles_made).label("tackles_made"),
            func.sum(PlayerStat.tackles_won).label("tackles_won"),
            func.sum(PlayerStat.blocks).label("blocks"),
            func.sum(PlayerStat.interceptions).label("interceptions"),
            func.sum(PlayerStat.pressing_direct).label("pressing_direct"),
            func.sum(PlayerStat.duels_won_aerial).label("duels_won_aerial"),
            func.sum(PlayerStat.duels_won_physical).label("duels_won_physical"),
            func.sum(PlayerStat.clearances).label("clearances"),
            func.sum(PlayerStat.possession_regains).label("possession_regains"),
            func.sum(PlayerStat.total_distance_m).label("total_distance_m"),
            func.sum(PlayerStat.high_speed_runs).label("high_speed_runs"),
            func.sum(PlayerStat.sprints).label("sprints"),
            func.max(PlayerStat.top_speed_kmh).label("top_speed_kmh"),
        )
        .join(Player, Player.id == PlayerStat.player_id)
        .where(PlayerStat.scope == "match")
        .group_by(PlayerStat.player_id)
    )
    if team_id is not None:
        query = query.where(Player.team_id == team_id)
    result = await db.execute(query)
    rows = result.all()
    return {
        str(r.player_id): {
            "appearances": _int(r.appearances) or 0,
            "goals": _int(r.goals) or 0,
            "yellow_cards": _int(r.yellow_cards) or 0,
            "red_cards": _int(r.red_cards) or 0,
            "minutes_played": _int(r.minutes_played) or 0,
            "passes_attempted": _int(r.passes_attempted),
            "passes_completed": _int(r.passes_completed),
            "crosses_attempted": _int(r.crosses_attempted),
            "crosses_completed": _int(r.crosses_completed),
            "take_ons": _int(r.take_ons),
            "ball_progressions": _int(r.ball_progressions),
            "attempts_at_goal": _int(r.attempts_at_goal),
            "total_offers": _int(r.total_offers),
            "offers_received": _int(r.offers_received),
            "tackles_made": _int(r.tackles_made),
            "tackles_won": _int(r.tackles_won),
            "blocks": _int(r.blocks),
            "interceptions": _int(r.interceptions),
            "pressing_direct": _int(r.pressing_direct),
            "duels_won_aerial": _int(r.duels_won_aerial),
            "duels_won_physical": _int(r.duels_won_physical),
            "clearances": _int(r.clearances),
            "possession_regains": _int(r.possession_regains),
            "total_distance_m": _float(r.total_distance_m, 1),
            "high_speed_runs": _int(r.high_speed_runs),
            "sprints": _int(r.sprints),
            "top_speed_kmh": _float(r.top_speed_kmh, 1),
        }
        for r in rows
    }


@router.get("/leaderboards")
async def get_leaderboards(db: AsyncSession = Depends(get_db)):
    """Return top scorers, most carded players, and team rankings."""

    # ── Top scorers ───────────────────────────────────────────────────────────
    scorers_result = await db.execute(
        select(
            Player.id, Player.name, Player.position, Player.jersey_number,
            Player.team_id,
            func.sum(PlayerStat.goals).label("total_goals"),
            func.sum(PlayerStat.yellow_cards).label("total_yellows"),
            func.sum(PlayerStat.red_cards).label("total_reds"),
            func.sum(PlayerStat.minutes_played).label("total_minutes"),
            func.count(PlayerStat.id).label("appearances"),
        )
        .join(PlayerStat, PlayerStat.player_id == Player.id)
        .where(PlayerStat.scope == "match")
        .group_by(Player.id, Player.name, Player.position, Player.jersey_number, Player.team_id)
        .having(func.sum(PlayerStat.goals) > 0)
        .order_by(func.sum(PlayerStat.goals).desc(), Player.name)
        .limit(50)
    )
    scorers = scorers_result.all()

    # Fetch team info for scorers
    scorer_team_ids = list({r.team_id for r in scorers})
    teams_map = {}
    if scorer_team_ids:
        t_result = await db.execute(select(Team).where(Team.id.in_(scorer_team_ids)))
        for t in t_result.scalars().all():
            teams_map[t.id] = {"id": t.id, "name": t.name, "short_code": t.short_code, "color": t.color}

    top_scorers = [
        {
            "player_id": r.id, "name": r.name, "position": r.position,
            "jersey_number": r.jersey_number, "team": teams_map.get(r.team_id),
            "goals": int(r.total_goals or 0),
            "yellow_cards": int(r.total_yellows or 0),
            "red_cards": int(r.total_reds or 0),
            "appearances": int(r.appearances or 0),
            "minutes": int(r.total_minutes or 0),
        }
        for r in scorers
    ]

    # ── Most carded players ───────────────────────────────────────────────────
    cards_result = await db.execute(
        select(
            Player.id, Player.name, Player.position, Player.jersey_number,
            Player.team_id,
            func.sum(PlayerStat.yellow_cards).label("total_yellows"),
            func.sum(PlayerStat.red_cards).label("total_reds"),
            func.count(PlayerStat.id).label("appearances"),
        )
        .join(PlayerStat, PlayerStat.player_id == Player.id)
        .where(PlayerStat.scope == "match")
        .group_by(Player.id, Player.name, Player.position, Player.jersey_number, Player.team_id)
        .having(func.sum(PlayerStat.yellow_cards) + func.sum(PlayerStat.red_cards) > 0)
        .order_by((func.sum(PlayerStat.yellow_cards) + func.sum(PlayerStat.red_cards) * 2).desc())
        .limit(30)
    )
    cards_rows = cards_result.all()

    card_team_ids = list({r.team_id for r in cards_rows})
    if card_team_ids:
        t_result2 = await db.execute(select(Team).where(Team.id.in_(card_team_ids)))
        for t in t_result2.scalars().all():
            teams_map[t.id] = {"id": t.id, "name": t.name, "short_code": t.short_code, "color": t.color}

    most_carded = [
        {
            "player_id": r.id, "name": r.name, "position": r.position,
            "jersey_number": r.jersey_number, "team": teams_map.get(r.team_id),
            "yellow_cards": int(r.total_yellows or 0),
            "red_cards": int(r.total_reds or 0),
            "appearances": int(r.appearances or 0),
        }
        for r in cards_rows
    ]

    # ── Team rankings ─────────────────────────────────────────────────────────
    teams_result = await db.execute(select(Team).order_by(Team.name))
    all_teams = teams_result.scalars().all()

    team_rankings = []
    for team in all_teams:
        goals_result = await db.execute(
            select(func.sum(
                case(
                    (Match.team_a_id == team.id, Match.score_a),
                    (Match.team_b_id == team.id, Match.score_b),
                    else_=0,
                )
            )).where(or_(Match.team_a_id == team.id, Match.team_b_id == team.id))
        )
        goals = int(goals_result.scalar_one_or_none() or 0)

        conceded_result = await db.execute(
            select(func.sum(
                case(
                    (Match.team_a_id == team.id, Match.score_b),
                    (Match.team_b_id == team.id, Match.score_a),
                    else_=0,
                )
            )).where(or_(Match.team_a_id == team.id, Match.team_b_id == team.id))
        )
        conceded = int(conceded_result.scalar_one_or_none() or 0)

        matches_result = await db.execute(
            select(func.count(Match.id)).where(
                or_(Match.team_a_id == team.id, Match.team_b_id == team.id)
            )
        )
        played = int(matches_result.scalar_one_or_none() or 0)

        # Avg possession, xG and in-contest from per-match rows (team_aggregate has no xG)
        match_avgs = await db.execute(
            select(
                func.avg(MatchStats.possession_team_a).label("avg_poss"),
                func.avg(MatchStats.xg_a).label("avg_xg"),
                func.avg(MatchStats.possession_in_contest).label("avg_ic"),
            ).where(
                MatchStats.team_id == team.id,
                MatchStats.scope == "match",
            )
        )
        avgs = match_avgs.one()

        team_rankings.append({
            "team": {"id": team.id, "name": team.name, "short_code": team.short_code, "color": team.color, "slug": team.slug},
            "played": played,
            "goals_scored": goals,
            "goals_conceded": conceded,
            "goal_diff": goals - conceded,
            "avg_possession": round(float(avgs.avg_poss), 1) if avgs.avg_poss is not None else None,
            "avg_xg": round(float(avgs.avg_xg), 2) if avgs.avg_xg is not None else None,
            "avg_in_contest": round(float(avgs.avg_ic), 1) if avgs.avg_ic is not None else None,
        })

    return {
        "top_scorers": top_scorers,
        "most_carded": most_carded,
        "team_rankings": team_rankings,
    }


@router.get("/goalkeeper-rankings")
async def get_goalkeeper_rankings(db: AsyncSession = Depends(get_db)):
    """Return aggregated stats per goalkeeper across all matches."""
    result = await db.execute(
        select(
            MatchGkStat.gk_name,
            MatchGkStat.team_id,
            func.count(MatchGkStat.match_id).label("matches"),
            func.sum(MatchGkStat.total_attempts_faced).label("total_attempts"),
            func.avg(MatchGkStat.save_pct).label("avg_save_pct"),
            func.sum(MatchGkStat.total_goal_interventions).label("total_goal_interventions"),
            func.sum(MatchGkStat.total_aerial_interventions).label("total_aerial_interventions"),
            func.sum(MatchGkStat.crosses_faced).label("total_crosses_faced"),
            func.sum(MatchGkStat.total_involvements).label("total_involvements"),
            func.sum(MatchGkStat.total_distributions).label("total_distributions"),
        )
        .where(MatchGkStat.scope == "match", MatchGkStat.gk_name.isnot(None))
        .group_by(MatchGkStat.gk_name, MatchGkStat.team_id)
        .order_by(func.count(MatchGkStat.match_id).desc(), MatchGkStat.gk_name)
    )
    rows = result.all()

    team_ids = list({r.team_id for r in rows})
    teams_map = {}
    if team_ids:
        t_result = await db.execute(select(Team).where(Team.id.in_(team_ids)))
        for t in t_result.scalars().all():
            teams_map[t.id] = {"id": t.id, "name": t.name, "short_code": t.short_code, "color": t.color, "slug": t.slug}

    return [
        {
            "gk_name": r.gk_name,
            "team": teams_map.get(r.team_id),
            "matches": int(r.matches or 0),
            "total_attempts_faced": _int(r.total_attempts),
            "avg_save_pct": _float(r.avg_save_pct, 1),
            "total_goal_interventions": _int(r.total_goal_interventions),
            "total_aerial_interventions": _int(r.total_aerial_interventions),
            "total_crosses_faced": _int(r.total_crosses_faced),
            "total_involvements": _int(r.total_involvements),
            "total_distributions": _int(r.total_distributions),
        }
        for r in rows
    ]
