SET NAMES utf8mb4;
CREATE DATABASE IF NOT EXISTS wc26 CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE wc26;

CREATE TABLE IF NOT EXISTS teams (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  short_code CHAR(3) NOT NULL,
  slug VARCHAR(100) NOT NULL,
  color VARCHAR(50) NOT NULL COMMENT 'CSS var name e.g. --c-yellow',
  group_letter CHAR(1),
  UNIQUE KEY uq_slug (slug),
  UNIQUE KEY uq_short_code (short_code)
);

CREATE TABLE IF NOT EXISTS matches (
  id INT AUTO_INCREMENT PRIMARY KEY,
  match_no INT NOT NULL,
  team_a_id INT NOT NULL,
  team_b_id INT NOT NULL,
  score_a INT DEFAULT 0,
  score_b INT DEFAULT 0,
  venue VARCHAR(200),
  match_date DATE,
  group_letter CHAR(1),
  is_featured TINYINT(1) DEFAULT 0,
  formation_a VARCHAR(20) DEFAULT NULL,
  formation_b VARCHAR(20) DEFAULT NULL,
  UNIQUE KEY uq_match_no (match_no),
  FOREIGN KEY (team_a_id) REFERENCES teams(id),
  FOREIGN KEY (team_b_id) REFERENCES teams(id)
);

