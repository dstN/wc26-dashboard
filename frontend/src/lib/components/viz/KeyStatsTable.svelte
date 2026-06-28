<script lang="ts">
	import type { Team } from '$lib/types/efi';
	import { teamTextColor } from '$lib/tokens';
	import { t } from '$lib/i18n';

	interface TeamStats {
		goals?: number | null;
		xg?: number | null;
		possession_pct?: number | null;
		in_contest_pct?: number | null;
		ball_recovery_time_avg?: number | null;
		shots_total?: number | null;
		shots_on_target?: number | null;
		passes_attempted?: number | null;
		passes_completed?: number | null;
		pass_completion_pct?: number | null;
		completed_line_breaks?: number | null;
		defensive_line_breaks?: number | null;
		crosses?: number | null;
		ball_progressions?: number | null;
		take_ons?: number | null;
		forced_turnovers?: number | null;
		tackles_made?: number | null;
		tackles_won?: number | null;
		interceptions?: number | null;
		blocks?: number | null;
		clearances?: number | null;
		possession_regains?: number | null;
		pressing_direct?: number | null;
		duels_won_aerial?: number | null;
		duels_won_physical?: number | null;
		total_distance_km?: number | null;
		gk_involvements?: number | null;
		gk_distributions?: number | null;
		gk_line_breaks?: number | null;
		gk_attempts_faced?: number | null;
		gk_save_pct?: number | null;
		gk_goal_interventions?: number | null;
		gk_crosses_faced?: number | null;
		gk_kick_from_feet?: number | null;
		gk_kick_from_hands?: number | null;
		gk_throw_distribution?: number | null;
		gk_aerial_interventions?: number | null;
		gk_name?: string | null;
		gk_save_retain?: number | null;
		gk_deflect_retain?: number | null;
		gk_save_deflect?: number | null;
		gk_save_attempt?: number | null;
		gk_no_save_attempt?: number | null;
		gk_crosses_inswing?: number | null;
		gk_crosses_outswing?: number | null;
		gk_crosses_driven?: number | null;
		gk_crosses_lofted?: number | null;
		gk_crosses_cutback?: number | null;
		gk_crosses_push?: number | null;
		gk_punches_complete?: number | null;
		gk_punches_incomplete?: number | null;
		gk_claims_complete?: number | null;
		gk_claims_incomplete?: number | null;
		gk_tipped_complete?: number | null;
		gk_tipped_incomplete?: number | null;
		set_plays?: number | null;
		free_kicks?: number | null;
		free_kicks_direct?: number | null;
		free_kicks_indirect?: number | null;
		corners?: number | null;
		throw_ins?: number | null;
		penalties?: number | null;
		corner_inswing?: number | null;
		corner_outswing?: number | null;
		corner_driven?: number | null;
		corner_lofted?: number | null;
		corner_direct_area_total?: number | null;
		corner_short_total?: number | null;
		corner_edge_total?: number | null;
	}

	let {
		stats_a,
		stats_b,
		team_a,
		team_b
	}: { stats_a: TeamStats; stats_b: TeamStats; team_a: Team; team_b: Team } = $props();

	const f = (v: number | null | undefined, suffix = '') =>
		v != null ? `${v}${suffix}` : '—';
	const fmt = (v: number | null | undefined, d = 2) =>
		v != null ? v.toFixed(d) : '—';

	type Row = { label: string; a: string; b: string; highlight?: boolean };
	type Group = { title: string; rows: Row[] };

	const groups: Group[] = $derived([
		{
			title: $t.keyStats.grpSummary,
			rows: [
				{ label: $t.keyStats.goals, a: f(stats_a.goals), b: f(stats_b.goals), highlight: true },
				{ label: $t.keyStats.xg, a: fmt(stats_a.xg), b: fmt(stats_b.xg) },
				{ label: $t.keyStats.shotsOnTarget, a: stats_a.shots_total != null ? `${stats_a.shots_total} (${stats_a.shots_on_target ?? 0})` : '—', b: stats_b.shots_total != null ? `${stats_b.shots_total} (${stats_b.shots_on_target ?? 0})` : '—' },
				{ label: $t.keyStats.possession, a: f(stats_a.possession_pct, '%'), b: f(stats_b.possession_pct, '%') },
				{ label: $t.keyStats.inContest, a: f(stats_a.in_contest_pct, '%'), b: f(stats_b.in_contest_pct, '%') },
				{ label: $t.keyStats.ballRecovery, a: stats_a.ball_recovery_time_avg != null ? `${stats_a.ball_recovery_time_avg}s` : '—', b: stats_b.ball_recovery_time_avg != null ? `${stats_b.ball_recovery_time_avg}s` : '—' },
				{ label: $t.keyStats.distance, a: f(stats_a.total_distance_km), b: f(stats_b.total_distance_km) },
			]
		},
		{
			title: $t.keyStats.grpPassing,
			rows: [
				{ label: $t.keyStats.passes, a: stats_a.passes_attempted != null ? `${stats_a.passes_attempted} (${stats_a.passes_completed ?? 0})` : '—', b: stats_b.passes_attempted != null ? `${stats_b.passes_attempted} (${stats_b.passes_completed ?? 0})` : '—' },
				{ label: $t.keyStats.passCompletion, a: f(stats_a.pass_completion_pct, '%'), b: f(stats_b.pass_completion_pct, '%') },
				{ label: $t.keyStats.lineBreaksComp, a: f(stats_a.completed_line_breaks), b: f(stats_b.completed_line_breaks) },
				{ label: $t.keyStats.lineBreaksDef, a: f(stats_a.defensive_line_breaks), b: f(stats_b.defensive_line_breaks) },
				{ label: $t.keyStats.crosses, a: f(stats_a.crosses), b: f(stats_b.crosses) },
				{ label: $t.keyStats.ballProgressions, a: f(stats_a.ball_progressions), b: f(stats_b.ball_progressions) },
				{ label: $t.keyStats.takeOns, a: f(stats_a.take_ons), b: f(stats_b.take_ons) },
			]
		},
		{
			title: $t.keyStats.grpDefensive,
			rows: [
				{ label: $t.keyStats.forcedTurnovers, a: f(stats_a.forced_turnovers), b: f(stats_b.forced_turnovers) },
				{ label: $t.keyStats.tackles, a: stats_a.tackles_made != null ? `${stats_a.tackles_made} (${stats_a.tackles_won ?? 0})` : '—', b: stats_b.tackles_made != null ? `${stats_b.tackles_made} (${stats_b.tackles_won ?? 0})` : '—' },
				{ label: $t.keyStats.interceptions, a: f(stats_a.interceptions), b: f(stats_b.interceptions) },
				{ label: $t.keyStats.blocks, a: f(stats_a.blocks), b: f(stats_b.blocks) },
				{ label: $t.keyStats.clearances, a: f(stats_a.clearances), b: f(stats_b.clearances) },
				{ label: $t.keyStats.regains, a: f(stats_a.possession_regains), b: f(stats_b.possession_regains) },
				{ label: $t.keyStats.pressures, a: f(stats_a.pressing_direct), b: f(stats_b.pressing_direct) },
				{ label: $t.keyStats.aerialDuels, a: f(stats_a.duels_won_aerial), b: f(stats_b.duels_won_aerial) },
				{ label: $t.keyStats.physicalDuels, a: f(stats_a.duels_won_physical), b: f(stats_b.duels_won_physical) },
			]
		},
		{
			title: $t.keyStats.grpSetPlays,
			rows: [
				{ label: $t.keyStats.setPlays, a: f(stats_a.set_plays), b: f(stats_b.set_plays) },
				{ label: $t.keyStats.freeKicks, a: stats_a.free_kicks != null ? `${stats_a.free_kicks} (${stats_a.free_kicks_direct ?? 0}D / ${stats_a.free_kicks_indirect ?? 0}I)` : '—', b: stats_b.free_kicks != null ? `${stats_b.free_kicks} (${stats_b.free_kicks_direct ?? 0}D / ${stats_b.free_kicks_indirect ?? 0}I)` : '—' },
				{ label: $t.keyStats.corners, a: f(stats_a.corners), b: f(stats_b.corners) },
				{ label: $t.keyStats.cornerDeliveryInswing, a: f(stats_a.corner_inswing), b: f(stats_b.corner_inswing) },
				{ label: $t.keyStats.cornerDeliveryOutswing, a: f(stats_a.corner_outswing), b: f(stats_b.corner_outswing) },
				{ label: $t.keyStats.cornerDeliveryDriven, a: f(stats_a.corner_driven), b: f(stats_b.corner_driven) },
				{ label: $t.keyStats.cornerDeliveryLofted, a: f(stats_a.corner_lofted), b: f(stats_b.corner_lofted) },
				{ label: $t.keyStats.cornerZoneDirectArea, a: f(stats_a.corner_direct_area_total), b: f(stats_b.corner_direct_area_total) },
				{ label: $t.keyStats.cornerZoneShort, a: f(stats_a.corner_short_total), b: f(stats_b.corner_short_total) },
				{ label: $t.keyStats.cornerZoneEdge, a: f(stats_a.corner_edge_total), b: f(stats_b.corner_edge_total) },
				{ label: $t.keyStats.throwIns, a: f(stats_a.throw_ins), b: f(stats_b.throw_ins) },
				{ label: $t.keyStats.penalties, a: f(stats_a.penalties), b: f(stats_b.penalties) },
			]
		},
	]);
