<script lang="ts">
	import type { Phase, Team } from '$lib/types/efi';
	import { phaseColor, teamTextColor } from '$lib/tokens';
	import { t } from '$lib/i18n';

	let {
		phases_a,
		phases_b,
		team_a,
		team_b
	}: { phases_a: Phase[]; phases_b: Phase[]; team_a: Team; team_b: Team } = $props();

	const PHASE_KEYS: Record<string, string> = {
		'Build Up Unopposed': 'buildUpUnopposed',
		'Build Up Opposed': 'buildUpOpposed',
		'Progression': 'progression',
		'Final Third': 'finalThird',
		'Long Ball': 'longBall',
		'Attacking Transition': 'attackingTransition',
		'Counter Attack': 'counterAttack',
		'Set Piece': 'setPiece',
		'High Press': 'highPress',
		'Mid Press': 'midPress',
		'Low Press': 'lowPress',
		'High Block': 'highBlock',
		'Mid Block': 'midBlock',
		'Low Block': 'lowBlock',
		'Recovery': 'recovery',
		'Defensive Transition': 'defensiveTransition',
		'Counter-press': 'counterPress',
	};

	// Keep the TS cast in the script block — `as`-casts in template markup have
	// repeatedly broken the rollup SSR build in this project.
	function phaseLabel(name: string): string {
		const dict: Record<string, string> = $t.phases;
		return dict[PHASE_KEYS[name]] ?? name;
	}

	const inPhases_a  = $derived(phases_a.filter((p) => p.phase_group === 'in'));
	const outPhases_a = $derived(phases_a.filter((p) => p.phase_group === 'out'));
	const inPhases_b  = $derived(phases_b.filter((p) => p.phase_group === 'in'));
	const outPhases_b = $derived(phases_b.filter((p) => p.phase_group === 'out'));

	const inNames  = $derived([...new Set([...inPhases_a,  ...inPhases_b ].map((p) => p.phase_name))]);
	const outNames = $derived([...new Set([...outPhases_a, ...outPhases_b].map((p) => p.phase_name))]);

	function getPct(phases: Phase[], name: string): number {
		return phases.find((p) => p.phase_name === name)?.pct ?? 0;
	}
</script>

