<script lang="ts">
	import type { PageData } from './$types';
	import SectionLabel from '$lib/components/primitives/SectionLabel.svelte';
	import { teamColorVar, badgeTextColor, flagCode } from '$lib/tokens';
	import { goto } from '$app/navigation';
	import { t } from '$lib/i18n';

	let { data }: { data: PageData } = $props();

	const type = $derived(data.type);
	const ids = $derived(data.ids ?? []);
	const entities = $derived(data.entities ?? []);
	const searchOptions = $derived(data.searchOptions ?? []);

	const MAX = 5;
	const isFull = $derived(entities.length >= MAX);

	// ── Search ─────────────────────────────────────────────────────────────────
	let searchQuery = $state('');
	// Active option for keyboard navigation of the combobox listbox (-1 = none).
	let activeIndex = $state(-1);

	const searchLabel = $derived(
		isFull
			? $t.compare.maxSelected
			: type === 'teams'
				? $t.compare.addTeam
				: type === 'players'
					? $t.compare.addPlayer
					: $t.compare.addMatch
	);

	const filteredOptions = $derived(
		searchQuery.length >= 2 && !isFull
			? searchOptions
					.filter(
						(o: any) =>
							o.name.toLowerCase().includes(searchQuery.toLowerCase()) &&
							!ids.includes(o.id)
					)
					.slice(0, 8)
			: []
	);

	function addEntity(id: number) {
		const newIds = [...ids, id];
		goto(`/compare?type=${type}&ids=${newIds.join(',')}`);
		searchQuery = '';
		activeIndex = -1;
	}

	// Keyboard operation of the combobox: arrows move the highlight, Enter picks
	// the active (or first) option, Escape clears. Makes the search fully usable
	// without a mouse (the options themselves select on pointer-down).
	function onSearchKeydown(e: KeyboardEvent) {
		const n = filteredOptions.length;
		if (e.key === 'ArrowDown') {
			e.preventDefault();
			if (n) activeIndex = (activeIndex + 1) % n;
		} else if (e.key === 'ArrowUp') {
			e.preventDefault();
			if (n) activeIndex = (activeIndex - 1 + n) % n;
		} else if (e.key === 'Enter') {
			const opt = filteredOptions[activeIndex] ?? filteredOptions[0];
			if (opt) {
				e.preventDefault();
				addEntity(opt.id);
			}
		} else if (e.key === 'Escape') {
			searchQuery = '';
			activeIndex = -1;
		}
	}

	function removeEntity(id: number) {
		const newIds = ids.filter((i: number) => i !== id);
		if (newIds.length === 0) goto(`/${type ?? 'teams'}`);
		else goto(`/compare?type=${type}&ids=${newIds.join(',')}`);
	}

	// Compact "AET" / "AET · 3-4 pens" note under a compared match's score.
	function scoreNote(m: { went_to_extra_time?: boolean; penalty_score_a?: number | null; penalty_score_b?: number | null }): string {
		const parts: string[] = [];
		if (m.went_to_extra_time) parts.push($t.match.aet);
		if (m.penalty_score_a != null && m.penalty_score_b != null) {
			parts.push(`${m.penalty_score_a}-${m.penalty_score_b} ${$t.match.pensShort}`);
		}
		return parts.join(' · ');
	}

	// ── Match metrics ──────────────────────────────────────────────────────────
	// Defined in the script block (not inline in the template) so labels are
	// translatable and no TS annotations leak into template markup.
	const MATCH_SCORE_METRICS = $derived([
		{ label: $t.compare.mTotalGoals, fn: (e: any) => (e.score_a ?? 0) + (e.score_b ?? 0), fmt: (v: number) => String(v) },
		{ label: $t.compare.mGoalsHome, fn: (e: any) => e.score_a ?? 0, fmt: (v: number) => String(v) },
		{ label: $t.compare.mGoalsAway, fn: (e: any) => e.score_b ?? 0, fmt: (v: number) => String(v) },
	]);
	const MATCH_POSSESSION_METRICS = $derived([
		{ label: $t.compare.mXgHome, key: 'xg_a', fmt: (v: number) => v.toFixed(2) },
		{ label: $t.compare.mXgAway, key: 'xg_b', fmt: (v: number) => v.toFixed(2) },
		{ label: $t.compare.mPossession, key: 'possession_team_a', fmt: (v: number) => `${v.toFixed(1)}%` },
		{ label: $t.compare.mInContest, key: 'possession_in_contest', fmt: (v: number) => `${v.toFixed(1)}%` },
		{ label: $t.compare.mTotalShots, key: 'shots_total', fmt: (v: number) => String(v) },
	]);
	function matchMetricVals(rowKey: string): (number | null)[] {
		return entities.map((e: any) => {
			const v = e.possession?.[rowKey];
			return v != null ? Number(v) : null;
		});
	}

	// ── Team metrics ───────────────────────────────────────────────────────────
	const TEAM_METRICS = $derived([
		{
			group: $t.compare.grpPossession,
			rows: [
				{ label: $t.compare.avgXg, key: 'xg', fmt: (v: number) => v.toFixed(2) },
				{ label: $t.compare.avgXgConceded, key: 'xg_conceded', fmt: (v: number) => v.toFixed(2) },
				{ label: $t.compare.avgPossession, key: 'possession_pct', fmt: (v: number) => `${v.toFixed(1)}%` },
				{ label: $t.compare.avgInContest, key: 'in_contest_pct', fmt: (v: number) => `${v.toFixed(1)}%` },
				{ label: $t.compare.avgShots, key: 'shots_total', fmt: (v: number) => v.toFixed(0) },
				{ label: $t.compare.avgShotsOnTarget, key: 'shots_on_target', fmt: (v: number) => v.toFixed(0) },
			],
		},
		{
			group: $t.compare.grpAttacking,
			rows: [
				{ label: $t.compare.avgGoals, key: 'goals', fmt: (v: number) => v.toFixed(1) },
				{ label: $t.compare.avgLineBreaks, key: 'completed_line_breaks', fmt: (v: number) => v.toFixed(0) },
				{ label: $t.compare.avgBallProgressions, key: 'ball_progressions', fmt: (v: number) => v.toFixed(0) },
				{ label: $t.compare.avgTakeOns, key: 'take_ons', fmt: (v: number) => v.toFixed(0) },
				{ label: $t.compare.avgCrosses, key: 'crosses', fmt: (v: number) => v.toFixed(0) },
				{ label: $t.compare.avgCorners, key: 'corners', fmt: (v: number) => v.toFixed(0) },
				{ label: $t.compare.avgSetPlays, key: 'set_plays', fmt: (v: number) => v.toFixed(0) },
			],
		},
		{
			group: $t.compare.grpPassing,
			rows: [
				{ label: $t.compare.avgPassesAtt, key: 'passes_attempted', fmt: (v: number) => v.toFixed(0) },
				{ label: $t.compare.avgPassesComp, key: 'passes_completed', fmt: (v: number) => v.toFixed(0) },
				{ label: $t.compare.avgPressing, key: 'pressing_direct', fmt: (v: number) => v.toFixed(0) },
			],
		},
		{
			group: $t.compare.grpDefensive,
			rows: [
				{ label: $t.compare.avgGoalsConceded, key: 'goals_conceded', fmt: (v: number) => v.toFixed(1) },
				{ label: $t.compare.avgDefLineBreaks, key: 'defensive_line_breaks', fmt: (v: number) => v.toFixed(0) },
				{ label: $t.compare.avgForcedTurnovers, key: 'forced_turnovers', fmt: (v: number) => v.toFixed(0) },
				{ label: $t.compare.avgTacklesWon, key: 'tackles_won', fmt: (v: number) => v.toFixed(0) },
				{ label: $t.compare.avgInterceptions, key: 'interceptions', fmt: (v: number) => v.toFixed(0) },
				{ label: $t.compare.avgClearances, key: 'clearances', fmt: (v: number) => v.toFixed(0) },
				{ label: $t.compare.avgAerialDuels, key: 'duels_won_aerial', fmt: (v: number) => v.toFixed(0) },
				{ label: $t.compare.avgPhysicalDuels, key: 'duels_won_physical', fmt: (v: number) => v.toFixed(0) },
			],
		},
		{
			group: $t.compare.grpPhysical,
			rows: [
				{ label: $t.compare.avgDistance, key: 'total_distance_km', fmt: (v: number) => v.toFixed(1) },
			],
		},
	]);

	function getTeamVal(entity: any, key: string): number | null {
		const avgs = entity?.avgStats?.averages;
		if (!avgs) return null;
		const v = avgs[key];
		return v != null ? Number(v) : null;
	}

	function maxTeamVal(key: string): number {
		return Math.max(...entities.map((e: any) => getTeamVal(e, key) ?? 0), 0.01);
	}

	// ── Player metrics ─────────────────────────────────────────────────────────
	const PLAYER_METRICS = $derived([
		{
			group: $t.compare.grpGeneral,
			rows: [
				{ label: $t.players.colApps, key: 'appearances', fmt: (v: number) => String(v) },
				{ label: $t.keyStats.goals, key: 'goals', fmt: (v: number) => String(v) },
				{ label: $t.playerDetail.minutes, key: 'minutes_played', fmt: (v: number) => `${v}'` },
				{ label: $t.players.colShots, key: 'attempts_at_goal', fmt: (v: number) => String(v ?? 0) },
				{ label: $t.keyStats.takeOns, key: 'take_ons', fmt: (v: number) => String(v ?? 0) },
				{ label: $t.players.colBallProgs, key: 'ball_progressions', fmt: (v: number) => String(v ?? 0) },
				{ label: $t.playerDetail.yellowCards, key: 'yellow_cards', fmt: (v: number) => String(v) },
				{ label: $t.playerDetail.redCards, key: 'red_cards', fmt: (v: number) => String(v) },
			],
		},
		{
			group: $t.compare.grpPassing,
			rows: [
				{ label: $t.playerDetail.passesAtt, key: 'passes_attempted', fmt: (v: number) => String(v ?? 0) },
				{ label: $t.compare.passesComp, key: 'passes_completed', fmt: (v: number) => String(v ?? 0) },
				{ label: $t.compare.passCompPct, key: 'pass_completion_pct', fmt: (v: number) => v != null ? `${v}%` : '—' },
				{ label: $t.playerDetail.crossesAtt, key: 'crosses_attempted', fmt: (v: number) => String(v ?? 0) },
				{ label: $t.compare.crossesComp, key: 'crosses_completed', fmt: (v: number) => String(v ?? 0) },
				{ label: $t.teams.statLineBreaks, key: 'lb_completed', fmt: (v: number) => String(v ?? 0) },
				{ label: $t.compare.lbAtt, key: 'lb_attempted', fmt: (v: number) => String(v ?? 0) },
				{ label: $t.playerDetail.switchesOfPlay, key: 'switches_of_play', fmt: (v: number) => String(v ?? 0) },
				{ label: $t.playerDetail.stepIns, key: 'step_ins', fmt: (v: number) => String(v ?? 0) },
			],
		},
		{
			group: $t.compare.grpDefensive,
			rows: [
				{ label: $t.playerDetail.tacklesMade, key: 'tackles_made', fmt: (v: number) => String(v ?? 0) },
				{ label: $t.teams.statTacklesWon, key: 'tackles_won', fmt: (v: number) => String(v ?? 0) },
				{ label: $t.keyStats.interceptions, key: 'interceptions', fmt: (v: number) => String(v ?? 0) },
				{ label: $t.keyStats.blocks, key: 'blocks', fmt: (v: number) => String(v ?? 0) },
				{ label: $t.keyStats.clearances, key: 'clearances', fmt: (v: number) => String(v ?? 0) },
				{ label: $t.keyStats.regains, key: 'possession_regains', fmt: (v: number) => String(v ?? 0) },
				{ label: $t.keyStats.aerialDuels, key: 'duels_won_aerial', fmt: (v: number) => String(v ?? 0) },
				{ label: $t.keyStats.physicalDuels, key: 'duels_won_physical', fmt: (v: number) => String(v ?? 0) },
				{ label: $t.compare.contesWon, key: 'possession_contests_won', fmt: (v: number) => String(v ?? 0) },
				{ label: $t.compare.pressingDirect, key: 'pressing_direct', fmt: (v: number) => String(v ?? 0) },
				{ label: $t.compare.pressingIndirect, key: 'pressing_indirect', fmt: (v: number) => String(v ?? 0) },
			],
		},
		{
			group: $t.compare.grpOffBall,
			rows: [
				{ label: $t.playerDetail.totalOffers, key: 'total_offers', fmt: (v: number) => String(v ?? 0) },
				{ label: $t.playerDetail.offersReceived, key: 'offers_received', fmt: (v: number) => String(v ?? 0) },
				{ label: $t.playerDetail.looseBallReceptions, key: 'loose_ball_receptions', fmt: (v: number) => String(v ?? 0) },
				{ label: $t.playerDetail.pushingOn, key: 'pushing_on', fmt: (v: number) => String(v ?? 0) },
				{ label: $t.playerDetail.pushToPressing, key: 'pushing_on_into_pressing', fmt: (v: number) => String(v ?? 0) },
			],
		},
		{
			group: $t.compare.grpPhysical,
			rows: [
				{ label: $t.teams.statDistanceKm, key: 'total_distance_m', fmt: (v: number) => v != null ? (v / 1000).toFixed(1) : '—' },
				{ label: $t.players.colHsRuns, key: 'high_speed_runs', fmt: (v: number) => String(v ?? 0) },
				{ label: $t.players.colSprints, key: 'sprints', fmt: (v: number) => String(v ?? 0) },
				{ label: $t.compare.topSpeed, key: 'top_speed_kmh', fmt: (v: number) => v != null ? `${v}` : '—' },
			],
		},
	]);

	function getPlayerVal(entity: any, key: string): number | null {
		const totals = entity?.totals;
		if (!totals) return null;
		const v = totals[key];
		return v != null ? Number(v) : null;
	}

	function maxPlayerVal(key: string): number {
		return Math.max(...entities.map((e: any) => getPlayerVal(e, key) ?? 0), 0.01);
	}

	const POS_COLOR: Record<string, string> = {
		GK: 'var(--c-lime)',
		DF: 'var(--c-teal)',
		MF: 'var(--c-blue)',
		FW: 'var(--c-red)',
	};

	function safeColorVar(color: string | undefined): string {
		if (!color) return 'var(--muted)';
		return teamColorVar(color);
	}
