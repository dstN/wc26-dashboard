from sqlalchemy import Boolean, Column, Integer, String, Date, ForeignKey
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
    # 'A'-'L' for group stage; 'R32'/'R16'/'QF'/'SF'/'3RD'/'FIN' for knockout
    group_letter = Column(String(3))
    formation_a = Column(String(20), nullable=True)
    formation_b = Column(String(20), nullable=True)
    # score_a/score_b already reflect extra time when played; this only flags
    # that ET happened (for an "AET" badge). Penalty score is separate from
    # score_a/score_b since a shootout doesn't change the match score.
    went_to_extra_time = Column(Boolean, nullable=False, default=False)
    penalty_score_a = Column(Integer, nullable=True)
    penalty_score_b = Column(Integer, nullable=True)
