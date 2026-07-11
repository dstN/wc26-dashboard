from typing import Optional

from pydantic import BaseModel


class OfferingStatSchema(BaseModel):
    total_offers_made: Optional[int] = None
    total_offers_received: Optional[int] = None
    offers_final_third: Optional[int] = None
    offers_middle_third: Optional[int] = None
    offers_defensive_third: Optional[int] = None
    inside_shape: Optional[int] = None
    outside_shape: Optional[int] = None
    most_player: Optional[str] = None
    most_count: Optional[int] = None

    model_config = {"from_attributes": True}


class OfferingStatsMatchSchema(BaseModel):
    team_a: Optional[OfferingStatSchema] = None
    team_b: Optional[OfferingStatSchema] = None