</script>

<svelte:head>
	<title>
		{type === 'teams' ? $t.compare.titleTeams : type === 'players' ? $t.compare.titlePlayers : type === 'matches' ? $t.compare.titleMatches : $t.compare.titleGeneric} — EFI Data Engine
	</title>
</svelte:head>

<div class="page">
	<header class="page-header">
		<SectionLabel label={$t.compare.label} />
		<h1 class="page-title">
			{type === 'teams' ? $t.compare.titleTeams : type === 'players' ? $t.compare.titlePlayers : type === 'matches' ? $t.compare.titleMatches : $t.compare.titleGeneric}
		</h1>
		<p class="page-sub">
			{#if entities.length >= 2}
				{entities.length} {type} {$t.compare.selectedCount} · <a href="/{type}" class="back-link">{$t.compare.changeSelection}</a>
			{:else}
				<a href="/{type ?? 'teams'}" class="back-link">{$t.compare.selectEntities}</a>
			{/if}
		</p>
	</header>

	<!-- ── Search bar (only when type known) ─────────────────────────────── -->
	{#if type && searchOptions.length > 0}
		<div class="search-section">
			<div class="search-wrap">
				<input
					class="search-input"
					type="text"
					role="combobox"
					aria-label={searchLabel}
					aria-autocomplete="list"
					aria-controls="compare-search-listbox"
					aria-expanded={filteredOptions.length > 0}
					aria-activedescendant={activeIndex >= 0 ? `compare-opt-${activeIndex}` : undefined}
					placeholder={searchLabel}
					disabled={isFull}
					autocomplete="off"
					bind:value={searchQuery}
					oninput={() => (activeIndex = -1)}
					onkeydown={onSearchKeydown}
					onblur={() => setTimeout(() => { searchQuery = ''; activeIndex = -1; }, 150)}
				/>
				{#if filteredOptions.length > 0}
					<div class="search-dropdown" role="listbox" id="compare-search-listbox">
						{#each filteredOptions as opt, i (opt.id)}
							<button
								class="search-option"
								class:search-option--active={i === activeIndex}
								id="compare-opt-{i}"
								role="option"
								aria-selected={i === activeIndex}
								onmousedown={(e) => {
									e.preventDefault();
									addEntity(opt.id);
								}}
							>
								<span class="option-name">{opt.name}</span>
								<span class="option-sub">{opt.sub}</span>
							</button>
						{/each}
					</div>
				{/if}
			</div>
			{#if ids.length >= 2}
				<p class="search-hint">{ids.length}/{MAX} {$t.compare.selectedCount} · {$t.compare.typeToAddMore}</p>
			{/if}
		</div>
	{/if}

	<!-- ── Empty state ────────────────────────────────────────────────────── -->
	{#if entities.length < 2}
		{#if !type}
			<div class="empty-state empty-state--pick">
				<p class="empty-title">{$t.compare.pickTitle}</p>
				<div class="pick-row">
					<a href="/teams" class="pick-card">
						<span class="pick-card__icon">🏳️</span>
						<span class="pick-card__label">{$t.nav.teams}</span>
						<span class="pick-card__sub">{$t.compare.pickTeamsSub}</span>
					</a>
					<a href="/players" class="pick-card">
						<span class="pick-card__icon">👤</span>
						<span class="pick-card__label">{$t.nav.players}</span>
						<span class="pick-card__sub">{$t.compare.pickPlayersSub}</span>
					</a>
					<a href="/matches" class="pick-card">
						<span class="pick-card__icon">⚽</span>
						<span class="pick-card__label">{$t.nav.matches}</span>
						<span class="pick-card__sub">{$t.compare.pickMatchesSub}</span>
					</a>
				</div>
			</div>
		{:else if ids.length === 1}
			<div class="empty-state">
				<p>
					1 {type === 'teams' ? $t.compare.singleTeam : type === 'players' ? $t.compare.singlePlayer : $t.compare.singleMatch} {$t.compare.singleHintAfter}
					<a href="/{type}">{$t.compare.listingPage}</a>.
				</p>
			</div>
		{:else}
			<div class="empty-state">
				<p>
					{$t.compare.selectHintBefore}
					{type} {$t.compare.selectHintFrom}
					<a href="/{type}">{$t.compare.rankingPage}</a>
					or search above.
				</p>
			</div>
		{/if}

	<!-- ── TEAM comparison ────────────────────────────────────────────────── -->
	{:else if type === 'teams'}
		<section class="compare-section">
			<div class="section-divider"></div>
			<div class="compare-body">
				<div class="compare-grid" style="--cols: {entities.length}">
					<div class="metric-col">
						<div class="metric-header">{$t.compare.metricLabel}</div>
					</div>
					{#each entities as entity}
						{@const tm = entity.team}
						<div class="entity-col">
							<div class="entity-header">
								<div class="entity-header__top">
									{#if flagCode(tm.short_code)}
										<span class="fi fi-{flagCode(tm.short_code)} entity-flag" aria-hidden="true"
										></span>
									{/if}
									<span
										class="entity-badge"
										style="background:{teamColorVar(tm.color)};color:{badgeTextColor(tm.color)};"
										>{tm.short_code}</span
									>
									<a href="/teams/{tm.id}" class="entity-name">{tm.name}</a>
								</div>
								<button
									class="entity-remove"
									aria-label="Remove {tm.name}"
									onclick={() => removeEntity(tm.id)}>✕</button
								>
							</div>
						</div>
					{/each}

					{#each TEAM_METRICS as grp}
						<div class="metric-group-label metric-col">{grp.group}</div>
						{#each Array(entities.length) as _}
							<div class="metric-group-label"></div>
						{/each}

						{#each grp.rows as row}
							{@const max = maxTeamVal(row.key)}
							<div class="metric-col metric-label">{row.label}</div>
							{#each entities as entity}
								{@const val = getTeamVal(entity, row.key)}
								<div class="entity-col metric-cell">
									{#if val != null}
										<div class="bar-wrap">
											<div
												class="bar"
												style="width:{(val / max) * 100}%; background:{teamColorVar(entity?.team?.color)};"
											></div>
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

	<!-- ── MATCH comparison ───────────────────────────────────────────────── -->
	{:else if type === 'matches'}
		<section class="compare-section">
			<div class="section-divider"></div>
			<div class="compare-body">
				<div class="compare-grid" style="--cols: {entities.length}">
					<div class="metric-col">
						<div class="metric-header">{$t.compare.metricLabel}</div>
					</div>
					{#each entities as entity}
						{@const m = entity}
						<div class="entity-col">
							<div class="entity-header">
								<div class="entity-header__top">
									{#if flagCode(m.team_a?.short_code)}
										<span class="fi fi-{flagCode(m.team_a.short_code)} entity-flag" aria-hidden="true"></span>
									{/if}
									<span class="match-score">{m.score_a ?? '–'}:{m.score_b ?? '–'}</span>
									{#if flagCode(m.team_b?.short_code)}
										<span class="fi fi-{flagCode(m.team_b.short_code)} entity-flag" aria-hidden="true"></span>
									{/if}
								</div>
								{#if m.went_to_extra_time || m.penalty_score_a != null}
									<span class="match-score-note">{scoreNote(m)}</span>
								{/if}
								<span class="entity-name match-teams">
									{m.team_a?.short_code ?? '?'} vs {m.team_b?.short_code ?? '?'}
								</span>
								<span class="match-meta-line">
									{$t.compare.matchNo} {m.match_no}{m.venue ? ` · ${m.venue}` : ''}
								</span>
								<button
									class="entity-remove"
									aria-label="Remove match"
									onclick={() => removeEntity(m.id)}>✕</button
								>
							</div>
						</div>
					{/each}

					<!-- Score group -->
					<div class="metric-group-label metric-col">{$t.compare.grpScore}</div>
					{#each Array(entities.length) as _}
						<div class="metric-group-label"></div>
					{/each}

					{#each MATCH_SCORE_METRICS as row}
						{@const vals = entities.map(row.fn)}
						{@const maxV = Math.max(...vals, 0.01)}
						<div class="metric-col metric-label">{row.label}</div>
						{#each entities as entity, i}
							{@const val = vals[i]}
							<div class="entity-col metric-cell">
								<div class="bar-wrap">
									<div class="bar" style="width:{(val / maxV) * 100}%; background: var(--accent);"></div>
								</div>
								<span class="metric-val">{row.fmt(val)}</span>
							</div>
						{/each}
					{/each}

					<!-- Possession group -->
					<div class="metric-group-label metric-col">{$t.compare.grpPossessionShooting}</div>
					{#each Array(entities.length) as _}
						<div class="metric-group-label"></div>
					{/each}

					{#each MATCH_POSSESSION_METRICS as row}
						{@const vals = matchMetricVals(row.key)}
						{@const maxV = Math.max(...vals.map((v) => v ?? 0), 0.01)}
						<div class="metric-col metric-label">{row.label}</div>
						{#each entities as entity, i}
							{@const val = vals[i]}
							<div class="entity-col metric-cell">
								{#if val != null}
									<div class="bar-wrap">
										<div class="bar" style="width:{(val / maxV) * 100}%; background: var(--accent);"></div>
									</div>
									<span class="metric-val">{row.fmt(val)}</span>
								{:else}
									<span class="metric-dash">—</span>
								{/if}
							</div>
						{/each}
					{/each}
				</div>
			</div>
		</section>

	<!-- ── PLAYER comparison ──────────────────────────────────────────────── -->
	{:else if type === 'players'}
		<section class="compare-section">
			<div class="section-divider"></div>
			<div class="compare-body">
				<div class="compare-grid" style="--cols: {entities.length}">
					<div class="metric-col">
						<div class="metric-header">{$t.compare.metricLabel}</div>
					</div>
					{#each entities as entity}
						{@const pl = entity.player}
						{@const posColor = POS_COLOR[pl?.position ?? ''] ?? 'var(--muted)'}
						<div class="entity-col">
							<div class="entity-header">
								<div class="entity-header__top">
									<span class="pos-chip" style="background:{posColor};">{pl?.position ?? '—'}</span>
									<span class="entity-badge player-badge"
										style="background:{safeColorVar(entity.team?.color)};color:{badgeTextColor(entity.team?.color ?? '--c-lime')};"
										>{entity.team?.short_code ?? '?'}</span
									>
									<a href="/players/{pl?.id}" class="entity-name">{pl?.name}</a>
								</div>
								<button
									class="entity-remove"
									aria-label="Remove {pl?.name}"
									onclick={() => removeEntity(pl?.id)}>✕</button
								>
							</div>
						</div>
					{/each}

					{#each PLAYER_METRICS as grp}
						<div class="metric-group-label metric-col">{grp.group}</div>
						{#each Array(entities.length) as _}
							<div class="metric-group-label"></div>
						{/each}

						{#each grp.rows as row}
							{@const max = maxPlayerVal(row.key)}
							<div class="metric-col metric-label">{row.label}</div>
							{#each entities as entity}
								{@const val = getPlayerVal(entity, row.key)}
								{@const barColor = safeColorVar(entity.team?.color)}
								<div class="entity-col metric-cell">
									{#if val != null}
										<div class="bar-wrap">
											<div
												class="bar"
												style="width:{(val / max) * 100}%; background:{barColor};"
											></div>
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
	{/if}
</div>

<style>
	.page {
		padding: 40px var(--sp-8);
		display: flex;
		flex-direction: column;
		gap: var(--sp-10);
	}
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
	.back-link {
		color: var(--accent);
		text-decoration: none;
		font-weight: 600;
	}
	.back-link:hover {
		text-decoration: underline;
	}

	/* ── Search ────────────────────────────────────────────────────────────── */
	.search-section {
		display: flex;
		flex-direction: column;
		gap: var(--sp-2);
		max-width: 480px;
	}
	.search-wrap {
		position: relative;
	}
	.search-input {
		width: 100%;
		padding: var(--sp-3) var(--sp-4);
		background: var(--surface);
		border: 1px solid var(--border);
		border-radius: var(--r-md);
		font-size: var(--fs-ui);
		color: var(--ink);
		font-family: inherit;
		transition: border-color 0.15s;
	}
	.search-input:focus {
		outline: none;
		border-color: var(--accent);
	}
	.search-input:disabled {
		opacity: 0.45;
		cursor: not-allowed;
	}
	.search-dropdown {
		position: absolute;
		top: calc(100% + 4px);
		left: 0;
		right: 0;
		background: var(--surface);
		border: 1px solid var(--border);
		border-radius: var(--r-md);
		box-shadow: 0 6px 20px rgba(0, 0, 0, 0.18);
		z-index: 100;
		overflow: hidden;
	}
	.search-option {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: var(--sp-3);
		width: 100%;
		padding: var(--sp-2) var(--sp-4);
		background: transparent;
		border: none;
		text-align: left;
		cursor: pointer;
		transition: background 0.12s;
		font-family: inherit;
	}
	.search-option:hover,
	.search-option--active {
		background: var(--border-soft);
	}
	.option-name {
		font-size: var(--fs-ui);
		font-weight: 600;
		color: var(--ink);
	}
	.option-sub {
		font-size: var(--fs-meta);
		color: var(--muted);
		flex-shrink: 0;
	}
	.search-hint {
		font-size: var(--fs-meta);
		color: var(--muted);
	}

	/* ── Section ───────────────────────────────────────────────────────────── */
	.section-divider {
		height: 1px;
		background: var(--border);
	}
	.compare-section {
		display: flex;
		flex-direction: column;
	}
	.compare-body {
		padding: var(--sp-8);
		overflow-x: auto;
	}

	/* ── Grid ──────────────────────────────────────────────────────────────── */
	.compare-grid {
		display: grid;
		grid-template-columns: 180px repeat(var(--cols), 1fr);
		gap: 0;
		min-width: 480px;
	}
	.metric-col {
		padding: var(--sp-2) var(--sp-3);
	}
	.entity-col {
		padding: var(--sp-2) var(--sp-3);
	}

	/* ── Entity header ─────────────────────────────────────────────────────── */
	.metric-header {
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
		flex-direction: column;
		gap: var(--sp-1);
		padding: var(--sp-3) var(--sp-2);
		border-bottom: 2px solid var(--border);
		position: relative;
	}
	.entity-header__top {
		display: flex;
		align-items: center;
		gap: var(--sp-2);
	}
	.entity-flag {
		width: 22px;
		height: 15px;
		border-radius: 2px;
		flex-shrink: 0;
	}
	.entity-badge {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		padding: 2px 6px;
		border-radius: var(--r-sm);
		font-size: var(--fs-meta);
		font-weight: 800;
		letter-spacing: 0.06em;
		flex-shrink: 0;
	}
	.player-badge {
		padding: 1px 5px;
	}
	.pos-chip {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		width: 28px;
		height: 18px;
		border-radius: var(--r-sm);
		font-size: 10px;
		font-weight: 800;
		letter-spacing: 0.05em;
		color: #fff;
		flex-shrink: 0;
	}
	.entity-name {
		font-size: var(--fs-ui);
		font-weight: 700;
		color: var(--ink);
		text-decoration: none;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
		display: block;
	}
	.entity-name:hover {
		color: var(--accent);
	}
	.entity-remove {
		position: absolute;
		top: var(--sp-2);
		right: var(--sp-1);
		width: 18px;
		height: 18px;
		border: none;
		background: transparent;
		color: var(--muted);
		font-size: 11px;
		cursor: pointer;
		display: inline-flex;
		align-items: center;
		justify-content: center;
		border-radius: var(--r-sm);
		padding: 0;
		line-height: 1;
		font-family: inherit;
		transition: background 0.12s, color 0.12s;
	}
	.entity-remove:hover {
		background: var(--border-soft);
		color: var(--ink);
	}

	/* ── Metric rows ───────────────────────────────────────────────────────── */
	.metric-group-label {
		font-size: var(--fs-meta);
		font-weight: 700;
		text-transform: uppercase;
		letter-spacing: 0.08em;
		color: var(--muted);
		padding: var(--sp-4) var(--sp-3) var(--sp-2);
		border-bottom: 1px solid var(--border);
	}
	.metric-label {
		font-size: var(--fs-ui);
		color: var(--muted);
		font-weight: 500;
		display: flex;
		align-items: center;
		border-bottom: 1px solid var(--border-soft);
	}
	.metric-cell {
		display: flex;
		flex-direction: column;
		gap: 4px;
		justify-content: center;
		border-bottom: 1px solid var(--border-soft);
	}
	.bar-wrap {
		height: 6px;
		background: var(--border-soft);
		border-radius: var(--r-pill);
		overflow: hidden;
	}
	.bar {
		height: 100%;
		border-radius: var(--r-pill);
		transition: width 0.4s ease;
	}
	.metric-val {
		font-size: var(--fs-meta);
		font-weight: 700;
		font-variant-numeric: tabular-nums;
		color: var(--ink);
	}
	.metric-dash {
		font-size: var(--fs-meta);
		color: var(--muted);
	}

	/* ── Empty state ───────────────────────────────────────────────────────── */
	.empty-state {
		padding: var(--sp-10) 0;
		font-size: var(--fs-h2);
		font-weight: 300;
		color: var(--muted);
	}
	.empty-state a {
		color: var(--accent);
	}
	.empty-state--pick {
		font-size: inherit;
	}
	.empty-title {
		font-size: var(--fs-h2);
		font-weight: 300;
		color: var(--muted);
		margin-bottom: var(--sp-6);
	}
	.pick-row {
		display: flex;
		gap: var(--sp-4);
		flex-wrap: wrap;
	}
	.pick-card {
		display: flex;
		flex-direction: column;
		gap: var(--sp-2);
		padding: var(--sp-6) var(--sp-8);
		border: 1px solid var(--border);
		border-radius: var(--r-md);
		text-decoration: none;
		transition: border-color 0.15s, box-shadow 0.15s;
		min-width: 160px;
	}
	.pick-card:hover {
		border-color: var(--accent);
		box-shadow: var(--shadow-card);
	}
	.pick-card__icon {
		font-size: 2rem;
	}
	.pick-card__label {
		font-size: var(--fs-ui);
		font-weight: 700;
		color: var(--ink);
	}
	.pick-card__sub {
		font-size: var(--fs-meta);
		color: var(--muted);
	}

	/* ── Match entity header extras ────────────────────────────────────────── */
	.match-score {
		font-size: var(--fs-h2);
		font-weight: 900;
		font-variant-numeric: tabular-nums;
		color: var(--ink);
		line-height: 1;
	}
	.match-score-note {
		display: block;
		font-size: var(--fs-meta);
		font-weight: 700;
		text-transform: uppercase;
		letter-spacing: 0.03em;
		color: var(--accent);
	}
	.match-teams {
		font-size: var(--fs-meta);
		font-weight: 600;
		color: var(--muted);
		white-space: normal;
	}
	.match-meta-line {
		font-size: var(--fs-meta);
		color: var(--muted);
		font-weight: 400;
	}

	/* ── Responsive ────────────────────────────────────────────────────────── */
	@media (max-width: 720px) {
		.page {
			padding: var(--sp-6) var(--sp-4);
		}
		.page-title {
			font-size: 2.25rem;
		}
		.compare-body {
			padding: var(--sp-4) var(--sp-4);
		}
		.compare-grid {
			grid-template-columns: 140px repeat(var(--cols), minmax(100px, 1fr));
		}
		.search-section {
			max-width: 100%;
		}
	}
</style>
