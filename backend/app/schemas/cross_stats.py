from typing import Optional

from pydantic import BaseModel


class CrossStatSchema(BaseModel):
    attempted: Optional[int] = None
    completed: Optional[int] = None
    zone_left: Optional[int] = None
    zone_center_left: Optional[int] = None
    zone_center_right: Optional[int] = None
    zone_right: Optional[int] = None
    type_inswing: Optional[int] = None
    type_outswing: Optional[int] = None
    type_driven: Optional[int] = None
    type_lofted: Optional[int] = None
    type_cutback: Optional[int] = None
    type_push_cross: Optional[int] = None
    most_player: Optional[str] = None
    most_count: Optional[int] = None

    model_config = {"from_attributes": True}


class CrossStatsMatchSchema(BaseModel):
    team_a: Optional[CrossStatSchema] = None
    team_b: Optional[CrossStatSchema] = None
