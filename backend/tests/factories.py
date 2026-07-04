import factory
from factory.alchemy import SQLAlchemyModelFactory

from app.models import Team, Match, MatchStats


class TeamFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Team
        sqlalchemy_session_persistence = "commit"

    name = factory.Sequence(lambda n: f"Team {n}")
    short_code = factory.Sequence(lambda n: f"T{n:02d}")
    slug = factory.Sequence(lambda n: f"team-{n}")
    color = "--c-blue"
    group_letter = "A"


class MatchFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Match
        sqlalchemy_session_persistence = "commit"

    match_no = factory.Sequence(lambda n: n + 100)
    team_a_id = factory.SelfAttribute("team_a.id")
    team_b_id = factory.SelfAttribute("team_b.id")
    score_a = 1
    score_b = 0
    venue = "Test Stadium"
    group_letter = "A"
    is_featured = 0


class MatchStatsFactory(SQLAlchemyModelFactory):
    class Meta:
        model = MatchStats
        sqlalchemy_session_persistence = "commit"

    scope = "match"
    possession_team_a = 55.0
    possession_team_b = 38.0
    possession_in_contest = 7.0
    ball_recovery_time_avg = 3.5
    xg_a = 2.0
    xg_b = 0.8
    goals_a = 1
    goals_b = 0
