-- ── Final Third Entries · all 40 matches ────────────────────────────────
SET NAMES utf8mb4;
USE wc26;

-- Match 1: MEX vs RSA
INSERT INTO final_third_entries (team_id, match_id, scope, zone, entry_count)
VALUES
  ((SELECT id FROM teams WHERE short_code = 'MEX'), (SELECT id FROM matches WHERE match_no = 1), 'match', 'left', 3),
  ((SELECT id FROM teams WHERE short_code = 'MEX'), (SELECT id FROM matches WHERE match_no = 1), 'match', 'left_inside', 6),
  ((SELECT id FROM teams WHERE short_code = 'MEX'), (SELECT id FROM matches WHERE match_no = 1), 'match', 'central', 14),
  ((SELECT id FROM teams WHERE short_code = 'MEX'), (SELECT id FROM matches WHERE match_no = 1), 'match', 'right_inside', 8),
  ((SELECT id FROM teams WHERE short_code = 'MEX'), (SELECT id FROM matches WHERE match_no = 1), 'match', 'right', 3),
  ((SELECT id FROM teams WHERE short_code = 'RSA'), (SELECT id FROM matches WHERE match_no = 1), 'match', 'left', 2),
  ((SELECT id FROM teams WHERE short_code = 'RSA'), (SELECT id FROM matches WHERE match_no = 1), 'match', 'left_inside', 8),
  ((SELECT id FROM teams WHERE short_code = 'RSA'), (SELECT id FROM matches WHERE match_no = 1), 'match', 'central', 5),
  ((SELECT id FROM teams WHERE short_code = 'RSA'), (SELECT id FROM matches WHERE match_no = 1), 'match', 'right_inside', 8),
  ((SELECT id FROM teams WHERE short_code = 'RSA'), (SELECT id FROM matches WHERE match_no = 1), 'match', 'right', 5)
ON DUPLICATE KEY UPDATE entry_count=VALUES(entry_count);

-- Match 2: KOR vs CZE
INSERT INTO final_third_entries (team_id, match_id, scope, zone, entry_count)
VALUES
  ((SELECT id FROM teams WHERE short_code = 'KOR'), (SELECT id FROM matches WHERE match_no = 2), 'match', 'left', 3),
  ((SELECT id FROM teams WHERE short_code = 'KOR'), (SELECT id FROM matches WHERE match_no = 2), 'match', 'left_inside', 9),
  ((SELECT id FROM teams WHERE short_code = 'KOR'), (SELECT id FROM matches WHERE match_no = 2), 'match', 'central', 11),
  ((SELECT id FROM teams WHERE short_code = 'KOR'), (SELECT id FROM matches WHERE match_no = 2), 'match', 'right_inside', 5),
  ((SELECT id FROM teams WHERE short_code = 'KOR'), (SELECT id FROM matches WHERE match_no = 2), 'match', 'right', 1),
  ((SELECT id FROM teams WHERE short_code = 'CZE'), (SELECT id FROM matches WHERE match_no = 2), 'match', 'left', 2),
  ((SELECT id FROM teams WHERE short_code = 'CZE'), (SELECT id FROM matches WHERE match_no = 2), 'match', 'left_inside', 3),
  ((SELECT id FROM teams WHERE short_code = 'CZE'), (SELECT id FROM matches WHERE match_no = 2), 'match', 'central', 8),
  ((SELECT id FROM teams WHERE short_code = 'CZE'), (SELECT id FROM matches WHERE match_no = 2), 'match', 'right_inside', 6),
  ((SELECT id FROM teams WHERE short_code = 'CZE'), (SELECT id FROM matches WHERE match_no = 2), 'match', 'right', 1)
ON DUPLICATE KEY UPDATE entry_count=VALUES(entry_count);

-- Match 3: CAN vs BIH
INSERT INTO final_third_entries (team_id, match_id, scope, zone, entry_count)
VALUES
  ((SELECT id FROM teams WHERE short_code = 'CAN'), (SELECT id FROM matches WHERE match_no = 3), 'match', 'left', 4),
  ((SELECT id FROM teams WHERE short_code = 'CAN'), (SELECT id FROM matches WHERE match_no = 3), 'match', 'left_inside', 10),
  ((SELECT id FROM teams WHERE short_code = 'CAN'), (SELECT id FROM matches WHERE match_no = 3), 'match', 'central', 13),
  ((SELECT id FROM teams WHERE short_code = 'CAN'), (SELECT id FROM matches WHERE match_no = 3), 'match', 'right_inside', 10),
  ((SELECT id FROM teams WHERE short_code = 'CAN'), (SELECT id FROM matches WHERE match_no = 3), 'match', 'right', 5),
  ((SELECT id FROM teams WHERE short_code = 'BIH'), (SELECT id FROM matches WHERE match_no = 3), 'match', 'left', 3),
  ((SELECT id FROM teams WHERE short_code = 'BIH'), (SELECT id FROM matches WHERE match_no = 3), 'match', 'left_inside', 7),
  ((SELECT id FROM teams WHERE short_code = 'BIH'), (SELECT id FROM matches WHERE match_no = 3), 'match', 'central', 11),
  ((SELECT id FROM teams WHERE short_code = 'BIH'), (SELECT id FROM matches WHERE match_no = 3), 'match', 'right_inside', 6),
  ((SELECT id FROM teams WHERE short_code = 'BIH'), (SELECT id FROM matches WHERE match_no = 3), 'match', 'right', 1)
ON DUPLICATE KEY UPDATE entry_count=VALUES(entry_count);

-- Match 4: USA vs PAR
INSERT INTO final_third_entries (team_id, match_id, scope, zone, entry_count)
VALUES
  ((SELECT id FROM teams WHERE short_code = 'USA'), (SELECT id FROM matches WHERE match_no = 4), 'match', 'left', 5),
  ((SELECT id FROM teams WHERE short_code = 'USA'), (SELECT id FROM matches WHERE match_no = 4), 'match', 'left_inside', 12),
  ((SELECT id FROM teams WHERE short_code = 'USA'), (SELECT id FROM matches WHERE match_no = 4), 'match', 'central', 13),
  ((SELECT id FROM teams WHERE short_code = 'USA'), (SELECT id FROM matches WHERE match_no = 4), 'match', 'right_inside', 9),
  ((SELECT id FROM teams WHERE short_code = 'USA'), (SELECT id FROM matches WHERE match_no = 4), 'match', 'right', 4),
  ((SELECT id FROM teams WHERE short_code = 'PAR'), (SELECT id FROM matches WHERE match_no = 4), 'match', 'left', 2),
  ((SELECT id FROM teams WHERE short_code = 'PAR'), (SELECT id FROM matches WHERE match_no = 4), 'match', 'left_inside', 4),
  ((SELECT id FROM teams WHERE short_code = 'PAR'), (SELECT id FROM matches WHERE match_no = 4), 'match', 'central', 4),
  ((SELECT id FROM teams WHERE short_code = 'PAR'), (SELECT id FROM matches WHERE match_no = 4), 'match', 'right_inside', 2),
  ((SELECT id FROM teams WHERE short_code = 'PAR'), (SELECT id FROM matches WHERE match_no = 4), 'match', 'right', 3)
ON DUPLICATE KEY UPDATE entry_count=VALUES(entry_count);

-- Match 5: HAI vs SCO
INSERT INTO final_third_entries (team_id, match_id, scope, zone, entry_count)
VALUES
  ((SELECT id FROM teams WHERE short_code = 'HAI'), (SELECT id FROM matches WHERE match_no = 5), 'match', 'left', 3),
  ((SELECT id FROM teams WHERE short_code = 'HAI'), (SELECT id FROM matches WHERE match_no = 5), 'match', 'left_inside', 4),
  ((SELECT id FROM teams WHERE short_code = 'HAI'), (SELECT id FROM matches WHERE match_no = 5), 'match', 'central', 8),
  ((SELECT id FROM teams WHERE short_code = 'HAI'), (SELECT id FROM matches WHERE match_no = 5), 'match', 'right_inside', 4),
  ((SELECT id FROM teams WHERE short_code = 'HAI'), (SELECT id FROM matches WHERE match_no = 5), 'match', 'right', 1),
  ((SELECT id FROM teams WHERE short_code = 'SCO'), (SELECT id FROM matches WHERE match_no = 5), 'match', 'left', 7),
  ((SELECT id FROM teams WHERE short_code = 'SCO'), (SELECT id FROM matches WHERE match_no = 5), 'match', 'left_inside', 11),
  ((SELECT id FROM teams WHERE short_code = 'SCO'), (SELECT id FROM matches WHERE match_no = 5), 'match', 'central', 10),
  ((SELECT id FROM teams WHERE short_code = 'SCO'), (SELECT id FROM matches WHERE match_no = 5), 'match', 'right_inside', 10),
  ((SELECT id FROM teams WHERE short_code = 'SCO'), (SELECT id FROM matches WHERE match_no = 5), 'match', 'right', 2)
