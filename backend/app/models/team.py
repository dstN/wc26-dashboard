from sqlalchemy import Column, Integer, String

from app.models.base import Base


class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    short_code = Column(String(3), nullable=False, unique=True)
    slug = Column(String(100), nullable=False, unique=True)
    color = Column(String(50), nullable=False)
    group_letter = Column(String(1))
