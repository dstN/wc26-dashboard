from pydantic import BaseModel
from typing import Optional


class PressureStatSchema(BaseModel):
    total_pressures: Optional[int] = None
    direct_pressures: Optional[int] = None
    avg_duration_s: Optional[float] = None
    forced_turnovers: Optional[int] = None
    ball_recovery_time_s: Optional[float] = None
    pushing_on_into_pressing: Optional[int] = None
    pushing_on: Optional[int] = None
    direction_inside: Optional[int] = None
    direction_outside: Optional[int] = None
    most_direct_player: Optional[str] = None
    most_direct_count: Optional[int] = None

    model_config = {"from_attributes": True}


class PressureStatsMatchSchema(BaseModel):
    team_a: Optional[PressureStatSchema] = None
    team_b: Optional[PressureStatSchema] = None
