from sqlalchemy import Column, Integer, String, Date, ForeignKey, SmallInteger
from app.models.base import Base


class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, autoincrement=True)
    match_no = Column(Integer, nullable=False, unique=True)
    team_a_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    team_b_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    score_a = Column(Integer, default=0)
    score_b = Column(Integer, default=0)
    venue = Column(String(200))
    match_date = Column(Date)
    group_letter = Column(String(1))
    is_featured = Column(SmallInteger, default=0)
    formation_a = Column(String(20), nullable=True)
    formation_b = Column(String(20), nullable=True)
