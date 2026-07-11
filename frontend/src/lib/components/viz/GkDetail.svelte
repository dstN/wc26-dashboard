<script lang="ts">
	import type { Team } from '$lib/types/efi';
	import { teamTextColor } from '$lib/tokens';
	import { t } from '$lib/i18n';

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

	const activityRows = $derived([
		{ label: $t.detail.gkTotalInvolvements, key: 'total_involvements', format: fmt },
		{ label: $t.detail.gkTotalDistributions, key: 'total_distributions', format: fmt },
		{ label: $t.detail.gkKickFromFeet, key: 'kick_from_feet', format: fmt },
		{ label: $t.detail.gkKickFromHands, key: 'kick_from_hands', format: fmt },
		{ label: $t.detail.gkThrowDistribution, key: 'throw_distribution', format: fmt },
		{ label: $t.detail.gkLineBreaks, key: 'gk_line_breaks', format: fmt },
	]);

	const attemptRows = $derived([
		{ label: $t.keyStats.attemptsFaced, key: 'total_attempts_faced', format: fmt },
		{ label: $t.keyStats.savePct, key: 'save_pct', format: fmtPct },
	]);

	const interventionRows = $derived([
		{ label: $t.detail.gkTotalInterventions, key: 'total_goal_interventions', format: fmt },
		{ label: $t.detail.gkSaveRetain, key: 'save_and_retain', format: fmt },
		{ label: $t.detail.gkDeflectRetain, key: 'deflect_and_retain', format: fmt },
		{ label: $t.detail.gkSaveDeflect, key: 'save_and_deflect', format: fmt },
		{ label: $t.detail.gkSaveAttempt, key: 'save_attempt', format: fmt },
		{ label: $t.detail.gkNoSaveAttempt, key: 'no_save_attempt', format: fmt },
	]);

	const aerialRows = $derived([
		{ label: $t.detail.gkTotalAerial, key: 'total_aerial_interventions', format: fmt },
		{ label: $t.detail.gkPunchesComplete, key: 'punches_complete', format: fmt },
		{ label: $t.detail.gkPunchesIncomplete, key: 'punches_incomplete', format: fmt },
		{ label: $t.detail.gkClaimsComplete, key: 'claims_complete', format: fmt },
		{ label: $t.detail.gkClaimsIncomplete, key: 'claims_incomplete', format: fmt },
		{ label: $t.detail.gkTippedComplete, key: 'tipped_palmed_complete', format: fmt },
		{ label: $t.detail.gkTippedIncomplete, key: 'tipped_palmed_incomplete', format: fmt },
	]);

	const crossesRows = $derived([
		{ label: $t.detail.gkTotalCrossed, key: 'crosses_faced', format: fmt },
		{ label: $t.playerDetail.inswing, key: 'crosses_faced_inswing', format: fmt },
		{ label: $t.playerDetail.outswing, key: 'crosses_faced_outswing', format: fmt },
		{ label: $t.playerDetail.driven, key: 'crosses_faced_driven', format: fmt },
		{ label: $t.playerDetail.lofted, key: 'crosses_faced_lofted', format: fmt },
		{ label: $t.playerDetail.cutback, key: 'crosses_faced_cutback', format: fmt },
		{ label: $t.playerDetail.pushCross, key: 'crosses_faced_push', format: fmt },
	]);
</script>

