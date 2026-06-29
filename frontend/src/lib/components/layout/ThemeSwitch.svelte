<script lang="ts">
	import { Switch } from 'bits-ui';
	import { toggleTheme, getTheme } from '$lib/theme/theme.svelte';

	const isDark = $derived(getTheme() === 'dark');
</script>

<div class="switch-wrap">
	<!-- Sun icon -->
	<svg class="theme-icon" class:theme-icon--active={!isDark} width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
		<circle cx="12" cy="12" r="5"/>
		<line x1="12" y1="1" x2="12" y2="3"/>
		<line x1="12" y1="21" x2="12" y2="23"/>
		<line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/>
		<line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
		<line x1="1" y1="12" x2="3" y2="12"/>
		<line x1="21" y1="12" x2="23" y2="12"/>
		<line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/>
		<line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
	</svg>
	<Switch.Root
		checked={isDark}
		onCheckedChange={() => toggleTheme()}
		aria-label="Toggle dark mode"
		class="switch-root"
	>
		<Switch.Thumb class="switch-thumb" />
	</Switch.Root>
	<!-- Moon icon -->
	<svg class="theme-icon" class:theme-icon--active={isDark} width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
		<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
	</svg>
</div>

<style>
	.switch-wrap {
		display: flex;
		align-items: center;
		gap: var(--sp-2);
	}
	.theme-icon {
		color: var(--border);
		flex-shrink: 0;
		transition: color 0.2s;
	}
	.theme-icon--active {
		color: var(--ink);
	}
	:global(.switch-root) {
		display: inline-flex;
		align-items: center;
		width: 36px;
		height: 20px;
		border-radius: var(--r-pill);
		background: var(--border);
		border: 1px solid var(--border);
		cursor: pointer;
		transition: background 0.2s;
		padding: 2px;
	}
	:global(.switch-root[data-state='checked']) {
		background: var(--accent);
		border-color: var(--accent);
	}
	:global(.switch-thumb) {
		display: block;
		width: 14px;
		height: 14px;
		border-radius: 50%;
		background: white;
		transition: transform 0.2s;
	}
	:global(.switch-root[data-state='checked'] .switch-thumb) {
		transform: translateX(16px);
	}
	:global([dir='rtl'] .switch-root) {
		direction: ltr;
	}
</style>
