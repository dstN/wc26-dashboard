<script lang="ts">
	import { getComparisonIds, getComparisonType, clearComparison, compareUrl } from '$lib/stores/comparison.svelte';

	const ids = $derived(getComparisonIds());
	const type = $derived(getComparisonType());
	const url = $derived(compareUrl());
	const label = $derived(type === 'teams' ? 'Teams' : type === 'players' ? 'Players' : '');
</script>

{#if ids.length >= 2}
	<div class="cbar" role="status" aria-live="polite">
		<span class="cbar__count">{ids.length}</span>
		<span class="cbar__label">{label} selected</span>
		<a href={url} class="cbar__btn">Compare →</a>
		<button class="cbar__clear" onclick={clearComparison} aria-label="Clear comparison">✕</button>
	</div>
{/if}

<style>
	.cbar {
		position: fixed;
		bottom: var(--sp-6);
		left: 50%;
		transform: translateX(-50%);
		display: flex;
		align-items: center;
		gap: var(--sp-4);
		padding: var(--sp-3) var(--sp-6);
		background: var(--ink);
		color: var(--bg);
		border-radius: var(--r-pill);
		box-shadow: 0 8px 24px rgba(0,0,0,0.35);
		z-index: 300;
		white-space: nowrap;
		animation: bar-in 0.2s ease;
	}

	@keyframes bar-in {
		from { opacity: 0; transform: translateX(-50%) translateY(12px); }
		to   { opacity: 1; transform: translateX(-50%) translateY(0); }
	}

	.cbar__count {
		font-size: var(--fs-ui);
		font-weight: 900;
		font-variant-numeric: tabular-nums;
		background: var(--accent);
		color: var(--accent-fg);
		border-radius: 50%;
		width: 24px;
		height: 24px;
		display: inline-flex;
		align-items: center;
		justify-content: center;
		flex-shrink: 0;
	}

	.cbar__label {
		font-size: var(--fs-ui);
		font-weight: 600;
		opacity: 0.8;
	}

	.cbar__btn {
		font-size: var(--fs-ui);
		font-weight: 700;
		color: var(--bg);
		text-decoration: none;
		padding: var(--sp-1) var(--sp-4);
		background: var(--accent);
		border-radius: var(--r-pill);
		transition: opacity 0.15s;
	}
	.cbar__btn:hover { opacity: 0.85; }

	.cbar__clear {
		background: transparent;
		border: none;
		color: var(--bg);
		cursor: pointer;
		font-size: var(--fs-ui);
		opacity: 0.7;
		padding: 0 var(--sp-1);
		transition: opacity 0.15s;
	}
	.cbar__clear:hover { opacity: 1; }
</style>
