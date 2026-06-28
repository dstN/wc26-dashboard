<script lang="ts">
	import type { TeamSpatial, TeamSpatialSplit, Team } from '$lib/types/efi';
	import { teamColorVar } from '$lib/tokens';

	let {
		spatial_a,
		spatial_b,
		team_a,
		team_b,
		compact = false,
		initialScenario = 'defensive'
	}: { spatial_a: TeamSpatialSplit | null; spatial_b: TeamSpatialSplit | null; team_a: Team; team_b: Team; compact?: boolean; initialScenario?: 'defensive' | 'possession' } = $props();

	// Scenario tab: defensive = out-of-possession, possession = in-possession
	let scenario = $state<'defensive' | 'possession'>(initialScenario);

	// Block toggles for each scenario
	let defBlockA = $state<'high' | 'mid' | 'low'>('mid');
	let defBlockB = $state<'high' | 'mid' | 'low'>('mid');
	let posBlockA = $state<'build_up_low' | 'build_up_mid' | 'final_third_phase'>('build_up_mid');
	let posBlockB = $state<'build_up_low' | 'build_up_mid' | 'final_third_phase'>('build_up_mid');

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

	const hasSpatialB = $derived(
		(spatial_b?.defensive?.length ?? 0) > 0 || (spatial_b?.possession?.length ?? 0) > 0
	);

	const PITCH = 105;
	const PITCH_W = 68;
	function pct(m: number): string {
		return `${((m / PITCH) * 100).toFixed(2)}%`;
	}
	function wpct(m: number | null): string {
		if (m == null) return '0%';
		const p = (m / PITCH_W) * 100;
		const margin = (100 - p) / 2;
		return `${margin.toFixed(2)}%`;
	}
</script>

