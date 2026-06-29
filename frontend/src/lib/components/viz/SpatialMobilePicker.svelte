<script lang="ts">
	import type { TeamSpatialSplit, Team } from '$lib/types/efi';
	import { teamColorVar } from '$lib/tokens';

	let {
		spatial_a,
		spatial_b,
		team_a,
		team_b,
	}: { spatial_a: TeamSpatialSplit | null; spatial_b: TeamSpatialSplit | null; team_a: Team; team_b: Team } = $props();

	let scenario = $state<'defensive' | 'possession'>('defensive');
	let selectedTeam = $state<'a' | 'b'>('a');
	let defBlock = $state<'high' | 'mid' | 'low'>('mid');
	let posBlock = $state<'build_up_low' | 'build_up_mid' | 'final_third_phase'>('build_up_mid');

	const defBlocks: Array<{ key: 'high' | 'mid' | 'low'; label: string }> = [
		{ key: 'high', label: 'High' },
		{ key: 'mid', label: 'Mid' },
		{ key: 'low', label: 'Low' },
	];
	const posBlocks: Array<{ key: 'build_up_low' | 'build_up_mid' | 'final_third_phase'; label: string }> = [
		{ key: 'build_up_low', label: 'Build-Up Low' },
		{ key: 'build_up_mid', label: 'Build-Up Mid' },
		{ key: 'final_third_phase', label: 'Final Third' },
	];

	const hasSpatialB = $derived(
		(spatial_b?.defensive?.length ?? 0) > 0 || (spatial_b?.possession?.length ?? 0) > 0
	);
	const currentSpatial = $derived(selectedTeam === 'a' ? spatial_a : spatial_b);
	const currentTeam = $derived(selectedTeam === 'a' ? team_a : team_b);
	const block = $derived(
		scenario === 'defensive'
			? (currentSpatial?.defensive ?? []).find((s) => s.block_type === defBlock)
			: (currentSpatial?.possession ?? []).find((s) => s.block_type === posBlock)
	);

	const PITCH = 105;
	const PITCH_W = 68;
	function pct(m: number): string { return `${((m / PITCH) * 100).toFixed(2)}%`; }
	function wpct(m: number | null): string {
		if (m == null) return '0%';
		return `${((100 - (m / PITCH_W) * 100) / 2).toFixed(2)}%`;
	}
</script>

