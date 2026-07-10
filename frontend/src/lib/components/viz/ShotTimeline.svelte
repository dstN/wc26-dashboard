<script lang="ts">
	import type { Team } from '$lib/types/efi';
	import { teamTextColor } from '$lib/tokens';
	import { t } from '$lib/i18n';

	interface Shot {
		minute: number;
		player_jersey: number | null;
		player_name: string | null;
		outcome: string | null;
		body_part: string | null;
		delivery_type: string | null;
	}

	let {
		shots_a,
		shots_b,
		team_a,
		team_b,
		playerNameMap = {}
	}: { shots_a: Shot[]; shots_b: Shot[]; team_a: Team; team_b: Team; playerNameMap?: Record<string, number> } = $props();

	function outcomeClass(outcome: string | null): string {
		if (!outcome) return 'neutral';
		if (outcome.includes('Goal')) return 'goal';
		if (outcome.includes('On Target')) return 'on-target';
		if (outcome.includes('Off Target')) return 'off-target';
		return 'blocked';
	}

	const tOutcomes = $derived({
		goal: $t.detail.shotGoal,
		blocked: $t.detail.shotBlocked,
		onTarget: $t.detail.shotOnTarget,
		offTarget: $t.detail.shotOffTarget,
	});

	function outcomeLabel(outcome: string | null): string {
		if (!outcome) return '—';
		if (outcome.includes('Goal')) return tOutcomes.goal;
		if (outcome.includes('Blocked')) return tOutcomes.blocked;
		if (outcome.includes('On Target')) return tOutcomes.onTarget;
		if (outcome.includes('Off Target')) return tOutcomes.offTarget;
		return outcome.split(' - ').pop() ?? outcome;
	}

	const allShots = $derived(
		[
			...shots_a.map((s) => ({ ...s, side: 'a' as const })),
			...shots_b.map((s) => ({ ...s, side: 'b' as const })),
		].sort((x, y) => x.minute - y.minute)
	);

	// Built here (not inline in the template) — a trailing space right before
	// {/if} gets trimmed by Svelte's whitespace collapsing, which silently
	// glued the jersey number to the name (e.g. "#7Messi").
	function playerLabel(shot: Shot): string {
		const name = shot.player_name ?? '—';
		return shot.player_jersey != null ? `#${shot.player_jersey} ${name}` : name;
	}
</script>

<div class="stl">
	<div class="stl__head">
		<a href="/teams/{team_a.id}" class="stl__team" style="color: {teamTextColor(team_a.color)}">{team_a.name}</a>
		<span class="stl__center">{$t.detail.shotLog}</span>
		<a href="/teams/{team_b.id}" class="stl__team stl__team--r" style="color: {teamTextColor(team_b.color)}">{team_b.name}</a>
	</div>

	<div class="stl__table">
		<div class="stl__row stl__row--header">
			<span>{$t.detail.shotMin}</span>
			<span>{$t.detail.shotPlayer}</span>
			<span>{$t.detail.shotBody}</span>
			<span>{$t.detail.shotDelivery}</span>
			<span>{$t.detail.shotOutcome}</span>
		</div>
		{#each allShots as shot}
			{@const pColor = shot.side === 'a' ? teamTextColor(team_a.color) : teamTextColor(team_b.color)}
			{@const pId = shot.player_name ? playerNameMap[shot.player_name] : undefined}
			<div class="stl__row stl__row--{shot.side}" class:stl__row--goal={shot.outcome?.includes('Goal')}>
				<span class="stl__min">{shot.minute}'</span>
				{#if pId}
					<a href="/players/{pId}" class="stl__player stl__player--link" style="color: {pColor}">
						{playerLabel(shot)}
					</a>
				{:else}
					<span class="stl__player" style="color: {pColor}">
						{playerLabel(shot)}
					</span>
				{/if}
				<span class="stl__meta">{shot.body_part ?? '—'}</span>
				<span class="stl__meta">{shot.delivery_type ?? '—'}</span>
				<span class="stl__outcome stl__outcome--{outcomeClass(shot.outcome)}">{outcomeLabel(shot.outcome)}</span>
			</div>
		{/each}
	</div>
</div>

<style>
	.stl { width: 100%; }

	.stl__head {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding-bottom: var(--sp-3);
		border-bottom: 2px solid var(--border);
		margin-bottom: var(--sp-2);
	}
	.stl__player--link {
		text-decoration: none;
	}
	.stl__player--link:hover { text-decoration: underline; }

	.stl__team {
		font-size: var(--fs-label);
		font-weight: 800;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		text-decoration: none;
	}
	.stl__team:hover { text-decoration: underline; }
	.stl__team--r { text-align: right; }
	.stl__center {
		font-size: var(--fs-label);
		font-weight: 600;
		color: var(--muted);
		text-transform: uppercase;
		letter-spacing: 0.1em;
	}

	.stl__table { display: flex; flex-direction: column; gap: 1px; }

	.stl__row {
		display: grid;
		grid-template-columns: 44px 1fr 100px 110px 100px;
		gap: var(--sp-2);
		padding: var(--sp-2) var(--sp-1);
		border-bottom: 1px solid var(--border-soft);
		font-size: var(--fs-meta);
		align-items: center;
	}
	.stl__row:last-child { border-bottom: none; }
	.stl__row--header {
		font-weight: 700;
		text-transform: uppercase;
		letter-spacing: 0.06em;
		color: var(--muted);
		font-size: var(--fs-meta);
		padding-bottom: var(--sp-1);
	}
	.stl__row--a { background: transparent; }
	.stl__row--b { background: var(--surface); border-radius: 2px; }
	.stl__row--goal { font-weight: 700; }

	.stl__min {
		font-variant-numeric: tabular-nums;
		font-weight: 600;
		color: var(--muted);
	}
	.stl__player {
		font-weight: 600;
		font-size: var(--fs-meta);
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
	}
	.stl__meta {
		color: var(--muted);
		font-size: var(--fs-meta);
	}

	.stl__outcome {
		font-size: var(--fs-meta);
		font-weight: 700;
		border-radius: var(--r-sm);
		padding: 2px 6px;
		text-align: center;
	}
	.stl__outcome--goal { background: var(--positive); color: #fff; }
	.stl__outcome--on-target { background: var(--c-yellow); color: #0c1a10; }
	.stl__outcome--off-target { background: var(--border); color: var(--muted); }
	.stl__outcome--blocked { background: var(--c-red); color: #fff; opacity: 0.7; }
	.stl__outcome--neutral { color: var(--muted); }

	@media (max-width: 720px) {
		.stl__row {
			grid-template-columns: 36px 1fr 80px 80px;
		}
		.stl__row > :nth-child(4) { display: none; }
	}
	@media (max-width: 520px) {
		.stl__row {
			grid-template-columns: 36px 1fr 80px;
		}
		.stl__row > :nth-child(3) { display: none; }
	}
</style>
