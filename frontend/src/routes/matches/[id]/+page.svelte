<script lang="ts">
	import type { PageData } from './$types';
	import PossessionBar from '$lib/components/viz/PossessionBar.svelte';
	import PhasesBar from '$lib/components/viz/PhasesBar.svelte';
	import PitchSpatial from '$lib/components/viz/PitchSpatial.svelte';
	import LineBreaksBars from '$lib/components/viz/LineBreaksBars.svelte';
	import FinalThirdZones from '$lib/components/viz/FinalThirdZones.svelte';
	import KeyStatsTable from '$lib/components/viz/KeyStatsTable.svelte';
	import ShotTimeline from '$lib/components/viz/ShotTimeline.svelte';
	import PassingNetwork from '$lib/components/viz/PassingNetwork.svelte';
	import CrossesDetail from '$lib/components/viz/CrossesDetail.svelte';
	import OfferingsDetail from '$lib/components/viz/OfferingsDetail.svelte';
	import MovementDetail from '$lib/components/viz/MovementDetail.svelte';
	import PressureDetail from '$lib/components/viz/PressureDetail.svelte';
	import DefensiveDetail from '$lib/components/viz/DefensiveDetail.svelte';
	import GkDetail from '$lib/components/viz/GkDetail.svelte';
	import SpatialMobilePicker from '$lib/components/viz/SpatialMobilePicker.svelte';
	import LineupPanel from '$lib/components/viz/LineupPanel.svelte';
	import PhaseFingerprint from '$lib/components/modules/PhaseFingerprint.svelte';
	import SectionLabel from '$lib/components/primitives/SectionLabel.svelte';
	import { teamColorVar, teamTextColor, flagCode, badgeTextColor } from '$lib/tokens';
	import { t } from '$lib/i18n';

	let { data }: { data: PageData } = $props();

	const m = $derived(data.match);
	const possession = $derived(data.possession);
	const phases = $derived(data.phases);
	const spatial = $derived(data.spatial);
	const lineBreaks = $derived(data.lineBreaks);
	const defensive = $derived(data.defensive);
	const finalThird = $derived(data.finalThird);
	const keyStats = $derived(data.keyStats);
	const shots = $derived(data.shots);
	const passingNetwork = $derived(data.passingNetwork);
	const crosses = $derived(data.crosses);
	const offerings = $derived(data.offerings);
	const movement = $derived(data.movement);
	const pressure = $derived(data.pressure);
	const gkStats = $derived(data.gkStats);
	const playerNameMap = $derived((data.playerNameMap ?? {}) as Record<string, number>);
	const lineup = $derived(data.lineup ?? null);

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

	function lineLabel(type: string): string {
		return type === 'defensive' ? $t.detail.lineDefensive : type === 'midfield' ? $t.detail.lineMidfield : $t.detail.lineAttacking;
	}
</script>

<svelte:head>
	<title>{m ? `${m.team_a.short_code} ${m.score_a}:${m.score_b} ${m.team_b.short_code}` : 'Match'} — EFI Data Engine</title>
</svelte:head>