ON DUPLICATE KEY UPDATE entry_count=VALUES(entry_count);

-- Match 6: AUS vs TUR
INSERT INTO final_third_entries (team_id, match_id, scope, zone, entry_count)
VALUES
  ((SELECT id FROM teams WHERE short_code = 'AUS'), (SELECT id FROM matches WHERE match_no = 6), 'match', 'left', 5),
  ((SELECT id FROM teams WHERE short_code = 'AUS'), (SELECT id FROM matches WHERE match_no = 6), 'match', 'left_inside', 10),
  ((SELECT id FROM teams WHERE short_code = 'AUS'), (SELECT id FROM matches WHERE match_no = 6), 'match', 'central', 12),
  ((SELECT id FROM teams WHERE short_code = 'AUS'), (SELECT id FROM matches WHERE match_no = 6), 'match', 'right_inside', 7),
  ((SELECT id FROM teams WHERE short_code = 'AUS'), (SELECT id FROM matches WHERE match_no = 6), 'match', 'right', 5),
  ((SELECT id FROM teams WHERE short_code = 'TUR'), (SELECT id FROM matches WHERE match_no = 6), 'match', 'left', 6),
  ((SELECT id FROM teams WHERE short_code = 'TUR'), (SELECT id FROM matches WHERE match_no = 6), 'match', 'left_inside', 3),
  ((SELECT id FROM teams WHERE short_code = 'TUR'), (SELECT id FROM matches WHERE match_no = 6), 'match', 'central', 5),
  ((SELECT id FROM teams WHERE short_code = 'TUR'), (SELECT id FROM matches WHERE match_no = 6), 'match', 'right_inside', 8),
  ((SELECT id FROM teams WHERE short_code = 'TUR'), (SELECT id FROM matches WHERE match_no = 6), 'match', 'right', 1)
ON DUPLICATE KEY UPDATE entry_count=VALUES(entry_count);

-- Match 7: BRA vs MAR
INSERT INTO final_third_entries (team_id, match_id, scope, zone, entry_count)
VALUES
  ((SELECT id FROM teams WHERE short_code = 'BRA'), (SELECT id FROM matches WHERE match_no = 7), 'match', 'left', 6),
  ((SELECT id FROM teams WHERE short_code = 'BRA'), (SELECT id FROM matches WHERE match_no = 7), 'match', 'left_inside', 7),
  ((SELECT id FROM teams WHERE short_code = 'BRA'), (SELECT id FROM matches WHERE match_no = 7), 'match', 'central', 11),
  ((SELECT id FROM teams WHERE short_code = 'BRA'), (SELECT id FROM matches WHERE match_no = 7), 'match', 'right_inside', 7),
  ((SELECT id FROM teams WHERE short_code = 'BRA'), (SELECT id FROM matches WHERE match_no = 7), 'match', 'right', 5),
  ((SELECT id FROM teams WHERE short_code = 'MAR'), (SELECT id FROM matches WHERE match_no = 7), 'match', 'left', 4),
  ((SELECT id FROM teams WHERE short_code = 'MAR'), (SELECT id FROM matches WHERE match_no = 7), 'match', 'left_inside', 8),
  ((SELECT id FROM teams WHERE short_code = 'MAR'), (SELECT id FROM matches WHERE match_no = 7), 'match', 'central', 7),
  ((SELECT id FROM teams WHERE short_code = 'MAR'), (SELECT id FROM matches WHERE match_no = 7), 'match', 'right_inside', 4),
  ((SELECT id FROM teams WHERE short_code = 'MAR'), (SELECT id FROM matches WHERE match_no = 7), 'match', 'right', 2)
ON DUPLICATE KEY UPDATE entry_count=VALUES(entry_count);

-- Match 8: QAT vs SUI
INSERT INTO final_third_entries (team_id, match_id, scope, zone, entry_count)
VALUES
  ((SELECT id FROM teams WHERE short_code = 'QAT'), (SELECT id FROM matches WHERE match_no = 8), 'match', 'left', 3),
  ((SELECT id FROM teams WHERE short_code = 'QAT'), (SELECT id FROM matches WHERE match_no = 8), 'match', 'left_inside', 9),
  ((SELECT id FROM teams WHERE short_code = 'QAT'), (SELECT id FROM matches WHERE match_no = 8), 'match', 'central', 8),
  ((SELECT id FROM teams WHERE short_code = 'QAT'), (SELECT id FROM matches WHERE match_no = 8), 'match', 'right_inside', 9),
  ((SELECT id FROM teams WHERE short_code = 'QAT'), (SELECT id FROM matches WHERE match_no = 8), 'match', 'right', 6),
  ((SELECT id FROM teams WHERE short_code = 'SUI'), (SELECT id FROM matches WHERE match_no = 8), 'match', 'left', 3),
  ((SELECT id FROM teams WHERE short_code = 'SUI'), (SELECT id FROM matches WHERE match_no = 8), 'match', 'left_inside', 10),
  ((SELECT id FROM teams WHERE short_code = 'SUI'), (SELECT id FROM matches WHERE match_no = 8), 'match', 'central', 14),
  ((SELECT id FROM teams WHERE short_code = 'SUI'), (SELECT id FROM matches WHERE match_no = 8), 'match', 'right_inside', 7),
  ((SELECT id FROM teams WHERE short_code = 'SUI'), (SELECT id FROM matches WHERE match_no = 8), 'match', 'right', 6)
ON DUPLICATE KEY UPDATE entry_count=VALUES(entry_count);

-- Match 9: CIV vs ECU
INSERT INTO final_third_entries (team_id, match_id, scope, zone, entry_count)
VALUES
  ((SELECT id FROM teams WHERE short_code = 'CIV'), (SELECT id FROM matches WHERE match_no = 9), 'match', 'left', 5),
  ((SELECT id FROM teams WHERE short_code = 'CIV'), (SELECT id FROM matches WHERE match_no = 9), 'match', 'left_inside', 8),
  ((SELECT id FROM teams WHERE short_code = 'CIV'), (SELECT id FROM matches WHERE match_no = 9), 'match', 'central', 13),
  ((SELECT id FROM teams WHERE short_code = 'CIV'), (SELECT id FROM matches WHERE match_no = 9), 'match', 'right_inside', 10),
  ((SELECT id FROM teams WHERE short_code = 'CIV'), (SELECT id FROM matches WHERE match_no = 9), 'match', 'right', 4),
  ((SELECT id FROM teams WHERE short_code = 'ECU'), (SELECT id FROM matches WHERE match_no = 9), 'match', 'left', 8),
  ((SELECT id FROM teams WHERE short_code = 'ECU'), (SELECT id FROM matches WHERE match_no = 9), 'match', 'left_inside', 10),
  ((SELECT id FROM teams WHERE short_code = 'ECU'), (SELECT id FROM matches WHERE match_no = 9), 'match', 'central', 10),
  ((SELECT id FROM teams WHERE short_code = 'ECU'), (SELECT id FROM matches WHERE match_no = 9), 'match', 'right_inside', 11),
  ((SELECT id FROM teams WHERE short_code = 'ECU'), (SELECT id FROM matches WHERE match_no = 9), 'match', 'right', 4)
ON DUPLICATE KEY UPDATE entry_count=VALUES(entry_count);

-- Match 10: GER vs CUR
INSERT INTO final_third_entries (team_id, match_id, scope, zone, entry_count)
VALUES
  ((SELECT id FROM teams WHERE short_code = 'GER'), (SELECT id FROM matches WHERE match_no = 10), 'match', 'left', 4),
  ((SELECT id FROM teams WHERE short_code = 'GER'), (SELECT id FROM matches WHERE match_no = 10), 'match', 'left_inside', 8),
  ((SELECT id FROM teams WHERE short_code = 'GER'), (SELECT id FROM matches WHERE match_no = 10), 'match', 'central', 10),
  ((SELECT id FROM teams WHERE short_code = 'GER'), (SELECT id FROM matches WHERE match_no = 10), 'match', 'right_inside', 9),
  ((SELECT id FROM teams WHERE short_code = 'GER'), (SELECT id FROM matches WHERE match_no = 10), 'match', 'right', 5),
  ((SELECT id FROM teams WHERE short_code = 'CUR'), (SELECT id FROM matches WHERE match_no = 10), 'match', 'left', 1),
  ((SELECT id FROM teams WHERE short_code = 'CUR'), (SELECT id FROM matches WHERE match_no = 10), 'match', 'left_inside', 4),
  ((SELECT id FROM teams WHERE short_code = 'CUR'), (SELECT id FROM matches WHERE match_no = 10), 'match', 'central', 9),
  ((SELECT id FROM teams WHERE short_code = 'CUR'), (SELECT id FROM matches WHERE match_no = 10), 'match', 'right_inside', 8),
  ((SELECT id FROM teams WHERE short_code = 'CUR'), (SELECT id FROM matches WHERE match_no = 10), 'match', 'right', 2)
