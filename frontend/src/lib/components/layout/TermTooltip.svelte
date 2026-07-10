<script lang="ts">
	import { Tooltip } from 'bits-ui';
	import type { Snippet } from 'svelte';

	let {
		term,
		definition,
		children
	}: { term: string; definition: string; children?: Snippet } = $props();
</script>

<Tooltip.Provider delayDuration={200}>
	<Tooltip.Root>
		<Tooltip.Trigger>
			{#snippet child({ props })}
				<span {...props} class="trigger" aria-label="{term}: {definition}">
					{@render children?.()}
				</span>
			{/snippet}
		</Tooltip.Trigger>
		<Tooltip.Content class="tooltip-content" sideOffset={4} avoidCollisions={true} collisionPadding={12}>
			<p class="tooltip-term">{term}</p>
			<p class="tooltip-def">{definition}</p>
			<Tooltip.Arrow class="tooltip-arrow" />
		</Tooltip.Content>
	</Tooltip.Root>
</Tooltip.Provider>

<style>
	.trigger {
		text-decoration: underline dotted var(--muted);
		cursor: help;
	}
	:global(.tooltip-content) {
		max-width: 260px;
		background: var(--ink);
		color: var(--bg);
		border-radius: var(--r-sm);
		padding: var(--sp-3) var(--sp-4);
		font-size: var(--fs-meta);
		z-index: 200;
		white-space: normal;
		word-break: break-word;
		line-height: 1.45;
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
	}
	.tooltip-term {
		font-weight: 700;
		margin-bottom: 4px;
	}
	.tooltip-def {
		font-weight: 400;
		opacity: 0.85;
		line-height: 1.5;
	}
	:global(.tooltip-arrow) {
		fill: var(--ink);
	}
</style>
