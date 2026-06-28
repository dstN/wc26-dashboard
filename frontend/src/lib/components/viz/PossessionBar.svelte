<script lang="ts">
	import type { MatchStats, Team } from '$lib/types/efi';
	import { teamColorVar, teamTextColor } from '$lib/tokens';

	let {
		stats,
		team_a,
		team_b
	}: { stats: MatchStats; team_a: Team; team_b: Team } = $props();

	const pA = $derived(stats.possession_team_a ?? 0);
	const pB = $derived(stats.possession_team_b ?? 0);
	const pC = $derived(stats.possession_in_contest ?? 0);
</script>

<figure
	class="possession"
	role="img"
	aria-label="{team_a.name} {pA}%, In Contest {pC}%, {team_b.name} {pB}%"
>
	<div class="possession__labels">
		<a href="/teams/{team_a.id}" class="possession__team" style="color: {teamTextColor(team_a.color)}">{team_a.name}</a>
		<span class="possession__contest-label">In Contest</span>
		<a href="/teams/{team_b.id}" class="possession__team possession__team--right" style="color: {teamTextColor(team_b.color)}">{team_b.name}</a>
	</div>
	<div class="possession__bar">
		<div
			class="possession__seg possession__seg--a"
			style="flex-basis: {pA}%; background: {teamColorVar(team_a.color)};"
		></div>
		<div class="possession__seg possession__seg--contest" style="flex-basis: {pC}%;"></div>
		<div
			class="possession__seg possession__seg--b"
			style="flex-basis: {pB}%; background: {teamColorVar(team_b.color)};"
		></div>
	</div>
	<div class="possession__values">
		<span class="possession__pct">{pA}%</span>
		<span class="possession__pct possession__pct--muted">{pC}%</span>
		<span class="possession__pct possession__pct--right">{pB}%</span>
	</div>
</figure>

<style>
	.possession {
		display: flex;
		flex-direction: column;
		gap: var(--sp-2);
	}
	.possession__labels {
		display: flex;
		justify-content: space-between;
	}
	.possession__team {
		font-size: var(--fs-label);
		font-weight: 700;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		text-decoration: none;
	}
	.possession__team:hover { text-decoration: underline; }
	.possession__team--right {
		text-align: right;
	}
	.possession__contest-label {
		font-size: var(--fs-label);
		font-weight: 600;
		color: var(--muted);
		text-transform: uppercase;
		letter-spacing: 0.08em;
	}
	.possession__bar {
		display: flex;
		height: 20px;
		border-radius: var(--r-pill);
		overflow: hidden;
		gap: 2px;
	}
	.possession__seg {
		flex-shrink: 0;
		transition: flex-basis 0.3s ease;
	}
	.possession__seg--contest {
		background: repeating-linear-gradient(
			45deg,
			var(--muted) 0,
			var(--muted) 4px,
			var(--border) 4px,
			var(--border) 8px
		);
		opacity: 0.6;
	}
	.possession__values {
		display: flex;
		justify-content: space-between;
	}
	.possession__pct {
		font-size: var(--fs-ui);
		font-weight: 700;
		font-variant-numeric: tabular-nums;
		color: var(--ink);
	}
	.possession__pct--muted {
		color: var(--muted);
	}
	.possession__pct--right {
		text-align: right;
	}
</style>
