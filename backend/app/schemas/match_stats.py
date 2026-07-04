from typing import Optional
from pydantic import BaseModel, ConfigDict


class MatchStatsSchema(BaseModel):
    possession_team_a: Optional[float] = None
    possession_team_b: Optional[float] = None
    possession_in_contest: Optional[float] = None
    ball_recovery_time_avg: Optional[float] = None
    xg_a: Optional[float] = None
    xg_b: Optional[float] = None
    goals_a: Optional[int] = None
    goals_b: Optional[int] = None
    shots_total: Optional[int] = None
    shots_on_target: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)
