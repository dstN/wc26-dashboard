<script lang="ts">
	import type { PageData } from './$types';
	import type { MatchMeta } from '$lib/types/efi';
	import SectionLabel from '$lib/components/primitives/SectionLabel.svelte';
	import { teamColorVar, flagCode, badgeTextColor } from '$lib/tokens';
	import { t } from '$lib/i18n';
	import { goto } from '$app/navigation';
	import { toggleComparison, isSelected, getComparisonIds, MAX_COMPARISON } from '$lib/stores/comparison.svelte';
	import { isKnockoutGroup, type StageFilter } from '$lib/stage';

	let { data }: { data: PageData } = $props();

	const cmpIds = $derived(getComparisonIds());
	const cmpFull = $derived(cmpIds.length >= MAX_COMPARISON);

	const matches: MatchMeta[] = $derived(data.matches ?? []);

	function isPending(m: MatchMeta): boolean {
		return m.score_a === 0 && m.score_b === 0 && !m.match_date;
	}

	// Compact "AET" / "AET · 3-4 pens" note under the scoreline. Built here
	// (not inline in markup) so no stray whitespace leaks into the rendered text.
	function scoreNote(m: MatchMeta): string {
		const parts: string[] = [];
		if (m.went_to_extra_time) parts.push($t.match.aet);
		if (m.penalty_score_a != null && m.penalty_score_b != null) {
			parts.push(`${m.penalty_score_a}-${m.penalty_score_b} ${$t.match.pensShort}`);
		}
		return parts.join(' · ');
	}

	function formatDate(raw: string): string {
		if (!raw) return '';
		try {
			return new Intl.DateTimeFormat('en-GB', {
				day: '2-digit',
				month: 'short',
				year: 'numeric'
			}).format(new Date(raw));
		} catch {
			return raw;
		}
	}

	// Filter state
	let filterGroup = $state('');
	let stageFilter: StageFilter = $state('all');

	const STAGE_OPTIONS = $derived([
		{ key: 'all' as const, label: $t.stage.all },
		{ key: 'group' as const, label: $t.stage.group },
		{ key: 'knockout' as const, label: $t.stage.knockout },
	]);

	// Reset the group/round dropdown whenever the stage changes — a previously
	// selected round (e.g. "R32") is meaningless once "Group Stage" is picked.
	$effect(() => {
		stageFilter;
		filterGroup = '';
	});

	const stageFilteredMatches = $derived(
		stageFilter === 'all'
			? matches
			: matches.filter((m) => isKnockoutGroup(m.group_letter) === (stageFilter === 'knockout'))
	);

	// Knockout rounds carry short labels in group_letter (R32/R16/QF/SF/3RD/FIN)
	const ROUND_LABELS = $derived<Record<string, string>>({
		R32: $t.tournament.roundOf32,
		R16: $t.tournament.roundOf16,
		QF: $t.tournament.quarterFinals,
		SF: $t.tournament.semiFinals,
		'3RD': $t.tournament.thirdPlace,
		FIN: $t.tournament.final,
	});
	const ROUND_ORDER = ['R32', 'R16', 'QF', 'SF', '3RD', 'FIN'];

	function groupHeading(g: string): string {
		// single letters are ALWAYS groups — guards group F against the FIN label
		if (!isKnockoutGroup(g)) return `${$t.match.group} ${g}`;
		return ROUND_LABELS[g] ?? `${$t.match.group} ${g}`;
	}

	// groups A–L alphabetically first, then knockout rounds in bracket order
	function groupSort(a: string, b: string): number {
		const ra = ROUND_ORDER.indexOf(a);
		const rb = ROUND_ORDER.indexOf(b);
		if (ra !== -1 || rb !== -1) {
			if (ra === -1) return -1;
			if (rb === -1) return 1;
			return ra - rb;
		}
		return a.localeCompare(b);
	}

	// All unique group letters for the filter dropdown (within the current stage)
	const allGroupKeys = $derived(
		[...new Set(stageFilteredMatches.map((m) => m.group_letter ?? '?'))].sort(groupSort)
	);

	const filteredMatches = $derived(
		filterGroup
			? stageFilteredMatches.filter((m) => (m.group_letter ?? '?') === filterGroup)
			: stageFilteredMatches
	);

	// Group matches by group letter
	const grouped = $derived(
		filteredMatches.reduce<Record<string, MatchMeta[]>>((acc, m) => {
			const key = m.group_letter ?? '?';
			(acc[key] ??= []).push(m);
			return acc;
		}, {})
	);

	const groupKeys = $derived(Object.keys(grouped).sort(groupSort));