{#if data.error && !m}
	<div class="error-state">
		<a href="/matches" class="back-link">{$t.match.backToMatches}</a>
		<p class="error-text">{$t.error.matchNotFound}</p>
	</div>
{:else if m}
	<!-- ── MATCH HEADER ──────────────────────────────────────────────────── -->
	<section class="match-header">
		<div class="match-header__nav">
			<a href="/matches" class="back-link">{$t.match.backToMatches}</a>
			<span class="match-meta">{$t.match.group} {m.group_letter} · {$t.match.matchNo} {m.match_no}</span>
		</div>

		{#if m.venue || m.match_date}
			<div class="match-context">
				{#if m.venue}<span class="match-venue">{m.venue}</span>{/if}
				{#if m.match_date}<span class="match-date">{formatDate(m.match_date)}</span>{/if}
			</div>
		{/if}

		<div class="scoreline">
			<div class="scoreline__team scoreline__team--left">
				<div class="team-identity">
					{#if flagCode(m.team_a.short_code)}
						<span class="fi fi-{flagCode(m.team_a.short_code)} scoreline__flag" aria-hidden="true"></span>
					{/if}
					<span class="team-badge" style="background:{teamColorVar(m.team_a.color)};color:{badgeTextColor(m.team_a.color)};">{m.team_a.short_code}</span>
				</div>
				<a href="/teams/{m.team_a.id}" class="team-name">{m.team_a.name}</a>
				{#if m.formation_a}<span class="team-formation">{m.formation_a}</span>{/if}
			</div>
			<div class="scoreline__score">
				<span class="score">{m.score_a}</span>
				<span class="colon">:</span>
				<span class="score">{m.score_b}</span>
			</div>
			<div class="scoreline__team scoreline__team--right">
				<div class="team-identity">
					<span class="team-badge" style="background:{teamColorVar(m.team_b.color)};color:{badgeTextColor(m.team_b.color)};">{m.team_b.short_code}</span>
					{#if flagCode(m.team_b.short_code)}
						<span class="fi fi-{flagCode(m.team_b.short_code)} scoreline__flag" aria-hidden="true"></span>
					{/if}
				</div>
				<a href="/teams/{m.team_b.id}" class="team-name">{m.team_b.name}</a>
				{#if m.formation_b}<span class="team-formation">{m.formation_b}</span>{/if}
			</div>
		</div>

		{#if possession}
			<div class="xg-row">
				<span class="xg" style="color: {teamTextColor(m.team_a.color)};">xG {(possession.xg_a ?? 0).toFixed(2)}</span>
				<span class="xg xg--right" style="color: {teamTextColor(m.team_b.color)};">xG {(possession.xg_b ?? 0).toFixed(2)}</span>
			</div>
		{/if}
	</section>

	<!-- ── POSSESSION ─────────────────────────────────────────────────────── -->
	{#if possession}
		<section class="detail-section">
			<div class="section-divider"></div>
			<div class="section-body">
				<SectionLabel label="{$t.detail.possession}" />
				<PossessionBar stats={possession} team_a={m.team_a} team_b={m.team_b} />
			</div>
		</section>
	{/if}

	<!-- ── FULL KEY STATS ──────────────────────────────────────────────────── -->
	{#if keyStats}
		<section class="detail-section">
			<div class="section-divider"></div>
			<div class="section-body">
				<KeyStatsTable
					stats_a={keyStats.a}
					stats_b={keyStats.b}
					team_a={m.team_a}
					team_b={m.team_b}
				/>
			</div>
		</section>
	{/if}

	<!-- ── LINEUP ────────────────────────────────────────────────────────── -->
	{#if lineup && (lineup.team_a?.starters?.length || lineup.team_b?.starters?.length)}
		<section class="detail-section">
			<div class="section-divider"></div>
			<div class="section-body">
				<SectionLabel label={$t.detail.lineup} />
				<LineupPanel
					lineup_a={lineup.team_a}
					lineup_b={lineup.team_b}
					team_a={m.team_a}
					team_b={m.team_b}
				/>
			</div>
		</section>
	{/if}

	<!-- ── PHASES + LINE BREAKS ───────────────────────────────────────────── -->
	{#if phases || lineBreaks}
		<section class="detail-section">
			<div class="section-divider"></div>
			<div class="two-col">
				{#if phases}
					<div class="two-col__cell">
						<SectionLabel label="{$t.detail.phases}" />
						<PhasesBar
							phases_a={phases.team_a}
							phases_b={phases.team_b}
							team_a={m.team_a}
							team_b={m.team_b}
						/>
					</div>
				{/if}
				{#if lineBreaks}
					<div class="two-col__cell">
						<SectionLabel label="{$t.detail.lineBreaks}" />
						<LineBreaksBars
							breaks_a={lineBreaks.team_a}
							breaks_b={lineBreaks.team_b}
							team_a={m.team_a}
							team_b={m.team_b}
						/>
					</div>
				{/if}
			</div>
		</section>
	{/if}

	<!-- ── PHASE FINGERPRINT ─────────────────────────────────────────────── -->
	{#if phases && (phases.team_a?.length || phases.team_b?.length)}
		<section class="detail-section">
			<div class="section-divider"></div>
			<div class="section-body">
				<SectionLabel label={$t.detail.phaseFingerprint} />
				<div class="fingerprint-wrap">
					<PhaseFingerprint
						{phases}
						team_a={m.team_a}
						team_b={m.team_b}
					/>
				</div>
			</div>
		</section>
	{/if}

	<!-- ── SPATIAL CONTROL ───────────────────────────────────────────────── -->
	{#if spatial}
		<section class="detail-section">
			<div class="section-divider"></div>

			<!-- Desktop: two columns, each locked to a scenario (hidden on mobile) -->
			<div class="spatial-desktop">
				<div class="section-body">
					<SectionLabel label={$t.detail.outOfPossession} />
					<PitchSpatial
						spatial_a={spatial.team_a}
						spatial_b={spatial.team_b}
						team_a={m.team_a}
						team_b={m.team_b}
						compact
						lockedScenario="defensive"
					/>
				</div>
				<div class="section-body">
					<SectionLabel label={$t.detail.inPossession} />
					<PitchSpatial
						spatial_a={spatial.team_a}
						spatial_b={spatial.team_b}
						team_a={m.team_a}
						team_b={m.team_b}
						compact
						lockedScenario="possession"
					/>
				</div>
			</div>

			<!-- Mobile: single pitch with scenario + team pickers (hidden on desktop) -->
			<div class="spatial-mobile section-body">
				<SectionLabel label="{$t.detail.spatial}" />
				<SpatialMobilePicker
					spatial_a={spatial.team_a}
					spatial_b={spatial.team_b}
					team_a={m.team_a}
					team_b={m.team_b}
				/>
			</div>
		</section>
	{/if}

	<!-- ── FINAL THIRD ENTRIES ────────────────────────────────────────────── -->
	{#if finalThird && (finalThird.team_a?.length || finalThird.team_b?.length)}
		<section class="detail-section">
			<div class="section-divider"></div>
			<div class="section-body">
				<SectionLabel label="{$t.detail.finalThirdEntries}" />
				<FinalThirdZones
					entries_a={finalThird.team_a ?? []}
					entries_b={finalThird.team_b ?? []}
					team_a={m.team_a}
					team_b={m.team_b}
				/>
			</div>
		</section>
	{/if}

	<!-- ── SHOT TIMELINE ──────────────────────────────────────────────────────── -->
	{#if shots && (shots.team_a?.length || shots.team_b?.length)}
		<section class="detail-section">
			<div class="section-divider"></div>
			<div class="section-body">
				<SectionLabel label={$t.detail.shotLog} />
				<ShotTimeline
					shots_a={shots.team_a ?? []}
					shots_b={shots.team_b ?? []}
					team_a={m.team_a}
					team_b={m.team_b}
					{playerNameMap}
				/>
			</div>
		</section>
	{/if}

	<!-- ── PASSING NETWORK + PRESSURE ────────────────────────────────────────── -->
	{#if passingNetwork || pressure}
		<section class="detail-section">
			<div class="section-divider"></div>
			<div class="two-col">
				{#if passingNetwork && (passingNetwork.team_a?.length || passingNetwork.team_b?.length)}
					<div class="two-col__cell">
						<SectionLabel label={$t.detail.passingNetwork} />
						<PassingNetwork
							conns_a={passingNetwork.team_a ?? []}
							conns_b={passingNetwork.team_b ?? []}
							team_a={m.team_a}
							team_b={m.team_b}
							{playerNameMap}
						/>
					</div>
				{/if}
				{#if pressure && (pressure.team_a || pressure.team_b)}
					<div class="two-col__cell">
						<SectionLabel label={$t.detail.defensivePressure} />
						<PressureDetail
							pressure_a={pressure.team_a}
							pressure_b={pressure.team_b}
							team_a={m.team_a}
							team_b={m.team_b}
						/>
					</div>
				{/if}
			</div>
		</section>
	{/if}

	<!-- ── CROSSES + OFFERINGS ───────────────────────────────────────────────── -->
	{#if crosses || offerings}
		<section class="detail-section">
			<div class="section-divider"></div>
			<div class="two-col">
				{#if crosses && (crosses.team_a || crosses.team_b)}
					<div class="two-col__cell">
						<SectionLabel label={$t.detail.crossesSection} />
						<CrossesDetail
							crosses_a={crosses.team_a}
							crosses_b={crosses.team_b}
							team_a={m.team_a}
							team_b={m.team_b}
						/>
					</div>
				{/if}
				{#if offerings && (offerings.team_a || offerings.team_b)}
					<div class="two-col__cell">
						<SectionLabel label={$t.detail.offering} />
						<OfferingsDetail
							offerings_a={offerings.team_a}
							offerings_b={offerings.team_b}
							team_a={m.team_a}
							team_b={m.team_b}
						/>
					</div>
				{/if}
			</div>
		</section>
	{/if}

	<!-- ── DEFENSIVE ACTIONS ────────────────────────────────────────────────── -->
	{#if defensive && (defensive.team_a || defensive.team_b)}
		<section class="detail-section">
			<div class="section-divider"></div>
			<div class="section-body">
				<SectionLabel label={$t.detail.defensiveActionsDetail} />
				<DefensiveDetail
					defensive_a={defensive.team_a}
					defensive_b={defensive.team_b}
					team_a={m.team_a}
					team_b={m.team_b}
				/>
			</div>
		</section>
	{/if}

	<!-- ── MOVEMENT ───────────────────────────────────────────────────────────── -->
	{#if movement && (movement.team_a || movement.team_b)}
		<section class="detail-section">
			<div class="section-divider"></div>
			<div class="section-body">
				<SectionLabel label={$t.detail.movementToReceive} />
				<MovementDetail
					movement_a={movement.team_a}
					movement_b={movement.team_b}
					team_a={m.team_a}
					team_b={m.team_b}
				/>
			</div>
		</section>
	{/if}

	<!-- ── GOALKEEPER STATS ──────────────────────────────────────────────────── -->
	{#if gkStats && (gkStats.team_a || gkStats.team_b)}
		<section class="detail-section">
			<div class="section-divider"></div>
			<div class="section-body">
				<SectionLabel label={$t.detail.gkStats} />
				<GkDetail
					gk_a={gkStats.team_a}
					gk_b={gkStats.team_b}
					team_a={m.team_a}
					team_b={m.team_b}
				/>
			</div>
		</section>
	{/if}
{/if}

<style>
	/* ── Error / back ────────────────────────────────────────────────── */
	.error-state {
		padding: var(--sp-10) var(--sp-8);
		display: flex;
		flex-direction: column;
		gap: var(--sp-4);
	}
	.error-text {
		color: var(--c-red);
		font-size: var(--fs-body);
	}

	/* ── Match header ────────────────────────────────────────────────── */
	.match-header {
		padding: 40px var(--sp-8) var(--sp-8);
		background: var(--surface);
		display: flex;
		flex-direction: column;
		gap: var(--sp-6);
	}
	.match-header__nav {
		display: flex;
		align-items: center;
		gap: var(--sp-5);
		flex-wrap: wrap;
	}
	.back-link {
		font-size: var(--fs-ui);
		font-weight: 600;
		color: var(--accent);
		text-decoration: none;
	}
	.back-link:hover {
		text-decoration: underline;
	}
	.match-meta {
		font-size: var(--fs-label);
		font-weight: 500;
		text-transform: uppercase;
		letter-spacing: 0.06em;
		color: var(--muted);
	}

	/* ── Venue / date above score ────────────────────────────────────── */
	.match-context {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: var(--sp-1);
	}
	.match-venue {
		font-size: var(--fs-ui);
		font-weight: 600;
		color: var(--ink);
		text-align: center;
	}
	.match-date {
		font-size: var(--fs-label);
		font-weight: 500;
		color: var(--muted);
		text-align: center;
	}

	/* ── Scoreline ───────────────────────────────────────────────────── */
	.scoreline {
		display: flex;
		align-items: center;
		justify-content: center;
		gap: var(--sp-8);
		flex-wrap: wrap;
	}
	.scoreline__team {
		display: flex;
		flex-direction: column;
		gap: var(--sp-2);
	}
	.scoreline__team--left {
		align-items: flex-end;
		text-align: right;
	}
	.scoreline__team--right {
		align-items: flex-start;
		text-align: left;
	}
	.team-identity {
		display: flex;
		align-items: center;
		gap: var(--sp-3);
	}
	.team-formation {
		font-size: var(--fs-meta);
		font-weight: 600;
		color: var(--muted);
		font-family: var(--font-mono, monospace);
		letter-spacing: 0.04em;
	}
	.scoreline__flag {
		width: 44px;
		height: 30px;
		border-radius: 3px;
		flex-shrink: 0;
		box-shadow: 0 1px 4px rgba(0,0,0,0.15);
	}
	.team-badge {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		padding: var(--sp-1) var(--sp-3);
		border-radius: var(--r-sm);
		font-size: var(--fs-ui);
		font-weight: 800;
		letter-spacing: 0.06em;
		min-width: 44px;
		min-height: 28px;
	}
	.team-name {
		font-size: var(--fs-h2);
		font-weight: 700;
		color: var(--ink);
		text-decoration: none;
	}
	a.team-name:hover {
		color: var(--accent);
		text-decoration: underline;
	}
	.scoreline__score {
		display: flex;
		align-items: center;
		gap: var(--sp-2);
	}
	.score {
		font-size: var(--fs-score);
		font-weight: 900;
		font-variant-numeric: tabular-nums;
		color: var(--ink);
		line-height: 1;
	}
	.colon {
		font-size: var(--fs-score);
		font-weight: 300;
		color: var(--muted);
	}

	/* ── xG row ──────────────────────────────────────────────────────── */
	.xg-row {
		display: flex;
		justify-content: center;
		gap: var(--sp-10);
	}
	.xg {
		font-size: var(--fs-ui);
		font-weight: 700;
		font-variant-numeric: tabular-nums;
		letter-spacing: 0.04em;
	}
	.xg--right {
		text-align: right;
	}

	/* ── Section wrapper ─────────────────────────────────────────────── */
	.section-divider {
		height: 1px;
		background: var(--border);
	}
	.section-body {
		padding: var(--sp-8) var(--sp-8);
		display: flex;
		flex-direction: column;
		gap: var(--sp-5);
	}

	/* ── Phase fingerprint ──────────────────────────────────────────── */
	.fingerprint-wrap {
		max-width: 480px;
		margin: 0 auto;
	}

	/* ── Spatial ────────────────────────────────────────────────────── */
	.spatial-desktop {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 0;
	}
	.spatial-desktop > .section-body + .section-body {
		border-left: 1px solid var(--border);
	}
	.spatial-mobile { display: none; }

	@media (max-width: 600px) {
		.spatial-desktop { display: none; }
		.spatial-mobile { display: flex; flex-direction: column; gap: var(--sp-5); }
	}

	/* ── KPI row ─────────────────────────────────────────────────────── */
	.kpi-row {
		display: flex;
		gap: var(--sp-6);
		flex-wrap: wrap;
		padding-top: var(--sp-2);
	}
	.kpi {
		display: flex;
		flex-direction: column;
		gap: var(--sp-1);
	}
	.kpi__value {
		font-size: var(--fs-stat);
		font-weight: 800;
		font-variant-numeric: tabular-nums;
		color: var(--ink);
		line-height: 1;
	}
	.kpi__label {
		font-size: var(--fs-label);
		font-weight: 600;
		text-transform: uppercase;
		letter-spacing: 0.08em;
		color: var(--muted);
	}

	/* ── Two-column layout ───────────────────────────────────────────── */
	.two-col {
		display: grid;
		grid-template-columns: 1fr 1fr;
		background: var(--border);
		gap: 1px;
	}
	.two-col__cell {
		padding: var(--sp-8);
		background: var(--bg);
		display: flex;
		flex-direction: column;
		gap: var(--sp-5);
	}


	/* ── Responsive ──────────────────────────────────────────────────── */
	@media (max-width: 1024px) {
		.two-col {
			grid-template-columns: 1fr;
		}
	}
	@media (max-width: 720px) {
		.match-header,
		.section-body,
		.two-col__cell {
			padding-left: var(--sp-4);
			padding-right: var(--sp-4);
		}
		.team-name {
			font-size: var(--fs-body);
		}
		.score {
			font-size: 2.5rem;
		}
		.scoreline {
			gap: var(--sp-4);
		}
		.scoreline__flag { width: 32px; height: 22px; }
		.kpi-row { gap: var(--sp-4); }
	}
	@media (max-width: 480px) {
		.team-name { display: none; }
		.scoreline { gap: var(--sp-3); }
		.score { font-size: 2rem; }
	}
</style>
