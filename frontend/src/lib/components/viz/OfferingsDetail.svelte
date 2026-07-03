<script lang="ts">
	import type { Team } from '$lib/types/efi';
	import { teamTextColor, teamColorVar } from '$lib/tokens';
	import { t } from '$lib/i18n';

	interface OfferingStat {
		total_offers_made: number | null;
		total_offers_received: number | null;
		offers_final_third: number | null;
		offers_middle_third: number | null;
		offers_defensive_third: number | null;
		inside_shape: number | null;
		outside_shape: number | null;
		most_player: string | null;
		most_count: number | null;
	}

	let {
		offerings_a,
		offerings_b,
		team_a,
		team_b
	}: { offerings_a: OfferingStat | null; offerings_b: OfferingStat | null; team_a: Team; team_b: Team } = $props();

	const thirds = $derived([
		{ key: 'offers_final_third' as const, label: $t.detail.finalThird },
		{ key: 'offers_middle_third' as const, label: $t.detail.middleThird },
		{ key: 'offers_defensive_third' as const, label: $t.detail.defThird },
	]);

	function maxOf(stat: OfferingStat | null, keys: string[]): number {
		if (!stat) return 1;
		return Math.max(...keys.map((k) => (stat as unknown as Record<string, number | null>)[k] ?? 0), 1);
	}

	const maxThird = $derived(Math.max(
		maxOf(offerings_a, thirds.map((t) => t.key)),
		maxOf(offerings_b, thirds.map((t) => t.key))
	));

	function shapePct(stat: OfferingStat | null, key: 'inside_shape' | 'outside_shape'): number {
		if (!stat) return 0;
		const total = (stat.inside_shape ?? 0) + (stat.outside_shape ?? 0);
		if (!total) return 0;
		return Math.round(((stat[key] ?? 0) / total) * 100);
	}
</script>

<div class="of">
	<!-- KPI cards -->
	<div class="of__kpi-row">
		{#each [{ team: team_a, stat: offerings_a }, { team: team_b, stat: offerings_b }] as { team, stat }}
			<div class="of__kpi">
				<span class="of__kpi-big" style="color: {teamTextColor(team.color)}">{stat?.total_offers_made ?? '—'}</span>
				<span class="of__kpi-label">{team.short_code} {$t.detail.offersMade}</span>
				<span class="of__kpi-sub">{stat?.total_offers_received ?? 0} {$t.detail.offersReceived}</span>
				{#if stat?.most_player}
					<span class="of__kpi-sub">{$t.detail.offersMost} {stat.most_count} — {stat.most_player}</span>
				{/if}
			</div>
		{/each}
	</div>

	<!-- Pitch third breakdown -->
	<div class="of__section-title">{$t.detail.offersByPitchThird}</div>
	<div class="of__bars">
		{#each thirds as third}
			<div class="of__bar-row">
				<span class="of__bar-label">{third.label}</span>
				<div class="of__bar-pair">
					<div class="of__bar-half of__bar-half--a">
						<div class="of__fill" style="width: {((offerings_a?.[third.key] ?? 0) / maxThird) * 100}%; background: {teamColorVar(team_a.color)};"></div>
						<span class="of__val">{offerings_a?.[third.key] ?? 0}</span>
					</div>
					<div class="of__bar-half of__bar-half--b">
						<span class="of__val">{offerings_b?.[third.key] ?? 0}</span>
						<div class="of__fill" style="width: {((offerings_b?.[third.key] ?? 0) / maxThird) * 100}%; background: {teamColorVar(team_b.color)};"></div>
					</div>
				</div>
			</div>
		{/each}
	</div>

	<!-- Shape: Inside vs Outside -->
	<div class="of__section-title">{$t.detail.offersInsideOutside}</div>
	<div class="of__shape-row">
		{#each [{ team: team_a, stat: offerings_a }, { team: team_b, stat: offerings_b }] as { team, stat }}
			<div class="of__shape-cell">
				<div class="of__shape-bar">
					<div class="of__shape-inside" style="width: {shapePct(stat, 'inside_shape')}%; background: {teamColorVar(team.color)};"></div>
				</div>
				<div class="of__shape-labels">
					<span style="color: {teamTextColor(team.color)}">{shapePct(stat, 'inside_shape')}% {$t.detail.offersIn}</span>
					<span class="of__muted">{shapePct(stat, 'outside_shape')}% {$t.detail.offersOut}</span>
				</div>
			</div>
		{/each}
	</div>
</div>

<style>
	.of { width: 100%; display: flex; flex-direction: column; gap: var(--sp-4); }

	.of__kpi-row {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: var(--sp-4);
	}
	.of__kpi { display: flex; flex-direction: column; gap: 2px; }
	.of__kpi-big {
		font-size: var(--fs-stat);
		font-weight: 900;
		line-height: 1;
		font-variant-numeric: tabular-nums;
	}
	.of__kpi-label {
		font-size: var(--fs-meta);
		font-weight: 700;
		text-transform: uppercase;
		letter-spacing: 0.08em;
		color: var(--muted);
	}
	.of__kpi-sub { font-size: var(--fs-meta); color: var(--muted); }

	.of__section-title {
		font-size: var(--fs-meta);
		font-weight: 700;
		text-transform: uppercase;
		letter-spacing: 0.1em;
		color: var(--muted);
		padding-top: var(--sp-2);
	}

	.of__bars { display: flex; flex-direction: column; gap: var(--sp-1); }
	.of__bar-row {
		display: grid;
		grid-template-columns: 90px 1fr;
		align-items: center;
		gap: var(--sp-2);
	}
	.of__bar-label {
		font-size: var(--fs-meta);
		font-weight: 600;
		color: var(--muted);
		text-align: right;
	}
	.of__bar-pair {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 2px;
	}
	.of__bar-half {
		display: flex;
		align-items: center;
		gap: var(--sp-1);
		height: 16px;
	}
	.of__bar-half--a { flex-direction: row; }
	.of__bar-half--b { flex-direction: row-reverse; }
	.of__fill {
		height: 10px;
		border-radius: 3px;
		opacity: 0.75;
		transition: width 0.3s;
	}
	.of__val {
		font-size: var(--fs-meta);
		font-variant-numeric: tabular-nums;
		font-weight: 600;
		color: var(--muted);
		min-width: 22px;
	}

	.of__shape-row {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: var(--sp-4);
	}
	.of__shape-cell { display: flex; flex-direction: column; gap: var(--sp-1); }
	.of__shape-bar {
		height: 12px;
		background: var(--border);
		border-radius: 6px;
		overflow: hidden;
	}
	.of__shape-inside {
		height: 100%;
		border-radius: 6px;
		opacity: 0.75;
	}
	.of__shape-labels {
		display: flex;
		justify-content: space-between;
		font-size: var(--fs-meta);
		font-weight: 600;
	}
	.of__muted { color: var(--muted); }
</style>
