<script lang="ts">
	import type { Team } from '$lib/types/efi';
	import { teamTextColor, teamColorVar } from '$lib/tokens';
	import { t } from '$lib/i18n';

	interface CrossStat {
		attempted: number | null;
		completed: number | null;
		zone_left: number | null;
		zone_center_left: number | null;
		zone_center_right: number | null;
		zone_right: number | null;
		type_inswing: number | null;
		type_outswing: number | null;
		type_driven: number | null;
		type_lofted: number | null;
		type_cutback: number | null;
		type_push_cross: number | null;
		most_player: string | null;
		most_count: number | null;
	}

	let {
		crosses_a,
		crosses_b,
		team_a,
		team_b
	}: { crosses_a: CrossStat | null; crosses_b: CrossStat | null; team_a: Team; team_b: Team } = $props();

	const types = $derived([
		{ key: 'type_inswing' as const, label: $t.playerDetail.inswing },
		{ key: 'type_outswing' as const, label: $t.playerDetail.outswing },
		{ key: 'type_driven' as const, label: $t.playerDetail.driven },
		{ key: 'type_lofted' as const, label: $t.playerDetail.lofted },
		{ key: 'type_cutback' as const, label: $t.playerDetail.cutback },
		{ key: 'type_push_cross' as const, label: $t.playerDetail.pushCross },
	]);

	const zones = $derived([
		{ key: 'zone_left' as const, label: $t.detail.crossLeft },
		{ key: 'zone_center_left' as const, label: $t.detail.crossCenterLeft },
		{ key: 'zone_center_right' as const, label: $t.detail.crossCenterRight },
		{ key: 'zone_right' as const, label: $t.detail.crossRight },
	]);

	function maxOf(stat: CrossStat | null, keys: string[]): number {
		if (!stat) return 1;
		return Math.max(...keys.map((k) => (stat as unknown as Record<string, number | null>)[k] ?? 0), 1);
	}

	const maxType = $derived(Math.max(
		maxOf(crosses_a, types.map((t) => t.key)),
		maxOf(crosses_b, types.map((t) => t.key))
	));
	const maxZone = $derived(Math.max(
		maxOf(crosses_a, zones.map((z) => z.key)),
		maxOf(crosses_b, zones.map((z) => z.key))
	));

	function pct(stat: CrossStat | null): string {
		if (!stat || !stat.attempted) return '—';
		const p = ((stat.completed ?? 0) / stat.attempted * 100).toFixed(0);
		return `${stat.completed ?? 0}/${stat.attempted} (${p}%)`;
	}
</script>

<div class="cx">
	<!-- Completion KPI row -->
	<div class="cx__kpi-row">
		{#each [{ team: team_a, stat: crosses_a }, { team: team_b, stat: crosses_b }] as { team, stat }}
			<div class="cx__kpi">
				<span class="cx__kpi-val" style="color: {teamTextColor(team.color)}">{pct(stat)}</span>
				<span class="cx__kpi-label">{team.short_code} {$t.detail.crossCompAtt}</span>
				{#if stat?.most_player}
					<span class="cx__kpi-note">{$t.detail.crossMost}: #{stat.most_count} {stat.most_player}</span>
				{/if}
			</div>
		{/each}
	</div>

	<!-- Delivery type bars -->
	<div class="cx__section-title">{$t.detail.crossDeliveryType}</div>
	<div class="cx__bars">
		{#each types as type}
			<div class="cx__bar-row">
				<span class="cx__bar-label">{type.label}</span>
				<div class="cx__bar-pair">
					<div class="cx__bar-half cx__bar-half--a">
						<div class="cx__fill" style="width: {((crosses_a?.[type.key] ?? 0) / maxType) * 100}%; background: {teamColorVar(team_a.color)};"></div>
						<span class="cx__bar-val">{crosses_a?.[type.key] ?? 0}</span>
					</div>
					<div class="cx__bar-half cx__bar-half--b">
						<span class="cx__bar-val">{crosses_b?.[type.key] ?? 0}</span>
						<div class="cx__fill" style="width: {((crosses_b?.[type.key] ?? 0) / maxType) * 100}%; background: {teamColorVar(team_b.color)};"></div>
					</div>
				</div>
			</div>
		{/each}
	</div>

	<!-- Zone bars -->
	<div class="cx__section-title">{$t.detail.crossZone}</div>
	<div class="cx__bars">
		{#each zones as zone}
			<div class="cx__bar-row">
				<span class="cx__bar-label">{zone.label}</span>
				<div class="cx__bar-pair">
					<div class="cx__bar-half cx__bar-half--a">
						<div class="cx__fill" style="width: {((crosses_a?.[zone.key] ?? 0) / maxZone) * 100}%; background: {teamColorVar(team_a.color)};"></div>
						<span class="cx__bar-val">{crosses_a?.[zone.key] ?? 0}</span>
					</div>
					<div class="cx__bar-half cx__bar-half--b">
						<span class="cx__bar-val">{crosses_b?.[zone.key] ?? 0}</span>
						<div class="cx__fill" style="width: {((crosses_b?.[zone.key] ?? 0) / maxZone) * 100}%; background: {teamColorVar(team_b.color)};"></div>
					</div>
				</div>
			</div>
		{/each}
	</div>
</div>

<style>
	.cx { width: 100%; display: flex; flex-direction: column; gap: var(--sp-4); }

	.cx__kpi-row {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: var(--sp-4);
	}
	.cx__kpi { display: flex; flex-direction: column; gap: 2px; }
	.cx__kpi-val {
		font-size: var(--fs-h2);
		font-weight: 800;
		font-variant-numeric: tabular-nums;
		line-height: 1.1;
	}
	.cx__kpi-label {
		font-size: var(--fs-meta);
		font-weight: 600;
		text-transform: uppercase;
		letter-spacing: 0.08em;
		color: var(--muted);
	}
	.cx__kpi-note {
		font-size: var(--fs-meta);
		color: var(--muted);
	}

	.cx__section-title {
		font-size: var(--fs-meta);
		font-weight: 700;
		text-transform: uppercase;
		letter-spacing: 0.1em;
		color: var(--muted);
		padding-top: var(--sp-2);
	}

	.cx__bars { display: flex; flex-direction: column; gap: var(--sp-1); }

	.cx__bar-row {
		display: grid;
		grid-template-columns: 80px 1fr;
		align-items: center;
		gap: var(--sp-2);
	}
	.cx__bar-label {
		font-size: var(--fs-meta);
		font-weight: 600;
		color: var(--muted);
		text-align: right;
	}
	.cx__bar-pair {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 2px;
	}
	.cx__bar-half {
		display: flex;
		align-items: center;
		gap: var(--sp-1);
		height: 16px;
	}
	.cx__bar-half--a { flex-direction: row; }
	.cx__bar-half--b { flex-direction: row-reverse; }

	.cx__fill {
		height: 10px;
		border-radius: 3px;
		opacity: 0.75;
		transition: width 0.3s ease;
		flex-shrink: 0;
	}
	.cx__bar-val {
		font-size: var(--fs-meta);
		font-variant-numeric: tabular-nums;
		font-weight: 600;
		color: var(--muted);
		min-width: 18px;
	}
</style>
