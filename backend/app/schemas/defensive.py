from typing import Optional

from pydantic import BaseModel, ConfigDict


class DefensiveActionSchema(BaseModel):
    forced_turnovers: int
    pressure_on_ball: str
    possession_regained: Optional[int] = None
    interceptions: Optional[int] = None
    tackles: Optional[int] = None
    possession_actions_per_da: Optional[float] = None
    blocks_total: Optional[int] = None
    blocks_passes: Optional[int] = None
    blocks_shots: Optional[int] = None
    blocks_crosses: Optional[int] = None
    blocks_clearances: Optional[int] = None
    contests_total: Optional[int] = None
    contests_physical: Optional[int] = None
    contests_aerial: Optional[int] = None
    contests_duels: Optional[int] = None
    most_regains_player: Optional[str] = None
    most_regains_count: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)
