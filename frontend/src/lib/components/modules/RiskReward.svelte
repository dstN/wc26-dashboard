<script lang="ts">
	import type { TeamSpatial, LineBreak, Team } from '$lib/types/efi';
	import { teamColorVar } from '$lib/tokens';

	let {
		spatial,
		line_breaks,
		team_a,
		team_b
	}: {
		spatial: { team_a: TeamSpatial[]; team_b: TeamSpatial[] };
		line_breaks: { team_a: LineBreak[]; team_b: LineBreak[] };
		team_a: Team;
		team_b: Team;
	} = $props();

	const W = 280;
	const H = 200;
	const PAD = 40;

	const midA = $derived(spatial.team_a.find((s) => s.block_type === 'mid'));
	const midB = $derived(spatial.team_b.find((s) => s.block_type === 'mid'));

	const lbConcededA = $derived(line_breaks.team_b.reduce((s, lb) => s + lb.completed, 0));
	const lbConcededB = $derived(line_breaks.team_a.reduce((s, lb) => s + lb.completed, 0));

	const maxLine = $derived(Math.max(midA?.defensive_line_height ?? 0, midB?.defensive_line_height ?? 0) + 5);
	const maxLB = $derived(Math.max(lbConcededA, lbConcededB) + 5);

	function sx(lineH: number): number {
		return PAD + ((lineH) / maxLine) * (W - PAD * 2);
	}
	function sy(lb: number): number {
		return H - PAD - (lb / maxLB) * (H - PAD * 2);
	}

	const midX = W / 2;
	const midY = H / 2;
</script>

<figure class="module" role="img" aria-label="Risk/Reward: Defensive Line Height vs Line Breaks Conceded">
	<p class="module__title">Risk / Reward</p>
	<p class="module__sub">Def line height vs line breaks conceded</p>
	<svg viewBox="0 0 {W} {H}" class="module__svg" aria-hidden="true">
		<!-- Quadrant shading -->
		<rect x={PAD} y={PAD} width={midX - PAD} height={midY - PAD} fill="var(--c-lime)" opacity="0.05" />
		<rect x={midX} y={PAD} width={W - PAD - midX} height={midY - PAD} fill="var(--c-red)" opacity="0.05" />
		<rect x={PAD} y={midY} width={midX - PAD} height={H - PAD - midY} fill="var(--c-teal)" opacity="0.05" />
		<rect x={midX} y={midY} width={W - PAD - midX} height={H - PAD - midY} fill="var(--c-orange)" opacity="0.05" />
		<!-- Crosshairs -->
		<line x1={midX} y1={PAD} x2={midX} y2={H - PAD} stroke="var(--border)" stroke-width="1" />
		<line x1={PAD} y1={midY} x2={W - PAD} y2={midY} stroke="var(--border)" stroke-width="1" />
		<!-- Labels -->
		<text x={PAD + 4} y={PAD + 12} font-size="7" fill="var(--c-lime)" font-weight="700">Passive &amp; Safe</text>
		<text x={midX + 4} y={PAD + 12} font-size="7" fill="var(--c-red)" font-weight="700">Reckless</text>
		<text x={PAD + 4} y={H - PAD - 4} font-size="7" fill="var(--c-teal)" font-weight="700">Aggressive &amp; Solid</text>
		<text x={midX + 4} y={H - PAD - 4} font-size="7" fill="var(--c-orange)" font-weight="700">Passive &amp; Exposed</text>
		<!-- Axes -->
		<line x1={PAD} y1={H - PAD} x2={W - PAD} y2={H - PAD} stroke="var(--border)" stroke-width="1" />
		<line x1={PAD} y1={PAD} x2={PAD} y2={H - PAD} stroke="var(--border)" stroke-width="1" />
		<!-- Points -->
		{#if midA}
			<circle cx={sx(midA.defensive_line_height)} cy={sy(lbConcededA)} r="8" fill={teamColorVar(team_a.color)} />
			<text x={sx(midA.defensive_line_height) + 10} y={sy(lbConcededA) + 4} font-size="9" fill={teamColorVar(team_a.color)} font-weight="700">{team_a.short_code}</text>
		{/if}
		{#if midB}
			<circle cx={sx(midB.defensive_line_height)} cy={sy(lbConcededB)} r="8" fill={teamColorVar(team_b.color)} />
			<text x={sx(midB.defensive_line_height) + 10} y={sy(lbConcededB) + 4} font-size="9" fill={teamColorVar(team_b.color)} font-weight="700">{team_b.short_code}</text>
		{/if}
		<text x={W / 2} y={H - 4} font-size="8" fill="var(--muted)" text-anchor="middle">Def Line Height (m)</text>
		<text x="10" y={H / 2} font-size="8" fill="var(--muted)" text-anchor="middle" transform="rotate(-90,10,{H/2})">LB Conceded</text>
	</svg>
</figure>

<style>
	.module { display: flex; flex-direction: column; gap: var(--sp-3); }
	.module__title { font-size: var(--fs-ui); font-weight: 800; color: var(--ink); }
	.module__sub { font-size: var(--fs-meta); color: var(--muted); }
	.module__svg { width: 100%; height: auto; display: block; }
</style>
