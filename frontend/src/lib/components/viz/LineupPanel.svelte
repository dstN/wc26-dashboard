<script lang="ts">
	import { teamColorVar, badgeTextColor } from '$lib/tokens';
	import { t } from '$lib/i18n';

	interface LineupPlayer {
		id: number;
		name: string;
		position: string | null;
		jersey_number: number | null;
		minutes_played: number;
		goals: number;
		yellow_cards: number;
		red_cards: number;
	}
	interface TeamLineup {
		starters: LineupPlayer[];
		subs: LineupPlayer[];
	}
	interface Team {
		id: number;
		name: string;
		short_code: string;
		color: string;
	}

	let {
		lineup_a,
		lineup_b,
		team_a,
		team_b,
	}: { lineup_a: TeamLineup; lineup_b: TeamLineup; team_a: Team; team_b: Team } = $props();

	function playerEvents(p: LineupPlayer): string[] {
		const evs: string[] = [];
		for (let i = 0; i < p.goals; i++) evs.push('⚽');
		for (let i = 0; i < p.yellow_cards; i++) evs.push('🟨');
		for (let i = 0; i < p.red_cards; i++) evs.push('🟥');
		return evs;
	}
</script>

<div class="lineup">
	{#each [
		{ team: team_a, lu: lineup_a, side: 'a' },
		{ team: team_b, lu: lineup_b, side: 'b' },
	] as { team, lu, side }}
		<div class="lineup__col">
			<div class="lineup__team-header">
				<span
					class="lu-badge"
					style="background: {teamColorVar(team.color)}; color: {badgeTextColor(team.color)};"
				>{team.short_code}</span>
				<span class="lu-team-name">{team.name}</span>
			</div>

			{#if lu.starters.length > 0}
				<div class="lu-group">
					<span class="lu-group-label">{$t.detail.startingXI}</span>
					{#each lu.starters as p (p.id)}
						<div class="lu-row">
							<span class="lu-num">{p.jersey_number ?? '—'}</span>
							<span class="lu-pos" data-pos={p.position}>{p.position ?? ''}</span>
							<a href="/players/{p.id}" class="lu-name">{p.name}</a>
							<span class="lu-events">
								{#each playerEvents(p) as ev}{ev}{/each}
							</span>
							<span class="lu-mins">{p.minutes_played}'</span>
						</div>
					{/each}
				</div>
			{/if}

			{#if lu.subs.length > 0}
				<div class="lu-group lu-group--subs">
					<span class="lu-group-label">{$t.detail.substitutes}</span>
					{#each lu.subs as p (p.id)}
						<div class="lu-row lu-row--sub">
							<span class="lu-num">{p.jersey_number ?? '—'}</span>
							<span class="lu-pos" data-pos={p.position}>{p.position ?? ''}</span>
							<a href="/players/{p.id}" class="lu-name">{p.name}</a>
							<span class="lu-events">
								{#each playerEvents(p) as ev}{ev}{/each}
							</span>
							<span class="lu-mins">{p.minutes_played}'</span>
						</div>
					{/each}
				</div>
			{/if}
		</div>
	{/each}
</div>

<style>
	.lineup {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: var(--sp-8);
	}

	.lineup__col {
		display: flex;
		flex-direction: column;
		gap: var(--sp-4);
	}

	.lineup__team-header {
		display: flex;
		align-items: center;
		gap: var(--sp-3);
		padding-bottom: var(--sp-3);
		border-bottom: 2px solid var(--border);
	}

	.lu-badge {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		padding: 2px 8px;
		border-radius: var(--r-sm);
		font-size: var(--fs-label);
		font-weight: 800;
		letter-spacing: 0.06em;
		flex-shrink: 0;
	}
	.lu-team-name {
		font-size: var(--fs-ui);
		font-weight: 700;
		color: var(--ink);
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	.lu-group {
		display: flex;
		flex-direction: column;
		gap: 2px;
	}
	.lu-group--subs {
		opacity: 0.75;
	}

	.lu-group-label {
		font-size: var(--fs-meta);
		font-weight: 700;
		text-transform: uppercase;
		letter-spacing: 0.08em;
		color: var(--muted);
		margin-bottom: var(--sp-1);
	}

	.lu-row {
		display: grid;
		grid-template-columns: 26px 28px 1fr auto auto;
		align-items: center;
		gap: var(--sp-2);
		padding: 3px var(--sp-2);
		border-radius: var(--r-sm);
		transition: background 0.1s;
	}
	.lu-row:hover {
		background: var(--border-soft);
	}
	.lu-row--sub .lu-name {
		color: var(--muted);
	}

	.lu-num {
		font-size: var(--fs-meta);
		font-weight: 800;
		font-variant-numeric: tabular-nums;
		color: var(--muted);
		text-align: right;
	}
	.lu-pos {
		font-size: 10px;
		font-weight: 700;
		text-transform: uppercase;
		letter-spacing: 0.04em;
		color: var(--muted);
		text-align: center;
	}
	[data-pos='GK'] { color: var(--c-lime-ink); }
	[data-pos='DF'] { color: var(--c-teal-ink); }
	[data-pos='MF'] { color: var(--c-blue-ink); }
	[data-pos='FW'] { color: var(--c-red-ink); }

	.lu-name {
		font-size: var(--fs-ui);
		font-weight: 600;
		color: var(--ink);
		text-decoration: none;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}
	.lu-name:hover { color: var(--accent); }

	.lu-events {
		font-size: 12px;
		line-height: 1;
		white-space: nowrap;
		flex-shrink: 0;
	}
	.lu-mins {
		font-size: var(--fs-meta);
		font-weight: 600;
		font-variant-numeric: tabular-nums;
		color: var(--muted);
		text-align: right;
		flex-shrink: 0;
	}

	@media (max-width: 720px) {
		.lineup { grid-template-columns: 1fr; gap: var(--sp-6); }
	}
</style>
