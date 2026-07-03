<script lang="ts">
	import type { LineBreak, Team } from '$lib/types/efi';
	import { teamColorVar, teamTextColor } from '$lib/tokens';
	import { t } from '$lib/i18n';

	let {
		breaks_a,
		breaks_b,
		team_a,
		team_b
	}: { breaks_a: LineBreak[]; breaks_b: LineBreak[]; team_a: Team; team_b: Team } = $props();

	const lineOrder: LineBreak['line_type'][] = ['defensive', 'midfield', 'attacking'];
	const lineLabels = $derived({
		defensive: $t.detail.lineDefensive,
		midfield: $t.detail.lineMidfield,
		attacking: $t.detail.lineAttacking,
	});

	function getBreak(breaks: LineBreak[], line: string): LineBreak | undefined {
		return breaks.find((b) => b.line_type === line);
	}

	function completionPct(completed: number, attempted: number): number {
		return attempted > 0 ? Math.round((completed / attempted) * 100) : 0;
	}
</script>

<figure class="lb" role="img" aria-label="Line breaks — {team_a.name} vs {team_b.name}">
	<!-- Team header row -->
	<div class="lb__teams">
		<a href="/teams/{team_a.id}" class="lb__team-name" style="color: {teamTextColor(team_a.color)}; text-align: right;">{team_a.name}</a>
		<span class="lb__center-label">{$t.detail.lineBreaks}</span>
		<a href="/teams/{team_b.id}" class="lb__team-name" style="color: {teamTextColor(team_b.color)};">{team_b.name}</a>
	</div>

	{#each lineOrder as line}
		{@const ba = getBreak(breaks_a, line)}
		{@const bb = getBreak(breaks_b, line)}
		{@const pctA = ba ? completionPct(ba.completed ?? 0, ba.attempted ?? 0) : 0}
		{@const pctB = bb ? completionPct(bb.completed ?? 0, bb.attempted ?? 0) : 0}
		<div class="lb__row">
			<!-- Team A side -->
			<div class="lb__side lb__side--left">
				{#if ba}
					<div class="lb__numbers lb__numbers--left">
						<span class="lb__completed">{ba.completed ?? 0}</span>
						<span class="lb__slash">/</span>
						<span class="lb__attempted">{ba.attempted ?? 0}</span>
						<span class="lb__pct">({pctA}%)</span>
					</div>
					<div class="lb__track lb__track--left">
						<div
							class="lb__fill lb__fill--left"
							style="width: {pctA}%; background: {teamColorVar(team_a.color)};"
						></div>
					</div>
				{:else}
					<div class="lb__side-empty"></div>
				{/if}
			</div>

			<!-- Center line label -->
			<div class="lb__center">{lineLabels[line] ?? line}</div>

			<!-- Team B side -->
			<div class="lb__side lb__side--right">
				{#if bb}
					<div class="lb__track lb__track--right">
						<div
							class="lb__fill lb__fill--right"
							style="width: {pctB}%; background: {teamColorVar(team_b.color)};"
						></div>
					</div>
					<div class="lb__numbers lb__numbers--right">
						<span class="lb__pct">({pctB}%)</span>
						<span class="lb__completed">{bb.completed ?? 0}</span>
						<span class="lb__slash">/</span>
						<span class="lb__attempted">{bb.attempted ?? 0}</span>
					</div>
				{:else}
					<div class="lb__side-empty"></div>
				{/if}
			</div>
		</div>
	{/each}
</figure>

<style>
	.lb {
		display: flex;
		flex-direction: column;
		gap: 0;
		width: 100%;
	}

	/* ── Team header ─────────────────────────────────────────────────── */
	.lb__teams {
		display: grid;
		grid-template-columns: 1fr 140px 1fr;
		align-items: center;
		padding-bottom: var(--sp-3);
	}
	.lb__team-name {
		font-size: var(--fs-label);
		font-weight: 800;
		text-transform: uppercase;
		letter-spacing: 0.04em;
		text-decoration: none;
	}
	.lb__team-name:hover { text-decoration: underline; }
	.lb__center-label {
		font-size: var(--fs-meta);
		font-weight: 700;
		text-transform: uppercase;
		letter-spacing: 0.1em;
		color: var(--muted);
		text-align: center;
	}

	/* ── Row ─────────────────────────────────────────────────────────── */
	.lb__row {
		display: grid;
		grid-template-columns: 1fr 140px 1fr;
		align-items: center;
		min-height: 44px;
		padding: var(--sp-2) 0;
		border-top: 1px solid var(--border-soft);
		gap: var(--sp-2);
	}
	.lb__row:last-child { border-bottom: 1px solid var(--border-soft); }

	/* ── Center line label ───────────────────────────────────────────── */
	.lb__center {
		font-size: 11px;
		font-weight: 600;
		color: var(--muted);
		text-align: center;
		padding: 0 var(--sp-2);
		line-height: 1.3;
	}

	/* ── Side cells ──────────────────────────────────────────────────── */
	.lb__side {
		display: flex;
		flex-direction: column;
		gap: var(--sp-1);
	}
	.lb__side--left { align-items: flex-end; }
	.lb__side--right { align-items: flex-start; }
	.lb__side-empty { flex: 1; }

	/* ── Numbers ─────────────────────────────────────────────────────── */
	.lb__numbers {
		display: flex;
		align-items: baseline;
		gap: 2px;
		font-variant-numeric: tabular-nums;
	}
	.lb__numbers--left { flex-direction: row-reverse; }
	.lb__numbers--right { flex-direction: row; }
	.lb__completed {
		font-size: var(--fs-ui);
		font-weight: 800;
		color: var(--ink);
	}
	.lb__slash {
		font-size: var(--fs-label);
		font-weight: 400;
		color: var(--muted);
	}
	.lb__attempted {
		font-size: var(--fs-ui);
		font-weight: 600;
		color: var(--muted);
	}
	.lb__pct {
		font-size: 11px;
		font-weight: 600;
		color: var(--muted);
		margin: 0 var(--sp-1);
	}

	/* ── Track + fill ────────────────────────────────────────────────── */
	.lb__track {
		width: 100%;
		height: 10px;
		background: var(--border-soft);
		border-radius: var(--r-pill);
		overflow: hidden;
		display: flex;
	}
	.lb__track--left { justify-content: flex-end; }
	.lb__track--right { justify-content: flex-start; }
	.lb__fill {
		height: 100%;
		border-radius: var(--r-pill);
		transition: width 0.4s ease;
		min-width: 3px;
	}

	/* ── Responsive ──────────────────────────────────────────────────── */
	@media (max-width: 600px) {
		.lb__teams,
		.lb__row {
			grid-template-columns: 1fr 100px 1fr;
		}
		.lb__pct { display: none; }
	}
</style>