ON DUPLICATE KEY UPDATE entry_count=VALUES(entry_count);

-- Match 11: NED vs JPN
INSERT INTO final_third_entries (team_id, match_id, scope, zone, entry_count)
VALUES
  ((SELECT id FROM teams WHERE short_code = 'NED'), (SELECT id FROM matches WHERE match_no = 11), 'match', 'left', 6),
  ((SELECT id FROM teams WHERE short_code = 'NED'), (SELECT id FROM matches WHERE match_no = 11), 'match', 'left_inside', 6),
  ((SELECT id FROM teams WHERE short_code = 'NED'), (SELECT id FROM matches WHERE match_no = 11), 'match', 'central', 8),
  ((SELECT id FROM teams WHERE short_code = 'NED'), (SELECT id FROM matches WHERE match_no = 11), 'match', 'right_inside', 8),
  ((SELECT id FROM teams WHERE short_code = 'NED'), (SELECT id FROM matches WHERE match_no = 11), 'match', 'right', 3),
  ((SELECT id FROM teams WHERE short_code = 'JPN'), (SELECT id FROM matches WHERE match_no = 11), 'match', 'left', 3),
  ((SELECT id FROM teams WHERE short_code = 'JPN'), (SELECT id FROM matches WHERE match_no = 11), 'match', 'left_inside', 3),
  ((SELECT id FROM teams WHERE short_code = 'JPN'), (SELECT id FROM matches WHERE match_no = 11), 'match', 'central', 5),
  ((SELECT id FROM teams WHERE short_code = 'JPN'), (SELECT id FROM matches WHERE match_no = 11), 'match', 'right_inside', 7),
  ((SELECT id FROM teams WHERE short_code = 'JPN'), (SELECT id FROM matches WHERE match_no = 11), 'match', 'right', 4)
ON DUPLICATE KEY UPDATE entry_count=VALUES(entry_count);

-- Match 12: SWE vs TUN
INSERT INTO final_third_entries (team_id, match_id, scope, zone, entry_count)
VALUES
  ((SELECT id FROM teams WHERE short_code = 'SWE'), (SELECT id FROM matches WHERE match_no = 12), 'match', 'left', 5),
  ((SELECT id FROM teams WHERE short_code = 'SWE'), (SELECT id FROM matches WHERE match_no = 12), 'match', 'left_inside', 10),
  ((SELECT id FROM teams WHERE short_code = 'SWE'), (SELECT id FROM matches WHERE match_no = 12), 'match', 'central', 12),
  ((SELECT id FROM teams WHERE short_code = 'SWE'), (SELECT id FROM matches WHERE match_no = 12), 'match', 'right_inside', 8),
  ((SELECT id FROM teams WHERE short_code = 'SWE'), (SELECT id FROM matches WHERE match_no = 12), 'match', 'right', 5),
  ((SELECT id FROM teams WHERE short_code = 'TUN'), (SELECT id FROM matches WHERE match_no = 12), 'match', 'left', 4),
  ((SELECT id FROM teams WHERE short_code = 'TUN'), (SELECT id FROM matches WHERE match_no = 12), 'match', 'left_inside', 5),
  ((SELECT id FROM teams WHERE short_code = 'TUN'), (SELECT id FROM matches WHERE match_no = 12), 'match', 'central', 8),
  ((SELECT id FROM teams WHERE short_code = 'TUN'), (SELECT id FROM matches WHERE match_no = 12), 'match', 'right_inside', 8),
  ((SELECT id FROM teams WHERE short_code = 'TUN'), (SELECT id FROM matches WHERE match_no = 12), 'match', 'right', 4)
ON DUPLICATE KEY UPDATE entry_count=VALUES(entry_count);

-- Match 13: KSA vs URU
INSERT INTO final_third_entries (team_id, match_id, scope, zone, entry_count)
VALUES
  ((SELECT id FROM teams WHERE short_code = 'KSA'), (SELECT id FROM matches WHERE match_no = 13), 'match', 'left', 1),
  ((SELECT id FROM teams WHERE short_code = 'KSA'), (SELECT id FROM matches WHERE match_no = 13), 'match', 'left_inside', 2),
  ((SELECT id FROM teams WHERE short_code = 'KSA'), (SELECT id FROM matches WHERE match_no = 13), 'match', 'central', 5),
  ((SELECT id FROM teams WHERE short_code = 'KSA'), (SELECT id FROM matches WHERE match_no = 13), 'match', 'right_inside', 7),
  ((SELECT id FROM teams WHERE short_code = 'KSA'), (SELECT id FROM matches WHERE match_no = 13), 'match', 'right', 1),
  ((SELECT id FROM teams WHERE short_code = 'URU'), (SELECT id FROM matches WHERE match_no = 13), 'match', 'left', 6),
  ((SELECT id FROM teams WHERE short_code = 'URU'), (SELECT id FROM matches WHERE match_no = 13), 'match', 'left_inside', 10),
  ((SELECT id FROM teams WHERE short_code = 'URU'), (SELECT id FROM matches WHERE match_no = 13), 'match', 'central', 9),
  ((SELECT id FROM teams WHERE short_code = 'URU'), (SELECT id FROM matches WHERE match_no = 13), 'match', 'right_inside', 9),
  ((SELECT id FROM teams WHERE short_code = 'URU'), (SELECT id FROM matches WHERE match_no = 13), 'match', 'right', 5)
ON DUPLICATE KEY UPDATE entry_count=VALUES(entry_count);

-- Match 14: ESP vs CPV
INSERT INTO final_third_entries (team_id, match_id, scope, zone, entry_count)
VALUES
  ((SELECT id FROM teams WHERE short_code = 'ESP'), (SELECT id FROM matches WHERE match_no = 14), 'match', 'left', 6),
  ((SELECT id FROM teams WHERE short_code = 'ESP'), (SELECT id FROM matches WHERE match_no = 14), 'match', 'left_inside', 10),
  ((SELECT id FROM teams WHERE short_code = 'ESP'), (SELECT id FROM matches WHERE match_no = 14), 'match', 'central', 11),
  ((SELECT id FROM teams WHERE short_code = 'ESP'), (SELECT id FROM matches WHERE match_no = 14), 'match', 'right_inside', 10),
  ((SELECT id FROM teams WHERE short_code = 'ESP'), (SELECT id FROM matches WHERE match_no = 14), 'match', 'right', 2),
  ((SELECT id FROM teams WHERE short_code = 'CPV'), (SELECT id FROM matches WHERE match_no = 14), 'match', 'left', 8),
  ((SELECT id FROM teams WHERE short_code = 'CPV'), (SELECT id FROM matches WHERE match_no = 14), 'match', 'left_inside', 6),
  ((SELECT id FROM teams WHERE short_code = 'CPV'), (SELECT id FROM matches WHERE match_no = 14), 'match', 'central', 14),
  ((SELECT id FROM teams WHERE short_code = 'CPV'), (SELECT id FROM matches WHERE match_no = 14), 'match', 'right_inside', 10),
  ((SELECT id FROM teams WHERE short_code = 'CPV'), (SELECT id FROM matches WHERE match_no = 14), 'match', 'right', 4)
ON DUPLICATE KEY UPDATE entry_count=VALUES(entry_count);

-- Match 15: IRN vs NZL
INSERT INTO final_third_entries (team_id, match_id, scope, zone, entry_count)
VALUES
  ((SELECT id FROM teams WHERE short_code = 'IRN'), (SELECT id FROM matches WHERE match_no = 15), 'match', 'left', 9),
  ((SELECT id FROM teams WHERE short_code = 'IRN'), (SELECT id FROM matches WHERE match_no = 15), 'match', 'left_inside', 9),
  ((SELECT id FROM teams WHERE short_code = 'IRN'), (SELECT id FROM matches WHERE match_no = 15), 'match', 'central', 10),
  ((SELECT id FROM teams WHERE short_code = 'IRN'), (SELECT id FROM matches WHERE match_no = 15), 'match', 'right_inside', 9),
  ((SELECT id FROM teams WHERE short_code = 'IRN'), (SELECT id FROM matches WHERE match_no = 15), 'match', 'right', 5),
  ((SELECT id FROM teams WHERE short_code = 'NZL'), (SELECT id FROM matches WHERE match_no = 15), 'match', 'left', 4),
  ((SELECT id FROM teams WHERE short_code = 'NZL'), (SELECT id FROM matches WHERE match_no = 15), 'match', 'left_inside', 3),
  ((SELECT id FROM teams WHERE short_code = 'NZL'), (SELECT id FROM matches WHERE match_no = 15), 'match', 'central', 9),
  ((SELECT id FROM teams WHERE short_code = 'NZL'), (SELECT id FROM matches WHERE match_no = 15), 'match', 'right_inside', 8),
  ((SELECT id FROM teams WHERE short_code = 'NZL'), (SELECT id FROM matches WHERE match_no = 15), 'match', 'right', 2)
