from pydantic import BaseModel
from typing import Optional


class ShotEventSchema(BaseModel):
    minute: float
    player_jersey: Optional[int] = None
    player_name: Optional[str] = None
    outcome: Optional[str] = None
    body_part: Optional[str] = None
    delivery_type: Optional[str] = None

    model_config = {"from_attributes": True}


class ShotLogSchema(BaseModel):
    team_a: list[ShotEventSchema]
    team_b: list[ShotEventSchema]
