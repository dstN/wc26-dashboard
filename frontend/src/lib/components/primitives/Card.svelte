<script lang="ts">
	let {
		padding = 'default',
		children
	}: { padding?: 'default' | 'compact' | 'none'; children?: import('svelte').Snippet } = $props();
</script>

<div class="card card--{padding}">
	{@render children?.()}
</div>

<style>
	.card {
		background: var(--surface);
		border: 1px solid var(--border);
		border-radius: var(--r-md);
		box-shadow: var(--shadow-card);
	}
	.card--default {
		padding: var(--sp-8) var(--sp-8);
	}
	.card--compact {
		padding: var(--sp-5) var(--sp-6);
	}
	.card--none {
		padding: 0;
	}
	@media (max-width: 1024px) {
		.card--default {
			padding: var(--sp-5) var(--sp-6);
		}
	}
</style>
