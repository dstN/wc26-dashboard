<script lang="ts">
	import type { Team } from '$lib/types/efi';
	import { teamTextColor, teamColorVar } from '$lib/tokens';
	import { t } from '$lib/i18n';

	interface DefensiveStat {
		forced_turnovers: number | null;
		pressure_on_ball: number | null;
		possession_regained: number | null;
		interceptions: number | null;
		tackles: number | null;
		possession_actions_per_da: number | null;
		blocks_total: number | null;
		blocks_passes: number | null;
		blocks_shots: number | null;
		blocks_crosses: number | null;
		blocks_clearances: number | null;
		contests_total: number | null;
		contests_physical: number | null;
		contests_aerial: number | null;
		contests_duels: number | null;
		most_regains_player?: string | null;
		most_regains_count?: number | null;
	}

	let {
		defensive_a,
		defensive_b,
		team_a,
		team_b
	}: { defensive_a: DefensiveStat | null; defensive_b: DefensiveStat | null; team_a: Team; team_b: Team } = $props();

	const summaryRows = $derived([
		{ label: $t.keyStats.forcedTurnovers, key: 'forced_turnovers', fmt: (v: number | null) => v?.toString() ?? '—' },
		{ label: $t.keyStats.regains, key: 'possession_regained', fmt: (v: number | null) => v?.toString() ?? '—' },
		{ label: $t.keyStats.interceptions, key: 'interceptions', fmt: (v: number | null) => v?.toString() ?? '—' },
		{ label: $t.detail.tackles, key: 'tackles', fmt: (v: number | null) => v?.toString() ?? '—' },
		{ label: $t.detail.actionsPerDefAction, key: 'possession_actions_per_da', fmt: (v: number | null) => v != null ? Number(v).toFixed(2) : '—' },
	]);

	const blockRows = $derived([
		{ label: $t.detail.blocksPass, key: 'blocks_passes', fmt: (v: number | null) => v?.toString() ?? '—' },
		{ label: $t.detail.blocksShot, key: 'blocks_shots', fmt: (v: number | null) => v?.toString() ?? '—' },
		{ label: $t.detail.blocksCross, key: 'blocks_crosses', fmt: (v: number | null) => v?.toString() ?? '—' },
		{ label: $t.detail.blocksClearance, key: 'blocks_clearances', fmt: (v: number | null) => v?.toString() ?? '—' },
		{ label: $t.detail.blocksTotal, key: 'blocks_total', fmt: (v: number | null) => v?.toString() ?? '—' },
	]);

	const contestRows = $derived([
		{ label: $t.keyStats.physicalDuels, key: 'contests_physical', fmt: (v: number | null) => v?.toString() ?? '—' },
		{ label: $t.keyStats.aerialDuels, key: 'contests_aerial', fmt: (v: number | null) => v?.toString() ?? '—' },
		{ label: $t.detail.duels, key: 'contests_duels', fmt: (v: number | null) => v?.toString() ?? '—' },
		{ label: $t.detail.contestsTotal, key: 'contests_total', fmt: (v: number | null) => v?.toString() ?? '—' },
	]);

	function get(stat: DefensiveStat | null, key: string): number | null {
		return stat ? (stat as unknown as Record<string, number | null>)[key] ?? null : null;
	}
</script>

