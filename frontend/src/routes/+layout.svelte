<script lang="ts">
	import '../app.css';
	import 'flag-icons/css/flag-icons.min.css';
	import { Tooltip } from 'bits-ui';
	import RainbowRail from '$lib/components/primitives/RainbowRail.svelte';
	import TopBar from '$lib/components/layout/TopBar.svelte';
	import Footer from '$lib/components/layout/Footer.svelte';
	import FloatingCompareBar from '$lib/components/layout/FloatingCompareBar.svelte';
	import { onMount } from 'svelte';
	import { initLocale } from '$lib/i18n';
	import type { Snippet } from 'svelte';

	import type { PageData } from './$types';
	let { children, data }: { children: Snippet; data: PageData } = $props();

	onMount(() => initLocale());
</script>

<Tooltip.Provider delayDuration={200}>
	<RainbowRail />
	<TopBar matchCount={data.matchCount ?? 0} />
	<main>
		{@render children()}
	</main>
	<Footer />
	<FloatingCompareBar />
</Tooltip.Provider>

<style>
	main {
		min-height: calc(100vh - 57px);
	}
</style>
