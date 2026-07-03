<script lang="ts">
	import type { Team } from '$lib/types/efi';
	import { teamTextColor, teamColorVar } from '$lib/tokens';
	import { t } from '$lib/i18n';

	interface PressureStat {
		total_pressures: number | null;
		direct_pressures: number | null;
		avg_duration_s: number | null;
		forced_turnovers: number | null;
		ball_recovery_time_s: number | null;
		pushing_on_into_pressing: number | null;
		pushing_on: number | null;
		direction_inside: number | null;
		direction_outside: number | null;
		most_direct_player: string | null;
		most_direct_count: number | null;
	}

	let {
		pressure_a,
		pressure_b,
		team_a,
		team_b
	}: { pressure_a: PressureStat | null; pressure_b: PressureStat | null; team_a: Team; team_b: Team } = $props();

	const rows = $derived([
		{ label: $t.detail.totalPressures, key: 'total_pressures', fmt: (v: number | null) => v?.toString() ?? '—' },
		{ label: $t.keyStats.pressures, key: 'direct_pressures', fmt: (v: number | null) => v?.toString() ?? '—' },
		{ label: $t.detail.avgDuration, key: 'avg_duration_s', fmt: (v: number | null) => v != null ? `${Number(v).toFixed(2)}s` : '—' },
		{ label: $t.keyStats.forcedTurnovers, key: 'forced_turnovers', fmt: (v: number | null) => v?.toString() ?? '—' },
		{ label: $t.keyStats.ballRecovery, key: 'ball_recovery_time_s', fmt: (v: number | null) => v != null ? `${Number(v).toFixed(2)}s` : '—' },
		{ label: $t.playerDetail.pushToPressing, key: 'pushing_on_into_pressing', fmt: (v: number | null) => v?.toString() ?? '—' },
		{ label: $t.playerDetail.pushingOn, key: 'pushing_on', fmt: (v: number | null) => v?.toString() ?? '—' },
		{ label: $t.detail.dirInside, key: 'direction_inside', fmt: (v: number | null) => v?.toString() ?? '—' },
		{ label: $t.detail.dirOutside, key: 'direction_outside', fmt: (v: number | null) => v?.toString() ?? '—' },
	]);

	function get(stat: PressureStat | null, key: string): number | null {
		return stat ? (stat as unknown as Record<string, number | null>)[key] ?? null : null;
	}
</script>

<div class="pr">
	<div class="pr__header">
		<a href="/teams/{team_a.id}" class="pr__tname" style="color: {teamTextColor(team_a.color)}">{team_a.name}</a>
		<span class="pr__center">{$t.detail.pressureHeader}</span>
		<a href="/teams/{team_b.id}" class="pr__tname pr__tname--r" style="color: {teamTextColor(team_b.color)}">{team_b.name}</a>
	</div>

	{#each rows as row}
		{@const va = get(pressure_a, row.key)}
		{@const vb = get(pressure_b, row.key)}
		<div class="pr__row">
			<span class="pr__val" style="color: {teamTextColor(team_a.color)}">{row.fmt(va)}</span>
			<span class="pr__label">{row.label}</span>
			<span class="pr__val pr__val--r" style="color: {teamTextColor(team_b.color)}">{row.fmt(vb)}</span>
		</div>
	{/each}

	{#if pressure_a?.most_direct_player || pressure_b?.most_direct_player}
		<div class="pr__callout-row">
			{#if pressure_a?.most_direct_player}
				<div class="pr__callout" style="border-color: {teamColorVar(team_a.color)}">
					<span class="pr__callout-val" style="color: {teamTextColor(team_a.color)}">{pressure_a.most_direct_count}</span>
					<span class="pr__callout-name">{pressure_a.most_direct_player}</span>
					<span class="pr__callout-label">{$t.detail.mostDirectPressures}</span>
				</div>
			{/if}
			{#if pressure_b?.most_direct_player}
				<div class="pr__callout" style="border-color: {teamColorVar(team_b.color)}">
					<span class="pr__callout-val" style="color: {teamTextColor(team_b.color)}">{pressure_b.most_direct_count}</span>
					<span class="pr__callout-name">{pressure_b.most_direct_player}</span>
					<span class="pr__callout-label">{$t.detail.mostDirectPressures}</span>
				</div>
			{/if}
		</div>
	{/if}
</div>

<style>
	.pr { width: 100%; }

	.pr__header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding-bottom: var(--sp-3);
		margin-bottom: var(--sp-2);
		border-bottom: 2px solid var(--border);
	}
	.pr__tname {
		font-size: var(--fs-label);
		font-weight: 800;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		text-decoration: none;
	}
	.pr__tname:hover { text-decoration: underline; }
	.pr__tname--r { text-align: right; }
	.pr__center {
		font-size: var(--fs-label);
		font-weight: 600;
		color: var(--muted);
		text-transform: uppercase;
		letter-spacing: 0.1em;
	}

	.pr__row {
		display: flex;
		align-items: center;
		padding: var(--sp-2) 0;
		border-bottom: 1px solid var(--border-soft);
	}
	.pr__row:last-of-type { border-bottom: none; }
	.pr__val {
		font-size: var(--fs-ui);
		font-weight: 700;
		font-variant-numeric: tabular-nums;
		width: 30%;
	}
	.pr__val--r { text-align: right; }
	.pr__label {
		font-size: var(--fs-ui);
		font-weight: 400;
		color: var(--muted);
		text-align: center;
		flex: 1;
	}

	.pr__callout-row {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: var(--sp-4);
		margin-top: var(--sp-5);
	}
	.pr__callout {
		display: flex;
		flex-direction: column;
		gap: 2px;
		padding: var(--sp-3);
		border-left: 3px solid;
		background: var(--surface);
		border-radius: var(--r-sm);
	}
	.pr__callout-val {
		font-size: var(--fs-stat);
		font-weight: 900;
		line-height: 1;
		font-variant-numeric: tabular-nums;
	}
	.pr__callout-name {
		font-size: var(--fs-ui);
		font-weight: 700;
		color: var(--ink);
	}
	.pr__callout-label {
		font-size: var(--fs-meta);
		font-weight: 600;
		text-transform: uppercase;
		letter-spacing: 0.08em;
		color: var(--muted);
	}
</style>
