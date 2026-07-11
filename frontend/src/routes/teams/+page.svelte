<script lang="ts">
	import type { PageData } from './$types';
	import SectionLabel from '$lib/components/primitives/SectionLabel.svelte';
	import TermTooltip from '$lib/components/layout/TermTooltip.svelte';
	import { teamTextColor, flagCode } from '$lib/tokens';
	import { t } from '$lib/i18n';
	import { toggleComparison, isSelected, getComparisonIds, MAX_COMPARISON } from '$lib/stores/comparison.svelte';

	let { data }: { data: PageData } = $props();

	interface TeamRanking {
		team: { id: number; name: string; short_code: string; color: string; slug: string };
		played: number;
		goals_scored: number;
		goals_conceded: number;
		goal_diff: number;
		avg_possession: number | null;
		avg_xg: number | null;
		avg_in_contest: number | null;
	}

	interface TopScorer {
		player_id: number; name: string; position: string; jersey_number: number | null;
		team: { id: number; name: string; short_code: string; color: string };
		goals: number; appearances: number; minutes: number;
	}
	interface MostCarded {
		player_id: number; name: string; position: string;
		team: { id: number; name: string; short_code: string; color: string };
		yellow_cards: number; red_cards: number; appearances: number;
	}

	const teamRankings: TeamRanking[] = $derived(data.leaderboards?.team_rankings ?? []);
	const topScorers: TopScorer[] = $derived((data.leaderboards?.top_scorers ?? []).slice(0, 15));
	const mostCarded: MostCarded[] = $derived((data.leaderboards?.most_carded ?? []).slice(0, 15));

	type RankSort = 'goals' | 'possession' | 'xg' | 'conceded';
	let rankSort: RankSort = $state('goals');
	let rankDir = $state<1 | -1>(-1);

	function setRankSort(key: RankSort) {
		if (rankSort === key) rankDir = rankDir === -1 ? 1 : -1;
		else { rankSort = key; rankDir = -1; }
	}

	// defined in the script block so no `as const` assertion sits in template markup
	const RANK_SORT_PILLS = $derived([
		{ key: 'goals', label: $t.teams.sortGoals },
		{ key: 'possession', label: $t.teams.sortPossession },
		{ key: 'xg', label: $t.teams.sortXg },
		{ key: 'conceded', label: $t.teams.sortConceded },
	] as const);

	const sortedRankings = $derived(
		[...teamRankings].sort((a, b) => {
			let val = 0;
			if (rankSort === 'goals') val = b.goals_scored - a.goals_scored;
			else if (rankSort === 'possession') val = (b.avg_possession ?? 0) - (a.avg_possession ?? 0);
			else if (rankSort === 'xg') val = (b.avg_xg ?? 0) - (a.avg_xg ?? 0);
			else if (rankSort === 'conceded') val = a.goals_conceded - b.goals_conceded;
			return rankDir === -1 ? val : -val;
		})
	);

	const f = (v: number | null | undefined, suffix = '') => v != null ? `${v}${suffix}` : '—';

	const cmpIds = $derived(getComparisonIds());
	const cmpFull = $derived(cmpIds.length >= MAX_COMPARISON);
</script>

<svelte:head>
	<title>{$t.nav.teams} — EFI Data Engine</title>
</svelte:head>

