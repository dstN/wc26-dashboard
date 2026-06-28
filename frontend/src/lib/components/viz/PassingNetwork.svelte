<script lang="ts">
	import type { Team } from '$lib/types/efi';
	import { teamTextColor, teamColorVar } from '$lib/tokens';

	interface Connection {
		rank_no: number;
		from_name: string | null;
		to_name: string | null;
		pct_of_team_passes: number | null;
	}

	let {
		conns_a,
		conns_b,
		team_a,
		team_b,
		playerNameMap = {}
	}: { conns_a: Connection[]; conns_b: Connection[]; team_a: Team; team_b: Team; playerNameMap?: Record<string, number> } = $props();
	function shortName(full: string | null): string {
		if (!full) return '—';
		const parts = full.trim().split(' ');
		if (parts.length === 1) return full;
		return `${parts[0][0]}. ${parts[parts.length - 1]}`;
	}

	const maxPct = $derived(
		Math.max(...conns_a.map((c) => Number(c.pct_of_team_passes ?? 0)), ...conns_b.map((c) => Number(c.pct_of_team_passes ?? 0)), 1)
	);
</script>

<div class="pn">
	<div class="pn__col">
		<a href="/teams/{team_a.id}" class="pn__col-header" style="color: {teamTextColor(team_a.color)}">{team_a.name}</a>
		{#each conns_a as c}
			{@const pct = Number(c.pct_of_team_passes ?? 0)}
			{@const barW = (pct / maxPct) * 100}
			{@const fromId = c.from_name ? playerNameMap[c.from_name] : undefined}
			{@const toId = c.to_name ? playerNameMap[c.to_name] : undefined}
			<div class="pn__row">
				<span class="pn__rank">#{c.rank_no}</span>
				<div class="pn__names">
					{#if fromId}<a href="/players/{fromId}" class="pn__from pn__name-link">{shortName(c.from_name)}</a>{:else}<span class="pn__from">{shortName(c.from_name)}</span>{/if}
					<span class="pn__arrow">→</span>
					{#if toId}<a href="/players/{toId}" class="pn__to pn__name-link">{shortName(c.to_name)}</a>{:else}<span class="pn__to">{shortName(c.to_name)}</span>{/if}
				</div>
				<div class="pn__bar-wrap">
					<div class="pn__bar" style="width: {barW}%; background: {teamColorVar(team_a.color)};"></div>
				</div>
				<span class="pn__pct">{pct.toFixed(1)}%</span>
			</div>
		{/each}
	</div>

	<div class="pn__divider"></div>

	<div class="pn__col">
		<a href="/teams/{team_b.id}" class="pn__col-header" style="color: {teamTextColor(team_b.color)}">{team_b.name}</a>
		{#each conns_b as c}
			{@const pct = Number(c.pct_of_team_passes ?? 0)}
			{@const barW = (pct / maxPct) * 100}
			{@const fromId = c.from_name ? playerNameMap[c.from_name] : undefined}
			{@const toId = c.to_name ? playerNameMap[c.to_name] : undefined}
			<div class="pn__row">
				<span class="pn__rank">#{c.rank_no}</span>
				<div class="pn__names">
					{#if fromId}<a href="/players/{fromId}" class="pn__from pn__name-link">{shortName(c.from_name)}</a>{:else}<span class="pn__from">{shortName(c.from_name)}</span>{/if}
					<span class="pn__arrow">→</span>
					{#if toId}<a href="/players/{toId}" class="pn__to pn__name-link">{shortName(c.to_name)}</a>{:else}<span class="pn__to">{shortName(c.to_name)}</span>{/if}
				</div>
				<div class="pn__bar-wrap">
					<div class="pn__bar" style="width: {barW}%; background: {teamColorVar(team_b.color)};"></div>
				</div>
				<span class="pn__pct">{pct.toFixed(1)}%</span>
			</div>
		{/each}
	</div>
</div>

<style>
	.pn {
		display: grid;
		grid-template-columns: 1fr 1px 1fr;
		gap: var(--sp-5);
		align-items: start;
	}
	.pn__divider { background: var(--border); align-self: stretch; }

	.pn__col-header {
		font-size: var(--fs-label);
		font-weight: 800;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		margin-bottom: var(--sp-3);
		text-decoration: none;
		display: block;
	}
	.pn__col-header:hover { text-decoration: underline; }

	.pn__row {
		display: grid;
		grid-template-columns: 26px 1fr 60px 40px;
		align-items: center;
		gap: var(--sp-2);
		padding: var(--sp-1) 0;
		border-bottom: 1px solid var(--border-soft);
	}
	.pn__row:last-child { border-bottom: none; }

	.pn__rank {
		font-size: var(--fs-meta);
		font-weight: 700;
		color: var(--muted);
	}
	.pn__names {
		display: flex;
		align-items: center;
		gap: var(--sp-1);
		min-width: 0;
		overflow: hidden;
	}
	.pn__from, .pn__to {
		font-size: var(--fs-meta);
		font-weight: 600;
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
		color: var(--ink);
	}
	.pn__name-link {
		text-decoration: none;
	}
	.pn__name-link:hover { text-decoration: underline; }
	.pn__arrow { color: var(--muted); font-size: var(--fs-meta); flex-shrink: 0; }

	.pn__bar-wrap {
		height: 6px;
		background: var(--border);
		border-radius: 3px;
		overflow: hidden;
	}
	.pn__bar {
		height: 100%;
		border-radius: 3px;
		transition: width 0.3s ease;
		opacity: 0.7;
	}
	.pn__pct {
		font-size: var(--fs-meta);
		font-weight: 700;
		font-variant-numeric: tabular-nums;
		color: var(--muted);
		text-align: right;
	}

	@media (max-width: 720px) {
		.pn { grid-template-columns: 1fr; }
		.pn__divider { height: 1px; width: 100%; }
	}
</style>
