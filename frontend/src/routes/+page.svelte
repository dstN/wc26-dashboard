<script lang="ts">
	import type { PageData } from './$types';
	import StripeMotif from '$lib/components/primitives/StripeMotif.svelte';
	import PossessionBar from '$lib/components/viz/PossessionBar.svelte';
	import { teamColorVar, badgeTextColor } from '$lib/tokens';
	import { t } from '$lib/i18n';
	import { isKnockoutGroup } from '$lib/stage';
	import { goto } from '$app/navigation';

	let { data }: { data: PageData } = $props();
	const d = $derived(data.dashboard);

	// Knockout rounds carry short labels in group_letter (R32/R16/QF/SF/3RD/FIN)
	const ROUND_LABELS = $derived<Record<string, string>>({
		R32: $t.tournament.roundOf32,
		R16: $t.tournament.roundOf16,
		QF: $t.tournament.quarterFinals,
		SF: $t.tournament.semiFinals,
		'3RD': $t.tournament.thirdPlace,
		FIN: $t.tournament.final,
	});

	function groupHeading(g: string): string {
		// single letters are ALWAYS groups — guards group F against the FIN label
		if (!isKnockoutGroup(g)) return `${$t.match.group} ${g}`;
		return ROUND_LABELS[g] ?? `${$t.match.group} ${g}`;
	}
</script>

<svelte:head>
	<title>{$t.nav.overview} — EFI Data Engine</title>
</svelte:head>

