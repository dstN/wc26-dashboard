<script lang="ts">
	import type { FinalThirdEntry, Team } from '$lib/types/efi';
	import { teamColorVar, teamTextColor } from '$lib/tokens';
	import { t } from '$lib/i18n';

	let {
		entries_a,
		entries_b,
		team_a,
		team_b
	}: { entries_a: FinalThirdEntry[]; entries_b: FinalThirdEntry[]; team_a: Team; team_b: Team } =
		$props();

	let showTeam = $state<'a' | 'b'>('a');
	const activeEntries = $derived(showTeam === 'a' ? entries_a : entries_b);
	const activeTeam = $derived(showTeam === 'a' ? team_a : team_b);

	const zoneOrder: FinalThirdEntry['zone'][] = [
		'left',
		'left_inside',
		'central',
		'right_inside',
		'right'
	];
	const zoneLabels: Record<FinalThirdEntry['zone'], string> = {
		left: 'L',
		left_inside: 'LI',
		central: 'C',
		right_inside: 'RI',
		right: 'R'
	};

	const maxCount = $derived(Math.max(...[...entries_a, ...entries_b].map((e) => e.count), 1));

	function barHeight(count: number): number {
		return Math.max(20, (count / maxCount) * 100);
	}
</script>

<!-- No role="img": the caption holds interactive team toggles that must stay
     reachable; zone counts below are labeled text. -->
<figure class="zones">
	<figcaption class="zones__caption">
		<span>{$t.detail.finalThirdEntries}</span>
		<div class="zones__toggle">
			<button
				class="zones__toggle-btn"
				class:zones__toggle-btn--active={showTeam === 'a'}
				aria-pressed={showTeam === 'a'}
				onclick={() => (showTeam = 'a')}
				style={showTeam === 'a' ? `color: ${teamTextColor(team_a.color)}` : ''}
			>
				{team_a.short_code}
			</button>
			<button
				class="zones__toggle-btn"
				class:zones__toggle-btn--active={showTeam === 'b'}
				aria-pressed={showTeam === 'b'}
				onclick={() => (showTeam = 'b')}
				style={showTeam === 'b' ? `color: ${teamTextColor(team_b.color)}` : ''}
			>
				{team_b.short_code}
			</button>
		</div>
	</figcaption>

	<div class="zones__bars">
		{#each zoneOrder as zone}
			{@const entry = activeEntries.find((e) => e.zone === zone)}
			<div class="zones__zone" class:zones__zone--central={zone === 'central'}>
				<div class="zones__bar-wrap">
					<div
						class="zones__bar"
						style="height: {barHeight(entry?.count ?? 0)}%; background: {teamColorVar(activeTeam.color)}; {zone === 'central' ? 'opacity:1;' : 'opacity:0.7;'}"
					></div>
				</div>
				<span class="zones__count">{entry?.count ?? 0}</span>
				<span class="zones__label">{zoneLabels[zone]}</span>
			</div>
		{/each}
	</div>
</figure>

<style>
	.zones {
		display: flex;
		flex-direction: column;
		gap: var(--sp-4);
	}
	.zones__caption {
		display: flex;
		align-items: center;
		justify-content: space-between;
		font-size: var(--fs-label);
		font-weight: 600;
		text-transform: uppercase;
		letter-spacing: 0.1em;
		color: var(--muted);
	}
	.zones__toggle {
		display: flex;
		gap: var(--sp-1);
	}
	.zones__toggle-btn {
		font-family: var(--font);
		font-size: var(--fs-label);
		font-weight: 700;
		letter-spacing: 0.05em;
		padding: var(--sp-1) var(--sp-3);
		border: 1px solid var(--border);
		border-radius: var(--r-sm);
		background: transparent;
		color: var(--muted);
		cursor: pointer;
		min-height: 28px;
		min-width: 44px;
		transition: all 0.15s;
	}
	.zones__toggle-btn--active {
		background: var(--surface);
		border-color: currentColor;
	}
	.zones__bars {
		display: flex;
		align-items: flex-end;
		gap: var(--sp-2);
		height: 120px;
	}
	.zones__zone {
		flex: 1;
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: var(--sp-1);
		height: 100%;
	}
	.zones__zone--central .zones__bar {
		border: 2px solid var(--border);
	}
	.zones__bar-wrap {
		flex: 1;
		width: 100%;
		display: flex;
		align-items: flex-end;
	}
	.zones__bar {
		width: 100%;
		border-radius: var(--r-sm) var(--r-sm) 0 0;
		transition: height 0.3s ease;
	}
	.zones__count {
		font-size: var(--fs-meta);
		font-weight: 700;
		font-variant-numeric: tabular-nums;
		color: var(--ink);
	}
	.zones__label {
		font-size: var(--fs-meta);
		font-weight: 600;
		color: var(--muted);
		letter-spacing: 0.05em;
	}
</style>
