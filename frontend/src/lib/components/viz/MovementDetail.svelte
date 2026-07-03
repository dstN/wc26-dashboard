<script lang="ts">
	import type { Team } from '$lib/types/efi';
	import { teamTextColor, teamColorVar } from '$lib/tokens';
	import { t } from '$lib/i18n';

	interface MovementStat {
		total_movements: number | null;
		phase_final_third: number | null;
		phase_progression: number | null;
		phase_build_up: number | null;
		type_in_front: number | null;
		type_in_between: number | null;
		type_out_to_in: number | null;
		type_in_to_out: number | null;
		type_in_behind: number | null;
		ft_in_front: number | null; ft_in_between: number | null; ft_out_to_in: number | null; ft_in_to_out: number | null; ft_in_behind: number | null;
		mid_in_front: number | null; mid_in_between: number | null; mid_out_to_in: number | null; mid_in_to_out: number | null; mid_in_behind: number | null;
		def_in_front: number | null; def_in_between: number | null; def_out_to_in: number | null; def_in_to_out: number | null; def_in_behind: number | null;
	}

	let {
		movement_a,
		movement_b,
		team_a,
		team_b
	}: { movement_a: MovementStat | null; movement_b: MovementStat | null; team_a: Team; team_b: Team } = $props();

	const phases = $derived([
		{ key: 'phase_final_third' as const, label: $t.detail.finalThirdPhase },
		{ key: 'phase_progression' as const, label: $t.detail.progressionPhase },
		{ key: 'phase_build_up' as const, label: $t.detail.buildUpPhase },
	]);

	const types = $derived([
		{ key: 'type_in_front' as const, label: $t.detail.typeInFront },
		{ key: 'type_in_between' as const, label: $t.detail.typeInBetween },
		{ key: 'type_out_to_in' as const, label: $t.detail.typeOutToIn },
		{ key: 'type_in_to_out' as const, label: $t.detail.typeInToOut },
		{ key: 'type_in_behind' as const, label: $t.detail.typeInBehind },
	]);

	const pitchThirds = $derived([
		{ prefix: 'ft' as const, label: $t.detail.finalThird },
		{ prefix: 'mid' as const, label: $t.detail.middleThird },
		{ prefix: 'def' as const, label: $t.detail.defThird },
	]);
	const typeKeys = ['in_front', 'in_between', 'out_to_in', 'in_to_out', 'in_behind'] as const;
	const typeLabels = $derived<Record<string, string>>({
		in_front: $t.detail.typeInFront,
		in_between: $t.detail.typeInBetween,
		out_to_in: $t.detail.typeOutToIn,
		in_to_out: $t.detail.typeInToOut,
		in_behind: $t.detail.typeInBehind,
	});

	function hasPitchThird(stat: MovementStat | null): boolean {
		return pitchThirds.some(p => typeKeys.some(t => (stat as unknown as Record<string, number | null>)[`${p.prefix}_${t}`] != null));
	}

	function maxOf(stat: MovementStat | null, keys: string[]): number {
		if (!stat) return 1;
		return Math.max(...keys.map((k) => (stat as unknown as Record<string, number | null>)[k] ?? 0), 1);
	}

	const maxPhase = $derived(Math.max(
		maxOf(movement_a, phases.map((p) => p.key)),
		maxOf(movement_b, phases.map((p) => p.key))
	));
	const maxType = $derived(Math.max(
		maxOf(movement_a, types.map((t) => t.key)),
		maxOf(movement_b, types.map((t) => t.key))
	));
</script>