<div class="smp">
	<!-- Row 1: scenario -->
	<div class="pill-group" role="group" aria-label="Scenario">
		<button class="pill pill--scenario" class:active={scenario === 'defensive'} onclick={() => scenario = 'defensive'}>Out of Possession</button>
		<button class="pill pill--scenario" class:active={scenario === 'possession'} onclick={() => scenario = 'possession'}>In Possession</button>
	</div>

	<!-- Row 2: team + block type -->
	<div class="controls-row">
		{#if hasSpatialB}
			<div class="pill-group" role="group" aria-label="Nation">
				<button class="pill pill--team" class:active={selectedTeam === 'a'} style="--tc:{teamColorVar(team_a.color)}" onclick={() => selectedTeam = 'a'}>{team_a.short_code}</button>
				<button class="pill pill--team" class:active={selectedTeam === 'b'} style="--tc:{teamColorVar(team_b.color)}" onclick={() => selectedTeam = 'b'}>{team_b.short_code}</button>
			</div>
		{/if}
		<div class="pill-group" role="group" aria-label="Block">
			{#if scenario === 'defensive'}
				{#each defBlocks as b}
					<button class="pill pill--sm pill--block" class:active={defBlock === b.key} onclick={() => defBlock = b.key}>{b.label}</button>
				{/each}
			{:else}
				{#each posBlocks as b}
					<button class="pill pill--sm pill--block" class:active={posBlock === b.key} onclick={() => posBlock = b.key}>{b.label}</button>
				{/each}
			{/if}
		</div>
	</div>

	<!-- Pitch -->
	<div class="pitch-wrap">
		<div class="pitch" role="img" aria-label="Pitch for {currentTeam.short_code}">
			<div class="pitch__center-line"></div>
			<div class="pitch__center-circle"></div>
			<div class="pitch__box pitch__box--top"></div>
			<div class="pitch__box pitch__box--bot"></div>
			{#if block}
				<div class="pitch__block" style="bottom:{pct(block.defensive_line_height)};height:{pct(block.team_length)};left:{wpct(block.width_m)};right:{wpct(block.width_m)};background:{teamColorVar(currentTeam.color)};"></div>
			{/if}
		</div>
		{#if block}
			{#if block.width_m != null}
				<div class="ann ann--width" style="left:{wpct(block.width_m)};right:{wpct(block.width_m)};bottom:calc({pct(block.defensive_line_height + block.team_length)} + 4px);">
					<span class="ann__line"></span><span class="ann__val">{block.width_m}m</span><span class="ann__line"></span>
				</div>
			{/if}
			<div class="ann ann--height" style="bottom:{pct(block.defensive_line_height)};height:{pct(block.team_length)};right:calc({wpct(block.width_m)} - 20px);">
				<span class="ann__val ann__val--vert">{block.team_length}m</span>
			</div>
			<div class="ann ann--dist" style="bottom:calc({pct(block.defensive_line_height)} - 18px);left:{wpct(block.width_m)};right:{wpct(block.width_m)};">
				<span class="ann__val ann__val--dist">{block.defensive_line_height}m</span>
			</div>
		{/if}
	</div>

	{#if block}
		<div class="kpis">
			<div class="kpi"><span class="kpi__label">{scenario === 'defensive' ? 'Def. Line' : 'Distance'}</span><span class="kpi__val" style="color:{teamColorVar(currentTeam.color)}">{block.defensive_line_height}m</span></div>
			<div class="kpi"><span class="kpi__label">Length</span><span class="kpi__val" style="color:{teamColorVar(currentTeam.color)}">{block.team_length}m</span></div>
			{#if block.width_m != null}<div class="kpi"><span class="kpi__label">Width</span><span class="kpi__val" style="color:{teamColorVar(currentTeam.color)}">{block.width_m}m</span></div>{/if}
		</div>
	{/if}
</div>

<style>
	.smp { display: flex; flex-direction: column; gap: var(--sp-4); }
	.controls-row { display: flex; align-items: center; justify-content: space-between; gap: var(--sp-3); flex-wrap: wrap; }

	.pill-group { display: flex; gap: 2px; background: var(--border); border-radius: var(--r-pill); padding: 2px; }
	.pill {
		padding: 5px var(--sp-4); font-size: var(--fs-meta); font-weight: 600; font-family: inherit;
		border-radius: var(--r-pill); cursor: pointer; color: var(--muted); background: transparent; border: none;
		transition: background 0.15s, color 0.15s; white-space: nowrap; line-height: 1;
	}
	/* Scenario pills — same as desktop scenario-tab */
	.pill--scenario.active { background: var(--ink); color: var(--bg); }
	/* Team nation pills — team color background */
	.pill--team.active { background: var(--tc, var(--ink)); color: #fff; }
	/* Block type pills — same yellow/forest as desktop toggle-item */
	.pill--block.active { background: var(--c-yellow); color: var(--c-forest); }
	.pill--sm { padding: 4px var(--sp-3); }

	.pitch-wrap { position: relative; }
	.pitch { position: relative; width: 100%; aspect-ratio: 68 / 105; background: var(--pitch); border: 2px solid var(--pitch-line); border-radius: var(--r-sm); overflow: hidden; }
	.pitch__center-line { position: absolute; left: 0; right: 0; top: 50%; height: 2px; background: var(--pitch-line); transform: translateY(-50%); }
	.pitch__center-circle { position: absolute; top: 50%; left: 50%; transform: translate(-50%,-50%); width: 40%; aspect-ratio: 1; border: 2px solid var(--pitch-line); border-radius: 50%; }
	.pitch__box { position: absolute; left: 18%; right: 18%; height: 17%; border: 2px solid var(--pitch-line); background: transparent; }
	.pitch__box--top { top: 0; border-top: none; border-radius: 0 0 6px 6px; }
	.pitch__box--bot { bottom: 0; border-bottom: none; border-radius: 6px 6px 0 0; }
	.pitch__block { position: absolute; opacity: 0.45; z-index: 1; }

	.ann { position: absolute; pointer-events: none; z-index: 3; }
	.ann--width { display: flex; align-items: center; gap: 3px; height: 14px; }
	.ann__line { flex: 1; height: 1px; background: var(--muted); opacity: 0.7; }
	.ann__val { font-size: 10px; font-weight: 700; font-variant-numeric: tabular-nums; white-space: nowrap; background: var(--surface); padding: 1px 3px; border-radius: 3px; color: var(--ink); line-height: 1; }
	.ann--height { display: flex; align-items: center; justify-content: center; width: 20px; }
	.ann__val--vert { writing-mode: vertical-rl; text-orientation: mixed; transform: rotate(180deg); }
	.ann--dist { display: flex; justify-content: flex-end; align-items: flex-start; height: 16px; }
	.ann__val--dist { opacity: 0.7; }

	.kpis { display: flex; gap: var(--sp-6); flex-wrap: wrap; }
	.kpi { display: flex; flex-direction: column; gap: 2px; }
	.kpi__label { font-size: var(--fs-label); font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; color: var(--muted); }
	.kpi__val { font-size: var(--fs-h2); font-weight: 800; font-variant-numeric: tabular-nums; line-height: 1.1; }
</style>