</script>

<div class="kst">
	<div class="kst__header">
		<a href="/teams/{team_a.id}" class="kst__tname" style="color: {teamTextColor(team_a.color)}">{team_a.name}</a>
		<span class="kst__center">{$t.keyStats.header}</span>
		<a href="/teams/{team_b.id}" class="kst__tname kst__tname--r" style="color: {teamTextColor(team_b.color)}">{team_b.name}</a>
	</div>
	{#each groups as group}
		<div class="kst__group-title">{group.title}</div>
		{#each group.rows as row}
			<div class="kst__row" class:kst__row--highlight={row.highlight}>
				<span class="kst__val kst__val--a" style="color: {teamTextColor(team_a.color)}">{row.a}</span>
				<span class="kst__label">{row.label}</span>
				<span class="kst__val kst__val--b" style="color: {teamTextColor(team_b.color)}">{row.b}</span>
			</div>
		{/each}
	{/each}
</div>

<style>
	.kst {
		width: 100%;
	}
	.kst__header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding-bottom: var(--sp-4);
		margin-bottom: var(--sp-2);
		border-bottom: 2px solid var(--border);
	}
	.kst__tname {
		font-size: var(--fs-label);
		font-weight: 800;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		text-decoration: none;
	}
	.kst__tname:hover { text-decoration: underline; }
	.kst__tname--r { text-align: right; }
	.kst__center {
		font-size: var(--fs-label);
		font-weight: 600;
		color: var(--muted);
		text-transform: uppercase;
		letter-spacing: 0.1em;
	}
	.kst__group-title {
		font-size: var(--fs-meta);
		font-weight: 700;
		text-transform: uppercase;
		letter-spacing: 0.1em;
		color: var(--muted);
		padding: var(--sp-5) 0 var(--sp-2);
	}
	.kst__row {
		display: flex;
		align-items: center;
		padding: var(--sp-2) 0;
		border-bottom: 1px solid var(--border-soft);
	}
	.kst__row:last-child { border-bottom: none; }
	.kst__row--highlight .kst__val {
		font-size: var(--fs-ui);
		font-weight: 900;
	}
	.kst__val {
		font-size: var(--fs-ui);
		font-weight: 700;
		font-variant-numeric: tabular-nums;
		width: 30%;
	}
	.kst__val--a { text-align: left; }
	.kst__val--b { text-align: right; }
	.kst__label {
		font-size: var(--fs-ui);
		font-weight: 400;
		color: var(--muted);
		text-align: center;
		flex: 1;
		padding: 0 var(--sp-2);
	}
</style>
