<script lang="ts">
	import type { MatchStats, Team } from '$lib/types/efi';
	import { teamColorVar } from '$lib/tokens';

	let { stats, team_a, team_b }: { stats: MatchStats; team_a: Team; team_b: Team } = $props();

	const W = 280;
	const H = 200;
	const PAD = 36;
	const maxXG = $derived(Math.max(stats.xg_a ?? 0, stats.xg_b ?? 0) + 1);
	const maxGoals = $derived(Math.max(stats.goals_a ?? 0, stats.goals_b ?? 0) + 1);

	function sx(xg: number): number {
		return PAD + (xg / maxXG) * (W - PAD * 2);
	}
	function sy(goals: number): number {
		return H - PAD - (goals / maxGoals) * (H - PAD * 2);
	}

	const diag = $derived(`M${sx(0)},${sy(0)} L${sx(Math.min(maxXG, maxGoals))},${sy(Math.min(maxXG, maxGoals))}`);
</script>

<figure class="module" role="img" aria-label="Efficiency Matrix: xG vs Goals">
	<p class="module__title">Efficiency Matrix</p>
	<p class="module__sub">xG vs Actual Goals — above diagonal = over-performance</p>
	<svg viewBox="0 0 {W} {H}" class="module__svg" aria-hidden="true">
		<!-- Over-performance region (above y=x line) -->
		<polygon
			points="{sx(0)},{sy(0)} {sx(maxXG)},{sy(0)} {sx(maxXG)},{sy(maxXG)}"
			fill="var(--c-lime)"
			opacity="0.08"
		/>
		<!-- Under-performance region -->
		<polygon
			points="{sx(0)},{sy(0)} {sx(0)},{sy(maxGoals)} {sx(maxGoals)},{sy(maxGoals)}"
			fill="var(--c-red)"
			opacity="0.06"
		/>
		<!-- Diagonal y=x spine -->
		<path d={diag} stroke="var(--muted)" stroke-width="1" stroke-dasharray="4 3" fill="none" />
		<!-- Axes -->
		<line x1={PAD} y1={H - PAD} x2={W - PAD} y2={H - PAD} stroke="var(--border)" stroke-width="1" />
		<line x1={PAD} y1={PAD} x2={PAD} y2={H - PAD} stroke="var(--border)" stroke-width="1" />
		<!-- Team A point: (xg_a, goals_a) -->
		<circle cx={sx(stats.xg_a ?? 0)} cy={sy(stats.goals_a ?? 0)} r="8" fill={teamColorVar(team_a.color)} />
		<text x={sx(stats.xg_a ?? 0) + 10} y={sy(stats.goals_a ?? 0) + 4} font-size="10" fill={teamColorVar(team_a.color)} font-weight="700">{team_a.short_code}</text>
		<!-- Team B point -->
		<circle cx={sx(stats.xg_b ?? 0)} cy={sy(stats.goals_b ?? 0)} r="8" fill={teamColorVar(team_b.color)} />
		<text x={sx(stats.xg_b ?? 0) + 10} y={sy(stats.goals_b ?? 0) + 4} font-size="10" fill={teamColorVar(team_b.color)} font-weight="700">{team_b.short_code}</text>
		<!-- Axis labels -->
		<text x={W / 2} y={H - 4} font-size="9" fill="var(--muted)" text-anchor="middle">Expected Goals (xG)</text>
		<text x="10" y={H / 2} font-size="9" fill="var(--muted)" text-anchor="middle" transform="rotate(-90,10,{H/2})">Goals</text>
	</svg>
	<p class="module__insight">
		<strong style="color: {teamColorVar(team_a.color)}">{team_a.name}</strong>: {stats.goals_a ?? 0} goals on {stats.xg_a ?? 0} xG
	</p>
</figure>

<style>
	.module { display: flex; flex-direction: column; gap: var(--sp-3); }
	.module__title { font-size: var(--fs-ui); font-weight: 800; color: var(--ink); }
	.module__sub { font-size: var(--fs-meta); color: var(--muted); }
	.module__svg { width: 100%; height: auto; display: block; }
	.module__insight { font-size: var(--fs-meta); color: var(--muted); }
</style>
