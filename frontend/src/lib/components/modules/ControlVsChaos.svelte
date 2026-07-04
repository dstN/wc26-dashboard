<script lang="ts">
	import type { MatchStats, TournamentOverview, Team } from '$lib/types/efi';
	import { teamColorVar } from '$lib/tokens';

	let {
		stats,
		overview,
		team_a,
		team_b
	}: { stats: MatchStats; overview: TournamentOverview; team_a: Team; team_b: Team } = $props();

	const W = 280;
	const H = 180;
	const PAD = 36;

	function sx(poss: number): number {
		return PAD + (poss / 100) * (W - PAD * 2);
	}
	function sy(inContest: number): number {
		return H - PAD - (inContest / 20) * (H - PAD * 2);
	}

	const chaosY = $derived(sy(overview.avg_in_contest_pct));
</script>

<figure class="module" role="img" aria-label="Control vs Chaos: Possession vs In-Contest">
	<p class="module__title">Control vs Chaos</p>
	<p class="module__sub">Possession share vs in-contest %. Chaos line = tournament median ({overview.avg_in_contest_pct}%)</p>
	<svg viewBox="0 0 {W} {H}" class="module__svg" aria-hidden="true">
		<!-- High chaos zone above line -->
		<rect x={PAD} y={PAD} width={W - PAD * 2} height={chaosY - PAD} fill="var(--c-red)" opacity="0.05" />
		<!-- Controlled zone below line -->
		<rect x={PAD} y={chaosY} width={W - PAD * 2} height={H - PAD - chaosY} fill="var(--c-lime)" opacity="0.05" />
		<!-- Chaos line -->
		<line x1={PAD} y1={chaosY} x2={W - PAD} y2={chaosY} stroke="var(--c-orange)" stroke-width="1.5" stroke-dasharray="6 3" />
		<text x={W - PAD - 2} y={chaosY - 4} font-size="7" fill="var(--c-orange)" text-anchor="end">CHAOS LINE</text>
		<!-- Axes -->
		<line x1={PAD} y1={H - PAD} x2={W - PAD} y2={H - PAD} stroke="var(--border)" stroke-width="1" />
		<line x1={PAD} y1={PAD} x2={PAD} y2={H - PAD} stroke="var(--border)" stroke-width="1" />
		<!-- Team A: (possession_team_a, in_contest) -->
		<circle cx={sx(stats.possession_team_a ?? 0)} cy={sy(stats.possession_in_contest ?? 0)} r="8" fill={teamColorVar(team_a.color)} />
		<text x={sx(stats.possession_team_a ?? 0) + 10} y={sy(stats.possession_in_contest ?? 0) + 4} font-size="9" fill={teamColorVar(team_a.color)} font-weight="700">{team_a.short_code}</text>
		<!-- Team B: (possession_team_b, in_contest) -->
		<circle cx={sx(stats.possession_team_b ?? 0)} cy={sy(stats.possession_in_contest ?? 0)} r="8" fill={teamColorVar(team_b.color)} />
		<text x={sx(stats.possession_team_b ?? 0) + 10} y={sy(stats.possession_in_contest ?? 0) + 4} font-size="9" fill={teamColorVar(team_b.color)} font-weight="700">{team_b.short_code}</text>
		<text x={W / 2} y={H - 4} font-size="8" fill="var(--muted)" text-anchor="middle">Possession %</text>
		<text x="10" y={H / 2} font-size="8" fill="var(--muted)" text-anchor="middle" transform="rotate(-90,10,{H/2})">In-Contest %</text>
	</svg>
</figure>

<style>
	.module { display: flex; flex-direction: column; gap: var(--sp-3); }
	.module__title { font-size: var(--fs-ui); font-weight: 800; color: var(--ink); }
	.module__sub { font-size: var(--fs-meta); color: var(--muted); }
	.module__svg { width: 100%; height: auto; display: block; }
</style>
