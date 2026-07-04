<script lang="ts">
	import type { FinalThirdEntry, Team } from '$lib/types/efi';
	import { teamColorVar } from '$lib/tokens';

	let {
		final_third,
		team_a,
		team_b
	}: { final_third: { team_a: FinalThirdEntry[]; team_b: FinalThirdEntry[] }; team_a: Team; team_b: Team } = $props();

	const zones: FinalThirdEntry['zone'][] = ['left', 'left_inside', 'central', 'right_inside', 'right'];
	const zoneShort: Record<string, string> = { left: 'L', left_inside: 'LI', central: 'C', right_inside: 'RI', right: 'R' };

	const maxCount = $derived(
		Math.max(...[...final_third.team_a, ...final_third.team_b].map((e) => e.count), 1)
	);

	function dominant(entries: FinalThirdEntry[]): string {
		const top = entries.reduce((m, e) => (e.count > (m?.count ?? 0) ? e : m), entries[0]);
		return top ? zoneShort[top.zone] : '-';
	}
</script>

<figure class="module" role="img" aria-label="Penetration Map: Final third entry channels">
	<p class="module__title">Penetration Map</p>
	<p class="module__sub">Entry channels — dominant: <strong style="color: {teamColorVar(team_a.color)}">{team_a.short_code} {dominant(final_third.team_a)}</strong></p>
	<div class="pmap__bars">
		{#each zones as zone}
			{@const ea = final_third.team_a.find((e) => e.zone === zone)}
			{@const eb = final_third.team_b.find((e) => e.zone === zone)}
			<div class="pmap__zone">
				<div class="pmap__bar-pair">
					<div class="pmap__bar pmap__bar--a" style="height: {((ea?.count ?? 0) / maxCount) * 80}px; background: {teamColorVar(team_a.color)};"></div>
					<div class="pmap__bar pmap__bar--b" style="height: {((eb?.count ?? 0) / maxCount) * 80}px; background: {teamColorVar(team_b.color)};"></div>
				</div>
				<span class="pmap__label">{zoneShort[zone]}</span>
			</div>
		{/each}
	</div>
	<div class="pmap__legend">
		<span class="pmap__leg-item"><span class="pmap__dot" style="background: {teamColorVar(team_a.color)};"></span>{team_a.short_code}</span>
		<span class="pmap__leg-item"><span class="pmap__dot" style="background: {teamColorVar(team_b.color)};"></span>{team_b.short_code}</span>
	</div>
</figure>

<style>
	.module { display: flex; flex-direction: column; gap: var(--sp-3); }
	.module__title { font-size: var(--fs-ui); font-weight: 800; color: var(--ink); }
	.module__sub { font-size: var(--fs-meta); color: var(--muted); }
	.pmap__bars { display: flex; gap: var(--sp-3); align-items: flex-end; height: 100px; }
	.pmap__zone { display: flex; flex-direction: column; align-items: center; gap: var(--sp-1); flex: 1; }
	.pmap__bar-pair { display: flex; gap: 2px; align-items: flex-end; }
	.pmap__bar { width: 12px; border-radius: var(--r-sm) var(--r-sm) 0 0; min-height: 4px; transition: height 0.3s; }
	.pmap__label { font-size: var(--fs-meta); font-weight: 600; color: var(--muted); }
	.pmap__legend { display: flex; gap: var(--sp-4); }
	.pmap__leg-item { display: flex; align-items: center; gap: var(--sp-1); font-size: var(--fs-meta); color: var(--muted); }
	.pmap__dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; }
</style>
