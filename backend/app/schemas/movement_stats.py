from pydantic import BaseModel
from typing import Optional


class MovementStatSchema(BaseModel):
    total_movements: Optional[int] = None
    phase_final_third: Optional[int] = None
    phase_progression: Optional[int] = None
    phase_build_up: Optional[int] = None
    type_in_front: Optional[int] = None
    type_in_between: Optional[int] = None
    type_out_to_in: Optional[int] = None
    type_in_to_out: Optional[int] = None
    type_in_behind: Optional[int] = None
    ft_in_front: Optional[int] = None
    ft_in_between: Optional[int] = None
    ft_out_to_in: Optional[int] = None
    ft_in_to_out: Optional[int] = None
    ft_in_behind: Optional[int] = None
    mid_in_front: Optional[int] = None
    mid_in_between: Optional[int] = None
    mid_out_to_in: Optional[int] = None
    mid_in_to_out: Optional[int] = None
    mid_in_behind: Optional[int] = None
    def_in_front: Optional[int] = None
    def_in_between: Optional[int] = None
    def_out_to_in: Optional[int] = None
    def_in_to_out: Optional[int] = None
    def_in_behind: Optional[int] = None

    model_config = {"from_attributes": True}


class MovementStatsMatchSchema(BaseModel):
    team_a: Optional[MovementStatSchema] = None
    team_b: Optional[MovementStatSchema] = None