{#if !d}
	<div class="error-state">
		<p>{$t.error.loadFailed}</p>
	</div>
{:else}
	<!-- ── SECTION 1: HERO ──────────────────────────────────────────────────── -->
	<section class="hero">
		<div class="hero__left">
			<p class="hero__eyebrow">{$t.hero.eyebrow}</p>
			<h1 class="hero__headline">
				<span>{$t.hero.line1}</span>
				<span>{$t.hero.line2}</span>
				<span>{$t.hero.line3}</span>
			</h1>
			<p class="hero__subtitle">
				{$t.hero.subtitle}
			</p>
			<div class="hero__stats">
				<div class="hero__stat">
					<span class="hero__stat-value">{d.overview.matches_played}</span>
					<span class="hero__stat-label">{$t.hero.matchesPlayed}</span>
				</div>
				<div class="hero__stat">
					<span class="hero__stat-value">{d.overview.goals_total}</span>
					<span class="hero__stat-label">{$t.hero.totalGoals}</span>
				</div>
				<div class="hero__stat">
					<span class="hero__stat-value">{d.overview.avg_in_contest_pct.toFixed(1)}%</span>
					<span class="hero__stat-label">{$t.hero.avgInContest}</span>
				</div>
			</div>
		</div>
		<div class="hero__right">
			<StripeMotif />
		</div>
	</section>

	<!-- ── SECTION 2: FEATURED MATCH BAND ─────────────────────────────────── -->
	<section class="match-band">
		<div class="match-band__header">
			<span class="match-band__featured-label">{$t.match.featuredLabel}</span>
			<span class="match-band__meta">{groupHeading(d.featured.group_letter)} · {$t.match.matchNo} {d.featured.match_no}</span>
			<span class="match-band__status">{d.featured.went_to_extra_time ? $t.match.aet : $t.match.fullTime}</span>
		</div>

		{#if d.featured.venue || d.featured.match_date}
			<div class="match-band__context">
				{#if d.featured.venue}<span class="match-band__venue">{d.featured.venue}</span>{/if}
				{#if d.featured.match_date}<span class="match-band__date">{d.featured.match_date}</span>{/if}
			</div>
		{/if}

		<div class="match-band__score-link" role="link" tabindex="0"
			onclick={() => goto(`/matches/${d.featured.id}`)}
			onkeydown={(e) => e.key === 'Enter' && goto(`/matches/${d.featured.id}`)}>
			<div class="match-band__score-row">
				<div class="match-band__team match-band__team--left">
					<a href="/teams/{d.featured.team_a.id}" class="match-band__team-name" onclick={(e) => e.stopPropagation()}>{d.featured.team_a.name}</a>
					<span
						class="match-band__badge"
						style="background: {teamColorVar(d.featured.team_a.color)}; color: {badgeTextColor(d.featured.team_a.color)};"
					>{d.featured.team_a.short_code}</span>
				</div>
				<div class="match-band__scoreline">
					<span class="match-band__score">{d.featured.score_a}</span>
					<span class="match-band__colon">:</span>
					<span class="match-band__score">{d.featured.score_b}</span>
				</div>
				<div class="match-band__team match-band__team--right">
					<span
						class="match-band__badge"
						style="background: {teamColorVar(d.featured.team_b.color)}; color: {badgeTextColor(d.featured.team_b.color)};"
					>{d.featured.team_b.short_code}</span>
					<a href="/teams/{d.featured.team_b.id}" class="match-band__team-name" onclick={(e) => e.stopPropagation()}>{d.featured.team_b.name}</a>
				</div>
			</div>
			{#if d.featured.penalty_score_a != null}
				<span class="match-band__pens">{$t.match.penalties}: {d.featured.penalty_score_a}-{d.featured.penalty_score_b}</span>
			{/if}
		</div>

		<div class="match-band__xg-row">
			<span class="match-band__xg">{d.head_to_head.xg_a != null ? d.head_to_head.xg_a.toFixed(2) : '—'} xG</span>
			<span class="match-band__xg match-band__xg--right">{d.head_to_head.xg_b != null ? d.head_to_head.xg_b.toFixed(2) : '—'} xG</span>
		</div>

		<div class="match-band__possession">
			<PossessionBar stats={d.head_to_head} team_a={d.featured.team_a} team_b={d.featured.team_b} />
		</div>

		<a href="/matches/{d.featured.id}" class="featured-cta">{$t.match.featuredCta}</a>
	</section>

{/if}

<style>
	/* ── Error state ─────────────────────────────────────────────────── */
	.error-state {
		padding: var(--sp-10);
		text-align: center;
		color: var(--muted);
		font-size: var(--fs-body);
	}

	/* ── SECTION 1: Hero ─────────────────────────────────────────────── */
	.hero {
		display: grid;
		grid-template-columns: 1.1fr 0.9fr;
		min-height: 440px;
	}

	.hero__left {
		padding: 52px 40px;
		display: flex;
		flex-direction: column;
		gap: var(--sp-6);
		justify-content: center;
		background: var(--surface);
	}

	.hero__eyebrow {
		font-size: var(--fs-label);
		font-weight: 700;
		text-transform: uppercase;
		letter-spacing: 0.14em;
		color: var(--c-red);
	}

	:global([data-theme='dark']) .hero__eyebrow {
		color: var(--c-lime);
	}

	.hero__headline {
		font-size: var(--fs-hero);
		font-weight: 800;
		line-height: 1.08;
		color: var(--ink);
		display: flex;
		flex-direction: column;
	}

	.hero__subtitle {
		font-size: var(--fs-body);
		color: var(--muted);
		max-width: 480px;
		line-height: 1.6;
	}

	.hero__stats {
		display: flex;
		gap: var(--sp-8);
		padding-top: var(--sp-2);
	}

	.hero__stat {
		display: flex;
		flex-direction: column;
		gap: var(--sp-1);
	}

	.hero__stat-value {
		font-size: var(--fs-stat);
		font-weight: 800;
		font-variant-numeric: tabular-nums;
		color: var(--ink);
		line-height: 1;
	}

	.hero__stat-label {
		font-size: var(--fs-label);
		font-weight: 600;
		text-transform: uppercase;
		letter-spacing: 0.08em;
		color: var(--muted);
	}

	.hero__right {
		background: #0b0b0f;
		min-height: 300px;
	}

	/* ── SECTION 2: Featured Match Band ─────────────────────────────── */
	.match-band {
		padding: 52px 40px;
		background: var(--surface);
		display: flex;
		flex-direction: column;
		gap: var(--sp-6);
	}

	.match-band__header {
		display: flex;
		align-items: center;
		gap: var(--sp-4);
	}

	.match-band__featured-label {
		font-size: var(--fs-label);
		font-weight: 700;
		text-transform: uppercase;
		letter-spacing: 0.12em;
		color: var(--accent);
	}

	.match-band__meta {
		font-size: var(--fs-label);
		font-weight: 500;
		color: var(--muted);
		text-transform: uppercase;
		letter-spacing: 0.06em;
	}

	.match-band__status {
		margin-left: auto;
		font-size: var(--fs-label);
		font-weight: 700;
		text-transform: uppercase;
		letter-spacing: 0.1em;
		color: var(--positive);
	}

	.match-band__context {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 3px;
		margin-top: calc(-1 * var(--sp-3));
	}
	.match-band__venue {
		font-size: var(--fs-ui);
		font-weight: 600;
		color: var(--ink);
		text-align: center;
	}
	.match-band__date {
		font-size: var(--fs-meta);
		color: var(--muted);
		text-align: center;
	}

	.match-band__score-link {
		display: block;
		cursor: pointer;
		border-radius: var(--r-md);
		transition: background 0.15s;
		margin: 0 -var(--sp-3);
		padding: var(--sp-2) var(--sp-3);
	}
	.match-band__score-link:hover {
		background: color-mix(in srgb, var(--border) 60%, transparent);
	}
	.match-band__pens {
		display: block;
		text-align: center;
		font-size: var(--fs-meta);
		font-weight: 600;
		color: var(--muted);
		margin-top: var(--sp-1);
	}

	.match-band__score-row {
		display: flex;
		align-items: center;
		justify-content: center;
		gap: var(--sp-6);
	}

	.match-band__team {
		display: flex;
		align-items: center;
		gap: var(--sp-3);
		/* shrink + wrap so long names (e.g. "Bosnia and Herzegovina") never
		   overflow the scoreline row */
		flex: 1 1 0;
		min-width: 0;
	}

	.match-band__team--left {
		flex-direction: row;
		justify-content: flex-end;
		text-align: right;
	}

	.match-band__team--right {
		flex-direction: row;
		justify-content: flex-start;
		text-align: left;
	}

	.match-band__team-name {
		font-size: var(--fs-h2);
		font-weight: 700;
		color: var(--ink);
		text-decoration: none;
		/* break only between words (not mid-word); long single words shrink
		   via the mobile stacked layout below */
		overflow-wrap: break-word;
		min-width: 0;
	}
	.match-band__team-name:hover { color: var(--accent); }

	.match-band__badge {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		padding: var(--sp-1) var(--sp-3);
		border-radius: var(--r-sm);
		font-size: var(--fs-ui);
		font-weight: 800;
		letter-spacing: 0.06em;
		text-transform: uppercase;
		line-height: 1;
		min-width: 44px;
		min-height: 28px;
		flex-shrink: 0;
	}

	.match-band__scoreline {
		display: flex;
		align-items: center;
		justify-content: center;
		gap: var(--sp-2);
		flex: 0 0 auto;
	}

	.match-band__score {
		font-size: var(--fs-score);
		font-weight: 900;
		font-variant-numeric: tabular-nums;
		color: var(--ink);
		line-height: 1;
	}

	.match-band__colon {
		font-size: var(--fs-score);
		font-weight: 300;
		color: var(--muted);
		line-height: 1;
	}

	.match-band__xg-row {
		display: flex;
		justify-content: space-between;
		padding: 0 var(--sp-3);
	}
	.match-band__xg {
		font-size: var(--fs-ui);
		font-weight: 600;
		color: var(--muted);
		font-variant-numeric: tabular-nums;
	}
	.match-band__xg--right { text-align: right; }

	.match-band__possession {
		padding: 0 var(--sp-3);
	}

	.featured-cta {
		display: inline-flex;
		align-items: center;
		gap: var(--sp-2);
		padding: var(--sp-3) var(--sp-5);
		background: var(--accent);
		color: var(--accent-fg);
		border-radius: var(--r-md);
		font-size: var(--fs-ui);
		font-weight: 700;
		text-decoration: none;
		transition: opacity 0.15s;
		align-self: center;
	}
	.featured-cta:hover { opacity: 0.85; }

	/* ── Responsive ──────────────────────────────────────────────────── */
	@media (max-width: 1024px) {
		.hero {
			grid-template-columns: 1fr;
		}
		.hero__right {
			min-height: 240px;
		}
	}

	@media (max-width: 720px) {
		.hero__left,
		.match-band {
			padding: var(--sp-6) var(--sp-4);
		}
		.hero__headline {
			font-size: 2.5rem;
		}
		.hero__stats {
			gap: var(--sp-5);
			flex-wrap: wrap;
		}
		.match-band__score-row {
			gap: var(--sp-3);
		}
		.match-band__team-name {
			font-size: var(--fs-body);
			text-align: center;
		}
		/* Mobile: stack the badge (abbreviation) above the full country name so
		   long names ("Switzerland", "Bosnia and Herzegovina") get the full
		   column width instead of breaking mid-word. */
		.match-band__team {
			gap: var(--sp-1);
			align-items: center;
		}
		.match-band__team--left {
			flex-direction: column-reverse;
			text-align: center;
		}
		.match-band__team--right {
			flex-direction: column;
			text-align: center;
		}
	}
</style>
