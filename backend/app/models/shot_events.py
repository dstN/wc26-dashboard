from sqlalchemy import Column, Integer, Numeric, String, ForeignKey
from app.models.base import Base


class ShotEvent(Base):
    __tablename__ = "shot_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=False)
    minute = Column(Numeric(5, 1), nullable=False)
    player_jersey = Column(Integer, nullable=True)
    player_name = Column(String(100), nullable=True)
    outcome = Column(String(100), nullable=True)
    body_part = Column(String(50), nullable=True)
    delivery_type = Column(String(50), nullable=True)