ON DUPLICATE KEY UPDATE entry_count=VALUES(entry_count);

-- Match 16: BEL vs EGY
INSERT INTO final_third_entries (team_id, match_id, scope, zone, entry_count)
VALUES
  ((SELECT id FROM teams WHERE short_code = 'BEL'), (SELECT id FROM matches WHERE match_no = 16), 'match', 'left', 4),
  ((SELECT id FROM teams WHERE short_code = 'BEL'), (SELECT id FROM matches WHERE match_no = 16), 'match', 'left_inside', 9),
  ((SELECT id FROM teams WHERE short_code = 'BEL'), (SELECT id FROM matches WHERE match_no = 16), 'match', 'central', 8),
  ((SELECT id FROM teams WHERE short_code = 'BEL'), (SELECT id FROM matches WHERE match_no = 16), 'match', 'right_inside', 10),
  ((SELECT id FROM teams WHERE short_code = 'BEL'), (SELECT id FROM matches WHERE match_no = 16), 'match', 'right', 3),
  ((SELECT id FROM teams WHERE short_code = 'EGY'), (SELECT id FROM matches WHERE match_no = 16), 'match', 'left', 7),
  ((SELECT id FROM teams WHERE short_code = 'EGY'), (SELECT id FROM matches WHERE match_no = 16), 'match', 'left_inside', 10),
  ((SELECT id FROM teams WHERE short_code = 'EGY'), (SELECT id FROM matches WHERE match_no = 16), 'match', 'central', 10),
  ((SELECT id FROM teams WHERE short_code = 'EGY'), (SELECT id FROM matches WHERE match_no = 16), 'match', 'right_inside', 7),
  ((SELECT id FROM teams WHERE short_code = 'EGY'), (SELECT id FROM matches WHERE match_no = 16), 'match', 'right', 4)
ON DUPLICATE KEY UPDATE entry_count=VALUES(entry_count);

-- Match 17: FRA vs SEN
INSERT INTO final_third_entries (team_id, match_id, scope, zone, entry_count)
VALUES
  ((SELECT id FROM teams WHERE short_code = 'FRA'), (SELECT id FROM matches WHERE match_no = 17), 'match', 'left', 5),
  ((SELECT id FROM teams WHERE short_code = 'FRA'), (SELECT id FROM matches WHERE match_no = 17), 'match', 'left_inside', 11),
  ((SELECT id FROM teams WHERE short_code = 'FRA'), (SELECT id FROM matches WHERE match_no = 17), 'match', 'central', 14),
  ((SELECT id FROM teams WHERE short_code = 'FRA'), (SELECT id FROM matches WHERE match_no = 17), 'match', 'right_inside', 7),
  ((SELECT id FROM teams WHERE short_code = 'FRA'), (SELECT id FROM matches WHERE match_no = 17), 'match', 'right', 6),
  ((SELECT id FROM teams WHERE short_code = 'SEN'), (SELECT id FROM matches WHERE match_no = 17), 'match', 'left', 5),
  ((SELECT id FROM teams WHERE short_code = 'SEN'), (SELECT id FROM matches WHERE match_no = 17), 'match', 'left_inside', 4),
  ((SELECT id FROM teams WHERE short_code = 'SEN'), (SELECT id FROM matches WHERE match_no = 17), 'match', 'central', 6),
  ((SELECT id FROM teams WHERE short_code = 'SEN'), (SELECT id FROM matches WHERE match_no = 17), 'match', 'right_inside', 6),
  ((SELECT id FROM teams WHERE short_code = 'SEN'), (SELECT id FROM matches WHERE match_no = 17), 'match', 'right', 3)
ON DUPLICATE KEY UPDATE entry_count=VALUES(entry_count);

-- Match 18: IRQ vs NOR
INSERT INTO final_third_entries (team_id, match_id, scope, zone, entry_count)
VALUES
  ((SELECT id FROM teams WHERE short_code = 'IRQ'), (SELECT id FROM matches WHERE match_no = 18), 'match', 'left', 1),
  ((SELECT id FROM teams WHERE short_code = 'IRQ'), (SELECT id FROM matches WHERE match_no = 18), 'match', 'left_inside', 4),
  ((SELECT id FROM teams WHERE short_code = 'IRQ'), (SELECT id FROM matches WHERE match_no = 18), 'match', 'central', 9),
  ((SELECT id FROM teams WHERE short_code = 'IRQ'), (SELECT id FROM matches WHERE match_no = 18), 'match', 'right_inside', 3),
  ((SELECT id FROM teams WHERE short_code = 'IRQ'), (SELECT id FROM matches WHERE match_no = 18), 'match', 'right', 1),
  ((SELECT id FROM teams WHERE short_code = 'NOR'), (SELECT id FROM matches WHERE match_no = 18), 'match', 'left', 7),
  ((SELECT id FROM teams WHERE short_code = 'NOR'), (SELECT id FROM matches WHERE match_no = 18), 'match', 'left_inside', 7),
  ((SELECT id FROM teams WHERE short_code = 'NOR'), (SELECT id FROM matches WHERE match_no = 18), 'match', 'central', 14),
  ((SELECT id FROM teams WHERE short_code = 'NOR'), (SELECT id FROM matches WHERE match_no = 18), 'match', 'right_inside', 8),
  ((SELECT id FROM teams WHERE short_code = 'NOR'), (SELECT id FROM matches WHERE match_no = 18), 'match', 'right', 3)
ON DUPLICATE KEY UPDATE entry_count=VALUES(entry_count);

-- Match 19: ARG vs ALG
INSERT INTO final_third_entries (team_id, match_id, scope, zone, entry_count)
VALUES
  ((SELECT id FROM teams WHERE short_code = 'ARG'), (SELECT id FROM matches WHERE match_no = 19), 'match', 'left', 6),
  ((SELECT id FROM teams WHERE short_code = 'ARG'), (SELECT id FROM matches WHERE match_no = 19), 'match', 'left_inside', 10),
  ((SELECT id FROM teams WHERE short_code = 'ARG'), (SELECT id FROM matches WHERE match_no = 19), 'match', 'central', 10),
  ((SELECT id FROM teams WHERE short_code = 'ARG'), (SELECT id FROM matches WHERE match_no = 19), 'match', 'right_inside', 8),
  ((SELECT id FROM teams WHERE short_code = 'ARG'), (SELECT id FROM matches WHERE match_no = 19), 'match', 'right', 6),
  ((SELECT id FROM teams WHERE short_code = 'ALG'), (SELECT id FROM matches WHERE match_no = 19), 'match', 'left', 6),
  ((SELECT id FROM teams WHERE short_code = 'ALG'), (SELECT id FROM matches WHERE match_no = 19), 'match', 'left_inside', 7),
  ((SELECT id FROM teams WHERE short_code = 'ALG'), (SELECT id FROM matches WHERE match_no = 19), 'match', 'central', 13),
  ((SELECT id FROM teams WHERE short_code = 'ALG'), (SELECT id FROM matches WHERE match_no = 19), 'match', 'right_inside', 11),
  ((SELECT id FROM teams WHERE short_code = 'ALG'), (SELECT id FROM matches WHERE match_no = 19), 'match', 'right', 7)
ON DUPLICATE KEY UPDATE entry_count=VALUES(entry_count);

-- Match 20: AUT vs JOR
INSERT INTO final_third_entries (team_id, match_id, scope, zone, entry_count)
VALUES
  ((SELECT id FROM teams WHERE short_code = 'AUT'), (SELECT id FROM matches WHERE match_no = 20), 'match', 'left', 6),
  ((SELECT id FROM teams WHERE short_code = 'AUT'), (SELECT id FROM matches WHERE match_no = 20), 'match', 'left_inside', 5),
  ((SELECT id FROM teams WHERE short_code = 'AUT'), (SELECT id FROM matches WHERE match_no = 20), 'match', 'central', 8),
  ((SELECT id FROM teams WHERE short_code = 'AUT'), (SELECT id FROM matches WHERE match_no = 20), 'match', 'right_inside', 8),
  ((SELECT id FROM teams WHERE short_code = 'AUT'), (SELECT id FROM matches WHERE match_no = 20), 'match', 'right', 5),
  ((SELECT id FROM teams WHERE short_code = 'JOR'), (SELECT id FROM matches WHERE match_no = 20), 'match', 'left', 5),
  ((SELECT id FROM teams WHERE short_code = 'JOR'), (SELECT id FROM matches WHERE match_no = 20), 'match', 'left_inside', 8),
  ((SELECT id FROM teams WHERE short_code = 'JOR'), (SELECT id FROM matches WHERE match_no = 20), 'match', 'central', 9),
  ((SELECT id FROM teams WHERE short_code = 'JOR'), (SELECT id FROM matches WHERE match_no = 20), 'match', 'right_inside', 4),
  ((SELECT id FROM teams WHERE short_code = 'JOR'), (SELECT id FROM matches WHERE match_no = 20), 'match', 'right', 2)
