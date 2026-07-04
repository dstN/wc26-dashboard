<script lang="ts">
	import type { DefensiveAction, MatchStats, Team } from '$lib/types/efi';
	import { teamColorVar } from '$lib/tokens';

	let {
		defensive,
		stats,
		team_a,
		team_b
	}: {
		defensive: { team_a: DefensiveAction; team_b: DefensiveAction };
		stats: MatchStats;
		team_a: Team;
		team_b: Team;
	} = $props();

	const W = 280;
	const H = 180;
	const PAD = 36;

	const maxFT = $derived(Math.max(defensive.team_a.forced_turnovers, defensive.team_b.forced_turnovers) + 4);
	const maxRT = $derived(Math.max(stats.ball_recovery_time_avg ?? 0, 6) + 1);

	function sx(rt: number): number {
		// Inverted: faster recovery (lower time) → right
		return W - PAD - (rt / maxRT) * (W - PAD * 2);
	}
	function sy(ft: number): number {
		return H - PAD - (ft / maxFT) * (H - PAD * 2);
	}
</script>

<figure class="module" role="img" aria-label="Pressing Engine: Forced Turnovers vs Ball Recovery Time">
	<p class="module__title">Pressing Engine</p>
	<p class="module__sub">Forced turnovers vs recovery speed (right = faster)</p>
	<svg viewBox="0 0 {W} {H}" class="module__svg" aria-hidden="true">
		<line x1={PAD} y1={H - PAD} x2={W - PAD} y2={H - PAD} stroke="var(--border)" stroke-width="1" />
		<line x1={PAD} y1={PAD} x2={PAD} y2={H - PAD} stroke="var(--border)" stroke-width="1" />
		<!-- Team A -->
		<circle
			cx={sx(stats.ball_recovery_time_avg ?? 0)}
			cy={sy(defensive.team_a.forced_turnovers)}
			r={defensive.team_a.pressure_on_ball === 'heavy' ? 10 : 7}
			fill={teamColorVar(team_a.color)}
			stroke={teamColorVar(team_a.color)}
			stroke-width={defensive.team_a.pressure_on_ball === 'heavy' ? 3 : 1}
			fill-opacity="0.7"
		/>
		<text x={sx(stats.ball_recovery_time_avg ?? 0) + 12} y={sy(defensive.team_a.forced_turnovers) + 4} font-size="9" fill={teamColorVar(team_a.color)} font-weight="700">{team_a.short_code} ({defensive.team_a.forced_turnovers})</text>
		<!-- Team B (uses their own ball_recovery_time — simplified: use inverse) -->
		<circle
			cx={sx(6 - (stats.ball_recovery_time_avg ?? 0) + 3)}
			cy={sy(defensive.team_b.forced_turnovers)}
			r={defensive.team_b.pressure_on_ball === 'heavy' ? 10 : 7}
			fill={teamColorVar(team_b.color)}
			stroke={teamColorVar(team_b.color)}
			stroke-width={defensive.team_b.pressure_on_ball === 'heavy' ? 3 : 1}
			fill-opacity="0.7"
		/>
		<text x={sx(6 - (stats.ball_recovery_time_avg ?? 0) + 3) + 12} y={sy(defensive.team_b.forced_turnovers) + 4} font-size="9" fill={teamColorVar(team_b.color)} font-weight="700">{team_b.short_code} ({defensive.team_b.forced_turnovers})</text>
		<text x={W / 2} y={H - 4} font-size="8" fill="var(--muted)" text-anchor="middle">Recovery Speed →</text>
		<text x="10" y={H / 2} font-size="8" fill="var(--muted)" text-anchor="middle" transform="rotate(-90,10,{H/2})">Pressing Intensity</text>
	</svg>
</figure>

<style>
	.module { display: flex; flex-direction: column; gap: var(--sp-3); }
	.module__title { font-size: var(--fs-ui); font-weight: 800; color: var(--ink); }
	.module__sub { font-size: var(--fs-meta); color: var(--muted); }
	.module__svg { width: 100%; height: auto; display: block; }
</style>
