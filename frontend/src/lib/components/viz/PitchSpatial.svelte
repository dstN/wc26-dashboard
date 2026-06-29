<script lang="ts">
	import type { TeamSpatialSplit, Team } from '$lib/types/efi';
	import { teamColorVar } from '$lib/tokens';

	let {
		spatial_a,
		spatial_b,
		team_a,
		team_b,
	}: { spatial_a: TeamSpatialSplit | null; spatial_b: TeamSpatialSplit | null; team_a: Team; team_b: Team } = $props();

	// Shared scenario (desktop uses one tab for both pitches)
	let scenario = $state<'defensive' | 'possession'>('defensive');

	// Desktop: independent block toggles per team
	let defBlockA = $state<'high' | 'mid' | 'low'>('mid');
	let defBlockB = $state<'high' | 'mid' | 'low'>('mid');
	let posBlockA = $state<'build_up_low' | 'build_up_mid' | 'final_third_phase'>('build_up_mid');
	let posBlockB = $state<'build_up_low' | 'build_up_mid' | 'final_third_phase'>('build_up_mid');

	// Mobile: single-team view
	let mobileTeam = $state<'a' | 'b'>('a');
	let mobileDefBlock = $state<'high' | 'mid' | 'low'>('mid');
	let mobilePosBlock = $state<'build_up_low' | 'build_up_mid' | 'final_third_phase'>('build_up_mid');

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

	// Desktop blocks
	const blockA = $derived(
		scenario === 'defensive'
			? (spatial_a?.defensive ?? []).find((s) => s.block_type === defBlockA)
			: (spatial_a?.possession ?? []).find((s) => s.block_type === posBlockA)
	);
	const blockB = $derived(
		scenario === 'defensive'
			? (spatial_b?.defensive ?? []).find((s) => s.block_type === defBlockB)
			: (spatial_b?.possession ?? []).find((s) => s.block_type === posBlockB)
	);

	// Mobile block (single team)
	const mobileSpatial = $derived(mobileTeam === 'a' ? spatial_a : spatial_b);
	const mobileCurrentTeam = $derived(mobileTeam === 'a' ? team_a : team_b);
	const mobileBlock = $derived(
		scenario === 'defensive'
			? (mobileSpatial?.defensive ?? []).find((s) => s.block_type === mobileDefBlock)
			: (mobileSpatial?.possession ?? []).find((s) => s.block_type === mobilePosBlock)
	);

	const PITCH = 105;
	const PITCH_W = 68;
	function pct(m: number): string { return `${((m / PITCH) * 100).toFixed(2)}%`; }
	function wpct(m: number | null): string {
		if (m == null) return '0%';
		return `${((100 - (m / PITCH_W) * 100) / 2).toFixed(2)}%`;
	}
</script>

