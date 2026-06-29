<script lang="ts">
	import { page } from '$app/stores';
	import SectionLabel from '$lib/components/primitives/SectionLabel.svelte';
</script>

<svelte:head>
	<title>Error — EFI Data Engine</title>
</svelte:head>

<section class="error-page">
	<SectionLabel label="Error {$page.status}" color="var(--c-red)" />
	<h1 class="error-title">Something went wrong</h1>
	<p class="error-msg">{$page.error?.message ?? 'An unexpected error occurred.'}</p>
	<a href="/" class="back-link">← Back to Home</a>
</section>

<style>
	.error-page {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		gap: var(--sp-6);
		padding: var(--sp-10);
		text-align: center;
		min-height: 60vh;
	}
	.error-title {
		font-size: var(--fs-h2);
		font-weight: 800;
		color: var(--ink);
	}
	.error-msg {
		font-size: var(--fs-body);
		color: var(--muted);
		max-width: 480px;
	}
	.back-link {
		font-size: var(--fs-ui);
		font-weight: 600;
		color: var(--accent);
		text-decoration: none;
	}
	.back-link:hover {
		text-decoration: underline;
	}
</style>