ON DUPLICATE KEY UPDATE entry_count=VALUES(entry_count);

-- Match 21: GHA vs PAN
INSERT INTO final_third_entries (team_id, match_id, scope, zone, entry_count)
VALUES
  ((SELECT id FROM teams WHERE short_code = 'GHA'), (SELECT id FROM matches WHERE match_no = 21), 'match', 'left', 1),
  ((SELECT id FROM teams WHERE short_code = 'GHA'), (SELECT id FROM matches WHERE match_no = 21), 'match', 'left_inside', 5),
  ((SELECT id FROM teams WHERE short_code = 'GHA'), (SELECT id FROM matches WHERE match_no = 21), 'match', 'central', 5),
  ((SELECT id FROM teams WHERE short_code = 'GHA'), (SELECT id FROM matches WHERE match_no = 21), 'match', 'right_inside', 7),
  ((SELECT id FROM teams WHERE short_code = 'GHA'), (SELECT id FROM matches WHERE match_no = 21), 'match', 'right', 4),
  ((SELECT id FROM teams WHERE short_code = 'PAN'), (SELECT id FROM matches WHERE match_no = 21), 'match', 'left', 5),
  ((SELECT id FROM teams WHERE short_code = 'PAN'), (SELECT id FROM matches WHERE match_no = 21), 'match', 'left_inside', 4),
  ((SELECT id FROM teams WHERE short_code = 'PAN'), (SELECT id FROM matches WHERE match_no = 21), 'match', 'central', 5),
  ((SELECT id FROM teams WHERE short_code = 'PAN'), (SELECT id FROM matches WHERE match_no = 21), 'match', 'right_inside', 3),
  ((SELECT id FROM teams WHERE short_code = 'PAN'), (SELECT id FROM matches WHERE match_no = 21), 'match', 'right', 5)
ON DUPLICATE KEY UPDATE entry_count=VALUES(entry_count);

-- Match 22: ENG vs CRO
INSERT INTO final_third_entries (team_id, match_id, scope, zone, entry_count)
VALUES
  ((SELECT id FROM teams WHERE short_code = 'ENG'), (SELECT id FROM matches WHERE match_no = 22), 'match', 'left', 3),
  ((SELECT id FROM teams WHERE short_code = 'ENG'), (SELECT id FROM matches WHERE match_no = 22), 'match', 'left_inside', 7),
  ((SELECT id FROM teams WHERE short_code = 'ENG'), (SELECT id FROM matches WHERE match_no = 22), 'match', 'central', 9),
  ((SELECT id FROM teams WHERE short_code = 'ENG'), (SELECT id FROM matches WHERE match_no = 22), 'match', 'right_inside', 6),
  ((SELECT id FROM teams WHERE short_code = 'ENG'), (SELECT id FROM matches WHERE match_no = 22), 'match', 'right', 4),
  ((SELECT id FROM teams WHERE short_code = 'CRO'), (SELECT id FROM matches WHERE match_no = 22), 'match', 'left', 5),
  ((SELECT id FROM teams WHERE short_code = 'CRO'), (SELECT id FROM matches WHERE match_no = 22), 'match', 'left_inside', 3),
  ((SELECT id FROM teams WHERE short_code = 'CRO'), (SELECT id FROM matches WHERE match_no = 22), 'match', 'central', 6),
  ((SELECT id FROM teams WHERE short_code = 'CRO'), (SELECT id FROM matches WHERE match_no = 22), 'match', 'right_inside', 7),
  ((SELECT id FROM teams WHERE short_code = 'CRO'), (SELECT id FROM matches WHERE match_no = 22), 'match', 'right', 3)
ON DUPLICATE KEY UPDATE entry_count=VALUES(entry_count);

-- Match 23: POR vs COD
INSERT INTO final_third_entries (team_id, match_id, scope, zone, entry_count)
VALUES
  ((SELECT id FROM teams WHERE short_code = 'POR'), (SELECT id FROM matches WHERE match_no = 23), 'match', 'left', 5),
  ((SELECT id FROM teams WHERE short_code = 'POR'), (SELECT id FROM matches WHERE match_no = 23), 'match', 'left_inside', 4),
  ((SELECT id FROM teams WHERE short_code = 'POR'), (SELECT id FROM matches WHERE match_no = 23), 'match', 'central', 10),
  ((SELECT id FROM teams WHERE short_code = 'POR'), (SELECT id FROM matches WHERE match_no = 23), 'match', 'right_inside', 7),
  ((SELECT id FROM teams WHERE short_code = 'POR'), (SELECT id FROM matches WHERE match_no = 23), 'match', 'right', 4),
  ((SELECT id FROM teams WHERE short_code = 'COD'), (SELECT id FROM matches WHERE match_no = 23), 'match', 'left', 3),
  ((SELECT id FROM teams WHERE short_code = 'COD'), (SELECT id FROM matches WHERE match_no = 23), 'match', 'left_inside', 8),
  ((SELECT id FROM teams WHERE short_code = 'COD'), (SELECT id FROM matches WHERE match_no = 23), 'match', 'central', 10),
  ((SELECT id FROM teams WHERE short_code = 'COD'), (SELECT id FROM matches WHERE match_no = 23), 'match', 'right_inside', 6),
  ((SELECT id FROM teams WHERE short_code = 'COD'), (SELECT id FROM matches WHERE match_no = 23), 'match', 'right', 1)
ON DUPLICATE KEY UPDATE entry_count=VALUES(entry_count);

-- Match 24: UZB vs COL
INSERT INTO final_third_entries (team_id, match_id, scope, zone, entry_count)
VALUES
  ((SELECT id FROM teams WHERE short_code = 'UZB'), (SELECT id FROM matches WHERE match_no = 24), 'match', 'left', 6),
  ((SELECT id FROM teams WHERE short_code = 'UZB'), (SELECT id FROM matches WHERE match_no = 24), 'match', 'left_inside', 5),
  ((SELECT id FROM teams WHERE short_code = 'UZB'), (SELECT id FROM matches WHERE match_no = 24), 'match', 'central', 6),
  ((SELECT id FROM teams WHERE short_code = 'UZB'), (SELECT id FROM matches WHERE match_no = 24), 'match', 'right_inside', 5),
  ((SELECT id FROM teams WHERE short_code = 'UZB'), (SELECT id FROM matches WHERE match_no = 24), 'match', 'right', 3),
  ((SELECT id FROM teams WHERE short_code = 'COL'), (SELECT id FROM matches WHERE match_no = 24), 'match', 'left', 7),
  ((SELECT id FROM teams WHERE short_code = 'COL'), (SELECT id FROM matches WHERE match_no = 24), 'match', 'left_inside', 5),
  ((SELECT id FROM teams WHERE short_code = 'COL'), (SELECT id FROM matches WHERE match_no = 24), 'match', 'central', 12),
  ((SELECT id FROM teams WHERE short_code = 'COL'), (SELECT id FROM matches WHERE match_no = 24), 'match', 'right_inside', 10),
  ((SELECT id FROM teams WHERE short_code = 'COL'), (SELECT id FROM matches WHERE match_no = 24), 'match', 'right', 6)
ON DUPLICATE KEY UPDATE entry_count=VALUES(entry_count);

-- Match 25: CZE vs RSA
INSERT INTO final_third_entries (team_id, match_id, scope, zone, entry_count)
VALUES
  ((SELECT id FROM teams WHERE short_code = 'CZE'), (SELECT id FROM matches WHERE match_no = 25), 'match', 'left', 1),
  ((SELECT id FROM teams WHERE short_code = 'CZE'), (SELECT id FROM matches WHERE match_no = 25), 'match', 'left_inside', 5),
  ((SELECT id FROM teams WHERE short_code = 'CZE'), (SELECT id FROM matches WHERE match_no = 25), 'match', 'central', 9),
  ((SELECT id FROM teams WHERE short_code = 'CZE'), (SELECT id FROM matches WHERE match_no = 25), 'match', 'right_inside', 4),
  ((SELECT id FROM teams WHERE short_code = 'CZE'), (SELECT id FROM matches WHERE match_no = 25), 'match', 'right', 1),
  ((SELECT id FROM teams WHERE short_code = 'RSA'), (SELECT id FROM matches WHERE match_no = 25), 'match', 'left', 2),
  ((SELECT id FROM teams WHERE short_code = 'RSA'), (SELECT id FROM matches WHERE match_no = 25), 'match', 'left_inside', 4),
  ((SELECT id FROM teams WHERE short_code = 'RSA'), (SELECT id FROM matches WHERE match_no = 25), 'match', 'central', 9),
  ((SELECT id FROM teams WHERE short_code = 'RSA'), (SELECT id FROM matches WHERE match_no = 25), 'match', 'right_inside', 6),
  ((SELECT id FROM teams WHERE short_code = 'RSA'), (SELECT id FROM matches WHERE match_no = 25), 'match', 'right', 1)
