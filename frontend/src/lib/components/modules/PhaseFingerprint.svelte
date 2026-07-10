<script lang="ts">
	import type { Phase, Team } from '$lib/types/efi';
	import { phaseColor, teamColorVar } from '$lib/tokens';
	import { t } from '$lib/i18n';

	let {
		phases,
		team_a,
		team_b
	}: { phases: { team_a: Phase[]; team_b: Phase[] }; team_a: Team; team_b: Team } = $props();

	const IN_PHASES = ['Build Up Unopposed', 'Build Up Opposed', 'Progression', 'Final Third', 'Long Ball', 'Attacking Transition'];
	const PHASE_KEYS: Record<string, string> = {
		'Build Up Unopposed': 'buildUpUnopposed',
		'Build Up Opposed': 'buildUpOpposed',
		'Progression': 'progression',
		'Final Third': 'finalThird',
		'Long Ball': 'longBall',
		'Attacking Transition': 'attackingTransition',
	};

	// TS cast stays in the script block — `as`-casts in template markup have
	// repeatedly broken the rollup SSR build in this project.
	function phaseLabel(name: string): string {
		const dict: Record<string, string> = $t.phases;
		return dict[PHASE_KEYS[name]] ?? name;
	}

	const N = IN_PHASES.length;
	const CX = 120;
	const CY = 110;
	const R = 80;

	function polarPoint(i: number, pct: number): { x: number; y: number } {
		const angle = (i / N) * 2 * Math.PI - Math.PI / 2;
		const r = (pct / 100) * R;
		return { x: CX + r * Math.cos(angle), y: CY + r * Math.sin(angle) };
	}

	function teamPolygon(phases: Phase[]): string {
		const inP = phases.filter((p) => p.phase_group === 'in');
		return IN_PHASES.map((name, i) => {
			const p = inP.find((ph) => ph.phase_name === name);
			const pt = polarPoint(i, p?.pct ?? 0);
			return `${pt.x},${pt.y}`;
		}).join(' ');
	}

	function spokeLine(i: number): string {
		const pt = polarPoint(i, 100);
		return `M${CX},${CY} L${pt.x},${pt.y}`;
	}

	function labelPos(i: number): { x: number; y: number } {
		const angle = (i / N) * 2 * Math.PI - Math.PI / 2;
		const r = R + 14;
		return { x: CX + r * Math.cos(angle), y: CY + r * Math.sin(angle) };
	}

	const polyA = $derived(teamPolygon(phases.team_a));
	const polyB = $derived(teamPolygon(phases.team_b));
</script>

<figure class="module" role="img" aria-label="Phase Fingerprint radar for {team_a.name} and {team_b.name}">
	<p class="module__title">{$t.detail.phaseFingerprint}</p>
	<p class="module__sub">{$t.detail.phaseDNA}</p>
	<svg viewBox="0 0 240 220" class="module__svg" aria-hidden="true">
		<!-- Background circles -->
		{#each [25, 50, 75, 100] as ring}
			<polygon
				points={IN_PHASES.map((_, i) => {
					const pt = polarPoint(i, ring);
					return `${pt.x},${pt.y}`;
				}).join(' ')}
				fill="none"
				stroke="var(--border)"
				stroke-width="0.5"
			/>
		{/each}
		<!-- Spokes -->
		{#each IN_PHASES as _, i}
			<path d={spokeLine(i)} stroke="var(--border)" stroke-width="0.5" fill="none" />
		{/each}
		<!-- Team polygons -->
		<polygon points={polyA} fill={teamColorVar(team_a.color)} fill-opacity="0.25" stroke={teamColorVar(team_a.color)} stroke-width="2" />
		<polygon points={polyB} fill={teamColorVar(team_b.color)} fill-opacity="0.15" stroke={teamColorVar(team_b.color)} stroke-width="1.5" stroke-dasharray="4 2" />
		<!-- Labels -->
		{#each IN_PHASES as name, i}
			{@const lp = labelPos(i)}
			<text x={lp.x} y={lp.y} font-size="7" fill="var(--muted)" text-anchor="middle" dominant-baseline="middle">{phaseLabel(name)}</text>
		{/each}
	</svg>
</figure>

<style>
	.module { display: flex; flex-direction: column; gap: var(--sp-3); }
	.module__title { font-size: var(--fs-ui); font-weight: 800; color: var(--ink); }
	.module__sub { font-size: var(--fs-meta); color: var(--muted); }
	.module__svg { width: 100%; height: auto; display: block; }
</style>