<div class="spatial" class:compact>
	<div class="spatial__header">
		<div class="scenario-tabs" role="group" aria-label="Scenario">
			<button
				class="scenario-tab"
				class:active={scenario === 'defensive'}
				onclick={() => scenario = 'defensive'}
			>Out of Possession</button>
			<button
				class="scenario-tab"
				class:active={scenario === 'possession'}
				onclick={() => scenario = 'possession'}
			>In Possession</button>
		</div>
	</div>

	<div class="pitches-row">
		<!-- ── Team A ── -->
		<div class="pitch-col">
			<div class="pitch-header">
				<span class="team-label" style="color: {teamColorVar(team_a.color)};">{team_a.short_code}</span>
				<div class="toggle-group" role="group">
					{#if scenario === 'defensive'}
						{#each defBlocks as b}
							<button class="toggle-item" class:active={defBlockA === b.key} onclick={() => defBlockA = b.key}>
								{b.label}
							</button>
						{/each}
					{:else}
						{#each posBlocks as b}
							<button class="toggle-item" class:active={posBlockA === b.key} onclick={() => posBlockA = b.key}>
								{b.label}
							</button>
						{/each}
					{/if}
				</div>
			</div>

			<div class="pitch-wrap">
				<div class="pitch" role="img" aria-label="Pitch for {team_a.short_code}">
					<div class="pitch__center-line"></div>
					<div class="pitch__center-circle"></div>
					<div class="pitch__box pitch__box--top"></div>
					<div class="pitch__box pitch__box--bot"></div>
					{#if blockA}
						<div
							class="pitch__block"
							style="
								bottom: {pct(blockA.defensive_line_height)};
								height: {pct(blockA.team_length)};
								left: {wpct(blockA.width_m)};
								right: {wpct(blockA.width_m)};
								background: {teamColorVar(team_a.color)};
							"
						></div>
					{/if}
				</div>
				{#if blockA}
					<!-- Width annotation above block -->
					{#if blockA.width_m != null}
						<div class="ann ann--width" style="
							left: {wpct(blockA.width_m)};
							right: {wpct(blockA.width_m)};
							bottom: calc({pct(blockA.defensive_line_height + blockA.team_length)} + 4px);
						">
							<span class="ann__line"></span>
							<span class="ann__val">{blockA.width_m}m</span>
							<span class="ann__line"></span>
						</div>
					{/if}
					<!-- Height annotation on right side -->
					<div class="ann ann--height" style="
						bottom: {pct(blockA.defensive_line_height)};
						height: {pct(blockA.team_length)};
						right: calc({wpct(blockA.width_m)} - 20px);
					">
						<span class="ann__val ann__val--vert">{blockA.team_length}m</span>
					</div>
					<!-- Distance label at bottom of block -->
					<div class="ann ann--dist" style="
						bottom: calc({pct(blockA.defensive_line_height)} - 18px);
						left: {wpct(blockA.width_m)};
						right: {wpct(blockA.width_m)};
					">
						<span class="ann__val ann__val--dist">{blockA.defensive_line_height}m</span>
					</div>
				{/if}
			</div>

			{#if blockA}
				<div class="kpis">
					<div class="kpi">
						<span class="kpi__label">{scenario === 'defensive' ? 'Def. Line' : 'Distance'}</span>
						<span class="kpi__val" style="color: {teamColorVar(team_a.color)};">{blockA.defensive_line_height}m</span>
					</div>
					<div class="kpi">
						<span class="kpi__label">Length</span>
						<span class="kpi__val" style="color: {teamColorVar(team_a.color)};">{blockA.team_length}m</span>
					</div>
					{#if blockA.width_m != null}
						<div class="kpi">
							<span class="kpi__label">Width</span>
							<span class="kpi__val" style="color: {teamColorVar(team_a.color)};">{blockA.width_m}m</span>
						</div>
					{/if}
				</div>
			{/if}
		</div>

		<!-- ── Team B ── -->
		{#if hasSpatialB}
		<div class="pitch-col">
			<div class="pitch-header">
				<span class="team-label" style="color: {teamColorVar(team_b.color)};">{team_b.short_code}</span>
				<div class="toggle-group" role="group">
					{#if scenario === 'defensive'}
						{#each defBlocks as b}
							<button class="toggle-item" class:active={defBlockB === b.key} onclick={() => defBlockB = b.key}>
								{b.label}
							</button>
						{/each}
					{:else}
						{#each posBlocks as b}
							<button class="toggle-item" class:active={posBlockB === b.key} onclick={() => posBlockB = b.key}>
								{b.label}
							</button>
						{/each}
					{/if}
				</div>
			</div>

			<div class="pitch-wrap">
				<div class="pitch" role="img" aria-label="Pitch for {team_b.short_code}">
					<div class="pitch__center-line"></div>
					<div class="pitch__center-circle"></div>
					<div class="pitch__box pitch__box--top"></div>
					<div class="pitch__box pitch__box--bot"></div>
					{#if blockB}
						<div
							class="pitch__block"
							style="
								bottom: {pct(blockB.defensive_line_height)};
								height: {pct(blockB.team_length)};
								left: {wpct(blockB.width_m)};
								right: {wpct(blockB.width_m)};
								background: {teamColorVar(team_b.color)};
							"
						></div>
					{/if}
				</div>
				{#if blockB}
					{#if blockB.width_m != null}
						<div class="ann ann--width" style="
							left: {wpct(blockB.width_m)};
							right: {wpct(blockB.width_m)};
							bottom: calc({pct(blockB.defensive_line_height + blockB.team_length)} + 4px);
						">
							<span class="ann__line"></span>
							<span class="ann__val">{blockB.width_m}m</span>
							<span class="ann__line"></span>
						</div>
					{/if}
					<div class="ann ann--height" style="
						bottom: {pct(blockB.defensive_line_height)};
						height: {pct(blockB.team_length)};
						right: calc({wpct(blockB.width_m)} - 20px);
					">
						<span class="ann__val ann__val--vert">{blockB.team_length}m</span>
					</div>
					<div class="ann ann--dist" style="
						bottom: calc({pct(blockB.defensive_line_height)} - 18px);
						left: {wpct(blockB.width_m)};
						right: {wpct(blockB.width_m)};
					">
						<span class="ann__val ann__val--dist">{blockB.defensive_line_height}m</span>
					</div>
				{/if}
			</div>

			{#if blockB}
				<div class="kpis">
					<div class="kpi">
						<span class="kpi__label">{scenario === 'defensive' ? 'Def. Line' : 'Distance'}</span>
						<span class="kpi__val" style="color: {teamColorVar(team_b.color)};">{blockB.defensive_line_height}m</span>
					</div>
					<div class="kpi">
						<span class="kpi__label">Length</span>
						<span class="kpi__val" style="color: {teamColorVar(team_b.color)};">{blockB.team_length}m</span>
					</div>
					{#if blockB.width_m != null}
						<div class="kpi">
							<span class="kpi__label">Width</span>
							<span class="kpi__val" style="color: {teamColorVar(team_b.color)};">{blockB.width_m}m</span>
						</div>
					{/if}
				</div>
			{/if}
		</div>
		{/if}
	</div>
</div>

<style>
	.spatial {
		display: flex;
		flex-direction: column;
		gap: var(--sp-4);
	}

	.spatial__header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: var(--sp-4);
		flex-wrap: wrap;
	}

	/* ── Scenario tabs ── */
	.scenario-tabs {
		display: flex;
		gap: 2px;
		background: var(--border);
		border-radius: var(--r-pill);
		padding: 2px;
	}
	.scenario-tab {
		padding: 4px var(--sp-3);
		font-size: var(--fs-meta);
		font-weight: 600;
		font-family: inherit;
		border-radius: var(--r-pill);
		cursor: pointer;
		color: var(--muted);
		background: transparent;
		border: none;
		transition: background 0.15s, color 0.15s;
		white-space: nowrap;
	}
	.scenario-tab.active {
		background: var(--ink);
		color: var(--bg);
	}

	/* ── Two pitches side by side ── */
	.pitches-row {
		display: flex;
		gap: var(--sp-8);
		flex-wrap: wrap;
	}

	.pitch-col {
		display: flex;
		flex-direction: column;
		gap: var(--sp-3);
		flex: 1;
		min-width: 140px;
	}
	.compact .pitch-col {
		max-width: 320px;
	}

	/* ── Header above each pitch ── */
	.pitch-header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: var(--sp-2);
		flex-wrap: wrap;
	}

	.team-label {
		font-size: var(--fs-label);
		font-weight: 800;
		text-transform: uppercase;
		letter-spacing: 0.06em;
	}

	/* ── Toggle group ── */
	.toggle-group {
		display: flex;
		gap: 2px;
		background: var(--border);
		border-radius: var(--r-pill);
		padding: 2px;
	}
	.toggle-item {
		padding: 3px var(--sp-2);
		font-size: var(--fs-meta);
		font-weight: 600;
		font-family: inherit;
		border-radius: var(--r-pill);
		cursor: pointer;
		color: var(--muted);
		background: transparent;
		border: none;
		min-height: 24px;
		transition: background 0.15s, color 0.15s;
		white-space: nowrap;
	}
	.toggle-item.active {
		background: var(--c-yellow);
		color: var(--c-forest);
	}

	/* ── Vertical pitch ── */
	.pitch {
		position: relative;
		width: 100%;
		aspect-ratio: 68 / 105;
		background: var(--pitch);
		border: 2px solid var(--pitch-line);
		border-radius: var(--r-sm);
		overflow: hidden;
	}

	/* Center line — horizontal */
	.pitch__center-line {
		position: absolute;
		left: 0;
		right: 0;
		top: 50%;
		height: 2px;
		background: var(--pitch-line);
		transform: translateY(-50%);
	}

	/* Center circle */
	.pitch__center-circle {
		position: absolute;
		top: 50%;
		left: 50%;
		transform: translate(-50%, -50%);
		width: 40%;
		aspect-ratio: 1;
		border: 2px solid var(--pitch-line);
		border-radius: 50%;
	}

	/* Penalty boxes — top and bottom */
	.pitch__box {
		position: absolute;
		left: 18%;
		right: 18%;
		height: 17%;
		border: 2px solid var(--pitch-line);
		background: transparent;
	}
	.pitch__box--top {
		top: 0;
		border-top: none;
		border-radius: 0 0 6px 6px;
	}
	.pitch__box--bot {
		bottom: 0;
		border-bottom: none;
		border-radius: 6px 6px 0 0;
	}

	/* Team block */
	.pitch__block {
		position: absolute;
		opacity: 0.45;
		z-index: 1;
	}

	/* Pitch wrapper — annotations live here so they can overflow the pitch element */
	.pitch-wrap {
		position: relative;
	}

	/* Annotations */
	.ann {
		position: absolute;
		pointer-events: none;
		z-index: 3;
	}
	.ann--width {
		display: flex;
		align-items: center;
		gap: 3px;
		height: 14px;
	}
	.ann__line {
		flex: 1;
		height: 1px;
		background: var(--muted);
		opacity: 0.7;
	}
	.ann__val {
		font-size: 10px;
		font-weight: 700;
		font-variant-numeric: tabular-nums;
		white-space: nowrap;
		background: var(--surface);
		padding: 1px 3px;
		border-radius: 3px;
		color: var(--ink);
		line-height: 1;
	}
	.ann--height {
		display: flex;
		align-items: center;
		justify-content: center;
		width: 20px;
	}
	.ann__val--vert {
		writing-mode: vertical-rl;
		text-orientation: mixed;
		transform: rotate(180deg);
	}
	.ann--dist {
		display: flex;
		justify-content: flex-end;
		align-items: flex-start;
		height: 16px;
	}
	.ann__val--dist {
		opacity: 0.7;
	}

	/* ── KPI row below pitch ── */
	.kpis {
		display: flex;
		gap: var(--sp-6);
	}
	.kpi {
		display: flex;
		flex-direction: column;
		gap: 2px;
	}
	.kpi__label {
		font-size: var(--fs-label);
		font-weight: 600;
		text-transform: uppercase;
		letter-spacing: 0.08em;
		color: var(--muted);
	}
	.kpi__val {
		font-size: var(--fs-h2);
		font-weight: 800;
		font-variant-numeric: tabular-nums;
		line-height: 1.1;
	}

	@media (max-width: 700px) {
		.pitches-row { gap: var(--sp-6); }
		.pitch-header { flex-direction: column; align-items: flex-start; }
	}
</style>