ON DUPLICATE KEY UPDATE entry_count=VALUES(entry_count);

-- Match 26: SUI vs BIH
INSERT INTO final_third_entries (team_id, match_id, scope, zone, entry_count)
VALUES
  ((SELECT id FROM teams WHERE short_code = 'SUI'), (SELECT id FROM matches WHERE match_no = 26), 'match', 'left', 3),
  ((SELECT id FROM teams WHERE short_code = 'SUI'), (SELECT id FROM matches WHERE match_no = 26), 'match', 'left_inside', 6),
  ((SELECT id FROM teams WHERE short_code = 'SUI'), (SELECT id FROM matches WHERE match_no = 26), 'match', 'central', 10),
  ((SELECT id FROM teams WHERE short_code = 'SUI'), (SELECT id FROM matches WHERE match_no = 26), 'match', 'right_inside', 5),
  ((SELECT id FROM teams WHERE short_code = 'SUI'), (SELECT id FROM matches WHERE match_no = 26), 'match', 'right', 1),
  ((SELECT id FROM teams WHERE short_code = 'BIH'), (SELECT id FROM matches WHERE match_no = 26), 'match', 'left', 6),
  ((SELECT id FROM teams WHERE short_code = 'BIH'), (SELECT id FROM matches WHERE match_no = 26), 'match', 'left_inside', 5),
  ((SELECT id FROM teams WHERE short_code = 'BIH'), (SELECT id FROM matches WHERE match_no = 26), 'match', 'central', 7),
  ((SELECT id FROM teams WHERE short_code = 'BIH'), (SELECT id FROM matches WHERE match_no = 26), 'match', 'right_inside', 10),
  ((SELECT id FROM teams WHERE short_code = 'BIH'), (SELECT id FROM matches WHERE match_no = 26), 'match', 'right', 5)
ON DUPLICATE KEY UPDATE entry_count=VALUES(entry_count);

-- Match 27: CAN vs QAT
INSERT INTO final_third_entries (team_id, match_id, scope, zone, entry_count)
VALUES
  ((SELECT id FROM teams WHERE short_code = 'CAN'), (SELECT id FROM matches WHERE match_no = 27), 'match', 'left', 1),
  ((SELECT id FROM teams WHERE short_code = 'CAN'), (SELECT id FROM matches WHERE match_no = 27), 'match', 'left_inside', 2),
  ((SELECT id FROM teams WHERE short_code = 'CAN'), (SELECT id FROM matches WHERE match_no = 27), 'match', 'central', 4),
  ((SELECT id FROM teams WHERE short_code = 'CAN'), (SELECT id FROM matches WHERE match_no = 27), 'match', 'right_inside', 4),
  ((SELECT id FROM teams WHERE short_code = 'CAN'), (SELECT id FROM matches WHERE match_no = 27), 'match', 'right', 2),
  ((SELECT id FROM teams WHERE short_code = 'QAT'), (SELECT id FROM matches WHERE match_no = 27), 'match', 'left', 3),
  ((SELECT id FROM teams WHERE short_code = 'QAT'), (SELECT id FROM matches WHERE match_no = 27), 'match', 'left_inside', 8),
  ((SELECT id FROM teams WHERE short_code = 'QAT'), (SELECT id FROM matches WHERE match_no = 27), 'match', 'central', 7),
  ((SELECT id FROM teams WHERE short_code = 'QAT'), (SELECT id FROM matches WHERE match_no = 27), 'match', 'right_inside', 6),
  ((SELECT id FROM teams WHERE short_code = 'QAT'), (SELECT id FROM matches WHERE match_no = 27), 'match', 'right', 4)
ON DUPLICATE KEY UPDATE entry_count=VALUES(entry_count);

-- Match 28: MEX vs KOR
INSERT INTO final_third_entries (team_id, match_id, scope, zone, entry_count)
VALUES
  ((SELECT id FROM teams WHERE short_code = 'MEX'), (SELECT id FROM matches WHERE match_no = 28), 'match', 'left', 3),
  ((SELECT id FROM teams WHERE short_code = 'MEX'), (SELECT id FROM matches WHERE match_no = 28), 'match', 'left_inside', 3),
  ((SELECT id FROM teams WHERE short_code = 'MEX'), (SELECT id FROM matches WHERE match_no = 28), 'match', 'central', 6),
  ((SELECT id FROM teams WHERE short_code = 'MEX'), (SELECT id FROM matches WHERE match_no = 28), 'match', 'right_inside', 3),
  ((SELECT id FROM teams WHERE short_code = 'MEX'), (SELECT id FROM matches WHERE match_no = 28), 'match', 'right', 2),
  ((SELECT id FROM teams WHERE short_code = 'KOR'), (SELECT id FROM matches WHERE match_no = 28), 'match', 'left', 9),
  ((SELECT id FROM teams WHERE short_code = 'KOR'), (SELECT id FROM matches WHERE match_no = 28), 'match', 'left_inside', 10),
  ((SELECT id FROM teams WHERE short_code = 'KOR'), (SELECT id FROM matches WHERE match_no = 28), 'match', 'central', 15),
  ((SELECT id FROM teams WHERE short_code = 'KOR'), (SELECT id FROM matches WHERE match_no = 28), 'match', 'right_inside', 11),
  ((SELECT id FROM teams WHERE short_code = 'KOR'), (SELECT id FROM matches WHERE match_no = 28), 'match', 'right', 5)
ON DUPLICATE KEY UPDATE entry_count=VALUES(entry_count);

-- Match 29: BRA vs HAI
INSERT INTO final_third_entries (team_id, match_id, scope, zone, entry_count)
VALUES
  ((SELECT id FROM teams WHERE short_code = 'BRA'), (SELECT id FROM matches WHERE match_no = 29), 'match', 'left', 2),
  ((SELECT id FROM teams WHERE short_code = 'BRA'), (SELECT id FROM matches WHERE match_no = 29), 'match', 'left_inside', 4),
  ((SELECT id FROM teams WHERE short_code = 'BRA'), (SELECT id FROM matches WHERE match_no = 29), 'match', 'central', 5),
  ((SELECT id FROM teams WHERE short_code = 'BRA'), (SELECT id FROM matches WHERE match_no = 29), 'match', 'right_inside', 2),
  ((SELECT id FROM teams WHERE short_code = 'BRA'), (SELECT id FROM matches WHERE match_no = 29), 'match', 'right', 4),
  ((SELECT id FROM teams WHERE short_code = 'HAI'), (SELECT id FROM matches WHERE match_no = 29), 'match', 'left', 8),
  ((SELECT id FROM teams WHERE short_code = 'HAI'), (SELECT id FROM matches WHERE match_no = 29), 'match', 'left_inside', 7),
  ((SELECT id FROM teams WHERE short_code = 'HAI'), (SELECT id FROM matches WHERE match_no = 29), 'match', 'central', 15),
  ((SELECT id FROM teams WHERE short_code = 'HAI'), (SELECT id FROM matches WHERE match_no = 29), 'match', 'right_inside', 9),
  ((SELECT id FROM teams WHERE short_code = 'HAI'), (SELECT id FROM matches WHERE match_no = 29), 'match', 'right', 2)
ON DUPLICATE KEY UPDATE entry_count=VALUES(entry_count);

-- Match 30: SCO vs MAR
INSERT INTO final_third_entries (team_id, match_id, scope, zone, entry_count)
VALUES
  ((SELECT id FROM teams WHERE short_code = 'SCO'), (SELECT id FROM matches WHERE match_no = 30), 'match', 'left', 4),
  ((SELECT id FROM teams WHERE short_code = 'SCO'), (SELECT id FROM matches WHERE match_no = 30), 'match', 'left_inside', 5),
  ((SELECT id FROM teams WHERE short_code = 'SCO'), (SELECT id FROM matches WHERE match_no = 30), 'match', 'central', 7),
  ((SELECT id FROM teams WHERE short_code = 'SCO'), (SELECT id FROM matches WHERE match_no = 30), 'match', 'right_inside', 6),
  ((SELECT id FROM teams WHERE short_code = 'SCO'), (SELECT id FROM matches WHERE match_no = 30), 'match', 'right', 1),
  ((SELECT id FROM teams WHERE short_code = 'MAR'), (SELECT id FROM matches WHERE match_no = 30), 'match', 'left', 4),
  ((SELECT id FROM teams WHERE short_code = 'MAR'), (SELECT id FROM matches WHERE match_no = 30), 'match', 'left_inside', 2),
  ((SELECT id FROM teams WHERE short_code = 'MAR'), (SELECT id FROM matches WHERE match_no = 30), 'match', 'central', 4),
  ((SELECT id FROM teams WHERE short_code = 'MAR'), (SELECT id FROM matches WHERE match_no = 30), 'match', 'right_inside', 2),
  ((SELECT id FROM teams WHERE short_code = 'MAR'), (SELECT id FROM matches WHERE match_no = 30), 'match', 'right', 4)
