from pydantic import BaseModel
from typing import Optional

from app.schemas.team import TeamSchema
from app.schemas.match_stats import MatchStatsSchema
from app.schemas.phase import PhaseSchema
from app.schemas.spatial import TeamSpatialSchema
from app.schemas.line_break import LineBreakSchema
from app.schemas.final_third import FinalThirdEntrySchema
from app.schemas.defensive import DefensiveActionSchema


class KpiCard(BaseModel):
    label: str
    value: str
    unit: str = ""


class TournamentOverviewSchema(BaseModel):
    matches_played: int
    goals_total: int
    avg_in_contest_pct: float


class MatchMeta(BaseModel):
    id: int
    match_no: int
    # nullable in the DB — an unplayed/fixture match must not 500 the list endpoints
    score_a: Optional[int] = None
    score_b: Optional[int] = None
    venue: str
    match_date: str
    group_letter: str
    team_a: TeamSchema
    team_b: TeamSchema
    formation_a: Optional[str] = None
    formation_b: Optional[str] = None
    went_to_extra_time: bool = False
    penalty_score_a: Optional[int] = None
    penalty_score_b: Optional[int] = None


class DashboardResponse(BaseModel):
    overview: TournamentOverviewSchema
    featured: MatchMeta
    possession: MatchStatsSchema
    head_to_head: MatchStatsSchema
    phases: dict[str, list[PhaseSchema]]
    spatial: dict[str, dict[str, list[TeamSpatialSchema]]]
    line_breaks: dict[str, list[LineBreakSchema]]
    final_third: dict[str, list[FinalThirdEntrySchema]]
    defensive: dict[str, DefensiveActionSchema]
    kpi_cards: list[KpiCard]