</script>

<svelte:head>
	<title>{$t.nav.matches} — EFI Data Engine</title>
</svelte:head>

<div class="page">
	<header class="page-header">
		<SectionLabel label={$t.match.allMatches} />
		<h1 class="page-title">{$t.match.overview}</h1>
		{#if data.error}
			<p class="error-note">{$t.error.loadFailed}</p>
		{/if}
		<div class="stage-pill-group" role="group" aria-label={$t.stage.ariaLabel}>
			{#each STAGE_OPTIONS as opt}
				<button
					class="stage-pill"
					class:stage-pill--active={stageFilter === opt.key}
					aria-pressed={stageFilter === opt.key}
					onclick={() => (stageFilter = opt.key)}
				>{opt.label}</button>
			{/each}
		</div>
		<div class="filter-bar">
			<select class="filter-select" bind:value={filterGroup} aria-label={$t.match.filterByGroup}>
				<option value="">{$t.match.allGroups}</option>
				{#each allGroupKeys as g}
					<option value={g}>{groupHeading(g)}</option>
				{/each}
			</select>
			{#if filterGroup}
				<button class="filter-clear" onclick={() => filterGroup = ''}>{$t.match.clearFilter}</button>
			{/if}
			<span class="filter-count" role="status" aria-live="polite">{filteredMatches.length} {$t.match.matches}</span>
		</div>
	</header>

	{#if matches.length === 0 && !data.error}
		<div class="empty">
			<p class="empty__text">{$t.match.noMatches}</p>
		</div>
	{:else}
		{#each groupKeys as gKey}
			<section class="group-section">
				<div class="group-header">
					<span class="group-letter">{groupHeading(gKey)}</span>
					<span class="group-count">{grouped[gKey].length} {$t.match.matches}</span>
				</div>
				<div class="cards-grid">
					{#each grouped[gKey] as match (match.id)}
						{@const pending = isPending(match)}
						<div class="match-card-link" role="link" tabindex="0"
							onclick={() => goto(`/matches/${match.id}`)}
							onkeydown={(e) => e.key === 'Enter' && goto(`/matches/${match.id}`)}>
						<article class="match-card">
							<div class="match-card__top">
								<abbr title="{groupHeading(gKey)} · {$t.match.matchNo} {match.match_no}" class="group-badge">
									{gKey}<span class="group-badge__num">·{match.match_no}</span>
								</abbr>
								<div class="card-top-right">
									{#if pending}
										<span class="status-badge status-badge--pending">{$t.match.pending}</span>
									{:else}
										<span class="status-badge status-badge--played">{$t.match.played}</span>
									{/if}
									<button
										class="cmp-check"
										class:cmp-check--on={isSelected(match.id)}
										disabled={!isSelected(match.id) && cmpFull}
										aria-label={isSelected(match.id) ? $t.a11y.removeFromComparison : $t.a11y.addToComparison}
										onclick={(e) => { e.stopPropagation(); toggleComparison(match.id, 'matches'); }}
									>
										{#if isSelected(match.id)}
											<svg width="10" height="8" viewBox="0 0 10 8" fill="none" aria-hidden="true"><path d="M1 4l3 3 5-6" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>
										{:else}+{/if}
									</button>
								</div>
							</div>

							<div class="match-card__score-row">
								<div class="team-side">
									<div class="team-side__top">
										{#if flagCode(match.team_a.short_code)}
											<span class="fi fi-{flagCode(match.team_a.short_code)} card-flag" aria-hidden="true"></span>
										{/if}
										<span
											class="team-badge"
											style="background: {teamColorVar(match.team_a.color)}; color: {badgeTextColor(match.team_a.color)};"
											aria-label={match.team_a.name}
										>
											{match.team_a.short_code}
										</span>
									</div>
									<a href="/teams/{match.team_a.id}" class="team-name">{match.team_a.name}</a>
									{#if match.formation_a}
										<span class="team-formation">{match.formation_a}</span>
									{/if}
								</div>

								<div class="score-block">
									{#if pending}
										<span class="score score--pending">–:–</span>
									{:else}
										<span class="score">{match.score_a}:{match.score_b}</span>
										{#if match.went_to_extra_time || match.penalty_score_a != null}
											<span class="score-note">{scoreNote(match)}</span>
										{/if}
									{/if}
								</div>

								<div class="team-side team-side--right">
									<div class="team-side__top">
										<span
											class="team-badge"
											style="background: {teamColorVar(match.team_b.color)}; color: {badgeTextColor(match.team_b.color)};"
											aria-label={match.team_b.name}
										>
											{match.team_b.short_code}
										</span>
										{#if flagCode(match.team_b.short_code)}
											<span class="fi fi-{flagCode(match.team_b.short_code)} card-flag" aria-hidden="true"></span>
										{/if}
									</div>
									<a href="/teams/{match.team_b.id}" class="team-name">{match.team_b.name}</a>
									{#if match.formation_b}
										<span class="team-formation">{match.formation_b}</span>
									{/if}
								</div>
							</div>

							<div class="match-card__meta">
								{#if match.venue}
									<span class="meta-item">{match.venue}</span>
								{/if}
								{#if match.match_date}
									<span class="meta-sep">·</span>
									<span class="meta-item">{formatDate(match.match_date)}</span>
								{/if}
							</div>
						</article>
						</div>
					{/each}
				</div>
			</section>
		{/each}
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
	.error-note {
		font-size: var(--fs-meta);
		color: var(--c-red);
		margin-top: var(--sp-1);
	}

	/* ── Stage filter ─────────────────────────────────────────────── */
	.stage-pill-group {
		display: flex;
		gap: 2px;
		background: var(--border);
		border-radius: var(--r-pill);
		padding: 2px;
		width: fit-content;
		flex-wrap: wrap;
	}
	.stage-pill {
		padding: 4px var(--sp-4);
		border: none;
		border-radius: var(--r-pill);
		background: transparent;
		font-size: var(--fs-meta);
		font-weight: 600;
		font-family: inherit;
		color: var(--muted);
		cursor: pointer;
		transition: background 0.15s, color 0.15s;
		white-space: nowrap;
	}
	.stage-pill:hover { background: color-mix(in srgb, var(--ink) 10%, transparent); color: var(--ink); }
	.stage-pill--active {
		background: var(--accent);
		color: var(--accent-fg);
	}

	/* ── Filter bar ───────────────────────────────────────────────── */
	.filter-bar {
		display: flex;
		align-items: center;
		gap: var(--sp-3);
		flex-wrap: wrap;
	}
	.filter-select {
		height: 38px;
		padding: 0 var(--sp-3);
		border: 1px solid var(--border);
		border-radius: var(--r-sm);
		background: var(--surface);
		color: var(--ink);
		font-size: var(--fs-ui);
		font-family: inherit;
		min-width: 200px;
	}
	.filter-clear {
		height: 38px;
		padding: 0 var(--sp-4);
		border: 1px solid var(--border);
		border-radius: var(--r-sm);
		background: transparent;
		color: var(--muted);
		font-size: var(--fs-ui);
		font-family: inherit;
		cursor: pointer;
	}
	.filter-clear:hover { color: var(--ink); border-color: var(--ink); }
	.filter-count {
		font-size: var(--fs-label);
		font-weight: 600;
		text-transform: uppercase;
		letter-spacing: 0.06em;
		color: var(--muted);
	}

	/* ── Empty state ─────────────────────────────────────────────────── */
	.empty {
		padding: var(--sp-10) 0;
	}
	.empty__text {
		font-size: var(--fs-h2);
		font-weight: 300;
		color: var(--muted);
	}

	/* ── Group section ───────────────────────────────────────────────── */
	.group-section {
		display: flex;
		flex-direction: column;
		gap: var(--sp-5);
	}
	.group-header {
		display: flex;
		align-items: baseline;
		gap: var(--sp-3);
	}
	.group-letter {
		font-size: var(--fs-h2);
		font-weight: 700;
		color: var(--ink);
	}
	.group-count {
		font-size: var(--fs-label);
		font-weight: 600;
		text-transform: uppercase;
		letter-spacing: 0.08em;
		color: var(--muted);
	}

	/* ── Cards grid ──────────────────────────────────────────────────── */
	.cards-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
		gap: var(--sp-5);
	}

	/* ── Match card link wrapper ─────────────────────────────────────── */
	.match-card-link {
		display: block;
		cursor: pointer;
		border-radius: var(--r-md);
		transition: transform 0.12s ease, box-shadow 0.12s ease;
	}
	.match-card-link:hover {
		transform: translateY(-2px);
	}
	.match-card-link:hover .match-card {
		box-shadow: 0 6px 20px color-mix(in srgb, var(--ink) 10%, transparent);
		border-color: var(--accent);
	}

	/* ── Match card ──────────────────────────────────────────────────── */
	.match-card {
		background: var(--surface);
		border: 1px solid var(--border);
		border-radius: var(--r-md);
		padding: 20px;
		display: flex;
		flex-direction: column;
		gap: var(--sp-4);
		box-shadow: var(--shadow-card);
	}

	.match-card__top {
		display: flex;
		align-items: center;
		justify-content: space-between;
	}
	.card-top-right {
		display: flex;
		align-items: center;
		gap: var(--sp-2);
	}
	.cmp-check {
		width: 22px; height: 22px;
		border: 2px solid var(--border);
		border-radius: var(--r-sm);
		background: transparent;
		color: var(--muted);
		font-size: 13px; font-weight: 800;
		cursor: pointer;
		display: inline-flex; align-items: center; justify-content: center;
		padding: 0;
		transition: border-color 0.15s, background 0.15s, color 0.15s;
		font-family: inherit; line-height: 1;
		flex-shrink: 0;
	}
	.cmp-check:hover:not(:disabled) { border-color: var(--accent); color: var(--accent); }
	.cmp-check--on { border-color: var(--accent); background: var(--accent); color: var(--accent-fg); }
	.cmp-check:disabled { opacity: 0.35; cursor: not-allowed; }

	/* Group badge */
	abbr.group-badge { text-decoration: none; cursor: help; }
	.group-badge {
		font-size: var(--fs-label);
		font-weight: 700;
		text-transform: uppercase;
		letter-spacing: 0.1em;
		color: var(--accent);
	}
	.group-badge__num {
		font-weight: 400;
		color: var(--muted);
	}

	/* Status badge */
	.status-badge {
		font-size: var(--fs-meta);
		font-weight: 600;
		text-transform: uppercase;
		letter-spacing: 0.08em;
		padding: 2px var(--sp-2);
		border-radius: var(--r-pill);
	}
	.status-badge--played {
		background: color-mix(in srgb, var(--positive) 12%, transparent);
		color: var(--positive);
	}
	.status-badge--pending {
		background: color-mix(in srgb, var(--muted) 12%, transparent);
		color: var(--muted);
	}

	/* Score row */
	.match-card__score-row {
		display: grid;
		grid-template-columns: 1fr auto 1fr;
		align-items: flex-start;
		gap: var(--sp-3);
	}

	.team-side {
		display: flex;
		flex-direction: column;
		align-items: flex-start;
		gap: var(--sp-1);
		min-width: 0;
	}
	.team-side--right {
		align-items: flex-end;
	}
	.team-side__top {
		display: flex;
		align-items: center;
		gap: var(--sp-2);
	}
	.card-flag {
		width: 28px;
		height: 19px;
		border-radius: 2px;
		flex-shrink: 0;
		box-shadow: 0 1px 3px rgba(0,0,0,0.15);
	}

	.team-badge {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		width: 36px;
		height: 36px;
		border-radius: var(--r-md);
		font-size: var(--fs-meta);
		font-weight: 700;
		color: #fff;
		letter-spacing: 0.04em;
		flex-shrink: 0;
	}

	.team-name {
		font-size: var(--fs-ui);
		font-weight: 600;
		color: var(--ink);
		text-decoration: none;
		line-height: 1.2;
		white-space: normal;
	}
	.team-name:hover { color: var(--accent); }
	.team-side--right .team-name { text-align: right; }
	.team-formation {
		font-size: var(--fs-meta);
		color: var(--muted);
		font-family: var(--font-mono, monospace);
	}

	.score-block {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		gap: 2px;
		flex-shrink: 0;
	}
	.score {
		font-size: var(--fs-score);
		font-weight: 900;
		font-variant-numeric: tabular-nums;
		color: var(--ink);
		line-height: 1;
	}
	.score-note {
		font-size: var(--fs-meta);
		font-weight: 700;
		text-transform: uppercase;
		letter-spacing: 0.04em;
		color: var(--accent);
		white-space: nowrap;
	}
	.score--pending {
		color: var(--muted);
		font-weight: 300;
	}

	/* Meta row */
	.match-card__meta {
		display: flex;
		align-items: center;
		gap: var(--sp-2);
		flex-wrap: wrap;
	}
	.meta-item {
		font-size: var(--fs-meta);
		color: var(--muted);
		font-weight: 500;
	}
	.meta-sep {
		color: var(--border);
		font-size: var(--fs-meta);
	}

	/* ── Responsive ──────────────────────────────────────────────────── */
	@media (max-width: 720px) {
		.page {
			padding: var(--sp-6) var(--sp-4);
		}
		.page-title {
			font-size: 2.25rem;
		}
		.cards-grid {
			grid-template-columns: 1fr;
		}
	}
</style>