ON DUPLICATE KEY UPDATE entry_count=VALUES(entry_count);

-- Match 31: TUR vs PAR
INSERT INTO final_third_entries (team_id, match_id, scope, zone, entry_count)
VALUES
  ((SELECT id FROM teams WHERE short_code = 'TUR'), (SELECT id FROM matches WHERE match_no = 31), 'match', 'left', 6),
  ((SELECT id FROM teams WHERE short_code = 'TUR'), (SELECT id FROM matches WHERE match_no = 31), 'match', 'left_inside', 3),
  ((SELECT id FROM teams WHERE short_code = 'TUR'), (SELECT id FROM matches WHERE match_no = 31), 'match', 'central', 7),
  ((SELECT id FROM teams WHERE short_code = 'TUR'), (SELECT id FROM matches WHERE match_no = 31), 'match', 'right_inside', 2),
  ((SELECT id FROM teams WHERE short_code = 'TUR'), (SELECT id FROM matches WHERE match_no = 31), 'match', 'right', 4),
  ((SELECT id FROM teams WHERE short_code = 'PAR'), (SELECT id FROM matches WHERE match_no = 31), 'match', 'left', 5),
  ((SELECT id FROM teams WHERE short_code = 'PAR'), (SELECT id FROM matches WHERE match_no = 31), 'match', 'left_inside', 7),
  ((SELECT id FROM teams WHERE short_code = 'PAR'), (SELECT id FROM matches WHERE match_no = 31), 'match', 'central', 5),
  ((SELECT id FROM teams WHERE short_code = 'PAR'), (SELECT id FROM matches WHERE match_no = 31), 'match', 'right_inside', 7),
  ((SELECT id FROM teams WHERE short_code = 'PAR'), (SELECT id FROM matches WHERE match_no = 31), 'match', 'right', 1)
ON DUPLICATE KEY UPDATE entry_count=VALUES(entry_count);

-- Match 32: USA vs AUS
INSERT INTO final_third_entries (team_id, match_id, scope, zone, entry_count)
VALUES
  ((SELECT id FROM teams WHERE short_code = 'USA'), (SELECT id FROM matches WHERE match_no = 32), 'match', 'left', 7),
  ((SELECT id FROM teams WHERE short_code = 'USA'), (SELECT id FROM matches WHERE match_no = 32), 'match', 'left_inside', 8),
  ((SELECT id FROM teams WHERE short_code = 'USA'), (SELECT id FROM matches WHERE match_no = 32), 'match', 'central', 11),
  ((SELECT id FROM teams WHERE short_code = 'USA'), (SELECT id FROM matches WHERE match_no = 32), 'match', 'right_inside', 8),
  ((SELECT id FROM teams WHERE short_code = 'USA'), (SELECT id FROM matches WHERE match_no = 32), 'match', 'right', 3),
  ((SELECT id FROM teams WHERE short_code = 'AUS'), (SELECT id FROM matches WHERE match_no = 32), 'match', 'left', 2),
  ((SELECT id FROM teams WHERE short_code = 'AUS'), (SELECT id FROM matches WHERE match_no = 32), 'match', 'left_inside', 8),
  ((SELECT id FROM teams WHERE short_code = 'AUS'), (SELECT id FROM matches WHERE match_no = 32), 'match', 'central', 10),
  ((SELECT id FROM teams WHERE short_code = 'AUS'), (SELECT id FROM matches WHERE match_no = 32), 'match', 'right_inside', 5),
  ((SELECT id FROM teams WHERE short_code = 'AUS'), (SELECT id FROM matches WHERE match_no = 32), 'match', 'right', 1)
ON DUPLICATE KEY UPDATE entry_count=VALUES(entry_count);

-- Match 33: GER vs CIV
INSERT INTO final_third_entries (team_id, match_id, scope, zone, entry_count)
VALUES
  ((SELECT id FROM teams WHERE short_code = 'GER'), (SELECT id FROM matches WHERE match_no = 33), 'match', 'left', 4),
  ((SELECT id FROM teams WHERE short_code = 'GER'), (SELECT id FROM matches WHERE match_no = 33), 'match', 'left_inside', 4),
  ((SELECT id FROM teams WHERE short_code = 'GER'), (SELECT id FROM matches WHERE match_no = 33), 'match', 'central', 10),
  ((SELECT id FROM teams WHERE short_code = 'GER'), (SELECT id FROM matches WHERE match_no = 33), 'match', 'right_inside', 8),
  ((SELECT id FROM teams WHERE short_code = 'GER'), (SELECT id FROM matches WHERE match_no = 33), 'match', 'right', 2),
  ((SELECT id FROM teams WHERE short_code = 'CIV'), (SELECT id FROM matches WHERE match_no = 33), 'match', 'left', 4),
  ((SELECT id FROM teams WHERE short_code = 'CIV'), (SELECT id FROM matches WHERE match_no = 33), 'match', 'left_inside', 5),
  ((SELECT id FROM teams WHERE short_code = 'CIV'), (SELECT id FROM matches WHERE match_no = 33), 'match', 'central', 7),
  ((SELECT id FROM teams WHERE short_code = 'CIV'), (SELECT id FROM matches WHERE match_no = 33), 'match', 'right_inside', 8),
  ((SELECT id FROM teams WHERE short_code = 'CIV'), (SELECT id FROM matches WHERE match_no = 33), 'match', 'right', 5)
ON DUPLICATE KEY UPDATE entry_count=VALUES(entry_count);

-- Match 34: ECU vs CUR
INSERT INTO final_third_entries (team_id, match_id, scope, zone, entry_count)
VALUES
  ((SELECT id FROM teams WHERE short_code = 'ECU'), (SELECT id FROM matches WHERE match_no = 34), 'match', 'left', 3),
  ((SELECT id FROM teams WHERE short_code = 'ECU'), (SELECT id FROM matches WHERE match_no = 34), 'match', 'left_inside', 5),
  ((SELECT id FROM teams WHERE short_code = 'ECU'), (SELECT id FROM matches WHERE match_no = 34), 'match', 'central', 12),
  ((SELECT id FROM teams WHERE short_code = 'ECU'), (SELECT id FROM matches WHERE match_no = 34), 'match', 'right_inside', 6),
  ((SELECT id FROM teams WHERE short_code = 'ECU'), (SELECT id FROM matches WHERE match_no = 34), 'match', 'right', 5),
  ((SELECT id FROM teams WHERE short_code = 'CUR'), (SELECT id FROM matches WHERE match_no = 34), 'match', 'left', 2),
  ((SELECT id FROM teams WHERE short_code = 'CUR'), (SELECT id FROM matches WHERE match_no = 34), 'match', 'left_inside', 5),
  ((SELECT id FROM teams WHERE short_code = 'CUR'), (SELECT id FROM matches WHERE match_no = 34), 'match', 'central', 5),
  ((SELECT id FROM teams WHERE short_code = 'CUR'), (SELECT id FROM matches WHERE match_no = 34), 'match', 'right_inside', 4),
  ((SELECT id FROM teams WHERE short_code = 'CUR'), (SELECT id FROM matches WHERE match_no = 34), 'match', 'right', 2)
ON DUPLICATE KEY UPDATE entry_count=VALUES(entry_count);

-- Match 35: NED vs SWE
INSERT INTO final_third_entries (team_id, match_id, scope, zone, entry_count)
VALUES
  ((SELECT id FROM teams WHERE short_code = 'NED'), (SELECT id FROM matches WHERE match_no = 35), 'match', 'left', 3),
  ((SELECT id FROM teams WHERE short_code = 'NED'), (SELECT id FROM matches WHERE match_no = 35), 'match', 'left_inside', 6),
  ((SELECT id FROM teams WHERE short_code = 'NED'), (SELECT id FROM matches WHERE match_no = 35), 'match', 'central', 10),
  ((SELECT id FROM teams WHERE short_code = 'NED'), (SELECT id FROM matches WHERE match_no = 35), 'match', 'right_inside', 8),
  ((SELECT id FROM teams WHERE short_code = 'NED'), (SELECT id FROM matches WHERE match_no = 35), 'match', 'right', 2),
  ((SELECT id FROM teams WHERE short_code = 'SWE'), (SELECT id FROM matches WHERE match_no = 35), 'match', 'left', 8),
  ((SELECT id FROM teams WHERE short_code = 'SWE'), (SELECT id FROM matches WHERE match_no = 35), 'match', 'left_inside', 10),
  ((SELECT id FROM teams WHERE short_code = 'SWE'), (SELECT id FROM matches WHERE match_no = 35), 'match', 'central', 9),
  ((SELECT id FROM teams WHERE short_code = 'SWE'), (SELECT id FROM matches WHERE match_no = 35), 'match', 'right_inside', 11),
  ((SELECT id FROM teams WHERE short_code = 'SWE'), (SELECT id FROM matches WHERE match_no = 35), 'match', 'right', 6)
ON DUPLICATE KEY UPDATE entry_count=VALUES(entry_count);