<!-- ── Scenario tab (shared) ─────────────────────────────────────────── -->
<div class="spatial">
	<div class="scenario-tabs" role="group" aria-label="Scenario">
		<button class="scenario-tab" class:active={scenario === 'defensive'} onclick={() => scenario = 'defensive'}>Out of Possession</button>
		<button class="scenario-tab" class:active={scenario === 'possession'} onclick={() => scenario = 'possession'}>In Possession</button>
	</div>

	<!-- ═══════════════════════════════════════════════════════════════════
	     DESKTOP — two pitches side by side
	     Hidden on mobile via CSS
	     ════════════════════════════════════════════════════════════════ -->
	<div class="desktop-pitches">
		{#snippet pitchCol(team: Team, block: typeof blockA, defBlock: 'high'|'mid'|'low', posBlock: 'build_up_low'|'build_up_mid'|'final_third_phase', onDefChange: (k: 'high'|'mid'|'low') => void, onPosChange: (k: 'build_up_low'|'build_up_mid'|'final_third_phase') => void)}
			<div class="pitch-col">
				<div class="pitch-header">
					<span class="team-label" style="color: {teamColorVar(team.color)}">{team.short_code}</span>
					<div class="toggle-group" role="group">
						{#if scenario === 'defensive'}
							{#each defBlocks as b}
								<button class="toggle-item" class:active={defBlock === b.key} onclick={() => onDefChange(b.key)}>{b.label}</button>
							{/each}
						{:else}
							{#each posBlocks as b}
								<button class="toggle-item" class:active={posBlock === b.key} onclick={() => onPosChange(b.key)}>{b.label}</button>
							{/each}
						{/if}
					</div>
				</div>
				<div class="pitch-wrap">
					<div class="pitch" role="img" aria-label="Pitch for {team.short_code}">
						<div class="pitch__center-line"></div>
						<div class="pitch__center-circle"></div>
						<div class="pitch__box pitch__box--top"></div>
						<div class="pitch__box pitch__box--bot"></div>
						{#if block}
							<div class="pitch__block" style="bottom:{pct(block.defensive_line_height)};height:{pct(block.team_length)};left:{wpct(block.width_m)};right:{wpct(block.width_m)};background:{teamColorVar(team.color)};"></div>
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
						<div class="kpi"><span class="kpi__label">{scenario === 'defensive' ? 'Def. Line' : 'Distance'}</span><span class="kpi__val" style="color:{teamColorVar(team.color)}">{block.defensive_line_height}m</span></div>
						<div class="kpi"><span class="kpi__label">Length</span><span class="kpi__val" style="color:{teamColorVar(team.color)}">{block.team_length}m</span></div>
						{#if block.width_m != null}<div class="kpi"><span class="kpi__label">Width</span><span class="kpi__val" style="color:{teamColorVar(team.color)}">{block.width_m}m</span></div>{/if}
					</div>
				{/if}
			</div>
		{/snippet}

		{@render pitchCol(team_a, blockA, defBlockA, posBlockA, (k) => defBlockA = k, (k) => posBlockA = k)}
		{#if hasSpatialB}
			{@render pitchCol(team_b, blockB, defBlockB, posBlockB, (k) => defBlockB = k, (k) => posBlockB = k)}
		{/if}
	</div>

	<!-- ═══════════════════════════════════════════════════════════════════
	     MOBILE — one pitch at a time with team + block pickers
	     Hidden on desktop via CSS
	     ════════════════════════════════════════════════════════════════ -->
	<div class="mobile-pitches">
		<!-- Team + block row -->
		<div class="mobile-controls">
			{#if hasSpatialB}
				<div class="pill-group" role="group" aria-label="Nation">
					<button class="pill" class:active={mobileTeam === 'a'} style="--tc:{teamColorVar(team_a.color)}" onclick={() => mobileTeam = 'a'}>{team_a.short_code}</button>
					<button class="pill" class:active={mobileTeam === 'b'} style="--tc:{teamColorVar(team_b.color)}" onclick={() => mobileTeam = 'b'}>{team_b.short_code}</button>
				</div>
			{:else}
				<span class="team-label" style="color:{teamColorVar(team_a.color)}">{team_a.short_code}</span>
			{/if}
			<div class="pill-group" role="group" aria-label="Block">
				{#if scenario === 'defensive'}
					{#each defBlocks as b}
						<button class="pill pill--sm" class:active={mobileDefBlock === b.key} onclick={() => mobileDefBlock = b.key}>{b.label}</button>
					{/each}
				{:else}
					{#each posBlocks as b}
						<button class="pill pill--sm" class:active={mobilePosBlock === b.key} onclick={() => mobilePosBlock = b.key}>{b.label}</button>
					{/each}
				{/if}
			</div>
		</div>

		<!-- Single pitch -->
		<div class="pitch-wrap">
			<div class="pitch" role="img" aria-label="Pitch for {mobileCurrentTeam.short_code}">
				<div class="pitch__center-line"></div>
				<div class="pitch__center-circle"></div>
				<div class="pitch__box pitch__box--top"></div>
				<div class="pitch__box pitch__box--bot"></div>
				{#if mobileBlock}
					<div class="pitch__block" style="bottom:{pct(mobileBlock.defensive_line_height)};height:{pct(mobileBlock.team_length)};left:{wpct(mobileBlock.width_m)};right:{wpct(mobileBlock.width_m)};background:{teamColorVar(mobileCurrentTeam.color)};"></div>
				{/if}
			</div>
			{#if mobileBlock}
				{#if mobileBlock.width_m != null}
					<div class="ann ann--width" style="left:{wpct(mobileBlock.width_m)};right:{wpct(mobileBlock.width_m)};bottom:calc({pct(mobileBlock.defensive_line_height + mobileBlock.team_length)} + 4px);">
						<span class="ann__line"></span><span class="ann__val">{mobileBlock.width_m}m</span><span class="ann__line"></span>
					</div>
				{/if}
				<div class="ann ann--height" style="bottom:{pct(mobileBlock.defensive_line_height)};height:{pct(mobileBlock.team_length)};right:calc({wpct(mobileBlock.width_m)} - 20px);">
					<span class="ann__val ann__val--vert">{mobileBlock.team_length}m</span>
				</div>
				<div class="ann ann--dist" style="bottom:calc({pct(mobileBlock.defensive_line_height)} - 18px);left:{wpct(mobileBlock.width_m)};right:{wpct(mobileBlock.width_m)};">
					<span class="ann__val ann__val--dist">{mobileBlock.defensive_line_height}m</span>
				</div>
			{/if}
		</div>
		{#if mobileBlock}
			<div class="kpis">
				<div class="kpi"><span class="kpi__label">{scenario === 'defensive' ? 'Def. Line' : 'Distance'}</span><span class="kpi__val" style="color:{teamColorVar(mobileCurrentTeam.color)}">{mobileBlock.defensive_line_height}m</span></div>
				<div class="kpi"><span class="kpi__label">Length</span><span class="kpi__val" style="color:{teamColorVar(mobileCurrentTeam.color)}">{mobileBlock.team_length}m</span></div>
				{#if mobileBlock.width_m != null}<div class="kpi"><span class="kpi__label">Width</span><span class="kpi__val" style="color:{teamColorVar(mobileCurrentTeam.color)}">{mobileBlock.width_m}m</span></div>{/if}
			</div>
		{/if}
	</div>
</div>

<style>
	.spatial { display: flex; flex-direction: column; gap: var(--sp-4); }

	/* ── Scenario tabs ── */
	.scenario-tabs { display: flex; gap: 2px; background: var(--border); border-radius: var(--r-pill); padding: 2px; align-self: flex-start; }
	.scenario-tab {
		padding: 4px var(--sp-3);
		font-size: var(--fs-meta); font-weight: 600; font-family: inherit;
		border-radius: var(--r-pill); cursor: pointer; color: var(--muted);
		background: transparent; border: none; transition: background 0.15s, color 0.15s; white-space: nowrap;
	}
	.scenario-tab.active { background: var(--ink); color: var(--bg); }

	/* ── Desktop two-pitch layout ── */
	.desktop-pitches { display: flex; gap: var(--sp-8); flex-wrap: wrap; }
	.mobile-pitches { display: none; }

	@media (max-width: 600px) {
		.desktop-pitches { display: none; }
		.mobile-pitches { display: flex; flex-direction: column; gap: var(--sp-4); }
	}

	/* ── Desktop pitch column ── */
	.pitch-col { display: flex; flex-direction: column; gap: var(--sp-3); flex: 1; min-width: 140px; max-width: 320px; }
	.pitch-header { display: flex; align-items: center; justify-content: space-between; gap: var(--sp-2); flex-wrap: wrap; }
	.team-label { font-size: var(--fs-label); font-weight: 800; text-transform: uppercase; letter-spacing: 0.06em; }
	.toggle-group { display: flex; gap: 2px; background: var(--border); border-radius: var(--r-pill); padding: 2px; }
	.toggle-item {
		padding: 3px var(--sp-2); font-size: var(--fs-meta); font-weight: 600; font-family: inherit;
		border-radius: var(--r-pill); cursor: pointer; color: var(--muted); background: transparent; border: none;
		min-height: 24px; transition: background 0.15s, color 0.15s; white-space: nowrap;
	}
	.toggle-item.active { background: var(--c-yellow); color: var(--c-forest); }

	/* ── Mobile controls ── */
	.mobile-controls { display: flex; align-items: center; justify-content: space-between; gap: var(--sp-3); flex-wrap: wrap; }
	.pill-group { display: flex; gap: 2px; background: var(--border); border-radius: var(--r-pill); padding: 2px; }
	.pill {
		padding: 5px var(--sp-4); font-size: var(--fs-meta); font-weight: 600; font-family: inherit;
		border-radius: var(--r-pill); cursor: pointer; color: var(--muted); background: transparent; border: none;
		transition: background 0.15s, color 0.15s; white-space: nowrap; line-height: 1;
	}
	.pill.active { background: var(--tc, var(--ink)); color: #fff; }
	.pill--sm { padding: 4px var(--sp-3); }

	/* ── Shared pitch ── */
	.pitch-wrap { position: relative; }
	.pitch {
		position: relative; width: 100%; aspect-ratio: 68 / 105;
		background: var(--pitch); border: 2px solid var(--pitch-line); border-radius: var(--r-sm); overflow: hidden;
	}
	.pitch__center-line { position: absolute; left: 0; right: 0; top: 50%; height: 2px; background: var(--pitch-line); transform: translateY(-50%); }
	.pitch__center-circle { position: absolute; top: 50%; left: 50%; transform: translate(-50%,-50%); width: 40%; aspect-ratio: 1; border: 2px solid var(--pitch-line); border-radius: 50%; }
	.pitch__box { position: absolute; left: 18%; right: 18%; height: 17%; border: 2px solid var(--pitch-line); background: transparent; }
	.pitch__box--top { top: 0; border-top: none; border-radius: 0 0 6px 6px; }
	.pitch__box--bot { bottom: 0; border-bottom: none; border-radius: 6px 6px 0 0; }
	.pitch__block { position: absolute; opacity: 0.45; z-index: 1; }

	/* ── Annotations ── */
	.ann { position: absolute; pointer-events: none; z-index: 3; }
	.ann--width { display: flex; align-items: center; gap: 3px; height: 14px; }
	.ann__line { flex: 1; height: 1px; background: var(--muted); opacity: 0.7; }
	.ann__val { font-size: 10px; font-weight: 700; font-variant-numeric: tabular-nums; white-space: nowrap; background: var(--surface); padding: 1px 3px; border-radius: 3px; color: var(--ink); line-height: 1; }
	.ann--height { display: flex; align-items: center; justify-content: center; width: 20px; }
	.ann__val--vert { writing-mode: vertical-rl; text-orientation: mixed; transform: rotate(180deg); }
	.ann--dist { display: flex; justify-content: flex-end; align-items: flex-start; height: 16px; }
	.ann__val--dist { opacity: 0.7; }

	/* ── KPIs ── */
	.kpis { display: flex; gap: var(--sp-6); flex-wrap: wrap; }
	.kpi { display: flex; flex-direction: column; gap: 2px; }
	.kpi__label { font-size: var(--fs-label); font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; color: var(--muted); }
	.kpi__val { font-size: var(--fs-h2); font-weight: 800; font-variant-numeric: tabular-nums; line-height: 1.1; }
</style>
