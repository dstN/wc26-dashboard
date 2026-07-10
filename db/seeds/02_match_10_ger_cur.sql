SET NAMES utf8mb4;
USE wc26;

-- Germany and Curaçao get explicit IDs so they are stable anchors across seeds.
-- All other 46 WC2026 teams are inserted by 03_team_aggregates.sql.
-- Full match data for all 36 matches is in 04_all_matches.sql (pmsr_to_sql.py).
INSERT INTO teams (id, name, short_code, slug, color, group_letter) VALUES
  (1, 'Germany', 'GER', 'germany', '--c-yellow', 'E'),
  (2, 'Curaçao', 'CUR', 'curacao', '--c-indigo', 'E')
ON DUPLICATE KEY UPDATE
  name=VALUES(name), color=VALUES(color), group_letter=VALUES(group_letter);