-- Match 36: TUN vs JPN
INSERT INTO final_third_entries (team_id, match_id, scope, zone, entry_count)
VALUES
  ((SELECT id FROM teams WHERE short_code = 'TUN'), (SELECT id FROM matches WHERE match_no = 36), 'match', 'left', 7),
  ((SELECT id FROM teams WHERE short_code = 'TUN'), (SELECT id FROM matches WHERE match_no = 36), 'match', 'left_inside', 3),
  ((SELECT id FROM teams WHERE short_code = 'TUN'), (SELECT id FROM matches WHERE match_no = 36), 'match', 'central', 7),
  ((SELECT id FROM teams WHERE short_code = 'TUN'), (SELECT id FROM matches WHERE match_no = 36), 'match', 'right_inside', 5),
  ((SELECT id FROM teams WHERE short_code = 'TUN'), (SELECT id FROM matches WHERE match_no = 36), 'match', 'right', 1),
  ((SELECT id FROM teams WHERE short_code = 'JPN'), (SELECT id FROM matches WHERE match_no = 36), 'match', 'left', 6),
  ((SELECT id FROM teams WHERE short_code = 'JPN'), (SELECT id FROM matches WHERE match_no = 36), 'match', 'left_inside', 6),
  ((SELECT id FROM teams WHERE short_code = 'JPN'), (SELECT id FROM matches WHERE match_no = 36), 'match', 'central', 5),
  ((SELECT id FROM teams WHERE short_code = 'JPN'), (SELECT id FROM matches WHERE match_no = 36), 'match', 'right_inside', 4),
  ((SELECT id FROM teams WHERE short_code = 'JPN'), (SELECT id FROM matches WHERE match_no = 36), 'match', 'right', 2)
ON DUPLICATE KEY UPDATE entry_count=VALUES(entry_count);

-- Match 37: URU vs CPV
INSERT INTO final_third_entries (team_id, match_id, scope, zone, entry_count)
VALUES
  ((SELECT id FROM teams WHERE short_code = 'URU'), (SELECT id FROM matches WHERE match_no = 37), 'match', 'left', 4),
  ((SELECT id FROM teams WHERE short_code = 'URU'), (SELECT id FROM matches WHERE match_no = 37), 'match', 'left_inside', 11),
  ((SELECT id FROM teams WHERE short_code = 'URU'), (SELECT id FROM matches WHERE match_no = 37), 'match', 'central', 11),
  ((SELECT id FROM teams WHERE short_code = 'URU'), (SELECT id FROM matches WHERE match_no = 37), 'match', 'right_inside', 7),
  ((SELECT id FROM teams WHERE short_code = 'URU'), (SELECT id FROM matches WHERE match_no = 37), 'match', 'right', 7),
  ((SELECT id FROM teams WHERE short_code = 'CPV'), (SELECT id FROM matches WHERE match_no = 37), 'match', 'left', 5),
  ((SELECT id FROM teams WHERE short_code = 'CPV'), (SELECT id FROM matches WHERE match_no = 37), 'match', 'left_inside', 10),
  ((SELECT id FROM teams WHERE short_code = 'CPV'), (SELECT id FROM matches WHERE match_no = 37), 'match', 'central', 12),
  ((SELECT id FROM teams WHERE short_code = 'CPV'), (SELECT id FROM matches WHERE match_no = 37), 'match', 'right_inside', 8),
  ((SELECT id FROM teams WHERE short_code = 'CPV'), (SELECT id FROM matches WHERE match_no = 37), 'match', 'right', 2)
ON DUPLICATE KEY UPDATE entry_count=VALUES(entry_count);

-- Match 38: ESP vs KSA
INSERT INTO final_third_entries (team_id, match_id, scope, zone, entry_count)
VALUES
  ((SELECT id FROM teams WHERE short_code = 'ESP'), (SELECT id FROM matches WHERE match_no = 38), 'match', 'left', 6),
  ((SELECT id FROM teams WHERE short_code = 'ESP'), (SELECT id FROM matches WHERE match_no = 38), 'match', 'left_inside', 5),
  ((SELECT id FROM teams WHERE short_code = 'ESP'), (SELECT id FROM matches WHERE match_no = 38), 'match', 'central', 6),
  ((SELECT id FROM teams WHERE short_code = 'ESP'), (SELECT id FROM matches WHERE match_no = 38), 'match', 'right_inside', 2),
  ((SELECT id FROM teams WHERE short_code = 'ESP'), (SELECT id FROM matches WHERE match_no = 38), 'match', 'right', 1),
  ((SELECT id FROM teams WHERE short_code = 'KSA'), (SELECT id FROM matches WHERE match_no = 38), 'match', 'left', 3),
  ((SELECT id FROM teams WHERE short_code = 'KSA'), (SELECT id FROM matches WHERE match_no = 38), 'match', 'left_inside', 9),
  ((SELECT id FROM teams WHERE short_code = 'KSA'), (SELECT id FROM matches WHERE match_no = 38), 'match', 'central', 8),
  ((SELECT id FROM teams WHERE short_code = 'KSA'), (SELECT id FROM matches WHERE match_no = 38), 'match', 'right_inside', 5),
  ((SELECT id FROM teams WHERE short_code = 'KSA'), (SELECT id FROM matches WHERE match_no = 38), 'match', 'right', 6)
ON DUPLICATE KEY UPDATE entry_count=VALUES(entry_count);

-- Match 39: BEL vs IRN
INSERT INTO final_third_entries (team_id, match_id, scope, zone, entry_count)
VALUES
  ((SELECT id FROM teams WHERE short_code = 'BEL'), (SELECT id FROM matches WHERE match_no = 39), 'match', 'left', 6),
  ((SELECT id FROM teams WHERE short_code = 'BEL'), (SELECT id FROM matches WHERE match_no = 39), 'match', 'left_inside', 10),
  ((SELECT id FROM teams WHERE short_code = 'BEL'), (SELECT id FROM matches WHERE match_no = 39), 'match', 'central', 10),
  ((SELECT id FROM teams WHERE short_code = 'BEL'), (SELECT id FROM matches WHERE match_no = 39), 'match', 'right_inside', 9),
  ((SELECT id FROM teams WHERE short_code = 'BEL'), (SELECT id FROM matches WHERE match_no = 39), 'match', 'right', 1),
  ((SELECT id FROM teams WHERE short_code = 'IRN'), (SELECT id FROM matches WHERE match_no = 39), 'match', 'left', 1),
  ((SELECT id FROM teams WHERE short_code = 'IRN'), (SELECT id FROM matches WHERE match_no = 39), 'match', 'left_inside', 7),
  ((SELECT id FROM teams WHERE short_code = 'IRN'), (SELECT id FROM matches WHERE match_no = 39), 'match', 'central', 5),
  ((SELECT id FROM teams WHERE short_code = 'IRN'), (SELECT id FROM matches WHERE match_no = 39), 'match', 'right_inside', 6),
  ((SELECT id FROM teams WHERE short_code = 'IRN'), (SELECT id FROM matches WHERE match_no = 39), 'match', 'right', 1)
ON DUPLICATE KEY UPDATE entry_count=VALUES(entry_count);

-- Match 40: NZL vs EGY
INSERT INTO final_third_entries (team_id, match_id, scope, zone, entry_count)
VALUES
  ((SELECT id FROM teams WHERE short_code = 'NZL'), (SELECT id FROM matches WHERE match_no = 40), 'match', 'left', 6),
  ((SELECT id FROM teams WHERE short_code = 'NZL'), (SELECT id FROM matches WHERE match_no = 40), 'match', 'left_inside', 8),
  ((SELECT id FROM teams WHERE short_code = 'NZL'), (SELECT id FROM matches WHERE match_no = 40), 'match', 'central', 7),
  ((SELECT id FROM teams WHERE short_code = 'NZL'), (SELECT id FROM matches WHERE match_no = 40), 'match', 'right_inside', 7),
  ((SELECT id FROM teams WHERE short_code = 'NZL'), (SELECT id FROM matches WHERE match_no = 40), 'match', 'right', 2),
  ((SELECT id FROM teams WHERE short_code = 'EGY'), (SELECT id FROM matches WHERE match_no = 40), 'match', 'left', 2),
  ((SELECT id FROM teams WHERE short_code = 'EGY'), (SELECT id FROM matches WHERE match_no = 40), 'match', 'left_inside', 4),
  ((SELECT id FROM teams WHERE short_code = 'EGY'), (SELECT id FROM matches WHERE match_no = 40), 'match', 'central', 3),
  ((SELECT id FROM teams WHERE short_code = 'EGY'), (SELECT id FROM matches WHERE match_no = 40), 'match', 'right_inside', 4),
  ((SELECT id FROM teams WHERE short_code = 'EGY'), (SELECT id FROM matches WHERE match_no = 40), 'match', 'right', 1)
ON DUPLICATE KEY UPDATE entry_count=VALUES(entry_count);