<div class="page">
	<header class="page-header">
		<SectionLabel label={$t.teams.label} />
		<h1 class="page-title">{$t.teams.rankingTitle}</h1>
		<p class="page-sub">{teamRankings.length} {$t.teams.rankingSubtitle}</p>
		{#if data.error}
			<p class="error-note">{$t.error.loadFailed}</p>
		{/if}
		<div class="stage-pill-group" role="group" aria-label={$t.stage.ariaLabel}>
			<a href="?" class="stage-pill" class:stage-pill--active={!data.stage} aria-current={!data.stage ? 'true' : undefined}>{$t.stage.all}</a>
			<a href="?stage=group" class="stage-pill" class:stage-pill--active={data.stage === 'group'} aria-current={data.stage === 'group' ? 'true' : undefined}>{$t.stage.group}</a>
			<a href="?stage=knockout" class="stage-pill" class:stage-pill--active={data.stage === 'knockout'} aria-current={data.stage === 'knockout' ? 'true' : undefined}>{$t.stage.knockout}</a>
		</div>
	</header>

	<!-- ── RANKING TABLE ─────────────────────────────────────────────────── -->
	{#if sortedRankings.length > 0}
		<section class="ranking-section">
			<div class="rank-header-row">
				<SectionLabel label={$t.teams.sectionComparison} />
				<div class="sort-pills">
					<span class="sort-label">{$t.teams.sortBy}</span>
					<div class="sort-pill-group">
						{#each RANK_SORT_PILLS as s}
							<button
								class="sort-pill"
								class:sort-pill--active={rankSort === s.key}
								onclick={() => setRankSort(s.key)}
							>{s.label}{rankSort === s.key ? (rankDir === -1 ? ' ↓' : ' ↑') : ''}</button>
						{/each}
					</div>
				</div>
			</div>
			<div class="rank-table-wrap">
				<table class="rank-table">
					<thead>
						<tr>
							<th class="cmp-col" title={$t.a11y.selectForComparison}></th>
							<th class="rk">#</th>
							<th>{$t.teams.colNation}</th>
							<th class="num">{$t.teams.colPlayed}</th>
							<th class="num">{$t.teams.sortGoals}</th>
							<th class="num">{$t.teams.sortConceded}</th>
							<th class="num">{$t.teams.colGoalDiff}</th>
							<th class="num">{$t.teams.colAvgPoss}</th>
							<th class="num">{$t.teams.colAvgXg}</th>
							<th class="num"><TermTooltip term="In Contest" definition="Moments when neither team controls the ball — aerial duels, blocked passes, and other loose-ball situations.">{$t.teams.colInContest}</TermTooltip></th>
						</tr>
					</thead>
					<tbody>
						{#each sortedRankings as r, i}
							<tr class:cmp-selected={isSelected(r.team.id)}>
								<td class="cmp-col">
									<button
										class="cmp-check"
										class:cmp-check--on={isSelected(r.team.id)}
										disabled={!isSelected(r.team.id) && cmpFull}
										onclick={() => toggleComparison(r.team.id, 'teams')}
										aria-label={isSelected(r.team.id) ? $t.a11y.removeFromComparison : $t.a11y.addToComparison}
										title={!isSelected(r.team.id) && cmpFull ? `Max ${MAX_COMPARISON} teams` : ''}
									>
										{#if isSelected(r.team.id)}
											<svg width="10" height="8" viewBox="0 0 10 8" fill="none" aria-hidden="true"><path d="M1 4l3 3 5-6" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>
										{:else}+{/if}
									</button>
								</td>
								<td class="rk rank-num">{i + 1}</td>
								<td>
									<a href="/teams/{r.team.id}" class="nation-link">
										{#if flagCode(r.team.short_code)}
											<span class="fi fi-{flagCode(r.team.short_code)} nation-flag" aria-hidden="true"></span>
										{/if}
										<span class="nation-code" style="color: {teamTextColor(r.team.color)};">{r.team.short_code}</span>
										<span class="nation-name">{r.team.name}</span>
									</a>
								</td>
								<td class="num muted">{r.played}</td>
								<td class="num goals-col">{r.goals_scored}</td>
								<td class="num">{r.goals_conceded}</td>
								<td class="num" class:positive={r.goal_diff > 0} class:negative={r.goal_diff < 0}>
									{r.goal_diff > 0 ? '+' : ''}{r.goal_diff}
								</td>
								<td class="num">{f(r.avg_possession, '%')}</td>
								<td class="num">{r.avg_xg != null ? r.avg_xg.toFixed(2) : '—'}</td>
								<td class="num">{f(r.avg_in_contest, '%')}</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		</section>
	{/if}

	<!-- ── TOP SCORERS ──────────────────────────────────────────────────── -->
	{#if topScorers.length > 0}
		<section class="lb-section">
			<SectionLabel label={$t.teams.sectionTopScorers} />
			<div class="rank-table-wrap">
				<table class="rank-table">
					<thead>
						<tr>
							<th class="rk">#</th>
							<th>{$t.stats.player}</th>
							<th>{$t.stats.team}</th>
							<th class="num">{$t.teams.sortGoals}</th>
							<th class="num">{$t.players.colApps}</th>
							<th class="num">{$t.teams.colMin}</th>
						</tr>
					</thead>
					<tbody>
						{#each topScorers as p, i}
							<tr>
								<td class="rk rank-num">{i + 1}</td>
								<td>
									<a href="/players/{p.player_id}" class="player-link">{p.name}</a>
									<span class="pos-tag">{p.position}</span>
								</td>
								<td>
									<a href="/teams/{p.team.id}" class="nation-link">
										{#if flagCode(p.team.short_code)}
											<span class="fi fi-{flagCode(p.team.short_code)} nation-flag" aria-hidden="true"></span>
										{/if}
										<span class="nation-code" style="color: {teamTextColor(p.team.color)};">{p.team.short_code}</span>
									</a>
								</td>
								<td class="num goals-col">{p.goals}</td>
								<td class="num muted">{p.appearances}</td>
								<td class="num muted">{p.minutes}</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		</section>
	{/if}

	<!-- ── MOST CARDED ───────────────────────────────────────────────────── -->
	{#if mostCarded.length > 0}
		<section class="lb-section">
			<SectionLabel label={$t.teams.sectionDiscipline} />
			<div class="rank-table-wrap">
				<table class="rank-table">
					<thead>
						<tr>
							<th class="rk">#</th>
							<th>{$t.stats.player}</th>
							<th>{$t.stats.team}</th>
							<th class="num">{$t.players.colYellow}</th>
							<th class="num">{$t.players.colRed}</th>
							<th class="num">{$t.players.colApps}</th>
						</tr>
					</thead>
					<tbody>
						{#each mostCarded as p, i}
							<tr>
								<td class="rk rank-num">{i + 1}</td>
								<td>
									<a href="/players/{p.player_id}" class="player-link">{p.name}</a>
									<span class="pos-tag">{p.position}</span>
								</td>
								<td>
									<a href="/teams/{p.team.id}" class="nation-link">
										{#if flagCode(p.team.short_code)}
											<span class="fi fi-{flagCode(p.team.short_code)} nation-flag" aria-hidden="true"></span>
										{/if}
										<span class="nation-code" style="color: {teamTextColor(p.team.color)};">{p.team.short_code}</span>
									</a>
								</td>
								<td class="num card-yellow">{p.yellow_cards}</td>
								<td class="num card-red">{p.red_cards}</td>
								<td class="num muted">{p.appearances}</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		</section>
	{/if}

	{#if teamRankings.length === 0 && !data.error}
		<div class="empty">
			<p class="empty__text">{$t.teams.noData}</p>
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

	/* ── Stage filter ─────────────────────────────────────────────────── */
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
		text-decoration: none;
		cursor: pointer;
		transition: background 0.15s, color 0.15s;
		white-space: nowrap;
	}
	.stage-pill:hover { background: color-mix(in srgb, var(--ink) 10%, transparent); color: var(--ink); }
	.stage-pill--active {
		background: var(--accent);
		color: var(--accent-fg);
	}

	/* ── Ranking section ─────────────────────────────────────────────── */
	.ranking-section {
		display: flex;
		flex-direction: column;
		gap: var(--sp-4);
	}
	.rank-header-row {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: var(--sp-4);
		flex-wrap: wrap;
	}
	.sort-pills {
		display: flex;
		align-items: center;
		gap: var(--sp-3);
		flex-wrap: wrap;
	}
	.sort-label {
		font-size: var(--fs-meta);
		font-weight: 600;
		text-transform: uppercase;
		letter-spacing: 0.06em;
		color: var(--muted);
	}
	.sort-pill-group {
		display: flex;
		gap: 2px;
		background: var(--border);
		border-radius: var(--r-pill);
		padding: 2px;
		flex-wrap: wrap;
	}
	.sort-pill {
		padding: 4px var(--sp-3);
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
	.sort-pill:hover { background: color-mix(in srgb, var(--ink) 10%, transparent); color: var(--ink); }
	.sort-pill--active {
		background: var(--accent);
		color: var(--accent-fg);
	}
	.rank-table-wrap { overflow-x: auto; }
	.rank-table {
		width: 100%;
		min-width: 600px;
		border-collapse: collapse;
		font-size: var(--fs-ui);
	}
	.rank-table thead th {
		text-align: left;
		font-size: var(--fs-meta);
		font-weight: 700;
		text-transform: uppercase;
		letter-spacing: 0.06em;
		color: var(--muted);
		padding: var(--sp-2) var(--sp-3);
		border-bottom: 2px solid var(--border);
	}
	.rank-table thead th.num { text-align: right; }
	.rank-table tbody tr { border-bottom: 1px solid var(--border-soft); }
	.rank-table tbody tr:last-child { border-bottom: none; }
	.rank-table tbody tr:hover { background: var(--border-soft); }
	.rank-table td { padding: var(--sp-2) var(--sp-3); vertical-align: middle; }
	.rk { width: 36px; }
	.rank-num { font-size: var(--fs-meta); font-weight: 700; color: var(--muted); }
	.num { text-align: right; font-variant-numeric: tabular-nums; }
	.goals-col { font-weight: 800; color: var(--accent); }
	.positive { color: var(--c-teal-ink); font-weight: 700; }
	.negative { color: var(--c-red); font-weight: 700; }
	.muted { color: var(--muted); }

	/* ── Comparison checkbox ────────────────────────────────────────── */
	.cmp-col { width: 32px; padding-left: var(--sp-2) !important; padding-right: 0 !important; }
	.cmp-check {
		width: 22px;
		height: 22px;
		border: 2px solid var(--border);
		border-radius: var(--r-sm);
		background: transparent;
		color: var(--muted);
		font-size: 13px;
		font-weight: 800;
		cursor: pointer;
		display: inline-flex;
		align-items: center;
		justify-content: center;
		padding: 0;
		transition: border-color 0.15s, background 0.15s, color 0.15s;
		font-family: inherit;
		line-height: 1;
	}
	.cmp-check:hover:not(:disabled) { border-color: var(--accent); color: var(--accent); }
	.cmp-check--on { border-color: var(--accent); background: var(--accent); color: var(--accent-fg); }
	.cmp-check:disabled { opacity: 0.35; cursor: not-allowed; }
	.cmp-selected { background: color-mix(in srgb, var(--accent) 5%, transparent) !important; }

	/* ── Nation link ─────────────────────────────────────────────────── */
	.nation-link {
		display: flex;
		align-items: center;
		gap: var(--sp-2);
		text-decoration: none;
	}
	.nation-link:hover .nation-name { color: var(--accent); text-decoration: underline; }
	.nation-flag {
		width: 24px;
		height: 16px;
		border-radius: 2px;
		flex-shrink: 0;
		box-shadow: 0 1px 3px rgba(0,0,0,0.12);
	}
	.nation-code {
		font-size: var(--fs-label);
		font-weight: 800;
		letter-spacing: 0.04em;
		flex-shrink: 0;
	}
	.nation-name {
		font-size: var(--fs-ui);
		font-weight: 600;
		color: var(--ink);
	}

	/* ── Leaderboard sections ────────────────────────────────────────── */
	.lb-section {
		display: flex;
		flex-direction: column;
		gap: var(--sp-4);
	}
	.player-link {
		font-weight: 700;
		color: var(--ink);
		text-decoration: none;
	}
	.player-link:hover { color: var(--accent); text-decoration: underline; }
	.pos-tag {
		font-size: var(--fs-meta);
		font-weight: 600;
		color: var(--muted);
		margin-left: var(--sp-2);
	}
	.card-yellow { font-weight: 800; color: var(--c-yellow-ink); }
	.card-red { font-weight: 800; color: var(--c-red); }

	/* ── Empty state ─────────────────────────────────────────────────── */
	.empty { padding: var(--sp-10) 0; }
	.empty__text { font-size: var(--fs-h2); font-weight: 300; color: var(--muted); }

	/* ── Responsive ──────────────────────────────────────────────────── */
	@media (max-width: 720px) {
		.page { padding: var(--sp-6) var(--sp-4); }
		.page-title { font-size: 2.25rem; }
	}
</style>