<div class="mv">
	<!-- Total KPIs -->
	<div class="mv__kpi-row">
		{#each [{ team: team_a, stat: movement_a }, { team: team_b, stat: movement_b }] as { team, stat }}
			<div class="mv__kpi">
				<span class="mv__kpi-big" style="color: {teamTextColor(team.color)}">{stat?.total_movements ?? '—'}</span>
				<span class="mv__kpi-label">{team.short_code} {$t.detail.movTotalMovements}</span>
			</div>
		{/each}
	</div>

	<!-- Phase breakdown -->
	<div class="mv__section-title">{$t.detail.movByPhase}</div>
	<div class="mv__bars">
		{#each phases as phase}
			<div class="mv__bar-row">
				<span class="mv__bar-label">{phase.label}</span>
				<div class="mv__bar-pair">
					<div class="mv__bar-half mv__bar-half--a">
						<div class="mv__fill" style="width: {((movement_a?.[phase.key] ?? 0) / maxPhase) * 100}%; background: {teamColorVar(team_a.color)};"></div>
						<span class="mv__val">{movement_a?.[phase.key] ?? 0}</span>
					</div>
					<div class="mv__bar-half mv__bar-half--b">
						<span class="mv__val">{movement_b?.[phase.key] ?? 0}</span>
						<div class="mv__fill" style="width: {((movement_b?.[phase.key] ?? 0) / maxPhase) * 100}%; background: {teamColorVar(team_b.color)};"></div>
					</div>
				</div>
			</div>
		{/each}
	</div>

	<!-- Movement type breakdown -->
	<div class="mv__section-title">{$t.detail.movByType}</div>
	<div class="mv__bars">
		{#each types as type}
			<div class="mv__bar-row">
				<span class="mv__bar-label">{type.label}</span>
				<div class="mv__bar-pair">
					<div class="mv__bar-half mv__bar-half--a">
						<div class="mv__fill" style="width: {((movement_a?.[type.key] ?? 0) / maxType) * 100}%; background: {teamColorVar(team_a.color)};"></div>
						<span class="mv__val">{movement_a?.[type.key] ?? 0}</span>
					</div>
					<div class="mv__bar-half mv__bar-half--b">
						<span class="mv__val">{movement_b?.[type.key] ?? 0}</span>
						<div class="mv__fill" style="width: {((movement_b?.[type.key] ?? 0) / maxType) * 100}%; background: {teamColorVar(team_b.color)};"></div>
					</div>
				</div>
			</div>
		{/each}
	</div>

	<!-- Pitch third breakdown -->
	{#if hasPitchThird(movement_a) || hasPitchThird(movement_b)}
		<div class="mv__section-title">{$t.detail.movByPitchThird}</div>
		<div class="mv__thirds">
			{#each pitchThirds as third}
				<div class="mv__third-block">
					<div class="mv__third-title">{third.label}</div>
					{#each typeKeys as t}
						{@const ka = `${third.prefix}_${t}` as keyof MovementStat}
						{@const va = movement_a?.[ka] ?? 0}
						{@const vb = movement_b?.[ka] ?? 0}
						{@const mx = Math.max(va as number, vb as number, 1)}
						<div class="mv__third-row">
							<span class="mv__third-lbl">{typeLabels[t]}</span>
							<div class="mv__third-bars">
								<div class="mv__third-bar" style="width: {((va as number) / mx) * 100}%; background: {teamColorVar(team_a.color)};"></div>
								<div class="mv__third-vals"><span>{va}</span><span class="mv__third-sep">·</span><span>{vb}</span></div>
								<div class="mv__third-bar mv__third-bar--b" style="width: {((vb as number) / mx) * 100}%; background: {teamColorVar(team_b.color)};"></div>
							</div>
						</div>
					{/each}
				</div>
			{/each}
		</div>
	{/if}
</div>

<style>
	.mv { width: 100%; display: flex; flex-direction: column; gap: var(--sp-4); }

	.mv__kpi-row {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: var(--sp-4);
	}
	.mv__kpi { display: flex; flex-direction: column; gap: 2px; }
	.mv__kpi-big {
		font-size: var(--fs-stat);
		font-weight: 900;
		line-height: 1;
		font-variant-numeric: tabular-nums;
	}
	.mv__kpi-label {
		font-size: var(--fs-meta);
		font-weight: 700;
		text-transform: uppercase;
		letter-spacing: 0.08em;
		color: var(--muted);
	}

	.mv__section-title {
		font-size: var(--fs-meta);
		font-weight: 700;
		text-transform: uppercase;
		letter-spacing: 0.1em;
		color: var(--muted);
		padding-top: var(--sp-2);
	}

	.mv__bars { display: flex; flex-direction: column; gap: var(--sp-1); }
	.mv__bar-row {
		display: grid;
		grid-template-columns: 120px 1fr;
		align-items: center;
		gap: var(--sp-2);
	}
	.mv__bar-label {
		font-size: var(--fs-meta);
		font-weight: 600;
		color: var(--muted);
		text-align: right;
	}
	.mv__bar-pair {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 2px;
	}
	.mv__bar-half {
		display: flex;
		align-items: center;
		gap: var(--sp-1);
		height: 16px;
	}
	.mv__bar-half--a { flex-direction: row; }
	.mv__bar-half--b { flex-direction: row-reverse; }
	.mv__fill {
		height: 10px;
		border-radius: 3px;
		opacity: 0.75;
		transition: width 0.3s;
	}
	.mv__val {
		font-size: var(--fs-meta);
		font-variant-numeric: tabular-nums;
		font-weight: 600;
		color: var(--muted);
		min-width: 22px;
	}

	.mv__thirds {
		display: grid;
		grid-template-columns: repeat(3, 1fr);
		gap: var(--sp-3);
	}
	.mv__third-block {
		display: flex;
		flex-direction: column;
		gap: 4px;
	}
	.mv__third-title {
		font-size: var(--fs-meta);
		font-weight: 700;
		text-transform: uppercase;
		letter-spacing: 0.08em;
		color: var(--muted);
		padding-bottom: 4px;
		border-bottom: 1px solid var(--border);
		margin-bottom: 2px;
	}
	.mv__third-row {
		display: flex;
		flex-direction: column;
		gap: 2px;
	}
	.mv__third-lbl {
		font-size: 10px;
		font-weight: 600;
		color: var(--muted);
	}
	.mv__third-bars {
		display: flex;
		flex-direction: column;
		gap: 1px;
	}
	.mv__third-bar {
		height: 6px;
		border-radius: 2px;
		opacity: 0.75;
		min-width: 2px;
	}
	.mv__third-bar--b { align-self: flex-end; }
	.mv__third-vals {
		display: flex;
		gap: 4px;
		font-size: 10px;
		font-variant-numeric: tabular-nums;
		color: var(--muted);
	}
	.mv__third-sep { color: var(--border); }

	@media (max-width: 600px) {
		.mv__thirds { grid-template-columns: 1fr; }
	}
</style>
