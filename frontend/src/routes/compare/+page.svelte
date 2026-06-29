<script lang="ts">
	import type { PageData } from './$types';
	import SectionLabel from '$lib/components/primitives/SectionLabel.svelte';
	import { teamColorVar, badgeTextColor, flagCode } from '$lib/tokens';

	let { data }: { data: PageData } = $props();

	const type = $derived(data.type);
	const entities = $derived(data.entities ?? []);

	const TEAM_METRICS = [
		{ group: 'Possession', rows: [
			{ label: 'Avg xG', key: 'xg', fmt: (v: number) => v.toFixed(2) },
			{ label: 'Avg Possession', key: 'possession_pct', fmt: (v: number) => `${v.toFixed(1)}%` },
			{ label: 'Avg In Contest', key: 'in_contest_pct', fmt: (v: number) => `${v.toFixed(1)}%` },
		]},
		{ group: 'Attacking', rows: [
			{ label: 'Avg Goals', key: 'goals', fmt: (v: number) => v.toFixed(1) },
			{ label: 'Avg Shots', key: 'shots_total', fmt: (v: number) => v.toFixed(0) },
			{ label: 'Avg Line Breaks', key: 'completed_line_breaks', fmt: (v: number) => v.toFixed(0) },
		]},
		{ group: 'Defensive', rows: [
			{ label: 'Avg Goals Conceded', key: 'goals_conceded', fmt: (v: number) => v.toFixed(1) },
			{ label: 'Avg Tackles Won', key: 'tackles_won', fmt: (v: number) => v.toFixed(0) },
			{ label: 'Avg Interceptions', key: 'interceptions', fmt: (v: number) => v.toFixed(0) },
		]},
	];

	function getTeamVal(entity: any, key: string): number | null {
		const avgs = entity?.avgStats?.averages;
		if (!avgs) return null;
		const v = avgs[key];
		return v != null ? Number(v) : null;
	}

	function maxVal(key: string): number {
		return Math.max(...entities.map((e: any) => getTeamVal(e, key) ?? 0), 0.01);
	}
</script>

<svelte:head>
	<title>Compare {type === 'teams' ? 'Teams' : 'Players'} — EFI Data Engine</title>
</svelte:head>

