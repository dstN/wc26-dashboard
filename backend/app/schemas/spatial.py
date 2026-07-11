from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

DEFENSIVE_BLOCKS = {"high", "mid", "low"}
POSSESSION_BLOCKS = {"build_up_low", "build_up_mid", "final_third_phase"}


class TeamSpatialSchema(BaseModel):
    defensive_line_height: float
    team_length: float
    width_m: Optional[float] = None
    block: str = Field(alias="block_type")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