<div class="gk" role="table" aria-label="{team_a.name} vs {team_b.name}">
	<div class="gk__header" role="row">
		<a href="/teams/{team_a.id}" class="gk__tname" role="columnheader" style="color: {teamTextColor(team_a.color)}">{team_a.name}</a>
		<span class="gk__center" role="columnheader">{$t.detail.goalkeepers}</span>
		<a href="/teams/{team_b.id}" class="gk__tname gk__tname--r" role="columnheader" style="color: {teamTextColor(team_b.color)}">{team_b.name}</a>
	</div>

	<!-- GK names -->
	{#if gk_a?.gk_name || gk_b?.gk_name}
		<div role="row" class="gk__row gk__row--name">
			<span role="cell" class="gk__name" style="color: {teamTextColor(team_a.color)}">{str(gk_a, 'gk_name') ?? '—'}</span>
			<span role="rowheader" class="gk__label">{$t.players.posGK}</span>
			<span role="cell" class="gk__name gk__name--r" style="color: {teamTextColor(team_b.color)}">{str(gk_b, 'gk_name') ?? '—'}</span>
		</div>
	{/if}

	<!-- Involvements & Distributions -->
	<div role="presentation" class="gk__subheader">{$t.detail.gkActivity}</div>
	{#each activityRows as row}
		{@const va = get(gk_a, row.key)}
		{@const vb = get(gk_b, row.key)}
		{#if va != null || vb != null}
			<div role="row" class="gk__row">
				<span role="cell" class="gk__val" style="color: {teamTextColor(team_a.color)}">{row.format(va)}</span>
				<span role="rowheader" class="gk__label">{row.label}</span>
				<span role="cell" class="gk__val gk__val--r" style="color: {teamTextColor(team_b.color)}">{row.format(vb)}</span>
			</div>
		{/if}
	{/each}

	<!-- Attempts Faced -->
	<div role="presentation" class="gk__subheader">{$t.detail.gkShotStopping}</div>
	{#each attemptRows as row}
		{@const va = get(gk_a, row.key)}
		{@const vb = get(gk_b, row.key)}
		{#if va != null || vb != null}
			<div role="row" class="gk__row">
				<span role="cell" class="gk__val" style="color: {teamTextColor(team_a.color)}">{row.format(va)}</span>
				<span role="rowheader" class="gk__label">{row.label}</span>
				<span role="cell" class="gk__val gk__val--r" style="color: {teamTextColor(team_b.color)}">{row.format(vb)}</span>
			</div>
		{/if}
	{/each}

	<!-- Goal Interventions -->
	<div role="presentation" class="gk__subheader">{$t.detail.gkShotStopping}</div>
	{#each interventionRows as row}
		{@const va = get(gk_a, row.key)}
		{@const vb = get(gk_b, row.key)}
		{#if va != null || vb != null}
			<div role="row" class="gk__row">
				<span role="cell" class="gk__val" style="color: {teamTextColor(team_a.color)}">{row.format(va)}</span>
				<span role="rowheader" class="gk__label">{row.label}</span>
				<span role="cell" class="gk__val gk__val--r" style="color: {teamTextColor(team_b.color)}">{row.format(vb)}</span>
			</div>
		{/if}
	{/each}

	<!-- Aerial Interventions -->
	<div role="presentation" class="gk__subheader">{$t.detail.gkAerialActions}</div>
	{#each aerialRows as row}
		{@const va = get(gk_a, row.key)}
		{@const vb = get(gk_b, row.key)}
		{#if va != null || vb != null}
			<div role="row" class="gk__row">
				<span role="cell" class="gk__val" style="color: {teamTextColor(team_a.color)}">{row.format(va)}</span>
				<span role="rowheader" class="gk__label">{row.label}</span>
				<span role="cell" class="gk__val gk__val--r" style="color: {teamTextColor(team_b.color)}">{row.format(vb)}</span>
			</div>
		{/if}
	{/each}

	<!-- Crosses Faced -->
	<div role="presentation" class="gk__subheader">{$t.detail.gkCrossesSection}</div>
	{#each crossesRows as row}
		{@const va = get(gk_a, row.key)}
		{@const vb = get(gk_b, row.key)}
		{#if va != null || vb != null}
			<div role="row" class="gk__row">
				<span role="cell" class="gk__val" style="color: {teamTextColor(team_a.color)}">{row.format(va)}</span>
				<span role="rowheader" class="gk__label">{row.label}</span>
				<span role="cell" class="gk__val gk__val--r" style="color: {teamTextColor(team_b.color)}">{row.format(vb)}</span>
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
