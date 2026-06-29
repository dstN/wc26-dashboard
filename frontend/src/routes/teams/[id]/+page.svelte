<script lang="ts">
	import type { PageData } from './$types';
	import SectionLabel from '$lib/components/primitives/SectionLabel.svelte';
	import PhasesBar from '$lib/components/viz/PhasesBar.svelte';
	import { teamColorVar, teamTextColor, flagCode } from '$lib/tokens';
	import { t } from '$lib/i18n';

	let { data }: { data: PageData } = $props();

	const team = $derived(data.team);
	const stats = $derived(data.stats);
	const matchList = $derived(data.matches ?? []);
	const players  = $derived(data.players ?? []);
	const phases   = $derived(data.phases ?? []);
	const playerStats: Record<string, any> = $derived(data.playerStats ?? {});

	const POSITION_ORDER: Record<string, number> = { GK: 0, DF: 1, MF: 2, FW: 3 };
	const sortedPlayers = $derived(
		[...players].sort((a: any, b: any) => {
			const pa = POSITION_ORDER[a.position ?? ''] ?? 9;
			const pb = POSITION_ORDER[b.position ?? ''] ?? 9;
			if (pa !== pb) return pa - pb;
			return (a.jersey_number ?? 99) - (b.jersey_number ?? 99);
		})
	);
	const posGroups = $derived(
		sortedPlayers.reduce<Record<string, any[]>>((acc, p: any) => {
			const k = p.position ?? 'Other';
			(acc[k] ??= []).push(p);
			return acc;
		}, {})
	);

	const POS_LABEL: Record<string, string> = { GK: 'Goalkeepers', DF: 'Defenders', MF: 'Midfielders', FW: 'Forwards' };
	const posOrder = ['GK', 'DF', 'MF', 'FW'];

	const inPhases  = $derived(phases.filter((p: any) => p.phase_group === 'in'));
	const outPhases = $derived(phases.filter((p: any) => p.phase_group === 'out'));
	const hasPhases = $derived(inPhases.length > 0 || outPhases.length > 0);

	function badgeTextColor(colorVar: string): string {
		return colorVar === '--c-yellow' || colorVar === '--c-lime' ? 'var(--c-forest)' : '#fff';
	}

	function formatDate(raw: string): string {
		if (!raw) return '';
		try {
			return new Intl.DateTimeFormat('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }).format(new Date(raw));
		} catch { return raw; }
	}

	const goalsScored = $derived(
		matchList.reduce((sum: number, entry: any) => {
			const m = entry.match;
			return sum + (m.team_a.id === team?.id ? (m.score_a ?? 0) : (m.score_b ?? 0));
		}, 0)
	);
	const goalsConceded = $derived(
		matchList.reduce((sum: number, entry: any) => {
			const m = entry.match;
			return sum + (m.team_a.id === team?.id ? (m.score_b ?? 0) : (m.score_a ?? 0));
		}, 0)
	);
	const wins = $derived(
		matchList.filter((entry: any) => {
			const m = entry.match;
			const isA = m.team_a.id === team?.id;
			return isA ? m.score_a > m.score_b : m.score_b > m.score_a;
		}).length
	);

	// Top performers by category
	const enrichedPlayers = $derived(
		players.map((p: any) => ({ ...p, stats: playerStats[String(p.id)] ?? null }))
	);

	const topScorer = $derived(
		[...enrichedPlayers]
			.filter((p) => (p.stats?.goals ?? 0) > 0)
			.sort((a, b) => (b.stats?.goals ?? 0) - (a.stats?.goals ?? 0))[0] ?? null
	);
	const topDefender = $derived(
		[...enrichedPlayers]
			.filter((p) => (p.stats?.tackles_won ?? 0) + (p.stats?.interceptions ?? 0) > 0)
			.sort((a, b) =>
				((b.stats?.tackles_won ?? 0) + (b.stats?.interceptions ?? 0)) -
				((a.stats?.tackles_won ?? 0) + (a.stats?.interceptions ?? 0))
			)[0] ?? null
	);
	const topPasser = $derived(
		[...enrichedPlayers]
			.filter((p) => (p.stats?.passes_attempted ?? 0) > 0)
			.sort((a, b) => (b.stats?.passes_attempted ?? 0) - (a.stats?.passes_attempted ?? 0))[0] ?? null
	);
	const topRunner = $derived(
		[...enrichedPlayers]
			.filter((p) => (p.stats?.total_distance_m ?? 0) > 0)
			.sort((a, b) => (b.stats?.total_distance_m ?? 0) - (a.stats?.total_distance_m ?? 0))[0] ?? null
	);
	const fastestPlayer = $derived(
		[...enrichedPlayers]
			.filter((p) => (p.stats?.top_speed_kmh ?? 0) > 0)
			.sort((a, b) => (b.stats?.top_speed_kmh ?? 0) - (a.stats?.top_speed_kmh ?? 0))[0] ?? null
	);

	const hasTopPerformers = $derived(topScorer || topDefender || topPasser || topRunner);

	const avgStats = $derived(data.avgStats ?? null);
	let statsMode = $state<'avg' | 'total'>('avg');

	function fv(totals: Record<string, number>, avgs: Record<string, number>, key: string, suffix = '', decimals = 1): string {
		const v = statsMode === 'avg' ? avgs[key] : totals[key];
		if (v == null) return '—';
		return `${Number(v).toFixed(decimals)}${suffix}`;
	}
</script>

<svelte:head>
	<title>{team?.name ?? 'Team'} — EFI Data Engine</title>
</svelte:head>

{#if data.error && !team}
	<div class="error-state">
		<a href="/teams" class="back-link">{$t.teams.backToTeams}</a>
		<p class="error-text">{$t.error.teamNotFound}</p>
	</div>
{:else if team}
	<!-- ── TEAM HEADER ────────────────────────────────────────────────────── -->
	<section class="team-header" style="--team-color: {teamColorVar(team.color)};">
		<div class="team-header__bar"></div>
		<div class="team-header__body">
			<div class="team-header__nav">
				<a href="/teams" class="back-link">{$t.teams.backToTeams}</a>
			</div>
			{#if flagCode(team.short_code)}
				<span class="team-header__flag fi fi-{flagCode(team.short_code)}" aria-hidden="true"></span>
			{/if}
			<div class="team-header__identity">
				<span
					class="team-badge"
					style="background: {teamColorVar(team.color)}; color: {badgeTextColor(team.color)};"
				>{team.short_code}</span>
				<h1 class="team-name">{team.name}</h1>
			</div>
			<div class="team-summary">
				<div class="summary-stat">
					<span class="summary-value">{matchList.length}</span>
					<span class="summary-label">{$t.teams.matches}</span>
				</div>
				<div class="summary-stat">
					<span class="summary-value">{wins}</span>
					<span class="summary-label">{$t.teams.wins}</span>
				</div>
				<div class="summary-stat">
					<span class="summary-value">{goalsScored}</span>
					<span class="summary-label">{$t.teams.goalsScored}</span>
				</div>
				<div class="summary-stat">
					<span class="summary-value">{goalsConceded}</span>
					<span class="summary-label">{$t.teams.goalsConceded}</span>
				</div>
				{#if stats?.possession_team_a != null}
					<div class="summary-stat">
						<span class="summary-value">{stats.possession_team_a.toFixed(1)}%</span>
						<span class="summary-label">{$t.teams.avgPossession}</span>
					</div>
				{/if}
				{#if stats?.possession_in_contest != null}
					<div class="summary-stat">
						<span class="summary-value">{stats.possession_in_contest.toFixed(1)}%</span>
						<span class="summary-label">{$t.detail.inContest}</span>
					</div>
				{/if}
				{#if avgStats && avgStats.averages?.xg != null}
					<div class="summary-stat">
						<span class="summary-value">{Number(avgStats.averages.xg).toFixed(2)}</span>
						<span class="summary-label">Avg xG</span>
					</div>
				{/if}
				{#if avgStats && avgStats.averages?.ball_recovery_m != null}
					<div class="summary-stat">
						<span class="summary-value">{Number(avgStats.averages.ball_recovery_m).toFixed(0)}m</span>
						<span class="summary-label">Avg Ball Recovery</span>
					</div>
				{/if}
			</div>
		</div>
	</section>

	<!-- ── PHASE OVERVIEW ────────────────────────────────────────────────── -->
	{#if hasPhases}
		<section class="matches-section">
			<div class="section-divider"></div>
			<div class="section-body">
				<SectionLabel label="Phase Profile" />
				<div class="phase-bars">
					{#if inPhases.length > 0}
						<div class="phase-group">
							<span class="phase-group__title">In Possession (avg %)</span>
							{#each inPhases as ph}
								<div class="phase-row">
									<span class="phase-row__label">{ph.phase_name}</span>
									<div class="phase-row__track">
										<div
											class="phase-row__fill"
											style="width: {Math.min(ph.pct, 60)}%; background: {teamColorVar(team.color)};"
										></div>
									</div>
									<span class="phase-row__pct">{ph.pct}%</span>
								</div>
							{/each}
						</div>
					{/if}
					{#if outPhases.length > 0}
						<div class="phase-group">
							<span class="phase-group__title">Out of Possession (avg %)</span>
							{#each outPhases as ph}
								<div class="phase-row">
									<span class="phase-row__label">{ph.phase_name}</span>
									<div class="phase-row__track">
										<div
											class="phase-row__fill phase-row__fill--out"
											style="width: {Math.min(ph.pct, 60)}%;"
										></div>
									</div>
									<span class="phase-row__pct">{ph.pct}%</span>
								</div>
							{/each}
						</div>
					{/if}
				</div>
			</div>
		</section>
	{/if}

	<!-- ── TOP PERFORMERS ────────────────────────────────────────────────── -->
	{#if hasTopPerformers}
		<section class="matches-section">
			<div class="section-divider"></div>
			<div class="section-body">
				<SectionLabel label="Top Performers" />
				<div class="performers-grid">
					{#if topScorer}
						<a href="/players/{topScorer.id}" class="performer-card">
							<span class="performer-label">Top Scorer</span>
							<span class="performer-val">{topScorer.stats.goals} goals</span>
							<span class="performer-name">{topScorer.name}</span>
							<span class="performer-pos" data-pos={topScorer.position}>{topScorer.position}</span>
						</a>
					{/if}
					{#if topDefender}
						<a href="/players/{topDefender.id}" class="performer-card">
							<span class="performer-label">Top Defender</span>
							<span class="performer-val">{(topDefender.stats.tackles_won ?? 0) + (topDefender.stats.interceptions ?? 0)} tkl+int</span>
							<span class="performer-name">{topDefender.name}</span>
							<span class="performer-pos" data-pos={topDefender.position}>{topDefender.position}</span>
						</a>
					{/if}
					{#if topPasser}
						<a href="/players/{topPasser.id}" class="performer-card">
							<span class="performer-label">Most Passes</span>
							<span class="performer-val">{topPasser.stats.passes_attempted} att.</span>
							<span class="performer-name">{topPasser.name}</span>
							<span class="performer-pos" data-pos={topPasser.position}>{topPasser.position}</span>
						</a>
					{/if}
					{#if topRunner}
						<a href="/players/{topRunner.id}" class="performer-card">
							<span class="performer-label">Most Distance</span>
							<span class="performer-val">{(topRunner.stats.total_distance_m / 1000).toFixed(1)} km</span>
							<span class="performer-name">{topRunner.name}</span>
							<span class="performer-pos" data-pos={topRunner.position}>{topRunner.position}</span>
						</a>
					{/if}
					{#if fastestPlayer}
						<a href="/players/{fastestPlayer.id}" class="performer-card">
							<span class="performer-label">Fastest Player</span>
							<span class="performer-val">{fastestPlayer.stats.top_speed_kmh} km/h</span>
							<span class="performer-name">{fastestPlayer.name}</span>
							<span class="performer-pos" data-pos={fastestPlayer.position}>{fastestPlayer.position}</span>
						</a>
					{/if}
				</div>
			</div>
		</section>
	{/if}

	<!-- ── AVG / TOTAL STATS ──────────────────────────────────────────────── -->
	{#if avgStats && avgStats.match_count > 0}
		{@const tot = avgStats.totals as Record<string, number>}
		{@const avg = avgStats.averages as Record<string, number>}
		<section class="matches-section">
			<div class="section-divider"></div>
			<div class="section-body">
				<div class="stats-header-row">
					<SectionLabel label="Match Stats ({avgStats.match_count} matches)" />
					<div class="mode-toggle">
						<button class="mode-btn" class:mode-btn--active={statsMode === 'avg'} onclick={() => statsMode = 'avg'}>Avg</button>
						<button class="mode-btn" class:mode-btn--active={statsMode === 'total'} onclick={() => statsMode = 'total'}>Total</button>
					</div>
				</div>
				<div class="stats-grid">
					{#each [
						{ group: 'Possession', rows: [
							{ label: 'xG', key: 'xg', decimals: 2 },
							{ label: 'xG Conceded', key: 'xg_conceded', decimals: 2 },
							{ label: 'Possession', key: 'possession_pct', suffix: '%' },
							{ label: 'In Contest', key: 'in_contest_pct', suffix: '%' },
						]},
						{ group: 'Attacking', rows: [
							{ label: 'Goals', key: 'goals', decimals: 0 },
							{ label: 'Shots', key: 'shots_total', decimals: 0 },
							{ label: 'Shots on Target', key: 'shots_on_target', decimals: 0 },
							{ label: 'Line Breaks', key: 'completed_line_breaks', decimals: 0 },
							{ label: 'Def. Line Breaks', key: 'defensive_line_breaks', decimals: 0 },
							{ label: 'Crosses', key: 'crosses', decimals: 0 },
							{ label: 'Ball Progressions', key: 'ball_progressions', decimals: 0 },
							{ label: 'Take-Ons', key: 'take_ons', decimals: 0 },
						]},
						{ group: 'Passing', rows: [
							{ label: 'Passes Attempted', key: 'passes_attempted', decimals: 0 },
							{ label: 'Passes Completed', key: 'passes_completed', decimals: 0 },
						]},
						{ group: 'Defensive', rows: [
							{ label: 'Goals Conceded', key: 'goals_conceded', decimals: 0 },
							{ label: 'Tackles Won', key: 'tackles_won', decimals: 0 },
							{ label: 'Interceptions', key: 'interceptions', decimals: 0 },
							{ label: 'Blocks', key: 'blocks', decimals: 0 },
							{ label: 'Clearances', key: 'clearances', decimals: 0 },
							{ label: 'Possession Regains', key: 'possession_regains', decimals: 0 },
							{ label: 'Forced Turnovers', key: 'forced_turnovers', decimals: 0 },
							{ label: 'Pressing', key: 'pressing_direct', decimals: 0 },
						]},
						{ group: 'Physical', rows: [
							{ label: 'Distance (km)', key: 'total_distance_km', decimals: 1 },
							{ label: 'Aerial Duels Won', key: 'duels_won_aerial', decimals: 0 },
							{ label: 'Physical Duels Won', key: 'duels_won_physical', decimals: 0 },
						]},
						{ group: 'GK', rows: [
							{ label: 'Attempts Faced', key: 'gk_attempts_faced', decimals: 0 },
							{ label: 'Save %', key: 'gk_save_pct', suffix: '%' },
							{ label: 'Crosses Faced', key: 'gk_crosses_faced', decimals: 0 },
							{ label: 'Involvements', key: 'gk_involvements', decimals: 0 },
							{ label: 'Distributions', key: 'gk_distributions', decimals: 0 },
						]},
						{ group: 'Set Plays', rows: [
							{ label: 'Set Plays', key: 'set_plays', decimals: 0 },
							{ label: 'Corners', key: 'corners', decimals: 0 },
							{ label: 'Free Kicks', key: 'free_kicks', decimals: 0 },
						]},
					] as group}
						<div class="stats-group">
							<h3 class="stats-group__title">{group.group}</h3>
							{#each group.rows as row}
								{@const val = fv(tot, avg, row.key, row.suffix ?? '', row.decimals ?? 1)}
								{#if val !== '—'}
									<div class="stats-row">
										<span class="stats-row__label">{row.label}</span>
										<span class="stats-row__val">{val}</span>
									</div>
								{/if}
							{/each}
						</div>
					{/each}
				</div>
			</div>
		</section>
	{/if}

	<!-- ── PLAYERS ────────────────────────────────────────────────────────── -->
	{#if players.length > 0}
		<section class="matches-section">
			<div class="section-divider"></div>
			<div class="section-body">
				<SectionLabel label="Squad · {players.length} Players" />
				<div class="squad">
					{#each posOrder as pos}
						{#if posGroups[pos]?.length}
							<div class="squad__group">
								<h3 class="squad__pos-title">{POS_LABEL[pos]}</h3>
								<div class="squad__grid">
									{#each posGroups[pos] as p (p.id)}
										{@const ps = playerStats[String(p.id)]}
										<a href="/players/{p.id}" class="squad__card">
											<span class="squad__num">#{p.jersey_number ?? '—'}</span>
											<span class="squad__name">{p.name}</span>
											{#if ps && (ps.goals > 0 || ps.yellow_cards > 0 || ps.red_cards > 0 || ps.minutes_played > 0)}
												<span class="squad__chips">
													{#if ps.goals > 0}
														<span class="squad__chip squad__chip--goal">⚽{ps.goals}</span>
													{/if}
													{#if ps.yellow_cards > 0}
														<span class="squad__chip squad__chip--yellow">🟨{ps.yellow_cards}</span>
													{/if}
													{#if ps.red_cards > 0}
														<span class="squad__chip squad__chip--red">🟥{ps.red_cards}</span>
													{/if}
													{#if ps.minutes_played > 0}
														<span class="squad__chip">{ps.appearances}g</span>
													{/if}
												</span>
											{/if}
										</a>
									{/each}
								</div>
							</div>
						{/if}
					{/each}
				</div>
			</div>
		</section>
	{/if}

	<!-- ── MATCH HISTORY ─────────────────────────────────────────────────── -->
	{#if matchList.length > 0}
		<section class="matches-section">
			<div class="section-divider"></div>
			<div class="section-body">
				<SectionLabel label="{$t.teams.matchHistory}" />
				<div class="match-list">
					{#each matchList as entry (entry.match.id)}
						{@const m = entry.match}
						{@const ms = entry.stats}
						{@const isTeamA = m.team_a.id === team.id}
						{@const opponent = isTeamA ? m.team_b : m.team_a}
						{@const teamScore = isTeamA ? m.score_a : m.score_b}
						{@const oppScore = isTeamA ? m.score_b : m.score_a}
						{@const won = teamScore > oppScore}
						{@const drew = teamScore === oppScore}
						<a href="/matches/{m.id}" class="match-row">
							<div class="match-row__meta">
								<span class="match-group">{$t.match.group} {m.group_letter} · {$t.match.matchNo} {m.match_no}</span>
								{#if m.match_date}
									<span class="match-date">{formatDate(m.match_date)}</span>
								{/if}
							</div>
							<div class="match-row__body">
								<div class="match-row__team">
									<span class="vs-label">vs</span>
									<span
										class="opp-badge"
										style="background: {teamColorVar(opponent.color)}; color: {badgeTextColor(opponent.color)};"
									>{opponent.short_code}</span>
									<span class="opp-name">{opponent.name}</span>
								</div>
								<div class="match-row__score">
									<span
										class="sc-badge"
										style="background: {teamColorVar(team.color)}; color: {badgeTextColor(team.color)};"
									>{team.short_code}</span>
									<span class="score-val" class:score-win={won} class:score-draw={drew} class:score-loss={!won && !drew}>{teamScore}</span>
									<span class="score-sep">:</span>
									<span class="score-val score-opp">{oppScore}</span>
									<span
										class="sc-badge"
										style="background: {teamColorVar(opponent.color)}; color: {badgeTextColor(opponent.color)};"
									>{opponent.short_code}</span>
								</div>
								<div class="match-row__stats">
									{#if ms?.possession_team_a != null}
										<span class="stat-pill">Poss {ms.possession_team_a.toFixed(1)}%</span>
									{/if}
									{#if ms?.xg_a != null}
										<span class="stat-pill">xG {ms.xg_a.toFixed(2)}</span>
									{/if}
								</div>
								<span class="result-badge" class:result-win={won} class:result-draw={drew} class:result-loss={!won && !drew}>
									{won ? 'W' : drew ? 'D' : 'L'}
								</span>
							</div>
							{#if m.venue}
								<p class="match-row__venue">{m.venue}</p>
							{/if}
						</a>
					{/each}
				</div>
			</div>
		</section>
	{/if}
{/if}

<style>
	.error-state {
		padding: var(--sp-10) var(--sp-8);
		display: flex;
		flex-direction: column;
		gap: var(--sp-4);
	}
	.error-text { color: var(--c-red); font-size: var(--fs-body); }

	/* ── Team header ─────────────────────────────────────────────────── */
	.team-header {
		background: var(--surface);
		display: flex;
		flex-direction: column;
	}
	.team-header__bar {
		height: 6px;
		background: var(--team-color);
	}
	.team-header__body {
		padding: 40px var(--sp-8);
		display: flex;
		flex-direction: column;
		gap: var(--sp-6);
	}
	.back-link {
		font-size: var(--fs-ui);
		font-weight: 600;
		color: var(--accent);
		text-decoration: none;
	}
	.back-link:hover { text-decoration: underline; }

	.team-header__identity {
		display: flex;
		align-items: center;
		gap: var(--sp-5);
	}
	.team-badge {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		padding: var(--sp-2) var(--sp-4);
		border-radius: var(--r-sm);
		font-size: var(--fs-h2);
		font-weight: 800;
		letter-spacing: 0.06em;
		min-width: 60px;
	}
	.team-name {
		font-size: var(--fs-hero);
		font-weight: 800;
		color: var(--ink);
		line-height: 1.05;
	}

	.team-summary {
		display: flex;
		gap: var(--sp-8);
		flex-wrap: wrap;
	}
	.summary-stat {
		display: flex;
		flex-direction: column;
		gap: var(--sp-1);
	}
	.summary-value {
		font-size: var(--fs-stat);
		font-weight: 800;
		font-variant-numeric: tabular-nums;
		color: var(--ink);
		line-height: 1;
	}
	.summary-label {
		font-size: var(--fs-label);
		font-weight: 600;
		text-transform: uppercase;
		letter-spacing: 0.08em;
		color: var(--muted);
	}

	/* ── Header flag watermark ──────────────────────────────────────── */
	.team-header__body { position: relative; overflow: hidden; }
	.team-header__flag {
		position: absolute;
		right: var(--sp-8);
		top: 50%;
		transform: translateY(-50%);
		width: 180px;
		height: 120px;
		border-radius: 6px;
		opacity: 0.12;
		pointer-events: none;
	}

	/* ── Section wrapper ─────────────────────────────────────────────── */
	.section-divider { height: 1px; background: var(--border); }
	.section-body {
		padding: var(--sp-8);
		display: flex;
		flex-direction: column;
		gap: var(--sp-5);
	}

	/* ── Phase bars ──────────────────────────────────────────────────── */
	.phase-bars {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: var(--sp-8);
	}
	.phase-group {
		display: flex;
		flex-direction: column;
		gap: var(--sp-3);
	}
	.phase-group__title {
		font-size: var(--fs-label);
		font-weight: 700;
		text-transform: uppercase;
		letter-spacing: 0.08em;
		color: var(--muted);
		margin-bottom: var(--sp-1);
	}
	.phase-row {
		display: grid;
		grid-template-columns: 160px 1fr 40px;
		align-items: center;
		gap: var(--sp-3);
	}
	.phase-row__label {
		font-size: var(--fs-meta);
		font-weight: 600;
		color: var(--ink);
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}
	.phase-row__track {
		height: 8px;
		background: var(--border-soft);
		border-radius: var(--r-pill);
		overflow: hidden;
	}
	.phase-row__fill {
		height: 100%;
		border-radius: var(--r-pill);
		transition: width 0.4s ease;
	}
	.phase-row__fill--out { background: var(--muted); }
	.phase-row__pct {
		font-size: var(--fs-meta);
		font-weight: 700;
		font-variant-numeric: tabular-nums;
		color: var(--muted);
		text-align: right;
	}

	/* ── Top performers grid ─────────────────────────────────────────── */
	.performers-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
		gap: var(--sp-4);
	}
	.performer-card {
		display: flex;
		flex-direction: column;
		gap: var(--sp-1);
		padding: var(--sp-5);
		background: var(--surface);
		border: 1px solid var(--border);
		border-radius: var(--r-md);
		text-decoration: none;
		transition: border-color 0.15s, transform 0.15s;
		min-width: 0;
		overflow: hidden;
	}
	.performer-card:hover {
		border-color: var(--accent);
		transform: translateY(-2px);
	}
	.performer-label {
		font-size: var(--fs-meta);
		font-weight: 700;
		text-transform: uppercase;
		letter-spacing: 0.08em;
		color: var(--muted);
	}
	.performer-val {
		font-size: var(--fs-h2);
		font-weight: 900;
		font-variant-numeric: tabular-nums;
		color: var(--accent);
		line-height: 1.1;
	}
	.performer-name {
		font-size: var(--fs-ui);
		font-weight: 700;
		color: var(--ink);
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}
	.performer-pos {
		font-size: var(--fs-meta);
		font-weight: 700;
		text-transform: uppercase;
		letter-spacing: 0.06em;
		color: var(--muted);
	}
	[data-pos='GK'] { color: var(--c-lime); }
	[data-pos='DF'] { color: var(--c-teal); }
	[data-pos='MF'] { color: var(--c-blue); }
	[data-pos='FW'] { color: var(--c-red); }

	/* ── Squad ───────────────────────────────────────────────────────── */
	.squad {
		display: flex;
		flex-direction: column;
		gap: var(--sp-6);
	}
	.squad__pos-title {
		font-size: var(--fs-label);
		font-weight: 700;
		text-transform: uppercase;
		letter-spacing: 0.08em;
		color: var(--muted);
		margin-bottom: var(--sp-2);
	}
	.squad__grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
		gap: var(--sp-3);
	}
	.squad__card {
		display: flex;
		align-items: center;
		gap: var(--sp-3);
		padding: var(--sp-3) var(--sp-4);
		background: var(--surface);
		border: 1px solid var(--border);
		border-radius: var(--r-sm);
		text-decoration: none;
		transition: border-color 0.12s;
	}
	.squad__card:hover {
		border-color: var(--accent);
	}
	.squad__num {
		font-size: var(--fs-meta);
		font-weight: 800;
		font-variant-numeric: tabular-nums;
		color: var(--muted);
		min-width: 26px;
		flex-shrink: 0;
	}
	.squad__name {
		font-size: var(--fs-ui);
		font-weight: 600;
		color: var(--ink);
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
		flex: 1;
	}
	.squad__chips {
		display: flex;
		gap: 3px;
		flex-shrink: 0;
		align-items: center;
	}
	.squad__chip {
		font-size: 10px;
		font-weight: 700;
		padding: 1px 4px;
		border-radius: 3px;
		background: color-mix(in srgb, var(--muted) 10%, transparent);
		color: var(--muted);
		font-variant-numeric: tabular-nums;
	}
	.squad__chip--goal { background: color-mix(in srgb, var(--accent) 15%, transparent); color: var(--accent); }
	.squad__chip--yellow { background: color-mix(in srgb, var(--c-yellow) 15%, transparent); color: var(--c-yellow); }
	.squad__chip--red { background: color-mix(in srgb, var(--c-red) 15%, transparent); color: var(--c-red); }

	/* ── Match list ──────────────────────────────────────────────────── */
	.match-list {
		display: flex;
		flex-direction: column;
		gap: var(--sp-3);
	}

	.match-row {
		display: flex;
		flex-direction: column;
		gap: var(--sp-2);
		padding: 20px;
		background: var(--surface);
		border: 1px solid var(--border);
		border-radius: var(--r-md);
		text-decoration: none;
		transition: border-color 0.12s, transform 0.12s;
	}
	.match-row:hover {
		border-color: var(--accent);
		transform: translateX(4px);
	}

	.match-row__meta {
		display: flex;
		align-items: center;
		gap: var(--sp-3);
	}
	.match-group {
		font-size: var(--fs-label);
		font-weight: 700;
		text-transform: uppercase;
		letter-spacing: 0.08em;
		color: var(--accent);
	}
	.match-date {
		font-size: var(--fs-label);
		color: var(--muted);
	}

	.match-row__body {
		display: flex;
		align-items: center;
		gap: var(--sp-5);
	}
	.match-row__team {
		display: flex;
		align-items: center;
		gap: var(--sp-2);
		flex: 1;
		min-width: 0;
	}
	.vs-label {
		font-size: var(--fs-label);
		font-weight: 600;
		color: var(--muted);
		text-transform: uppercase;
		letter-spacing: 0.06em;
		flex-shrink: 0;
	}
	.sc-badge {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		padding: 2px 6px;
		border-radius: var(--r-sm);
		font-size: var(--fs-meta);
		font-weight: 800;
		letter-spacing: 0.04em;
		flex-shrink: 0;
	}
	.opp-badge {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		padding: 2px 8px;
		border-radius: var(--r-sm);
		font-size: var(--fs-label);
		font-weight: 800;
		letter-spacing: 0.04em;
		flex-shrink: 0;
	}
	.opp-name {
		font-size: var(--fs-ui);
		font-weight: 600;
		color: var(--ink);
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	.match-row__score {
		display: flex;
		align-items: center;
		gap: var(--sp-1);
		flex-shrink: 0;
	}
	.score-val {
		font-size: var(--fs-h2);
		font-weight: 900;
		font-variant-numeric: tabular-nums;
		line-height: 1;
		color: var(--ink);
	}
	.score-win { color: var(--positive); }
	.score-loss { color: var(--c-red); }
	.score-draw { color: var(--muted); }
	.score-opp { color: var(--muted); font-weight: 700; }
	.score-sep { color: var(--border); font-size: var(--fs-h2); }

	.match-row__stats {
		display: flex;
		gap: var(--sp-2);
		flex-wrap: wrap;
		flex: 1;
		justify-content: flex-end;
	}
	.stat-pill {
		font-size: var(--fs-meta);
		font-weight: 600;
		font-variant-numeric: tabular-nums;
		padding: 3px 8px;
		border-radius: var(--r-pill);
		background: color-mix(in srgb, var(--muted) 10%, transparent);
		color: var(--muted);
	}

	.result-badge {
		width: 28px;
		height: 28px;
		border-radius: 50%;
		display: inline-flex;
		align-items: center;
		justify-content: center;
		font-size: var(--fs-label);
		font-weight: 800;
		flex-shrink: 0;
	}
	.result-win { background: color-mix(in srgb, var(--positive) 15%, transparent); color: var(--positive); }
	.result-draw { background: color-mix(in srgb, var(--muted) 15%, transparent); color: var(--muted); }
	.result-loss { background: color-mix(in srgb, var(--c-red) 15%, transparent); color: var(--c-red); }

	.match-row__venue {
		font-size: var(--fs-meta);
		color: var(--muted);
		padding-top: var(--sp-1);
	}

	/* ── Avg/Total Stats section ────────────────────────────────────── */
	.stats-header-row {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: var(--sp-4);
		margin-bottom: var(--sp-4);
	}
	.mode-toggle {
		display: flex;
		gap: 2px;
		background: var(--border);
		border-radius: var(--r-pill);
		padding: 2px;
	}
	.mode-btn {
		padding: var(--sp-1) var(--sp-4);
		font-size: var(--fs-meta);
		font-weight: 700;
		font-family: inherit;
		border-radius: var(--r-pill);
		border: none;
		cursor: pointer;
		background: transparent;
		color: var(--muted);
		transition: background 0.15s, color 0.15s;
	}
	.mode-btn--active { background: var(--accent); color: var(--bg); }
	.stats-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
		gap: var(--sp-6);
	}
	.stats-group { display: flex; flex-direction: column; gap: var(--sp-2); }
	.stats-group__title {
		font-size: var(--fs-meta);
		font-weight: 700;
		text-transform: uppercase;
		letter-spacing: 0.08em;
		color: var(--muted);
		padding-bottom: var(--sp-1);
		border-bottom: 1px solid var(--border);
	}
	.stats-row {
		display: flex;
		justify-content: space-between;
		align-items: baseline;
		gap: var(--sp-2);
	}
	.stats-row__label {
		font-size: var(--fs-ui);
		color: var(--muted);
		font-weight: 500;
	}
	.stats-row__val {
		font-size: var(--fs-ui);
		font-weight: 700;
		font-variant-numeric: tabular-nums;
		color: var(--ink);
	}

	/* ── Responsive ──────────────────────────────────────────────────── */
	@media (max-width: 900px) {
		.phase-bars { grid-template-columns: 1fr; }
		.phase-row { grid-template-columns: 130px 1fr 36px; }
	}
	@media (max-width: 720px) {
		.team-header__body, .section-body {
			padding: var(--sp-8) var(--sp-4);
		}
		.team-header__flag { width: 120px; height: 80px; right: var(--sp-4); }
		.team-name { font-size: 2.25rem; }
		.team-summary { gap: var(--sp-5); }
		.match-row__stats { display: none; }
		.match-row__body { gap: var(--sp-3); }
		.squad__grid { grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); }
		.performers-grid { grid-template-columns: repeat(2, 1fr); }
		.phase-row { grid-template-columns: 100px 1fr 32px; }
	}
</style>
