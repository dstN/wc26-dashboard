from pydantic import BaseModel
from typing import Optional


class PassingConnectionSchema(BaseModel):
    rank_no: int
    from_name: Optional[str] = None
    to_name: Optional[str] = None
    pct_of_team_passes: Optional[float] = None

    model_config = {"from_attributes": True}


class PassingNetworkSchema(BaseModel):
    team_a: list[PassingConnectionSchema]
    team_b: list[PassingConnectionSchema]
