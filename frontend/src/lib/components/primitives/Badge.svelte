<script lang="ts">
	import type { Team } from '$lib/types/efi';
	import { teamColorVar, badgeTextColor } from '$lib/tokens';

	let { team, size = 'md' }: { team: Team; size?: 'sm' | 'md' } = $props();

	const textColor = $derived(badgeTextColor(team.color));
</script>

<span
	class="badge badge--{size}"
	style="background: {teamColorVar(team.color)}; color: {textColor};"
	aria-label={team.name}
>
	{team.short_code}
</span>

<style>
	.badge {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		border-radius: var(--r-sm);
		font-weight: 700;
		letter-spacing: 0.05em;
		font-variant-numeric: tabular-nums;
		white-space: nowrap;
	}
	.badge--md {
		font-size: var(--fs-ui);
		padding: var(--sp-1) var(--sp-3);
		min-height: 28px;
	}
	.badge--sm {
		font-size: var(--fs-meta);
		padding: 2px var(--sp-2);
		min-height: 22px;
	}
</style>
