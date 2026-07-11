from sqlalchemy import Column, Computed, Enum, ForeignKey, Integer

from app.models.base import Base


class MatchMovementStat(Base):
    __tablename__ = "match_movement_stats"

    id = Column(Integer, primary_key=True, autoincrement=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=True)
    scope = Column(Enum("match", "team_aggregate"), nullable=False, default="match")
    match_key = Column(Integer, Computed("IFNULL(match_id,0)"), nullable=False)
    total_movements = Column(Integer, nullable=True)
    phase_final_third = Column(Integer, nullable=True)
    phase_progression = Column(Integer, nullable=True)
    phase_build_up = Column(Integer, nullable=True)
    type_in_front = Column(Integer, nullable=True)
    type_in_between = Column(Integer, nullable=True)
    type_out_to_in = Column(Integer, nullable=True)
    type_in_to_out = Column(Integer, nullable=True)
    type_in_behind = Column(Integer, nullable=True)
    ft_in_front = Column(Integer, nullable=True)
    ft_in_between = Column(Integer, nullable=True)
    ft_out_to_in = Column(Integer, nullable=True)
    ft_in_to_out = Column(Integer, nullable=True)
    ft_in_behind = Column(Integer, nullable=True)
    mid_in_front = Column(Integer, nullable=True)
    mid_in_between = Column(Integer, nullable=True)
    mid_out_to_in = Column(Integer, nullable=True)
    mid_in_to_out = Column(Integer, nullable=True)
    mid_in_behind = Column(Integer, nullable=True)
    def_in_front = Column(Integer, nullable=True)
    def_in_between = Column(Integer, nullable=True)
    def_out_to_in = Column(Integer, nullable=True)
    def_in_to_out = Column(Integer, nullable=True)
    def_in_behind = Column(Integer, nullable=True)
