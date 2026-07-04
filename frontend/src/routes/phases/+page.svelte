<script lang="ts">
	import type { PageData } from './$types';
	import type { TournamentOverview } from '$lib/types/efi';
	import SectionLabel from '$lib/components/primitives/SectionLabel.svelte';
	import KpiStat from '$lib/components/primitives/KpiStat.svelte';
	import { t } from '$lib/i18n';

	let { data }: { data: PageData } = $props();

	const overview: TournamentOverview | null = $derived(data.overview ?? null);

	function fmt(n: number, decimals = 0): string {
		return n?.toLocaleString('de-DE', { maximumFractionDigits: decimals }) ?? '—';
	}
</script>

<svelte:head>
	<title>Tournament — EFI Data Engine</title>
</svelte:head>

<div class="page">
	<header class="page-header">
		<SectionLabel label="{$t.tournament.label}" />
		<h1 class="page-title">{$t.tournament.title}</h1>
		<p class="page-sub">{$t.tournament.subtitle}</p>
		{#if data.error}
			<p class="error-note">{$t.error.loadFailed}</p>
		{/if}
	</header>

	{#if overview}
		<!-- KPI strip -->
		<section class="kpi-section">
			<SectionLabel label="{$t.tournament.kpiLabel}" />
			<div class="kpi-grid">
				<div class="kpi-card">
					<KpiStat
						label="{$t.tournament.matchesPlayed}"
						value={fmt(overview.matches_played)}
					/>
				</div>
				<div class="kpi-card">
					<KpiStat
						label="{$t.tournament.totalGoals}"
						value={fmt(overview.goals_total)}
					/>
				</div>
				<div class="kpi-card">
					<KpiStat
						label="{$t.tournament.avgContested}"
						value={fmt(overview.avg_in_contest_pct, 1)}
						unit="%"
					/>
				</div>
				{#if overview.matches_played > 0}
					<div class="kpi-card">
						<KpiStat
							label="{$t.tournament.goalsPerMatch}"
							value={fmt(overview.goals_total / overview.matches_played, 2)}
						/>
					</div>
				{/if}
			</div>
		</section>

		<!-- Phase progress -->
		<section class="phases-section">
			<SectionLabel label="{$t.tournament.formatLabel}" />
			<div class="phases-cards">
				<article class="phase-card phase-card--active">
					<div class="phase-card__indicator phase-card__indicator--active"></div>
					<div class="phase-card__body">
						<span class="phase-name">{$t.tournament.groupStage}</span>
						<span class="phase-meta">{$t.tournament.groupStageDetails}</span>
						<div class="phase-progress">
							<div class="progress-bar">
								<div
									class="progress-bar__fill"
									style="width: {Math.min(100, (overview.matches_played / 72) * 100).toFixed(1)}%;"
								></div>
							</div>
							<span class="progress-label">{overview.matches_played} / 72</span>
						</div>
					</div>
				</article>

				{#each [
					{ name: $t.tournament.roundOf32, games: 16, unlocks: 72 },
					{ name: $t.tournament.roundOf16, games: 8, unlocks: 88 },
					{ name: $t.tournament.quarterFinals, games: 4, unlocks: 96 },
					{ name: $t.tournament.semiFinals, games: 2, unlocks: 100 },
					{ name: $t.tournament.thirdPlace, games: 1, unlocks: 102 },
					{ name: $t.tournament.final, games: 1, unlocks: 103 }
				] as phase}
					{@const unlocked = overview.matches_played >= phase.unlocks}
					<article class="phase-card" class:phase-card--locked={!unlocked}>
						<div class="phase-card__indicator" class:phase-card__indicator--locked={!unlocked}></div>
						<div class="phase-card__body">
							<span class="phase-name">{phase.name}</span>
							<span class="phase-meta">{phase.games} {$t.match.matches}</span>
							{#if !unlocked}
								<span class="phase-locked-note">{$t.tournament.availableFrom} {phase.unlocks}</span>
							{/if}
						</div>
					</article>
				{/each}
			</div>
		</section>

		<!-- Info block -->
		<section class="info-section">
			<div class="info-card">
				<SectionLabel label="{$t.tournament.analysisLabel}" />
				<p class="info-text">
					{$t.tournament.analysisText} <strong>{overview.matches_played}</strong> {$t.tournament.analysisOf}
				</p>
				<a href="/" class="info-link">{$t.tournament.backToOverview}</a>
			</div>
		</section>
	{:else}
		<div class="empty">
			<p class="empty__text">{$t.tournament.noData}</p>
			<a href="/" class="back">{$t.tournament.backLink}</a>
		</div>
	{/if}
</div>

<style>
	.page {
		padding: 40px var(--sp-8);
		display: flex;
		flex-direction: column;
		gap: var(--sp-10);
	}

	/* ── Page header ─────────────────────────────────────────────────── */
	.page-header {
		display: flex;
		flex-direction: column;
		gap: var(--sp-3);
	}
	.page-title {
		font-size: var(--fs-hero);
		font-weight: 800;
		line-height: 1.05;
		color: var(--ink);
	}
	.page-sub {
		font-size: var(--fs-ui);
		font-weight: 500;
		color: var(--muted);
	}
	.error-note {
		font-size: var(--fs-meta);
		color: var(--c-red);
		margin-top: var(--sp-1);
	}

	/* ── KPI section ─────────────────────────────────────────────────── */
	.kpi-section {
		display: flex;
		flex-direction: column;
		gap: var(--sp-5);
	}
	.kpi-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
		gap: var(--sp-5);
	}
	.kpi-card {
		background: var(--surface);
		border: 1px solid var(--border);
		border-radius: 10px;
		padding: 20px var(--sp-6);
		box-shadow: var(--shadow-card);
	}

	/* ── Phases section ──────────────────────────────────────────────── */
	.phases-section {
		display: flex;
		flex-direction: column;
		gap: var(--sp-5);
	}
	.phases-cards {
		display: flex;
		flex-direction: column;
		gap: var(--sp-3);
	}

	.phase-card {
		background: var(--surface);
		border: 1px solid var(--border);
		border-radius: 10px;
		padding: 20px;
		display: flex;
		align-items: flex-start;
		gap: var(--sp-4);
		box-shadow: var(--shadow-card);
	}
	.phase-card--locked {
		opacity: 0.55;
	}

	.phase-card__indicator {
		width: 12px;
		height: 12px;
		border-radius: var(--r-pill);
		background: var(--accent);
		flex-shrink: 0;
		margin-top: 4px;
	}
	.phase-card__indicator--locked {
		background: var(--border);
	}
	.phase-card__indicator--active {
		background: var(--positive);
		box-shadow: 0 0 0 3px color-mix(in srgb, var(--positive) 25%, transparent);
	}

	.phase-card__body {
		display: flex;
		flex-direction: column;
		gap: var(--sp-2);
		flex: 1;
	}

	.phase-name {
		font-size: var(--fs-h2);
		font-weight: 700;
		color: var(--ink);
	}
	.phase-meta {
		font-size: var(--fs-label);
		font-weight: 600;
		text-transform: uppercase;
		letter-spacing: 0.08em;
		color: var(--muted);
	}
	.phase-locked-note {
		font-size: var(--fs-meta);
		color: var(--muted);
		font-style: italic;
	}

	/* Progress bar */
	.phase-progress {
		display: flex;
		align-items: center;
		gap: var(--sp-3);
		margin-top: var(--sp-2);
	}
	.progress-bar {
		flex: 1;
		height: 6px;
		background: var(--border);
		border-radius: var(--r-pill);
		overflow: hidden;
	}
	.progress-bar__fill {
		height: 100%;
		background: var(--positive);
		border-radius: var(--r-pill);
		transition: width 0.4s ease;
	}
	.progress-label {
		font-size: var(--fs-meta);
		font-weight: 600;
		font-variant-numeric: tabular-nums;
		color: var(--muted);
		white-space: nowrap;
	}

	/* ── Info section ────────────────────────────────────────────────── */
	.info-section {
		padding-bottom: var(--sp-8);
	}
	.info-card {
		background: var(--surface);
		border: 1px solid var(--border);
		border-radius: 10px;
		padding: var(--sp-8);
		display: flex;
		flex-direction: column;
		gap: var(--sp-5);
		box-shadow: var(--shadow-card);
	}
	.info-text {
		font-size: var(--fs-body);
		color: var(--ink);
		line-height: 1.7;
		max-width: 640px;
	}
	.info-text strong {
		font-weight: 700;
		color: var(--accent);
	}
	.info-link {
		font-size: var(--fs-ui);
		font-weight: 600;
		color: var(--accent);
		text-decoration: none;
	}
	.info-link:hover {
		text-decoration: underline;
	}

	/* ── Empty state ─────────────────────────────────────────────────── */
	.empty {
		padding: var(--sp-10) 0;
		display: flex;
		flex-direction: column;
		gap: var(--sp-5);
	}
	.empty__text {
		font-size: var(--fs-h2);
		font-weight: 300;
		color: var(--muted);
	}
	.back {
		font-size: var(--fs-ui);
		color: var(--accent);
		text-decoration: none;
		font-weight: 600;
	}

	/* ── Responsive ──────────────────────────────────────────────────── */
	@media (max-width: 720px) {
		.page {
			padding: var(--sp-6) var(--sp-4);
		}
		.page-title {
			font-size: 2.25rem;
		}
		.kpi-grid {
			grid-template-columns: repeat(2, 1fr);
		}
	}
</style>
