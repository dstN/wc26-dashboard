<script lang="ts">
	import type { PageData } from './$types';
	import { teamColorVar, teamTextColor, flagCode, badgeTextColor } from '$lib/tokens';
	import SectionLabel from '$lib/components/primitives/SectionLabel.svelte';
	import { t } from '$lib/i18n';

	let { data }: { data: PageData } = $props();

	const player = $derived(data.player);
	const team = $derived(data.team);
	const totals = $derived(data.totals);
	const perMatch = $derived(data.per_match ?? []);
	const lineBreaks = $derived(data.lineBreaks ?? []);

	const posLabel = $derived<Record<string, string>>({
		GK: $t.players.posGK, DF: $t.players.posDF, MF: $t.players.posMF, FW: $t.players.posFW
	});
	const posColor: Record<string, string> = {
		GK: 'var(--c-lime)', DF: 'var(--c-teal)', MF: 'var(--c-blue)', FW: 'var(--c-red)'
	};

	function formatDate(raw: string | null): string {
		if (!raw) return '—';
		try {
			return new Intl.DateTimeFormat('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }).format(new Date(raw));
		} catch { return raw; }
	}

	const f = (v: number | null | undefined, suffix = '') => v != null ? `${v}${suffix}` : '—';
	const fkm = (v: number | null | undefined) => v != null ? (v / 1000).toFixed(1) + ' km' : '—';

</script>

<svelte:head>
	<title>{player?.name ?? 'Player'} — EFI Data Engine</title>
</svelte:head>

{#if data.error || !player}
	<div class="error-state">
		<a href="/players" class="back-link">{$t.playerDetail.backToPlayers}</a>
		<p class="error-text">{$t.playerDetail.notFound}</p>
	</div>
{:else}
	<!-- ── HEADER ─────────────────────────────────────────────────────────── -->
	<section class="player-header">
		<div class="player-header__nav">
			<a href="/players" class="back-link">{$t.playerDetail.backToPlayers}</a>
			{#if team}
				<a href="/teams/{team.id}" class="back-link" style="color: {teamTextColor(team.color)};">
					{team.name}
				</a>
			{/if}
		</div>
		<div class="player-hero">
			<div class="player-hero__left">
				{#if team && flagCode(team.short_code)}
					<span class="fi fi-{flagCode(team.short_code)} hero-flag" aria-hidden="true"></span>
				{/if}
				<div>
					<div class="hero-pos" style="color: {posColor[player.position ?? ''] ?? 'var(--muted)'};">
						{posLabel[player.position ?? ''] ?? player.position ?? '—'}
					</div>
					<h1 class="hero-name">{player.name}</h1>
					{#if team}
						<div class="hero-team">
							<span
								class="team-badge"
								style="background: {teamColorVar(team.color)}; color: {badgeTextColor(team.color)};"
							>{team.short_code}</span>
							<span class="hero-team-name">{team.name}</span>
						</div>
					{/if}
				</div>
			</div>
			<div class="hero-number">#{player.jersey_number ?? '—'}</div>
		</div>
	</section>

	<!-- ── CAREER TOTALS ─────────────────────────────────────────────────── -->
	{#if totals}
		<section class="detail-section">
			<div class="section-divider"></div>
			<div class="section-body">
				<SectionLabel label={$t.playerDetail.tournamentTotals} />
				<div class="totals-grid">
					<div class="total-card">
						<span class="total-val">{totals.appearances ?? 0}</span>
						<span class="total-lbl">{$t.playerDetail.appearances}</span>
					</div>
					<div class="total-card">
						<span class="total-val">{totals.goals ?? 0}</span>
						<span class="total-lbl">{$t.keyStats.goals}</span>
					</div>
					<div class="total-card">
						<span class="total-val">{totals.minutes_played ?? 0}</span>
						<span class="total-lbl">{$t.playerDetail.minutes}</span>
					</div>
					{#if totals.passes_attempted != null}
						<div class="total-card">
							<span class="total-val">{totals.passes_attempted}</span>
							<span class="total-lbl">{$t.playerDetail.passesAttempted}</span>
						</div>
						<div class="total-card">
							<span class="total-val">{totals.pass_completion_pct != null ? `${totals.pass_completion_pct}%` : '—'}</span>
							<span class="total-lbl">{$t.playerDetail.passCompletion}</span>
						</div>
					{/if}
					{#if totals.attempts_at_goal != null}
						<div class="total-card">
							<span class="total-val">{totals.attempts_at_goal}</span>
							<span class="total-lbl">{$t.playerDetail.shots}</span>
						</div>
					{/if}
					{#if totals.tackles_made != null}
						<div class="total-card">
							<span class="total-val">{totals.tackles_made}</span>
							<span class="total-lbl">{$t.playerDetail.tacklesMade}</span>
						</div>
						<div class="total-card">
							<span class="total-val">{totals.tackles_won ?? '—'}</span>
							<span class="total-lbl">{$t.playerDetail.tacklesWon}</span>
						</div>
						<div class="total-card">
							<span class="total-val">{totals.interceptions ?? '—'}</span>
							<span class="total-lbl">{$t.keyStats.interceptions}</span>
						</div>
						<div class="total-card">
							<span class="total-val">{totals.clearances ?? '—'}</span>
							<span class="total-lbl">{$t.keyStats.clearances}</span>
						</div>
						{#if totals.blocks != null}
							<div class="total-card">
								<span class="total-val">{totals.blocks}</span>
								<span class="total-lbl">{$t.keyStats.blocks}</span>
							</div>
						{/if}
						{#if totals.possession_regains != null}
							<div class="total-card">
								<span class="total-val">{totals.possession_regains}</span>
								<span class="total-lbl">{$t.keyStats.regains}</span>
							</div>
						{/if}
						{#if totals.duels_won_aerial != null}
							<div class="total-card">
								<span class="total-val">{totals.duels_won_aerial}</span>
								<span class="total-lbl">{$t.keyStats.aerialDuels}</span>
							</div>
						{/if}
						{#if totals.duels_won_physical != null}
							<div class="total-card">
								<span class="total-val">{totals.duels_won_physical}</span>
								<span class="total-lbl">{$t.keyStats.physicalDuels}</span>
							</div>
						{/if}
						{#if totals.pressing_direct != null}
							<div class="total-card">
								<span class="total-val">{totals.pressing_direct}</span>
								<span class="total-lbl">{$t.keyStats.pressures}</span>
							</div>
						{/if}
						{#if totals.pressing_indirect != null}
							<div class="total-card">
								<span class="total-val">{totals.pressing_indirect}</span>
								<span class="total-lbl">{$t.playerDetail.indirectPressures}</span>
							</div>
						{/if}
						{#if totals.possession_contests_won != null}
							<div class="total-card">
								<span class="total-val">{totals.possession_contests_won}</span>
								<span class="total-lbl">{$t.playerDetail.contestsWon}</span>
							</div>
						{/if}
						{#if totals.pushing_on_into_pressing != null}
							<div class="total-card">
								<span class="total-val">{totals.pushing_on_into_pressing}</span>
								<span class="total-lbl">{$t.playerDetail.pushToPressing}</span>
							</div>
						{/if}
					{/if}
					{#if totals.total_distance_m != null}
						<div class="total-card">
							<span class="total-val">{fkm(totals.total_distance_m)}</span>
							<span class="total-lbl">{$t.playerDetail.totalDistance}</span>
						</div>
					{/if}
					{#if totals.top_speed_kmh != null}
						<div class="total-card total-card--highlight">
							<span class="total-val">{totals.top_speed_kmh} km/h</span>
							<span class="total-lbl">{$t.players.colTopSpeed}</span>
						</div>
					{/if}
					{#if totals.sprints != null}
						<div class="total-card">
							<span class="total-val">{totals.sprints}</span>
							<span class="total-lbl">{$t.players.colSprints}</span>
						</div>
					{/if}
					{#if totals.high_speed_runs != null}
						<div class="total-card">
							<span class="total-val">{totals.high_speed_runs}</span>
							<span class="total-lbl">{$t.players.colHsRuns}</span>
						</div>
					{/if}
					{#if totals.total_offers != null}
						<div class="total-card">
							<span class="total-val">{totals.total_offers}</span>
							<span class="total-lbl">{$t.playerDetail.totalOffers}</span>
						</div>
					{/if}
					{#if totals.offers_received != null}
						<div class="total-card">
							<span class="total-val">{totals.offers_received}</span>
							<span class="total-lbl">{$t.playerDetail.offersReceived}</span>
						</div>
					{/if}
					{#if totals.switches_of_play != null}
						<div class="total-card">
							<span class="total-val">{totals.switches_of_play}</span>
							<span class="total-lbl">{$t.playerDetail.switchesOfPlay}</span>
						</div>
					{/if}
					{#if totals.step_ins != null}
						<div class="total-card">
							<span class="total-val">{totals.step_ins}</span>
							<span class="total-lbl">{$t.playerDetail.stepIns}</span>
						</div>
					{/if}
					{#if totals.lb_attempted != null}
						<div class="total-card">
							<span class="total-val">{totals.lb_completed ?? '—'} / {totals.lb_attempted}</span>
							<span class="total-lbl">{$t.playerDetail.lineBreaksCompAtt}</span>
						</div>
					{/if}
					{#if totals.loose_ball_receptions != null}
						<div class="total-card">
							<span class="total-val">{totals.loose_ball_receptions}</span>
							<span class="total-lbl">{$t.playerDetail.looseBallReceptions}</span>
						</div>
					{/if}
					{#if totals.pushing_on != null}
						<div class="total-card">
							<span class="total-val">{totals.pushing_on}</span>
							<span class="total-lbl">{$t.playerDetail.pushingOn}</span>
						</div>
					{/if}
					{#if totals.possession_interrupted != null}
						<div class="total-card">
							<span class="total-val">{totals.possession_interrupted}</span>
							<span class="total-lbl">{$t.playerDetail.possessionInterrupted}</span>
						</div>
					{/if}
					{#if totals.dist_zone1_m != null}
						<div class="total-card">
							<span class="total-val">{(totals.dist_zone1_m / 1000).toFixed(2)} km</span>
							<span class="total-lbl">{$t.playerDetail.walkZone}</span>
						</div>
					{/if}
					{#if totals.dist_zone2_m != null}
						<div class="total-card">
							<span class="total-val">{(totals.dist_zone2_m / 1000).toFixed(2)} km</span>
							<span class="total-lbl">{$t.playerDetail.jogZone}</span>
						</div>
					{/if}
					{#if totals.dist_zone3_m != null}
						<div class="total-card">
							<span class="total-val">{(totals.dist_zone3_m / 1000).toFixed(2)} km</span>
							<span class="total-lbl">{$t.playerDetail.runZone}</span>
						</div>
					{/if}
					{#if totals.dist_zone4_m != null}
						<div class="total-card">
							<span class="total-val">{(totals.dist_zone4_m / 1000).toFixed(2)} km</span>
							<span class="total-lbl">{$t.playerDetail.highSpeedZone}</span>
						</div>
					{/if}
					{#if totals.dist_zone5_m != null}
						<div class="total-card">
							<span class="total-val">{(totals.dist_zone5_m / 1000).toFixed(2)} km</span>
							<span class="total-lbl">{$t.playerDetail.sprintZone}</span>
						</div>
					{/if}
					{#if totals.yellow_cards}
						<div class="total-card total-card--yellow">
							<span class="total-val">{totals.yellow_cards}</span>
							<span class="total-lbl">{$t.playerDetail.yellowCards}</span>
						</div>
					{/if}
					{#if totals.red_cards}
						<div class="total-card total-card--red">
							<span class="total-val">{totals.red_cards}</span>
							<span class="total-lbl">{$t.playerDetail.redCards}</span>
						</div>
					{/if}
				</div>
			</div>
		</section>
	{/if}

	<!-- ── PER-MATCH BREAKDOWN ───────────────────────────────────────────── -->
	{#if perMatch.length > 0}
		<section class="detail-section">
			<div class="section-divider"></div>
			<div class="section-body">
				<SectionLabel label={$t.playerDetail.matchByMatch} />
				<div class="matches-table-wrap">
					<table class="matches-table">
						<thead>
							<tr>
								<th>{$t.playerDetail.colMatch}</th>
								<th>{$t.playerDetail.colOpponent}</th>
								<th>{$t.playerDetail.colStatus}</th>
								<th class="num">{$t.playerDetail.colMin}</th>
								<th class="num">{$t.keyStats.goals}</th>
								<th class="num">{$t.playerDetail.colPasses}</th>
								<th class="num">{$t.players.colPassPct}</th>
								<th class="num">{$t.playerDetail.shots}</th>
								<th class="num">{$t.playerDetail.colTkl}</th>
								<th class="num">{$t.playerDetail.colInt}</th>
								<th class="num">{$t.playerDetail.colDist}</th>
								<th class="num">{$t.playerDetail.colSpeed}</th>
							</tr>
						</thead>
						<tbody>
							{#each perMatch as m}
								<tr>
									<td class="match-no">#{m.match_no ?? '—'}</td>
									<td>
										{#if m.opponent}
											<a href="/teams/{m.opponent.id}" class="opp-link">
												{m.opponent.short_code}
											</a>
										{:else}
											—
										{/if}
									</td>
									<td>
										<span class="status-badge" class:status-started={m.started}>
											{m.started ? $t.playerDetail.statusStarted : $t.playerDetail.statusSub}
										</span>
									</td>
									<td class="num">{f(m.minutes_played)}</td>
									<td class="num">{m.goals ?? 0}</td>
									<td class="num">{m.passes_attempted != null ? `${m.passes_attempted} (${m.passes_completed ?? 0})` : '—'}</td>
									<td class="num">{f(m.pass_completion_pct, '%')}</td>
									<td class="num">{f(m.attempts_at_goal)}</td>
									<td class="num">{f(m.tackles_won)}</td>
									<td class="num">{f(m.interceptions)}</td>
									<td class="num">{m.total_distance_m != null ? (m.total_distance_m / 1000).toFixed(1) : '—'}</td>
									<td class="num">{m.top_speed_kmh != null ? `${m.top_speed_kmh}` : '—'}</td>
								</tr>
							{/each}
						</tbody>
					</table>
				</div>
			</div>
		</section>

		<!-- ── FULL STATS BREAKDOWN ──────────────────────────────────────────── -->
		<section class="detail-section">
			<div class="section-divider"></div>
			<div class="section-body">
				<SectionLabel label={$t.playerDetail.allStatsPerMatch} />
				{#each perMatch as m}
					{#if m.passes_attempted != null || m.tackles_made != null || m.total_distance_m != null}
						<div class="match-detail-block">
							<div class="match-detail-header">
								<span class="match-detail-no">Match #{m.match_no}</span>
								{#if m.opponent}
									<a href="/teams/{m.opponent.id}" class="opp-link">vs {m.opponent.name}</a>
								{/if}
								<span class="match-detail-date">{formatDate(m.match_date)}</span>
							</div>
							<div class="stat-grid">
								{#if m.passes_attempted != null}
									<div class="stat-item"><span class="si-v">{m.passes_attempted}</span><span class="si-l">{$t.playerDetail.passesAtt}</span></div>
									<div class="stat-item"><span class="si-v">{m.passes_completed ?? '—'}</span><span class="si-l">{$t.playerDetail.completed}</span></div>
									<div class="stat-item"><span class="si-v">{f(m.pass_completion_pct, '%')}</span><span class="si-l">{$t.players.colPassPct}</span></div>
								{/if}
								{#if m.crosses_attempted != null}
									<div class="stat-item"><span class="si-v">{m.crosses_attempted}</span><span class="si-l">{$t.playerDetail.crossesAtt}</span></div>
									<div class="stat-item"><span class="si-v">{m.crosses_completed ?? '—'}</span><span class="si-l">{$t.playerDetail.comp}</span></div>
								{/if}
								{#if m.crosses_inswing != null || m.crosses_outswing != null}
									<div class="stat-item"><span class="si-v">{f(m.crosses_inswing)}</span><span class="si-l">{$t.playerDetail.inswing}</span></div>
									<div class="stat-item"><span class="si-v">{f(m.crosses_outswing)}</span><span class="si-l">{$t.playerDetail.outswing}</span></div>
									<div class="stat-item"><span class="si-v">{f(m.crosses_driven)}</span><span class="si-l">{$t.playerDetail.driven}</span></div>
									<div class="stat-item"><span class="si-v">{f(m.crosses_lofted)}</span><span class="si-l">{$t.playerDetail.lofted}</span></div>
									<div class="stat-item"><span class="si-v">{f(m.crosses_cutback)}</span><span class="si-l">{$t.playerDetail.cutback}</span></div>
									<div class="stat-item"><span class="si-v">{f(m.crosses_push_cross)}</span><span class="si-l">{$t.playerDetail.pushCross}</span></div>
								{/if}
								{#if m.ball_progressions != null}
									<div class="stat-item"><span class="si-v">{m.ball_progressions}</span><span class="si-l">{$t.playerDetail.ballProgs}</span></div>
								{/if}
								{#if m.take_ons != null}
									<div class="stat-item"><span class="si-v">{m.take_ons}</span><span class="si-l">{$t.playerDetail.takeOns}</span></div>
								{/if}
								{#if m.attempts_at_goal != null}
									<div class="stat-item"><span class="si-v">{m.attempts_at_goal}</span><span class="si-l">{$t.playerDetail.shots}</span></div>
								{/if}
								{#if m.total_offers != null}
									<div class="stat-item"><span class="si-v">{m.total_offers}</span><span class="si-l">{$t.playerDetail.offers}</span></div>
									<div class="stat-item"><span class="si-v">{m.offers_received ?? '—'}</span><span class="si-l">{$t.playerDetail.received}</span></div>
								{/if}
								{#if m.tackles_made != null}
									<div class="stat-item"><span class="si-v">{m.tackles_made}</span><span class="si-l">{$t.playerDetail.tackles}</span></div>
									<div class="stat-item"><span class="si-v">{m.tackles_won ?? '—'}</span><span class="si-l">{$t.playerDetail.tklWon}</span></div>
									<div class="stat-item"><span class="si-v">{f(m.interceptions)}</span><span class="si-l">{$t.playerDetail.intercep}</span></div>
									<div class="stat-item"><span class="si-v">{f(m.blocks)}</span><span class="si-l">{$t.keyStats.blocks}</span></div>
									<div class="stat-item"><span class="si-v">{f(m.clearances)}</span><span class="si-l">{$t.keyStats.clearances}</span></div>
								{/if}
								{#if m.pressing_direct != null}
									<div class="stat-item"><span class="si-v">{m.pressing_direct}</span><span class="si-l">{$t.playerDetail.directPress}</span></div>
								{/if}
								{#if m.pressing_indirect != null}
									<div class="stat-item"><span class="si-v">{m.pressing_indirect}</span><span class="si-l">{$t.playerDetail.indirectPress}</span></div>
								{/if}
								{#if m.possession_contests_won != null}
									<div class="stat-item"><span class="si-v">{m.possession_contests_won}</span><span class="si-l">{$t.playerDetail.contestsWon}</span></div>
								{/if}
								{#if m.pushing_on_into_pressing != null}
									<div class="stat-item"><span class="si-v">{m.pushing_on_into_pressing}</span><span class="si-l">{$t.playerDetail.pushToPressing}</span></div>
								{/if}
								{#if m.duels_won_aerial != null}
									<div class="stat-item"><span class="si-v">{m.duels_won_aerial}</span><span class="si-l">{$t.playerDetail.aerialDuels}</span></div>
									<div class="stat-item"><span class="si-v">{f(m.duels_won_physical)}</span><span class="si-l">{$t.playerDetail.physDuels}</span></div>
								{/if}
								{#if m.possession_regains != null}
									<div class="stat-item"><span class="si-v">{m.possession_regains}</span><span class="si-l">{$t.playerDetail.possRegains}</span></div>
								{/if}
								{#if m.total_distance_m != null}
									<div class="stat-item"><span class="si-v">{(m.total_distance_m / 1000).toFixed(1)} km</span><span class="si-l">{$t.playerDetail.distance}</span></div>
									<div class="stat-item"><span class="si-v">{f(m.high_speed_runs)}</span><span class="si-l">{$t.players.colHsRuns}</span></div>
									<div class="stat-item"><span class="si-v">{f(m.sprints)}</span><span class="si-l">{$t.players.colSprints}</span></div>
									<div class="stat-item"><span class="si-v">{m.top_speed_kmh ?? '—'} km/h</span><span class="si-l">{$t.players.colTopSpeed}</span></div>
								{/if}
							</div>
						</div>
					{/if}
				{/each}
			</div>
		</section>
	{/if}

	<!-- ── LINE BREAKS ──────────────────────────────────────────────────── -->
	{#if lineBreaks.length > 0}
		<section class="detail-section">
			<div class="section-divider"></div>
			<div class="section-body">
				<SectionLabel label={$t.playerDetail.lineBreaksPerMatch} />
				<div class="matches-table-wrap">
					<table class="matches-table">
						<thead>
							<tr>
								<th>{$t.playerDetail.colMatch}</th>
								<th class="num">{$t.playerDetail.lbAtt}</th>
								<th class="num">{$t.playerDetail.lbComp}</th>
								<th class="num">{$t.playerDetail.lbThrough}</th>
								<th class="num">{$t.playerDetail.lbAround}</th>
								<th class="num">{$t.playerDetail.lbOver}</th>
								<th class="num">{$t.playerDetail.lbPass}</th>
								<th class="num">{$t.playerDetail.lbCross}</th>
								<th class="num">{$t.playerDetail.lbBallProg}</th>
							</tr>
						</thead>
						<tbody>
							{#each lineBreaks as lb}
								<tr>
									<td class="match-no">#{lb.match_no ?? '—'}</td>
									<td class="num">{lb.attempted ?? '—'}</td>
									<td class="num">{lb.completed ?? '—'}</td>
									<td class="num">{lb.dir_through ?? '—'}</td>
									<td class="num">{lb.dir_around ?? '—'}</td>
									<td class="num">{lb.dir_over ?? '—'}</td>
									<td class="num">{lb.dist_pass ?? '—'}</td>
									<td class="num">{lb.dist_cross ?? '—'}</td>
									<td class="num">{lb.dist_ball_prog ?? '—'}</td>
								</tr>
								{#if lb.unit_4u_attacking != null || lb.unit_3u_attacking != null || lb.unit_2u_midfield != null}
									<tr class="unit-row">
										<td colspan="9">
											<div class="unit-grid">
												{#if lb.unit_4u_attacking != null}
													<span class="unit-chip">4u Att: {lb.unit_4u_attacking}</span>
												{/if}
												{#if lb.unit_4u_attacking_mid != null}
													<span class="unit-chip">4u AM: {lb.unit_4u_attacking_mid}</span>
												{/if}
												{#if lb.unit_4u_midfield != null}
													<span class="unit-chip">4u Mid: {lb.unit_4u_midfield}</span>
												{/if}
												{#if lb.unit_4u_defensive != null}
													<span class="unit-chip">4u Def: {lb.unit_4u_defensive}</span>
												{/if}
												{#if lb.unit_3u_attacking != null}
													<span class="unit-chip">3u Att: {lb.unit_3u_attacking}</span>
												{/if}
												{#if lb.unit_3u_midfield != null}
													<span class="unit-chip">3u Mid: {lb.unit_3u_midfield}</span>
												{/if}
												{#if lb.unit_3u_defensive != null}
													<span class="unit-chip">3u Def: {lb.unit_3u_defensive}</span>
												{/if}
												{#if lb.unit_2u_midfield != null}
													<span class="unit-chip">2u Mid: {lb.unit_2u_midfield}</span>
												{/if}
												{#if lb.unit_2u_defensive != null}
													<span class="unit-chip">2u Def: {lb.unit_2u_defensive}</span>
												{/if}
											</div>
										</td>
									</tr>
								{/if}
							{/each}
						</tbody>
					</table>
				</div>
			</div>
		</section>
	{/if}
{/if}

<style>
	/* ── Error/back ──────────────────────────────────────────────────── */
	.error-state {
		padding: var(--sp-10) var(--sp-8);
		display: flex;
		flex-direction: column;
		gap: var(--sp-4);
	}
	.error-text { color: var(--c-red); }
	.back-link {
		font-size: var(--fs-ui);
		font-weight: 600;
		color: var(--accent);
		text-decoration: none;
	}
	.back-link:hover { text-decoration: underline; }

	/* ── Player header ───────────────────────────────────────────────── */
	.player-header {
		padding: 40px var(--sp-8) var(--sp-8);
		background: var(--surface);
		display: flex;
		flex-direction: column;
		gap: var(--sp-5);
	}
	.player-header__nav {
		display: flex;
		align-items: center;
		gap: var(--sp-6);
	}
	.player-hero {
		display: flex;
		align-items: flex-start;
		justify-content: space-between;
		gap: var(--sp-6);
	}
	.player-hero__left {
		display: flex;
		align-items: center;
		gap: var(--sp-5);
	}
	.hero-flag {
		width: 60px;
		height: 42px;
		border-radius: 4px;
		box-shadow: 0 2px 8px rgba(0,0,0,0.18);
		flex-shrink: 0;
	}
	.hero-pos {
		font-size: var(--fs-label);
		font-weight: 700;
		text-transform: uppercase;
		letter-spacing: 0.1em;
		margin-bottom: var(--sp-1);
	}
	.hero-name {
		font-size: var(--fs-hero);
		font-weight: 900;
		line-height: 1.05;
		color: var(--ink);
	}
	.hero-team {
		display: flex;
		align-items: center;
		gap: var(--sp-2);
		margin-top: var(--sp-2);
	}
	.team-badge {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		padding: 2px 8px;
		border-radius: var(--r-sm);
		font-size: var(--fs-label);
		font-weight: 800;
		letter-spacing: 0.04em;
	}
	.hero-team-name {
		font-size: var(--fs-ui);
		font-weight: 600;
		color: var(--muted);
	}
	.hero-number {
		font-size: 5rem;
		font-weight: 900;
		font-variant-numeric: tabular-nums;
		color: var(--border);
		line-height: 1;
		flex-shrink: 0;
		letter-spacing: -0.03em;
	}

	/* ── Section ─────────────────────────────────────────────────────── */
	.section-divider { height: 1px; background: var(--border); }
	.section-body {
		padding: var(--sp-8);
		display: flex;
		flex-direction: column;
		gap: var(--sp-5);
	}

	/* ── Career totals grid ──────────────────────────────────────────── */
	.totals-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
		gap: var(--sp-3);
	}
	.total-card {
		background: var(--surface);
		border: 1px solid var(--border);
		border-radius: var(--r-md);
		padding: var(--sp-4) var(--sp-5);
		display: flex;
		flex-direction: column;
		gap: var(--sp-1);
	}
	.total-card--highlight {
		border-color: var(--accent);
		background: color-mix(in srgb, var(--accent) 6%, var(--surface));
	}
	.total-card--yellow {
		border-color: var(--c-yellow);
		background: color-mix(in srgb, var(--c-yellow) 8%, var(--surface));
	}
	.total-card--red {
		border-color: var(--c-red);
		background: color-mix(in srgb, var(--c-red) 8%, var(--surface));
	}
	.total-val {
		font-size: var(--fs-h2);
		font-weight: 800;
		font-variant-numeric: tabular-nums;
		color: var(--ink);
		line-height: 1.1;
	}
	.total-lbl {
		font-size: var(--fs-meta);
		font-weight: 600;
		text-transform: uppercase;
		letter-spacing: 0.06em;
		color: var(--muted);
	}

	/* ── Matches table ───────────────────────────────────────────────── */
	.matches-table-wrap {
		overflow-x: auto;
	}
	.matches-table {
		width: 100%;
		min-width: 700px;
		border-collapse: collapse;
		font-size: var(--fs-ui);
	}
	.matches-table thead th {
		text-align: left;
		font-size: var(--fs-meta);
		font-weight: 700;
		text-transform: uppercase;
		letter-spacing: 0.06em;
		color: var(--muted);
		padding: var(--sp-2) var(--sp-3);
		border-bottom: 2px solid var(--border);
	}
	.matches-table tbody tr {
		border-bottom: 1px solid var(--border-soft);
	}
	.matches-table tbody tr:last-child { border-bottom: none; }
	.matches-table td {
		padding: var(--sp-2) var(--sp-3);
		color: var(--ink);
	}
	.matches-table td.num {
		text-align: right;
		font-variant-numeric: tabular-nums;
		font-weight: 500;
	}
	.matches-table th.num { text-align: right; }
	.match-no {
		font-weight: 700;
		color: var(--muted);
		font-variant-numeric: tabular-nums;
	}
	.opp-link {
		font-weight: 700;
		text-decoration: none;
		color: var(--accent);
	}
	.opp-link:hover { text-decoration: underline; }
	.status-badge {
		font-size: var(--fs-meta);
		font-weight: 700;
		text-transform: uppercase;
		letter-spacing: 0.06em;
		padding: 2px 6px;
		border-radius: 3px;
		background: var(--border-soft);
		color: var(--muted);
	}
	.status-started {
		background: color-mix(in srgb, var(--accent) 15%, transparent);
		color: var(--accent);
	}

	/* ── Per-match detail blocks ─────────────────────────────────────── */
	.match-detail-block {
		background: var(--surface);
		border: 1px solid var(--border);
		border-radius: var(--r-md);
		padding: var(--sp-5) var(--sp-6);
		display: flex;
		flex-direction: column;
		gap: var(--sp-4);
	}
	.match-detail-header {
		display: flex;
		align-items: center;
		gap: var(--sp-4);
		flex-wrap: wrap;
	}
	.match-detail-no {
		font-size: var(--fs-ui);
		font-weight: 800;
		color: var(--ink);
	}
	.match-detail-date {
		font-size: var(--fs-meta);
		color: var(--muted);
		margin-inline-start: auto;
	}
	.stat-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(90px, 1fr));
		gap: var(--sp-3);
	}
	.stat-item {
		display: flex;
		flex-direction: column;
		gap: 2px;
	}
	.si-v {
		font-size: var(--fs-ui);
		font-weight: 700;
		font-variant-numeric: tabular-nums;
		color: var(--ink);
	}
	.si-l {
		font-size: 10px;
		font-weight: 600;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		color: var(--muted);
	}

	/* ── Unit breakdown row ─────────────────────────────────────────── */
	.unit-row td {
		padding: 2px var(--sp-3) var(--sp-2);
		background: color-mix(in srgb, var(--accent) 4%, transparent);
	}
	.unit-grid {
		display: flex;
		flex-wrap: wrap;
		gap: 4px;
	}
	.unit-chip {
		font-size: 10px;
		font-weight: 600;
		font-variant-numeric: tabular-nums;
		color: var(--muted);
		background: var(--border-soft);
		border-radius: 3px;
		padding: 1px 5px;
	}

	/* ── Responsive ──────────────────────────────────────────────────── */
	@media (max-width: 720px) {
		.player-header, .section-body {
			padding-left: var(--sp-4);
			padding-right: var(--sp-4);
		}
		.hero-name { font-size: 2.25rem; }
		.hero-number { font-size: 3.5rem; }
		.hero-flag { width: 44px; height: 30px; }
	}
</style>