<div class="page">
	<header class="page-header">
		<SectionLabel label="COMPARE" />
		<h1 class="page-title">
			{type === 'teams' ? 'Team Comparison' : type === 'players' ? 'Player Comparison' : 'Comparison'}
		</h1>
		<p class="page-sub">
			{#if entities.length >= 2}
				{entities.length} {type} selected · <a href="/{type}" class="back-link">← Change selection</a>
			{:else}
				<a href="/{type ?? 'teams'}" class="back-link">← Select entities to compare</a>
			{/if}
		</p>
	</header>

	{#if entities.length < 2}
		<div class="empty-state">
			<p>Select 2–{5} {type ?? 'entities'} from the <a href="/{type ?? 'teams'}">ranking page</a> to compare.</p>
		</div>
	{:else if type === 'teams'}
		<!-- ── TEAM HEADERS ──────────────────────────────────────────────── -->
		<section class="compare-section">
			<div class="section-divider"></div>
			<div class="compare-body">
				<div class="compare-grid" style="--cols: {entities.length}">
					<div class="metric-col">
						<div class="metric-header">Metric</div>
					</div>
					{#each entities as entity}
						{@const t = entity.team}
						<div class="entity-col">
							<div class="entity-header">
								{#if flagCode(t.short_code)}
									<span class="fi fi-{flagCode(t.short_code)} entity-flag" aria-hidden="true"></span>
								{/if}
								<span class="entity-badge" style="background:{teamColorVar(t.color)};color:{badgeTextColor(t.color)};">{t.short_code}</span>
								<a href="/teams/{t.id}" class="entity-name">{t.name}</a>
							</div>
						</div>
					{/each}

					{#each TEAM_METRICS as grp}
						<div class="metric-group-label metric-col">{grp.group}</div>
						{#each Array(entities.length) as _}
							<div class="metric-group-label"></div>
						{/each}

						{#each grp.rows as row}
							{@const max = maxVal(row.key)}
							<div class="metric-col metric-label">{row.label}</div>
							{#each entities as entity}
								{@const val = getTeamVal(entity, row.key)}
								<div class="entity-col metric-cell">
									{#if val != null}
										<div class="bar-wrap">
											<div class="bar" style="width:{(val / max) * 100}%; background:{teamColorVar(entity.team.color)};"></div>
										</div>
										<span class="metric-val">{row.fmt(val)}</span>
									{:else}
										<span class="metric-dash">—</span>
									{/if}
								</div>
							{/each}
						{/each}
					{/each}
				</div>
			</div>
		</section>
	{:else if type === 'players'}
		<section class="compare-section">
			<div class="section-divider"></div>
			<div class="compare-body">
				<p class="coming-soon">Full player comparison view coming in the next session — stat rows with bar charts, position-aware metric selection.</p>
				<div class="player-cards">
					{#each entities as entity}
						{@const p = entity.player ?? entity}
						<a href="/players/{p.id}" class="player-card">
							<span class="player-card__pos">{p.position}</span>
							<span class="player-card__name">{p.name}</span>
							<span class="player-card__team">{p.team?.short_code ?? ''}</span>
						</a>
					{/each}
				</div>
			</div>
		</section>
	{/if}
</div>

<style>
	.page {
		padding: 40px var(--sp-8);
		display: flex;
		flex-direction: column;
		gap: var(--sp-10);
	}
	.page-header { display: flex; flex-direction: column; gap: var(--sp-3); }
	.page-title { font-size: var(--fs-hero); font-weight: 800; line-height: 1.05; color: var(--ink); }
	.page-sub { font-size: var(--fs-ui); font-weight: 500; color: var(--muted); }
	.back-link { color: var(--accent); text-decoration: none; font-weight: 600; }
	.back-link:hover { text-decoration: underline; }

	.section-divider { height: 1px; background: var(--border); }

	.compare-section { display: flex; flex-direction: column; }
	.compare-body { padding: var(--sp-8); overflow-x: auto; }

	.compare-grid {
		display: grid;
		grid-template-columns: 200px repeat(var(--cols), 1fr);
		gap: 0;
		min-width: 500px;
	}

	.metric-col { padding: var(--sp-2) var(--sp-3); }
	.entity-col { padding: var(--sp-2) var(--sp-3); }

	.metric-header, .entity-header {
		padding: var(--sp-3) var(--sp-3);
		font-size: var(--fs-meta);
		font-weight: 700;
		text-transform: uppercase;
		letter-spacing: 0.06em;
		color: var(--muted);
		border-bottom: 2px solid var(--border);
	}
	.entity-header {
		display: flex;
		align-items: center;
		gap: var(--sp-2);
		color: var(--ink);
	}
	.entity-flag { width: 24px; height: 16px; border-radius: 2px; }
	.entity-badge {
		display: inline-flex; align-items: center; justify-content: center;
		padding: 2px 6px; border-radius: var(--r-sm);
		font-size: var(--fs-meta); font-weight: 800; letter-spacing: 0.06em;
		flex-shrink: 0;
	}
	.entity-name {
		font-size: var(--fs-ui); font-weight: 700; color: var(--ink);
		text-decoration: none; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
	}
	.entity-name:hover { color: var(--accent); }

	.metric-group-label {
		font-size: var(--fs-meta); font-weight: 700;
		text-transform: uppercase; letter-spacing: 0.08em;
		color: var(--muted);
		padding: var(--sp-4) var(--sp-3) var(--sp-2);
		border-bottom: 1px solid var(--border);
	}

	.metric-label {
		font-size: var(--fs-ui); color: var(--muted); font-weight: 500;
		display: flex; align-items: center;
		border-bottom: 1px solid var(--border-soft);
	}

	.metric-cell {
		display: flex; flex-direction: column; gap: 4px; justify-content: center;
		border-bottom: 1px solid var(--border-soft);
	}
	.bar-wrap { height: 6px; background: var(--border-soft); border-radius: var(--r-pill); overflow: hidden; }
	.bar { height: 100%; border-radius: var(--r-pill); transition: width 0.4s ease; }
	.metric-val { font-size: var(--fs-meta); font-weight: 700; font-variant-numeric: tabular-nums; color: var(--ink); }
	.metric-dash { font-size: var(--fs-meta); color: var(--muted); }

	.empty-state {
		padding: var(--sp-10) 0;
		font-size: var(--fs-h2); font-weight: 300; color: var(--muted);
	}
	.empty-state a { color: var(--accent); }

	.coming-soon {
		font-size: var(--fs-ui); color: var(--muted); font-style: italic;
		padding: var(--sp-4) 0;
	}
	.player-cards {
		display: flex; gap: var(--sp-4); flex-wrap: wrap;
	}
	.player-card {
		display: flex; flex-direction: column; gap: var(--sp-1);
		padding: var(--sp-4) var(--sp-5);
		border: 1px solid var(--border); border-radius: var(--r-md);
		text-decoration: none;
		transition: border-color 0.15s;
	}
	.player-card:hover { border-color: var(--accent); }
	.player-card__pos { font-size: var(--fs-meta); font-weight: 700; text-transform: uppercase; color: var(--muted); }
	.player-card__name { font-size: var(--fs-ui); font-weight: 700; color: var(--ink); }
	.player-card__team { font-size: var(--fs-meta); color: var(--muted); }

	@media (max-width: 720px) {
		.page { padding: var(--sp-6) var(--sp-4); }
		.page-title { font-size: 2.25rem; }
	}
</style>
