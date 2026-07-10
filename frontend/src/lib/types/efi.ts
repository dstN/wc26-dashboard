export interface Team {
	id: number;
	name: string;
	short_code: string;
	slug: string;
	color: string;
}

export interface MatchMeta {
	id: number;
	match_no: number;
	// null for unplayed/fixture matches (backend serialises nullable DB columns)
	score_a: number | null;
	score_b: number | null;
	venue: string;
	match_date: string;
	group_letter: string;
	team_a: Team;
	team_b: Team;
	formation_a?: string | null;
	formation_b?: string | null;
	// score_a/score_b already reflect extra time when played; this only flags
	// that ET happened (for an "AET" badge). Penalty score is separate since
	// a shootout doesn't change the match score.
	went_to_extra_time: boolean;
	penalty_score_a?: number | null;
	penalty_score_b?: number | null;
}

export interface MatchStats {
	possession_team_a: number | null;
	possession_team_b: number | null;
	possession_in_contest: number | null;
	ball_recovery_time_avg: number | null;
	xg_a: number | null;
	xg_b: number | null;
	goals_a: number | null;
	goals_b: number | null;
}

export interface TeamSpatial {
	defensive_line_height: number;
	team_length: number;
	width_m: number | null;
	block_type: 'high' | 'mid' | 'low' | 'build_up_low' | 'build_up_mid' | 'final_third_phase';
}

export interface TeamSpatialSplit {
	defensive: TeamSpatial[];
	possession: TeamSpatial[];
}

export interface Phase {
	phase_name: string;
	pct: number;
	phase_group: 'in' | 'out';
}

export interface LineBreak {
	line_type: 'defensive' | 'midfield' | 'attacking';
	attempted: number;
	completed: number;
}

export interface FinalThirdEntry {
	zone: 'left' | 'left_inside' | 'central' | 'right_inside' | 'right';
	count: number;
}

export interface DefensiveAction {
	forced_turnovers: number;
	pressure_on_ball: 'moderate' | 'heavy';
}

export interface KpiCard {
	label: string;
	value: string;
	unit?: string;
}

export interface TournamentOverview {
	matches_played: number;
	goals_total: number;
	avg_in_contest_pct: number;
	// per-stage played counts (only on GET /overview, not GET /dashboard):
	// { group: number, R32: number, R16: number, QF: number, SF: number, '3RD': number, FIN: number }
	stage_counts?: Record<string, number>;
}

export interface DashboardData {
	overview: TournamentOverview;
	featured: MatchMeta;
	possession: MatchStats;
	head_to_head: MatchStats;
	phases: { team_a: Phase[]; team_b: Phase[] };
	spatial: { team_a: TeamSpatialSplit; team_b: TeamSpatialSplit };
	line_breaks: { team_a: LineBreak[]; team_b: LineBreak[] };
	final_third: { team_a: FinalThirdEntry[]; team_b: FinalThirdEntry[] };
	defensive: { team_a: DefensiveAction; team_b: DefensiveAction };
	kpi_cards: KpiCard[];
}
