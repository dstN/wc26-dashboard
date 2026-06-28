<script lang="ts">
	import type { Team } from '$lib/types/efi';
	import { teamTextColor, teamColorVar } from '$lib/tokens';

	interface GkStat {
		gk_name?: string | null;
		total_involvements?: number | null;
		total_distributions?: number | null;
		kick_from_feet?: number | null;
		kick_from_hands?: number | null;
		throw_distribution?: number | null;
		gk_line_breaks?: number | null;
		total_attempts_faced?: number | null;
		save_pct?: number | null;
		total_goal_interventions?: number | null;
		save_and_retain?: number | null;
		deflect_and_retain?: number | null;
		save_and_deflect?: number | null;
		save_attempt?: number | null;
		no_save_attempt?: number | null;
		total_aerial_interventions?: number | null;
		punches_complete?: number | null;
		punches_incomplete?: number | null;
		claims_complete?: number | null;
		claims_incomplete?: number | null;
		tipped_palmed_complete?: number | null;
		tipped_palmed_incomplete?: number | null;
		crosses_faced?: number | null;
		crosses_faced_inswing?: number | null;
		crosses_faced_outswing?: number | null;
		crosses_faced_driven?: number | null;
		crosses_faced_lofted?: number | null;
		crosses_faced_cutback?: number | null;
		crosses_faced_push?: number | null;
	}

	let {
		gk_a,
		gk_b,
		team_a,
		team_b
	}: { gk_a: GkStat | null; gk_b: GkStat | null; team_a: Team; team_b: Team } = $props();

	function get(stat: GkStat | null, key: string): number | null {
		return stat ? (stat as unknown as Record<string, number | null>)[key] ?? null : null;
	}

	function str(stat: GkStat | null, key: string): string | null {
		return stat ? (stat as unknown as Record<string, string | null>)[key] ?? null : null;
	}

	function fmt(v: number | null): string {
		return v != null ? String(v) : '—';
	}
	function fmtPct(v: number | null): string {
		return v != null ? `${v}%` : '—';
	}
</script>

