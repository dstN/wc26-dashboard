<script lang="ts">
	import RainbowRail from '$lib/components/primitives/RainbowRail.svelte';
	import SectionLabel from '$lib/components/primitives/SectionLabel.svelte';
	import Badge from '$lib/components/primitives/Badge.svelte';
	import KpiStat from '$lib/components/primitives/KpiStat.svelte';
	import Card from '$lib/components/primitives/Card.svelte';
	import StripeMotif from '$lib/components/primitives/StripeMotif.svelte';
	import PossessionBar from '$lib/components/viz/PossessionBar.svelte';
	import StatTable from '$lib/components/viz/StatTable.svelte';

	const teamA = { id: 1, name: 'Germany', color: 'red', group: 'E' };
	const teamB = { id: 2, name: 'Curaçao', color: 'blue', group: 'E' };

	const stats = {
		possession_team_a: 57.8,
		possession_in_contest: 6.9,
		possession_team_b: 35.3,
		goals_a: 7,
		goals_b: 1,
		xg_a: 3.1,
		xg_b: 0.4,
		ball_recovery_time_avg: 4.2
	};
</script>

<main class="ks">
	<h1 class="ks__title">Kitchen Sink</h1>
	<p class="ks__sub">Primitive component showcase · dev only</p>

	<section class="ks__section">
		<h2>RainbowRail</h2>
		<RainbowRail />
	</section>

	<section class="ks__section">
		<h2>SectionLabel</h2>
		<SectionLabel>Possession</SectionLabel>
		<SectionLabel>Head to Head</SectionLabel>
	</section>

	<section class="ks__section">
		<h2>Badge</h2>
		<div style="display:flex; gap: 8px; flex-wrap:wrap;">
			<Badge>LIVE</Badge>
			<Badge variant="muted">GROUP E</Badge>
			<Badge variant="accent">MATCH 10</Badge>
		</div>
	</section>

	<section class="ks__section">
		<h2>KpiStat</h2>
		<div style="display:flex; gap: 16px; flex-wrap:wrap;">
			<KpiStat label="xG" value="3.1" team={teamA} />
			<KpiStat label="Goals" value="7" team={teamA} />
			<KpiStat label="Recovery" value="4.2s" team={teamA} />
		</div>
	</section>

	<section class="ks__section">
		<h2>Card</h2>
		<Card>
			<p>Card content goes here.</p>
		</Card>
	</section>

	<section class="ks__section">
		<h2>StripeMotif</h2>
		<StripeMotif />
	</section>

	<section class="ks__section">
		<h2>PossessionBar</h2>
		<PossessionBar {stats} team_a={teamA} team_b={teamB} />
	</section>

	<section class="ks__section">
		<h2>StatTable</h2>
		<StatTable {stats} team_a={teamA} team_b={teamB} />
	</section>
</main>

<style>
	.ks {
		max-width: 800px;
		margin: 0 auto;
		padding: var(--sp-8);
		display: flex;
		flex-direction: column;
		gap: var(--sp-8);
	}
	.ks__title {
		font-size: var(--fs-display);
		font-weight: 800;
	}
	.ks__sub {
		color: var(--muted);
		font-size: var(--fs-ui);
	}
	.ks__section {
		display: flex;
		flex-direction: column;
		gap: var(--sp-4);
		padding-bottom: var(--sp-6);
		border-bottom: 1px solid var(--border-soft);
	}
	.ks__section h2 {
		font-size: var(--fs-label);
		font-weight: 700;
		text-transform: uppercase;
		letter-spacing: 0.08em;
		color: var(--muted);
	}
</style>
