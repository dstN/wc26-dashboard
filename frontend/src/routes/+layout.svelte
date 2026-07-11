<script lang="ts">
	import '../app.css';
	import 'flag-icons/css/flag-icons.min.css';
	import { Tooltip } from 'bits-ui';
	import RainbowRail from '$lib/components/primitives/RainbowRail.svelte';
	import TopBar from '$lib/components/layout/TopBar.svelte';
	import Footer from '$lib/components/layout/Footer.svelte';
	import FloatingCompareBar from '$lib/components/layout/FloatingCompareBar.svelte';
	import { onMount } from 'svelte';
	import { initLocale, t } from '$lib/i18n';
	import type { Snippet } from 'svelte';

	import type { LayoutData } from './$types';
	let { children, data }: { children: Snippet; data: LayoutData } = $props();

	onMount(() => initLocale());
</script>

<Tooltip.Provider delayDuration={200}>
	<a class="skip-link" href="#main">{$t.a11y.skipToContent}</a>
	<RainbowRail />
	<TopBar matchCount={data.matchCount ?? 0} />
	<main id="main" tabindex="-1">
		{@render children()}
	</main>
	<Footer />
	<FloatingCompareBar />
</Tooltip.Provider>

<style>
	main {
		min-height: calc(100vh - 57px);
	}
	main:focus {
		outline: none;
	}
	/* Skip link: off-screen until keyboard-focused (WCAG 2.4.1) */
	.skip-link {
		position: absolute;
		left: 8px;
		top: -48px;
		z-index: 300;
		padding: var(--sp-2) var(--sp-4);
		background: var(--surface);
		color: var(--ink);
		border: 2px solid var(--accent);
		border-radius: var(--r-sm);
		font-size: var(--fs-ui);
		font-weight: 600;
		transition: top 0.15s ease;
	}
	.skip-link:focus {
		top: 8px;
	}
</style>