CREATE TABLE IF NOT EXISTS tournament_overview (
  id INT AUTO_INCREMENT PRIMARY KEY,
  matches_played INT DEFAULT 0,
  goals_total INT DEFAULT 0,
  avg_in_contest_pct DECIMAL(5,2) DEFAULT 0.00,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Stat tables share this pattern:
--   scope ENUM('match','team_aggregate')
--   match_id nullable FK → matches
--   match_key GENERATED ALWAYS AS (IFNULL(match_id,0)) STORED
--   UNIQUE KEY on (team_id, match_key, scope[, discriminator])
-- This allows safe ON DUPLICATE KEY UPDATE even when match_id IS NULL.

CREATE TABLE IF NOT EXISTS match_stats (
  id INT AUTO_INCREMENT PRIMARY KEY,
  team_id INT NOT NULL,
  match_id INT DEFAULT NULL,
  scope ENUM('match','team_aggregate') NOT NULL DEFAULT 'match',
  match_key INT GENERATED ALWAYS AS (IFNULL(match_id,0)) STORED,
  possession_team_a DECIMAL(5,2),
  possession_team_b DECIMAL(5,2),
  possession_in_contest DECIMAL(5,2),
  ball_recovery_time_avg DECIMAL(5,2),
  xg_a DECIMAL(5,2),
  xg_b DECIMAL(5,2),
  goals_a INT,
  goals_b INT,
  shots_total INT DEFAULT NULL,
  shots_on_target INT DEFAULT NULL,
  UNIQUE KEY uq_ms (team_id, match_key, scope),
  FOREIGN KEY (team_id) REFERENCES teams(id),
  FOREIGN KEY (match_id) REFERENCES matches(id)
);

CREATE TABLE IF NOT EXISTS match_phases (
  id INT AUTO_INCREMENT PRIMARY KEY,
  team_id INT NOT NULL,
  match_id INT DEFAULT NULL,
  scope ENUM('match','team_aggregate') NOT NULL DEFAULT 'match',
  match_key INT GENERATED ALWAYS AS (IFNULL(match_id,0)) STORED,
  phase_name VARCHAR(100) NOT NULL,
  phase_group ENUM('in','out') NOT NULL,
  pct DECIMAL(5,2),
  UNIQUE KEY uq_mp (team_id, match_key, scope, phase_name),
  FOREIGN KEY (team_id) REFERENCES teams(id),
  FOREIGN KEY (match_id) REFERENCES matches(id)
);

-- Session 8: block_type extended with possession scenarios; width_m added
CREATE TABLE IF NOT EXISTS team_spatial_stats (
  id INT AUTO_INCREMENT PRIMARY KEY,
  team_id INT NOT NULL,
  match_id INT DEFAULT NULL,
  scope ENUM('match','team_aggregate') NOT NULL DEFAULT 'match',
  match_key INT GENERATED ALWAYS AS (IFNULL(match_id,0)) STORED,
  block_type ENUM('high','mid','low','build_up_low','build_up_mid','final_third_phase') NOT NULL DEFAULT 'mid',
  defensive_line_height DECIMAL(5,2),
  team_length DECIMAL(5,2),
  width_m DECIMAL(5,2),
  UNIQUE KEY uq_tss (team_id, match_key, scope, block_type),
  FOREIGN KEY (team_id) REFERENCES teams(id),
  FOREIGN KEY (match_id) REFERENCES matches(id)
);

CREATE TABLE IF NOT EXISTS line_breaks (
  id INT AUTO_INCREMENT PRIMARY KEY,
  team_id INT NOT NULL,
  match_id INT DEFAULT NULL,
  scope ENUM('match','team_aggregate') NOT NULL DEFAULT 'match',
  match_key INT GENERATED ALWAYS AS (IFNULL(match_id,0)) STORED,
  line_type ENUM('defensive','midfield','attacking') NOT NULL,
  attempted INT DEFAULT 0,
  completed INT DEFAULT 0,
  UNIQUE KEY uq_lb (team_id, match_key, scope, line_type),
  FOREIGN KEY (team_id) REFERENCES teams(id),
  FOREIGN KEY (match_id) REFERENCES matches(id)
);

CREATE TABLE IF NOT EXISTS final_third_entries (
  id INT AUTO_INCREMENT PRIMARY KEY,
  team_id INT NOT NULL,
  match_id INT DEFAULT NULL,
  scope ENUM('match','team_aggregate') NOT NULL DEFAULT 'match',
  match_key INT GENERATED ALWAYS AS (IFNULL(match_id,0)) STORED,
  zone ENUM('left','left_inside','central','right_inside','right') NOT NULL,
  entry_count INT DEFAULT 0,
  UNIQUE KEY uq_fte (team_id, match_key, scope, zone),
  FOREIGN KEY (team_id) REFERENCES teams(id),
  FOREIGN KEY (match_id) REFERENCES matches(id)
);

-- Session 10: extended with full defensive action breakdown
CREATE TABLE IF NOT EXISTS defensive_actions (
  id INT AUTO_INCREMENT PRIMARY KEY,
  team_id INT NOT NULL,
  match_id INT DEFAULT NULL,
  scope ENUM('match','team_aggregate') NOT NULL DEFAULT 'match',
  match_key INT GENERATED ALWAYS AS (IFNULL(match_id,0)) STORED,
  forced_turnovers INT DEFAULT 0,
  pressure_on_ball ENUM('moderate','heavy') DEFAULT 'moderate',
  -- Extended fields from pages 25/26
  possession_regained INT DEFAULT NULL,
  interceptions INT DEFAULT NULL,
  tackles INT DEFAULT NULL,
  possession_actions_per_da DECIMAL(5,2) DEFAULT NULL,
  blocks_total INT DEFAULT NULL,
  blocks_passes INT DEFAULT NULL,
  blocks_shots INT DEFAULT NULL,
  blocks_crosses INT DEFAULT NULL,
  blocks_clearances INT DEFAULT NULL,
  contests_total INT DEFAULT NULL,
  contests_physical INT DEFAULT NULL,
  contests_aerial INT DEFAULT NULL,
  contests_duels INT DEFAULT NULL,
  most_regains_player VARCHAR(100) DEFAULT NULL,
  most_regains_count INT DEFAULT NULL,
  UNIQUE KEY uq_da (team_id, match_key, scope),
  FOREIGN KEY (team_id) REFERENCES teams(id),
  FOREIGN KEY (match_id) REFERENCES matches(id)
);

CREATE TABLE IF NOT EXISTS players (
  id INT AUTO_INCREMENT PRIMARY KEY,
  team_id INT NOT NULL,
  name VARCHAR(100) NOT NULL,
  position VARCHAR(50),
  jersey_number INT,
  UNIQUE KEY uq_player (team_id, jersey_number),
  FOREIGN KEY (team_id) REFERENCES teams(id)
);

-- Session 10: added OOP extras, physical zones, offers breakdown
CREATE TABLE IF NOT EXISTS player_stats (
  id INT AUTO_INCREMENT PRIMARY KEY,
  player_id INT NOT NULL,
  match_id INT DEFAULT NULL,
  scope ENUM('match','team_aggregate') NOT NULL DEFAULT 'match',
  match_key INT GENERATED ALWAYS AS (IFNULL(match_id,0)) STORED,
  -- Match summary (page 2)
  saves INT DEFAULT 0,
  goals_conceded INT DEFAULT 0,
  xg_faced DECIMAL(5,2) DEFAULT 0.00,
  goals INT DEFAULT 0,
  yellow_cards INT DEFAULT 0,
  red_cards INT DEFAULT 0,
  started TINYINT(1) DEFAULT 1,
  minutes_played INT DEFAULT 90,
  -- In Possession — Distributions (page 42/44)
  passes_attempted INT DEFAULT NULL,
  passes_completed INT DEFAULT NULL,
  pass_completion_pct INT DEFAULT NULL,
  switches_of_play INT DEFAULT NULL,
  crosses_attempted INT DEFAULT NULL,
  crosses_completed INT DEFAULT NULL,
  lb_attempted INT DEFAULT NULL,
  lb_completed INT DEFAULT NULL,
  ball_progressions INT DEFAULT NULL,
  take_ons INT DEFAULT NULL,
  step_ins INT DEFAULT NULL,
  attempts_at_goal INT DEFAULT NULL,
  -- In Possession — Offers & Receptions (page 43/45)
  total_offers INT DEFAULT NULL,
  offers_received INT DEFAULT NULL,
  offers_in_front INT DEFAULT NULL,
  offers_in_between INT DEFAULT NULL,
  offers_out_to_in INT DEFAULT NULL,
  offers_in_to_out INT DEFAULT NULL,
  offers_in_behind INT DEFAULT NULL,
  offers_no_movement INT DEFAULT NULL,
  -- Out of Possession (page 47/48)
  tackles_made INT DEFAULT NULL,
  tackles_won INT DEFAULT NULL,
  blocks INT DEFAULT NULL,
  interceptions INT DEFAULT NULL,
  pressing_direct INT DEFAULT NULL,
  pressing_indirect INT DEFAULT NULL,
  duels_won_aerial INT DEFAULT NULL,
  duels_won_physical INT DEFAULT NULL,
  possession_contests_won INT DEFAULT NULL,
  clearances INT DEFAULT NULL,
  possession_regains INT DEFAULT NULL,
  loose_ball_receptions INT DEFAULT NULL,
  pushing_on INT DEFAULT NULL,
  pushing_on_into_pressing INT DEFAULT NULL,
  possession_interrupted INT DEFAULT NULL,
  -- Physical Data (page 50/51)
  total_distance_m DECIMAL(8,1) DEFAULT NULL,
  dist_zone1_m DECIMAL(8,1) DEFAULT NULL,
  dist_zone2_m DECIMAL(8,1) DEFAULT NULL,
  dist_zone3_m DECIMAL(8,1) DEFAULT NULL,
  dist_zone4_m DECIMAL(8,1) DEFAULT NULL,
  dist_zone5_m DECIMAL(8,1) DEFAULT NULL,
  high_speed_runs INT DEFAULT NULL,
  sprints INT DEFAULT NULL,
  top_speed_kmh DECIMAL(4,1) DEFAULT NULL,
  -- Cross delivery type (pages 18/19)
  crosses_inswing INT DEFAULT NULL,
  crosses_outswing INT DEFAULT NULL,
  crosses_driven INT DEFAULT NULL,
  crosses_lofted INT DEFAULT NULL,
  crosses_cutback INT DEFAULT NULL,
  crosses_push_cross INT DEFAULT NULL,
  UNIQUE KEY uq_ps (player_id, match_key, scope),
  FOREIGN KEY (player_id) REFERENCES players(id),
  FOREIGN KEY (match_id) REFERENCES matches(id)
);

CREATE TABLE IF NOT EXISTS match_gk_stats (
  id INT AUTO_INCREMENT PRIMARY KEY,
  team_id INT NOT NULL,
  match_id INT DEFAULT NULL,
  scope ENUM('match','team_aggregate') NOT NULL DEFAULT 'match',
  match_key INT GENERATED ALWAYS AS (IFNULL(match_id,0)) STORED,
  total_involvements INT DEFAULT NULL,
  total_distributions INT DEFAULT NULL,
  kick_from_feet INT DEFAULT NULL,
  kick_from_hands INT DEFAULT NULL,
  throw_distribution INT DEFAULT NULL,
  gk_line_breaks INT DEFAULT NULL,
  total_attempts_faced INT DEFAULT NULL,
  save_pct DECIMAL(5,2) DEFAULT NULL,
  total_goal_interventions INT DEFAULT NULL,
  total_aerial_interventions INT DEFAULT NULL,
  crosses_faced INT DEFAULT NULL,
  -- GK goalkeeper name
  gk_name VARCHAR(100) DEFAULT NULL,
  -- Goal intervention breakdown (pages 34/35)
  save_and_retain INT DEFAULT NULL,
  deflect_and_retain INT DEFAULT NULL,
  save_and_deflect INT DEFAULT NULL,
  save_attempt INT DEFAULT NULL,
  no_save_attempt INT DEFAULT NULL,
  -- Crosses faced delivery type breakdown (pages 36/37)
  crosses_faced_inswing INT DEFAULT NULL,
  crosses_faced_outswing INT DEFAULT NULL,
  crosses_faced_driven INT DEFAULT NULL,
  crosses_faced_lofted INT DEFAULT NULL,
  crosses_faced_cutback INT DEFAULT NULL,
  crosses_faced_push INT DEFAULT NULL,
  -- Aerial intervention breakdown (pages 36/37)
  punches_complete INT DEFAULT NULL,
  punches_incomplete INT DEFAULT NULL,
  claims_complete INT DEFAULT NULL,
  claims_incomplete INT DEFAULT NULL,
  tipped_palmed_complete INT DEFAULT NULL,
  tipped_palmed_incomplete INT DEFAULT NULL,
  UNIQUE KEY uq_gks (team_id, match_key, scope),
  FOREIGN KEY (team_id) REFERENCES teams(id),
  FOREIGN KEY (match_id) REFERENCES matches(id)
);

-- Session 10: extended with corner delivery type/style breakdown
CREATE TABLE IF NOT EXISTS match_set_play_stats (
  id INT AUTO_INCREMENT PRIMARY KEY,
  team_id INT NOT NULL,
  match_id INT DEFAULT NULL,
  scope ENUM('match','team_aggregate') NOT NULL DEFAULT 'match',
  match_key INT GENERATED ALWAYS AS (IFNULL(match_id,0)) STORED,
  set_plays INT DEFAULT NULL,
  free_kicks INT DEFAULT NULL,
  free_kicks_direct INT DEFAULT NULL,
  free_kicks_indirect INT DEFAULT NULL,
  penalties INT DEFAULT NULL,
  corners INT DEFAULT NULL,
  throw_ins INT DEFAULT NULL,
  -- Corner delivery type breakdown (pages 39/40)
  corner_direct_area_left INT DEFAULT NULL,
  corner_direct_area_right INT DEFAULT NULL,
  corner_direct_area_total INT DEFAULT NULL,
  corner_short_left INT DEFAULT NULL,
  corner_short_right INT DEFAULT NULL,
  corner_short_total INT DEFAULT NULL,
  corner_edge_left INT DEFAULT NULL,
  corner_edge_right INT DEFAULT NULL,
  corner_edge_total INT DEFAULT NULL,
  -- Corner delivery style
  corner_inswing INT DEFAULT NULL,
  corner_outswing INT DEFAULT NULL,
  corner_driven INT DEFAULT NULL,
  corner_lofted INT DEFAULT NULL,
  UNIQUE KEY uq_sps (team_id, match_key, scope),
  FOREIGN KEY (team_id) REFERENCES teams(id),
  FOREIGN KEY (match_id) REFERENCES matches(id)
);

-- Session 10: shot log per match per team (pages 15/17)
-- DELETE before re-insert (no unique key on individual shots — same player can score twice in same minute)
CREATE TABLE IF NOT EXISTS shot_events (
  id INT AUTO_INCREMENT PRIMARY KEY,
  team_id INT NOT NULL,
  match_id INT NOT NULL,
  minute DECIMAL(5,1) NOT NULL,
  player_jersey INT,
  player_name VARCHAR(100),
  outcome VARCHAR(100),
  body_part VARCHAR(50),
  delivery_type VARCHAR(50),
  KEY idx_se_match (match_id),
  KEY idx_se_team (team_id),
  FOREIGN KEY (team_id) REFERENCES teams(id),
  FOREIGN KEY (match_id) REFERENCES matches(id)
);

-- Session 10: top-5 passing connections per match per team (pages 12/13)
CREATE TABLE IF NOT EXISTS passing_connections (
  id INT AUTO_INCREMENT PRIMARY KEY,
  team_id INT NOT NULL,
  match_id INT NOT NULL,
  rank_no INT NOT NULL COMMENT '1–5',
  from_name VARCHAR(100),
  to_name VARCHAR(100),
  pct_of_team_passes DECIMAL(5,2),
  UNIQUE KEY uq_pc (team_id, match_id, rank_no),
  FOREIGN KEY (team_id) REFERENCES teams(id),
  FOREIGN KEY (match_id) REFERENCES matches(id)
);

-- Session 10: team crossing stats per match (pages 18/19)
CREATE TABLE IF NOT EXISTS cross_stats (
  id INT AUTO_INCREMENT PRIMARY KEY,
  team_id INT NOT NULL,
  match_id INT DEFAULT NULL,
  scope ENUM('match','team_aggregate') NOT NULL DEFAULT 'match',
  match_key INT GENERATED ALWAYS AS (IFNULL(match_id,0)) STORED,
  attempted INT DEFAULT NULL,
  completed INT DEFAULT NULL,
  zone_left INT DEFAULT NULL,
  zone_center_left INT DEFAULT NULL,
  zone_center_right INT DEFAULT NULL,
  zone_right INT DEFAULT NULL,
  type_inswing INT DEFAULT NULL,
  type_outswing INT DEFAULT NULL,
  type_driven INT DEFAULT NULL,
  type_lofted INT DEFAULT NULL,
  type_cutback INT DEFAULT NULL,
  type_push_cross INT DEFAULT NULL,
  most_player VARCHAR(100),
  most_count INT DEFAULT NULL,
  UNIQUE KEY uq_cs (team_id, match_key, scope),
  FOREIGN KEY (team_id) REFERENCES teams(id),
  FOREIGN KEY (match_id) REFERENCES matches(id)
);

-- Session 10: offering to receive stats per match (pages 20/21)
CREATE TABLE IF NOT EXISTS match_offering_stats (
  id INT AUTO_INCREMENT PRIMARY KEY,
  team_id INT NOT NULL,
  match_id INT DEFAULT NULL,
  scope ENUM('match','team_aggregate') NOT NULL DEFAULT 'match',
  match_key INT GENERATED ALWAYS AS (IFNULL(match_id,0)) STORED,
  total_offers_made INT DEFAULT NULL,
  total_offers_received INT DEFAULT NULL,
  offers_final_third INT DEFAULT NULL,
  offers_middle_third INT DEFAULT NULL,
  offers_defensive_third INT DEFAULT NULL,
  inside_shape INT DEFAULT NULL,
  outside_shape INT DEFAULT NULL,
  most_player VARCHAR(100),
  most_count INT DEFAULT NULL,
  UNIQUE KEY uq_mos (team_id, match_key, scope),
  FOREIGN KEY (team_id) REFERENCES teams(id),
  FOREIGN KEY (match_id) REFERENCES matches(id)
);

-- Session 10: movement to receive stats per match (pages 22/23)
CREATE TABLE IF NOT EXISTS match_movement_stats (
  id INT AUTO_INCREMENT PRIMARY KEY,
  team_id INT NOT NULL,
  match_id INT DEFAULT NULL,
  scope ENUM('match','team_aggregate') NOT NULL DEFAULT 'match',
  match_key INT GENERATED ALWAYS AS (IFNULL(match_id,0)) STORED,
  total_movements INT DEFAULT NULL,
  phase_final_third INT DEFAULT NULL,
  phase_progression INT DEFAULT NULL,
  phase_build_up INT DEFAULT NULL,
  type_in_front INT DEFAULT NULL,
  type_in_between INT DEFAULT NULL,
  type_out_to_in INT DEFAULT NULL,
  type_in_to_out INT DEFAULT NULL,
  type_in_behind INT DEFAULT NULL,
  -- Movement by pitch third (pages 22/23)
  ft_in_front INT DEFAULT NULL,
  ft_in_between INT DEFAULT NULL,
  ft_out_to_in INT DEFAULT NULL,
  ft_in_to_out INT DEFAULT NULL,
  ft_in_behind INT DEFAULT NULL,
  mid_in_front INT DEFAULT NULL,
  mid_in_between INT DEFAULT NULL,
  mid_out_to_in INT DEFAULT NULL,
  mid_in_to_out INT DEFAULT NULL,
  mid_in_behind INT DEFAULT NULL,
  def_in_front INT DEFAULT NULL,
  def_in_between INT DEFAULT NULL,
  def_out_to_in INT DEFAULT NULL,
  def_in_to_out INT DEFAULT NULL,
  def_in_behind INT DEFAULT NULL,
  UNIQUE KEY uq_mms (team_id, match_key, scope),
  FOREIGN KEY (team_id) REFERENCES teams(id),
  FOREIGN KEY (match_id) REFERENCES matches(id)
);

-- Session 10: defensive pressure stats per match (page 29)
CREATE TABLE IF NOT EXISTS match_pressure_stats (
  id INT AUTO_INCREMENT PRIMARY KEY,
  team_id INT NOT NULL,
  match_id INT DEFAULT NULL,
  scope ENUM('match','team_aggregate') NOT NULL DEFAULT 'match',
  match_key INT GENERATED ALWAYS AS (IFNULL(match_id,0)) STORED,
  total_pressures INT DEFAULT NULL,
  direct_pressures INT DEFAULT NULL,
  avg_duration_s DECIMAL(5,2) DEFAULT NULL,
  forced_turnovers INT DEFAULT NULL,
  ball_recovery_time_s DECIMAL(5,2) DEFAULT NULL,
  pushing_on_into_pressing INT DEFAULT NULL,
  pushing_on INT DEFAULT NULL,
  direction_inside INT DEFAULT NULL,
  direction_outside INT DEFAULT NULL,
  most_direct_player VARCHAR(100),
  most_direct_count INT DEFAULT NULL,
  UNIQUE KEY uq_mps (team_id, match_key, scope),
  FOREIGN KEY (team_id) REFERENCES teams(id),
  FOREIGN KEY (match_id) REFERENCES matches(id)
);

-- Session 11: per-player line break data (pages 10/11)
CREATE TABLE IF NOT EXISTS player_line_breaks (
  id INT AUTO_INCREMENT PRIMARY KEY,
  player_id INT NOT NULL,
  match_id INT DEFAULT NULL,
  scope ENUM('match','team_aggregate') NOT NULL DEFAULT 'match',
  match_key INT GENERATED ALWAYS AS (IFNULL(match_id,0)) STORED,
  attempted INT DEFAULT NULL,
  completed INT DEFAULT NULL,
  dir_through INT DEFAULT NULL,
  dir_around INT DEFAULT NULL,
  dir_over INT DEFAULT NULL,
  dist_pass INT DEFAULT NULL,
  dist_cross INT DEFAULT NULL,
  dist_ball_prog INT DEFAULT NULL,
  unit_4u_attacking INT DEFAULT NULL,
  unit_4u_attacking_mid INT DEFAULT NULL,
  unit_4u_midfield INT DEFAULT NULL,
  unit_4u_defensive INT DEFAULT NULL,
  unit_3u_attacking INT DEFAULT NULL,
  unit_3u_midfield INT DEFAULT NULL,
  unit_3u_defensive INT DEFAULT NULL,
  unit_2u_midfield INT DEFAULT NULL,
  unit_2u_defensive INT DEFAULT NULL,
  UNIQUE KEY uq_plb (player_id, match_key, scope),
  FOREIGN KEY (player_id) REFERENCES players(id),
  FOREIGN KEY (match_id) REFERENCES matches(id)
);
