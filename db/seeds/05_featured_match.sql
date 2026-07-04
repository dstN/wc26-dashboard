SET NAMES utf8mb4;
USE wc26;

-- Mark match 10 (Germany 7-1 Curaçao) as the featured/showcase match.
-- Runs after 04_all_matches.sql which inserts all matches with is_featured=0.
UPDATE matches SET is_featured = 1 WHERE match_no = 10;

-- Compute tournament overview from real match data.
UPDATE tournament_overview SET
  goals_total       = (SELECT SUM(score_a + score_b) FROM matches),
  avg_in_contest_pct = (SELECT ROUND(AVG(possession_in_contest), 2) FROM match_stats WHERE scope = 'match')
WHERE id = 1;