<figure class="phases" role="img" aria-label="Phases of play — {team_a.name} vs {team_b.name}">

	<!-- Team header row -->
	<div class="phases__team-row">
		<span class="phases__team-name" style="color: {teamTextColor(team_a.color)}; text-align: right;">{team_a.name}</span>
		<span class="phases__center-blank"></span>
		<span class="phases__team-name" style="color: {teamTextColor(team_b.color)};">{team_b.name}</span>
	</div>

	<!-- IN POSSESSION -->
	<div class="phases__section-title">{$t.phases.inPossessionHeader}</div>
	{#each inNames as name}
		{@const pctA = getPct(inPhases_a, name)}
		{@const pctB = getPct(inPhases_b, name)}
		<div class="phases__row">
			<!-- Team A bar (right-aligned, grows left) -->
			<div class="phases__bar-cell phases__bar-cell--left">
				<span class="phases__pct">{pctA > 0 ? pctA + '%' : ''}</span>
				<div class="phases__track phases__track--left">
					<div
						class="phases__fill phases__fill--left"
						style="width: {pctA}%; background: {phaseColor(name)};"
					></div>
				</div>
			</div>
			<!-- Phase name center -->
			<div class="phases__phase-name">{phaseLabel(name)}</div>
			<!-- Team B bar (left-aligned, grows right) -->
			<div class="phases__bar-cell phases__bar-cell--right">
				<div class="phases__track phases__track--right">
					<div
						class="phases__fill phases__fill--right"
						style="width: {pctB}%; background: {phaseColor(name)};"
					></div>
				</div>
				<span class="phases__pct phases__pct--right">{pctB > 0 ? pctB + '%' : ''}</span>
			</div>
		</div>
	{/each}

	<!-- OUT OF POSSESSION -->
	<div class="phases__section-title phases__section-title--out">{$t.phases.outOfPossessionHeader}</div>
	{#each outNames as name}
		{@const pctA = getPct(outPhases_a, name)}
		{@const pctB = getPct(outPhases_b, name)}
		<div class="phases__row">
			<div class="phases__bar-cell phases__bar-cell--left">
				<span class="phases__pct">{pctA > 0 ? pctA + '%' : ''}</span>
				<div class="phases__track phases__track--left">
					<div
						class="phases__fill phases__fill--left"
						style="width: {pctA}%; background: {phaseColor(name)};"
					></div>
				</div>
			</div>
			<div class="phases__phase-name">{phaseLabel(name)}</div>
			<div class="phases__bar-cell phases__bar-cell--right">
				<div class="phases__track phases__track--right">
					<div
						class="phases__fill phases__fill--right"
						style="width: {pctB}%; background: {phaseColor(name)};"
					></div>
				</div>
				<span class="phases__pct phases__pct--right">{pctB > 0 ? pctB + '%' : ''}</span>
			</div>
		</div>
	{/each}

</figure>

<style>
	.phases {
		display: flex;
		flex-direction: column;
		gap: 0;
		width: 100%;
	}

	/* ── Team header ─────────────────────────────────────────────────── */
	.phases__team-row {
		display: grid;
		grid-template-columns: 1fr 180px 1fr;
		gap: 0;
		padding: 0 0 var(--sp-3);
	}
	.phases__team-name {
		font-size: var(--fs-label);
		font-weight: 800;
		letter-spacing: 0.04em;
		text-transform: uppercase;
	}
	.phases__center-blank {
		text-align: center;
	}

	/* ── Section header ──────────────────────────────────────────────── */
	.phases__section-title {
		font-size: var(--fs-meta);
		font-weight: 700;
		letter-spacing: 0.12em;
		text-transform: uppercase;
		color: var(--accent);
		text-align: center;
		padding: var(--sp-3) 0 var(--sp-2);
		border-top: 1px solid var(--border-soft);
		margin-top: var(--sp-2);
	}
	.phases__section-title--out {
		color: var(--muted);
	}

	/* ── Phase row ───────────────────────────────────────────────────── */
	.phases__row {
		display: grid;
		grid-template-columns: 1fr 180px 1fr;
		align-items: center;
		min-height: 28px;
		gap: var(--sp-2);
		border-bottom: 1px solid var(--border-soft);
		padding: 3px 0;
	}
	.phases__row:last-child {
		border-bottom: none;
	}

	/* ── Phase name center column ────────────────────────────────────── */
	.phases__phase-name {
		font-size: 11px;
		font-weight: 500;
		color: var(--muted);
		text-align: center;
		padding: 0 var(--sp-2);
		line-height: 1.2;
	}

	/* ── Bar cells ───────────────────────────────────────────────────── */
	.phases__bar-cell {
		display: flex;
		align-items: center;
		gap: var(--sp-2);
		height: 18px;
	}
	.phases__bar-cell--left {
		justify-content: flex-end;
		flex-direction: row;
	}
	.phases__bar-cell--right {
		justify-content: flex-start;
		flex-direction: row;
	}

	/* ── Track ───────────────────────────────────────────────────────── */
	.phases__track {
		flex: 1;
		height: 14px;
		background: var(--border-soft);
		border-radius: 2px;
		overflow: hidden;
		position: relative;
	}
	.phases__track--left {
		display: flex;
		justify-content: flex-end;
	}
	.phases__track--right {
		display: flex;
		justify-content: flex-start;
	}
	.phases__fill {
		height: 100%;
		border-radius: 2px;
		transition: width 0.4s ease;
		min-width: 2px;
	}
	.phases__fill--left {
		border-radius: 2px 0 0 2px;
	}
	.phases__fill--right {
		border-radius: 0 2px 2px 0;
	}

	/* ── % labels ────────────────────────────────────────────────────── */
	.phases__pct {
		font-size: 11px;
		font-weight: 700;
		font-variant-numeric: tabular-nums;
		color: var(--ink);
		min-width: 28px;
		text-align: right;
		flex-shrink: 0;
	}
	.phases__pct--right {
		text-align: left;
	}

	/* ── Responsive ──────────────────────────────────────────────────── */
	@media (max-width: 600px) {
		.phases__team-row,
		.phases__row {
			grid-template-columns: 1fr 120px 1fr;
		}
		.phases__phase-name {
			font-size: 10px;
		}
	}
</style>