<div class="gk">
	<div class="gk__header">
		<a href="/teams/{team_a.id}" class="gk__tname" style="color: {teamTextColor(team_a.color)}">{team_a.name}</a>
		<span class="gk__center">Goalkeepers</span>
		<a href="/teams/{team_b.id}" class="gk__tname gk__tname--r" style="color: {teamTextColor(team_b.color)}">{team_b.name}</a>
	</div>

	<!-- GK names -->
	{#if gk_a?.gk_name || gk_b?.gk_name}
		<div class="gk__row gk__row--name">
			<span class="gk__name" style="color: {teamTextColor(team_a.color)}">{str(gk_a, 'gk_name') ?? '—'}</span>
			<span class="gk__label">Goalkeeper</span>
			<span class="gk__name gk__name--r" style="color: {teamTextColor(team_b.color)}">{str(gk_b, 'gk_name') ?? '—'}</span>
		</div>
	{/if}

	<!-- Involvements & Distributions -->
	<div class="gk__subheader">Activity</div>
	{#each [
		{ label: 'Total Involvements', key: 'total_involvements', format: fmt },
		{ label: 'Total Distributions', key: 'total_distributions', format: fmt },
		{ label: 'Kick from Feet', key: 'kick_from_feet', format: fmt },
		{ label: 'Kick from Hands', key: 'kick_from_hands', format: fmt },
		{ label: 'Throw Distribution', key: 'throw_distribution', format: fmt },
		{ label: 'GK Line Breaks', key: 'gk_line_breaks', format: fmt },
	] as row}
		{@const va = get(gk_a, row.key)}
		{@const vb = get(gk_b, row.key)}
		{#if va != null || vb != null}
			<div class="gk__row">
				<span class="gk__val" style="color: {teamTextColor(team_a.color)}">{row.format(va)}</span>
				<span class="gk__label">{row.label}</span>
				<span class="gk__val gk__val--r" style="color: {teamTextColor(team_b.color)}">{row.format(vb)}</span>
			</div>
		{/if}
	{/each}

	<!-- Attempts Faced -->
	<div class="gk__subheader">Attempts Faced</div>
	{#each [
		{ label: 'Attempts Faced', key: 'total_attempts_faced', format: fmt },
		{ label: 'Save %', key: 'save_pct', format: fmtPct },
	] as row}
		{@const va = get(gk_a, row.key)}
		{@const vb = get(gk_b, row.key)}
		{#if va != null || vb != null}
			<div class="gk__row">
				<span class="gk__val" style="color: {teamTextColor(team_a.color)}">{row.format(va)}</span>
				<span class="gk__label">{row.label}</span>
				<span class="gk__val gk__val--r" style="color: {teamTextColor(team_b.color)}">{row.format(vb)}</span>
			</div>
		{/if}
	{/each}

	<!-- Goal Interventions -->
	<div class="gk__subheader">Goal Interventions</div>
	{#each [
		{ label: 'Total Interventions', key: 'total_goal_interventions', format: fmt },
		{ label: 'Save & Retain', key: 'save_and_retain', format: fmt },
		{ label: 'Deflect & Retain', key: 'deflect_and_retain', format: fmt },
		{ label: 'Save & Deflect', key: 'save_and_deflect', format: fmt },
		{ label: 'Save Attempt', key: 'save_attempt', format: fmt },
		{ label: 'No Save Attempt', key: 'no_save_attempt', format: fmt },
	] as row}
		{@const va = get(gk_a, row.key)}
		{@const vb = get(gk_b, row.key)}
		{#if va != null || vb != null}
			<div class="gk__row">
				<span class="gk__val" style="color: {teamTextColor(team_a.color)}">{row.format(va)}</span>
				<span class="gk__label">{row.label}</span>
				<span class="gk__val gk__val--r" style="color: {teamTextColor(team_b.color)}">{row.format(vb)}</span>
			</div>
		{/if}
	{/each}

	<!-- Aerial Interventions -->
	<div class="gk__subheader">Aerial Interventions</div>
	{#each [
		{ label: 'Total Aerial', key: 'total_aerial_interventions', format: fmt },
		{ label: 'Punches — Complete', key: 'punches_complete', format: fmt },
		{ label: 'Punches — Incomplete', key: 'punches_incomplete', format: fmt },
		{ label: 'Claims — Complete', key: 'claims_complete', format: fmt },
		{ label: 'Claims — Incomplete', key: 'claims_incomplete', format: fmt },
		{ label: 'Tipped/Palmed — Complete', key: 'tipped_palmed_complete', format: fmt },
		{ label: 'Tipped/Palmed — Incomplete', key: 'tipped_palmed_incomplete', format: fmt },
	] as row}
		{@const va = get(gk_a, row.key)}
		{@const vb = get(gk_b, row.key)}
		{#if va != null || vb != null}
			<div class="gk__row">
				<span class="gk__val" style="color: {teamTextColor(team_a.color)}">{row.format(va)}</span>
				<span class="gk__label">{row.label}</span>
				<span class="gk__val gk__val--r" style="color: {teamTextColor(team_b.color)}">{row.format(vb)}</span>
			</div>
		{/if}
	{/each}

	<!-- Crosses Faced -->
	<div class="gk__subheader">Crosses Faced</div>
	{#each [
		{ label: 'Total Crosses Faced', key: 'crosses_faced', format: fmt },
		{ label: 'Inswing', key: 'crosses_faced_inswing', format: fmt },
		{ label: 'Outswing', key: 'crosses_faced_outswing', format: fmt },
		{ label: 'Driven', key: 'crosses_faced_driven', format: fmt },
		{ label: 'Lofted', key: 'crosses_faced_lofted', format: fmt },
		{ label: 'Cutback', key: 'crosses_faced_cutback', format: fmt },
		{ label: 'Push Cross', key: 'crosses_faced_push', format: fmt },
	] as row}
		{@const va = get(gk_a, row.key)}
		{@const vb = get(gk_b, row.key)}
		{#if va != null || vb != null}
			<div class="gk__row">
				<span class="gk__val" style="color: {teamTextColor(team_a.color)}">{row.format(va)}</span>
				<span class="gk__label">{row.label}</span>
				<span class="gk__val gk__val--r" style="color: {teamTextColor(team_b.color)}">{row.format(vb)}</span>
			</div>
		{/if}
	{/each}
</div>

<style>
	.gk { width: 100%; }

	.gk__header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding-bottom: var(--sp-3);
		margin-bottom: var(--sp-2);
		border-bottom: 2px solid var(--border);
	}
	.gk__tname {
		font-size: var(--fs-label);
		font-weight: 800;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		text-decoration: none;
	}
	.gk__tname:hover { text-decoration: underline; }
	.gk__tname--r { text-align: right; }
	.gk__center {
		font-size: var(--fs-label);
		font-weight: 600;
		color: var(--muted);
		text-transform: uppercase;
		letter-spacing: 0.1em;
	}

	.gk__subheader {
		font-size: var(--fs-meta);
		font-weight: 700;
		text-transform: uppercase;
		letter-spacing: 0.08em;
		color: var(--muted);
		padding: var(--sp-3) 0 var(--sp-1);
		border-bottom: 1px solid var(--border);
		margin-top: var(--sp-3);
	}

	.gk__row {
		display: flex;
		align-items: center;
		padding: var(--sp-2) 0;
		border-bottom: 1px solid var(--border-soft);
	}
	.gk__row:last-of-type { border-bottom: none; }
	.gk__row--name { padding: var(--sp-3) 0; }

	.gk__val {
		font-size: var(--fs-ui);
		font-weight: 700;
		font-variant-numeric: tabular-nums;
		width: 30%;
	}
	.gk__val--r { text-align: right; }

	.gk__name {
		font-size: var(--fs-ui);
		font-weight: 700;
		width: 30%;
	}
	.gk__name--r { text-align: right; }

	.gk__label {
		font-size: var(--fs-ui);
		font-weight: 400;
		color: var(--muted);
		text-align: center;
		flex: 1;
	}
</style>