<div class="dd">
	<div class="dd__header">
		<a href="/teams/{team_a.id}" class="dd__tname" style="color: {teamTextColor(team_a.color)}">{team_a.name}</a>
		<span class="dd__center">{$t.detail.defensiveHeader}</span>
		<a href="/teams/{team_b.id}" class="dd__tname dd__tname--r" style="color: {teamTextColor(team_b.color)}">{team_b.name}</a>
	</div>

	{#each summaryRows as row}
		{@const va = get(defensive_a, row.key)}
		{@const vb = get(defensive_b, row.key)}
		<div class="dd__row">
			<span class="dd__val" style="color: {teamTextColor(team_a.color)}">{row.fmt(va)}</span>
			<span class="dd__label">{row.label}</span>
			<span class="dd__val dd__val--r" style="color: {teamTextColor(team_b.color)}">{row.fmt(vb)}</span>
		</div>
	{/each}

	<div class="dd__subheader">{$t.detail.blocksBreakdown}</div>
	{#each blockRows as row}
		{@const va = get(defensive_a, row.key)}
		{@const vb = get(defensive_b, row.key)}
		<div class="dd__row dd__row--sub">
			<span class="dd__val" style="color: {teamTextColor(team_a.color)}">{row.fmt(va)}</span>
			<span class="dd__label">{row.label}</span>
			<span class="dd__val dd__val--r" style="color: {teamTextColor(team_b.color)}">{row.fmt(vb)}</span>
		</div>
	{/each}

	<div class="dd__subheader">{$t.detail.possessionContests}</div>
	{#each contestRows as row}
		{@const va = get(defensive_a, row.key)}
		{@const vb = get(defensive_b, row.key)}
		<div class="dd__row dd__row--sub">
			<span class="dd__val" style="color: {teamTextColor(team_a.color)}">{row.fmt(va)}</span>
			<span class="dd__label">{row.label}</span>
			<span class="dd__val dd__val--r" style="color: {teamTextColor(team_b.color)}">{row.fmt(vb)}</span>
		</div>
	{/each}

	{#if defensive_a?.most_regains_player || defensive_b?.most_regains_player}
		<div class="dd__callout-row">
			{#if defensive_a?.most_regains_player}
				<div class="dd__callout">
					<span class="dd__callout-val" style="color: {teamTextColor(team_a.color)}">{defensive_a.most_regains_count}</span>
					<span class="dd__callout-name">
						<span class="dd__callout-dot" style="background: {teamColorVar(team_a.color)}"></span>
						{defensive_a.most_regains_player}
					</span>
					<span class="dd__callout-label">{$t.detail.mostPossessionRegains}</span>
				</div>
			{/if}
			{#if defensive_b?.most_regains_player}
				<div class="dd__callout">
					<span class="dd__callout-val" style="color: {teamTextColor(team_b.color)}">{defensive_b.most_regains_count}</span>
					<span class="dd__callout-name">
						<span class="dd__callout-dot" style="background: {teamColorVar(team_b.color)}"></span>
						{defensive_b.most_regains_player}
					</span>
					<span class="dd__callout-label">{$t.detail.mostPossessionRegains}</span>
				</div>
			{/if}
		</div>
	{/if}
</div>

<style>
	.dd { width: 100%; }

	.dd__header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding-bottom: var(--sp-3);
		margin-bottom: var(--sp-2);
		border-bottom: 2px solid var(--border);
	}
	.dd__tname {
		font-size: var(--fs-label);
		font-weight: 800;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		text-decoration: none;
	}
	.dd__tname:hover { text-decoration: underline; }
	.dd__tname--r { text-align: right; }
	.dd__center {
		font-size: var(--fs-label);
		font-weight: 600;
		color: var(--muted);
		text-transform: uppercase;
		letter-spacing: 0.1em;
	}

	.dd__subheader {
		font-size: var(--fs-meta);
		font-weight: 700;
		text-transform: uppercase;
		letter-spacing: 0.08em;
		color: var(--muted);
		padding: var(--sp-3) 0 var(--sp-1);
		border-bottom: 1px solid var(--border);
		margin-top: var(--sp-3);
	}

	.dd__row {
		display: flex;
		align-items: center;
		padding: var(--sp-2) 0;
		border-bottom: 1px solid var(--border-soft);
	}
	.dd__row:last-of-type { border-bottom: none; }
	.dd__row--sub { padding: var(--sp-1) 0; }
	.dd__val {
		font-size: var(--fs-ui);
		font-weight: 700;
		font-variant-numeric: tabular-nums;
		width: 30%;
	}
	.dd__val--r { text-align: right; }
	.dd__label {
		font-size: var(--fs-ui);
		font-weight: 400;
		color: var(--muted);
		text-align: center;
		flex: 1;
	}

	.dd__callout-row {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: var(--sp-4);
		margin-top: var(--sp-5);
	}
	.dd__callout {
		display: flex;
		flex-direction: column;
		gap: 2px;
		padding: var(--sp-3);
		background: var(--surface);
		border: 1px solid var(--border);
		border-radius: var(--r-md);
		box-shadow: var(--shadow-card);
	}
	.dd__callout-val {
		font-size: var(--fs-stat);
		font-weight: 900;
		line-height: 1;
		font-variant-numeric: tabular-nums;
	}
	.dd__callout-name {
		display: flex;
		align-items: center;
		gap: 6px;
		font-size: var(--fs-ui);
		font-weight: 700;
		color: var(--ink);
	}
	.dd__callout-dot {
		width: 8px;
		height: 8px;
		border-radius: 50%;
		flex-shrink: 0;
	}
	.dd__callout-label {
		font-size: var(--fs-meta);
		font-weight: 600;
		text-transform: uppercase;
		letter-spacing: 0.08em;
		color: var(--muted);
	}
</style>
