<script lang="ts">
	import type { MatchStats, Team } from '$lib/types/efi';
	import { teamTextColor } from '$lib/tokens';
	import { t } from '$lib/i18n';

	let { stats, team_a, team_b }: { stats: MatchStats; team_a: Team; team_b: Team } = $props();

	const n = (v: number | null, fallback = 0) => v ?? fallback;
	const fmt = (v: number | null, d = 2) => v != null ? v.toFixed(d) : '—';

	const rows: Array<{ label: string; a: string | number; b: string | number }> = $derived([
		{ label: $t.keyStats.goals, a: n(stats.goals_a), b: n(stats.goals_b) },
		{ label: $t.stats.xg, a: fmt(stats.xg_a), b: fmt(stats.xg_b) },
		{ label: $t.keyStats.possession, a: `${n(stats.possession_team_a)}%`, b: `${n(stats.possession_team_b)}%` },
		{ label: $t.keyStats.inContest, a: `${n(stats.possession_in_contest)}%`, b: `${n(stats.possession_in_contest)}%` },
		{ label: $t.detail.ballRecovery, a: stats.ball_recovery_time_avg != null ? `${stats.ball_recovery_time_avg}s` : '—', b: '-' },
		{ label: $t.detail.xgShot, a: fmt(stats.xg_a != null ? stats.xg_a / Math.max(n(stats.goals_a), 1) : null), b: fmt(stats.xg_b != null ? stats.xg_b / Math.max(n(stats.goals_b), 1) : null) },
		{ label: $t.detail.efficiency, a: stats.xg_a != null ? `${((n(stats.goals_a) / Math.max(stats.xg_a, 0.01)) * 100).toFixed(0)}%` : '—', b: stats.xg_b != null ? `${((n(stats.goals_b) / Math.max(stats.xg_b, 0.01)) * 100).toFixed(0)}%` : '—' },
		{ label: $t.detail.outOfPossession, a: stats.possession_team_a != null && stats.possession_in_contest != null ? `${(100 - stats.possession_team_a - stats.possession_in_contest).toFixed(1)}%` : '—', b: stats.possession_team_b != null && stats.possession_in_contest != null ? `${(100 - stats.possession_team_b - stats.possession_in_contest).toFixed(1)}%` : '—' }
	]);
</script>

<div class="stat-table-wrap">
	<div class="stat-table__header">
		<span class="stat-table__team-name" style="color: {teamTextColor(team_a.color)}">{team_a.name}</span>
		<span class="stat-table__header-center">{$t.detail.headToHead.toUpperCase()}</span>
		<span class="stat-table__team-name stat-table__team-name--right" style="color: {teamTextColor(team_b.color)}">{team_b.name}</span>
	</div>
	<table class="stat-table" aria-label={$t.a11y.headToHeadStats}>
		<tbody>
			{#each rows as row}
				<tr class="stat-table__row">
					<td class="stat-table__val stat-table__val--a" style="color: {teamTextColor(team_a.color)}">{row.a}</td>
					<td class="stat-table__label">{row.label}</td>
					<td class="stat-table__val stat-table__val--b" style="color: {teamTextColor(team_b.color)}">{row.b}</td>
				</tr>
			{/each}
		</tbody>
	</table>
</div>

<style>
	.stat-table-wrap {
		width: 100%;
	}
	.stat-table__header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: var(--sp-4);
	}
	.stat-table__team-name {
		font-size: var(--fs-label);
		font-weight: 700;
		text-transform: uppercase;
		letter-spacing: 0.05em;
	}
	.stat-table__team-name--right {
		text-align: right;
	}
	.stat-table__header-center {
		font-size: var(--fs-label);
		font-weight: 600;
		color: var(--muted);
		text-transform: uppercase;
		letter-spacing: 0.1em;
	}
	.stat-table {
		width: 100%;
		border-collapse: collapse;
	}
	.stat-table__row {
		border-bottom: 1px solid var(--border-soft);
		min-height: 44px;
	}
	.stat-table__row:last-child { border-bottom: none; }
	.stat-table__row:hover { background: var(--border-soft); }
	.stat-table__val {
		font-size: var(--fs-ui);
		font-weight: 800;
		font-variant-numeric: tabular-nums;
		padding: var(--sp-3) 0;
		width: 30%;
	}
	.stat-table__val--a {
		text-align: left;
	}
	.stat-table__val--b {
		text-align: right;
	}
	.stat-table__label {
		font-size: var(--fs-ui);
		font-weight: 500;
		color: var(--muted);
		text-align: center;
		padding: var(--sp-3) var(--sp-2);
		width: 40%;
	}
</style>
