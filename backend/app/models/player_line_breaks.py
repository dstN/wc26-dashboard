from sqlalchemy import Column, Integer, ForeignKey, Enum, Computed
from app.models.base import Base


class PlayerLineBreak(Base):
    __tablename__ = "player_line_breaks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=True)
    scope = Column(Enum("match", "team_aggregate"), nullable=False, default="match")
    match_key = Column(Integer, Computed("IFNULL(match_id,0)"), nullable=False)
    attempted = Column(Integer, nullable=True)
    completed = Column(Integer, nullable=True)
    dir_through = Column(Integer, nullable=True)
    dir_around = Column(Integer, nullable=True)
    dir_over = Column(Integer, nullable=True)
    dist_pass = Column(Integer, nullable=True)
    dist_cross = Column(Integer, nullable=True)
    dist_ball_prog = Column(Integer, nullable=True)
    unit_4u_attacking = Column(Integer, nullable=True)
    unit_4u_attacking_mid = Column(Integer, nullable=True)
    unit_4u_midfield = Column(Integer, nullable=True)
    unit_4u_defensive = Column(Integer, nullable=True)
    unit_3u_attacking = Column(Integer, nullable=True)
    unit_3u_midfield = Column(Integer, nullable=True)
    unit_3u_defensive = Column(Integer, nullable=True)
    unit_2u_midfield = Column(Integer, nullable=True)
    unit_2u_defensive = Column(Integer, nullable=True)
